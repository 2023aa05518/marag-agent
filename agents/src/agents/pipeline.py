"""
SupervisorPipeline: Multi-agent processing pipeline with supervisor coordination.
Features dynamic agent creation and tool-based retrieval.
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from opik.integrations.langchain import OpikTracer

from src.utils.llm_utils import get_llm
from src.utils.mcp_utils import get_mcp_server_config
from src.api.models import QueryRequest, QueryResponse

# Setup logging
logger = logging.getLogger(__name__)


class SupervisorPipeline:
    """
    Multi-agent processing pipeline with supervisor coordination.
    Creates agents dynamically per query and coordinates their execution.
    """
    
    def __init__(self, ragas_validator=None, agent_output_processor=None):
        self.client = None
        self._initialized = False
        self.ragas_validator = ragas_validator
        self.agent_output_processor = agent_output_processor
        logger.debug("SupervisorPipeline instance created")
    
    async def initialize(self):
        """Initialize MCP client"""
        if self._initialized:
            return
            
        # Setup MCP client only - tools and agents will be created per query
        # Note: MultiServerMCPClient doesn't need explicit connect() call
        self.client = MultiServerMCPClient(get_mcp_server_config())
        self._initialized = True
        logger.info("SupervisorPipeline initialized")
    
    def _create_retriever_agent(self, tools: List[Any]) -> Any:
        """Create a retriever agent with available tools"""
        return create_react_agent(
            name="retriever_query_agent",
            model=get_llm(),
            tools=tools,
            prompt=(
                "You are a document retriever agent. your job is to query collection and return the relevant records\n\n"
                "INSTRUCTIONS:\n"
                "- extract the collection name from query text . if not present then return with valid reason and ask for collection information."
                "- query collection name using given query_text "
                "- Return tenent and database name along with collection name in the response to supervisor"
                "- Assist ONLY with retrieving query results related to vector database, DO NOT do any other activity\n"
                "- After you're done with your tasks, respond to the supervisor directly\n"
                "- Respond ONLY with the results of your work, do NOT include ANY other text."
            )
        )
    
    def _create_critique_agent(self) -> Any:
        """Create a critique agent for answer evaluation"""
        return create_react_agent(
            name="critique_agent",
            model=get_llm(),
            tools=[],
            prompt=(
                "You are a critique agent. Your job is to judge the answer and the context retrieved by the retriever agent.\n\n"
                "INSTRUCTIONS:\n"
                "- Check if the answer is supported by the provided context.\n"
                "- If you find hallucination (information not present in the context) , "
                "- Respond with a message to the supervisor to re-run the query with more context.\n"
                "- If the answer is from the provided context , respond with 'APPROVED' and a brief justification.\n"
                "- Respond ONLY with your judgment and reasoning, do NOT include any other text."
            )
        )
    
    def _create_supervisor_agent(self, agents: List[Any]) -> Any:
        """Create a supervisor agent for coordination"""
        return create_supervisor(
            model=get_llm(),
            agents=agents,
            prompt=(
                "You are a supervisor managing agents:\n"
                "- A retriever agent for document queries.\n"
                "- A critique agent (judge) to check for hallucination and completeness.\n"
                "Workflow:\n"
                "1. Assign the query to the retriever agent.\n"
                "2. Pass the retriever's answer and context to the critique agent.\n"
                "3. If the critique agent requests more context, re-run the retriever agent with an expanded query.\n"
                "4. Repeat process only one time the critique agent approves the answer.\n"
                "Do not do any work yourself. Assign work to one agent at a time."
            ),
            add_handoff_back_messages=True,
            output_mode="full_history",
        ).compile()
    
    def _format_query(self, request: QueryRequest) -> str:
        """Format user query for agents"""
        return f"query_text= {request.query_text}. Fetch results k={request.k}. from collection name={request.collection_name}. Format the results in human readable form and generate output in separate rows."
    
    async def process_query(self, request: QueryRequest) -> QueryResponse:
        """
        Process a query through the multi-agent system.
        
        Args:
            request: QueryRequest containing query details
            
        Returns:
            QueryResponse with results and metadata
        """
        start_time = time.time()
        
        try:
            # Ensure pipeline is initialized
            await self.initialize()
            
            # Create fresh session for this query
            async with self.client.session("chroma") as session:
                # Load tools for this session
                tools = await load_mcp_tools(session)
                
                # Create agents for this query
                retriever_agent = self._create_retriever_agent(tools)
                critique_agent = self._create_critique_agent()
                
                # Create supervisor with agents
                supervisor = self._create_supervisor_agent([retriever_agent, critique_agent])
                
                # Format the query
                formatted_query = self._format_query(request)
                
                # Setup Opik tracer
                opik_tracer = OpikTracer(
                    graph=supervisor.get_graph(xray=True),
                    tags=["multi-agent", "marag"],
                    metadata={"environment": "development", "version": "1.0"}
                )
                
                # Process query through supervisor
                logger.info("Starting supervisor agent pipeline")
                chunk = None
                messages = []
                
                async for chunk in supervisor.astream(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": formatted_query,
                            }
                        ]
                    },
                    config={"callbacks": [opik_tracer]}
                ):
                    if chunk:
                        messages.append(chunk)
                
                # Extract final result
                logger.debug(f"Pipeline result extraction starting, chunk available: {chunk is not None}")
                if chunk is not None:
                    final_message_history = chunk["supervisor"]["messages"]
                    # Get the last message as the final answer
                    final_answer = final_message_history[-1].content if final_message_history else "No answer generated"
                else:
                    final_answer = "No output from supervisor."
                
                logger.debug(f"Final answer extracted: {len(final_answer)} characters")
                execution_time = time.time() - start_time
                
                # Prepare metadata
                metadata = {
                    "agents_used": ["retriever_query_agent", "critique_agent", "supervisor"],
                    "execution_time_seconds": round(execution_time, 2),
                    "collection_name": request.collection_name,
                    "k_results": request.k,
                    "total_chunks": len(messages),
                    "tools_available": len(tools)
                }
                
                logger.debug(f"Validation check - enable_validation: {getattr(request, 'enable_validation', 'MISSING')}")
                
                # Run RAGAS validation if enabled
                validation_result = None
                logger.debug(f"Validation components - enable_validation: {request.enable_validation}, "
                           f"has_ragas_validator: {self.ragas_validator is not None}, "
                           f"has_agent_output_processor: {self.agent_output_processor is not None}")
                if request.enable_validation and self.ragas_validator and self.agent_output_processor:
                    try:
                        # Prepare agent outputs for validation
                        agent_outputs = {
                            "messages": final_message_history,
                            "supervisor_result": final_answer
                        }
                        
                        # LOG 1: Pipeline sending to AgentOutputProcessor
                        logger.debug(f"Pipeline sending to AgentOutputProcessor: {len(final_message_history)} messages, "
                                   f"supervisor result: {len(final_answer)} chars")
                        
                        # Process outputs to RAGAS format
                        ragas_input = self.agent_output_processor.prepare_ragas_input(
                            query=request.query_text,
                            agent_outputs=agent_outputs
                        )
                        
                        # Validate with RAGAS
                        validation = await self.ragas_validator.validate_response(ragas_input)
                        
                        validation_result = {
                            "passed": validation.passed,
                            "overall_score": validation.overall_score,
                            "metrics": validation.metrics
                        }
                        
                    except Exception as e:
                        logger.error(f"RAGAS validation failed: {e}")
                        validation_result = {
                            "passed": False,
                            "error": str(e)
                        }
                
                return QueryResponse(
                    status="success",
                    result=final_answer,
                    metadata=metadata,
                    validation=validation_result
                )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            return QueryResponse(
                status="error",
                result=f"Pipeline execution failed: {str(e)}",
                metadata={
                    "execution_time_seconds": round(execution_time, 2),
                    "error_type": type(e).__name__
                }
            )


# Global pipeline instance (singleton pattern)
_pipeline_instance = None

async def get_pipeline() -> SupervisorPipeline:
    """Get or create pipeline instance"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = SupervisorPipeline()
        await _pipeline_instance.initialize()
    return _pipeline_instance
