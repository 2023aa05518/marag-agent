"""
SupervisorPipeline: Multi-agent processing pipeline with supervisor coordination.
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

from src.services import LLMProvider
from src.utils.mcp_utils import get_mcp_server_config
from src.api.models import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)


class SupervisorPipeline:
    
    def __init__(self, llm_provider: LLMProvider, ragas_validator=None, agent_output_processor=None):
        self.llm_provider = llm_provider
        self.client = None
        self._initialized = False
        self.ragas_validator = ragas_validator
        self.agent_output_processor = agent_output_processor
    
    async def initialize(self):
        if self._initialized:
            return
        self.client = MultiServerMCPClient(get_mcp_server_config())
        self._initialized = True
        logger.info("Pipeline: Started")
    
    def _create_retriever_agent(self, tools: List[Any]) -> Any:
        logger.info("Agent: Retriever started")
        agent = create_react_agent(
            name="retriever_query_agent",
            model=self.llm_provider.get("gemini"),
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
                "- If you cannot find any relevant context, respond with 'No context available to answer this question' and exit no further action needed."
            )
        )
        logger.info("Agent: Retriever completed")
        return agent
    
    def _create_critique_agent(self) -> Any:
        logger.info("Agent: Critique started")
        agent = create_react_agent(
            name="critique_agent",
            model=self.llm_provider.get("gemini"),
            tools=[],
            prompt=(
                "You are a critique agent. Your job is to judge the answer and the context retrieved by the retriever agent.\n\n"
                "INSTRUCTIONS:\n"
                "- Check if the answer is supported by the provided context.\n"
                "- If you find hallucination (information not present in the context) , "
                "- Respond with a message to the supervisor to re-run the query with more context.\n"
                "- If the answer is from the provided context , respond with 'APPROVED' and a brief justification.\n"
                "- Respond ONLY with your judgment and reasoning, do NOT include any other text."
                "- If you cannot find any relevant context, respond with 'No context available to answer this question' and exit no further action needed."
            )
        )
        logger.info("Agent: Critique completed")
        return agent
    
    def _create_supervisor_agent(self, agents: List[Any]) -> Any:
        logger.info("Agent: Supervisor started")
        agent = create_supervisor(
            model=self.llm_provider.get("gemini"),
            agents=agents,
            prompt=(
                "You are a supervisor managing agents:\n"
                "- A retriever agent for document queries.\n"
                "- A critique agent (judge) to check for hallucination and completeness.\n"
                "Workflow:\n"
                "- Assign the query to the retriever agent.\n"
                "- If the retriever agent returns no results then send user response 'No context available to answer this question' and exit no further action needed \n"
                "- If the retriever agent returns results: then only pass the results to the critique agent.\n"
                "- If the critique agent requests more context, re-run the retriever agent with an expanded query.\n"
                "- Repeat process only one time the critique agent approves the answer.\n"
                "- Do not do any work yourself. Assign work to one agent at a time."
            ),
            add_handoff_back_messages=True,
            output_mode="full_history",
        ).compile()
        logger.info("Agent: Supervisor completed")
        return agent
    
    def _format_query(self, request: QueryRequest) -> str:
        return f"query_text= {request.query_text}. Fetch results k={request.k}. from collection name={request.collection_name}. Format the results in human readable form and generate output in separate rows."
    
    async def process_query(self, request: QueryRequest) -> QueryResponse:
        start_time = time.time()
        try:
            await self.initialize()
            async with self.client.session("chroma") as session:
                tools = await load_mcp_tools(session)
                retriever_agent = self._create_retriever_agent(tools)
                critique_agent = self._create_critique_agent()
                supervisor = self._create_supervisor_agent([retriever_agent, critique_agent])
                formatted_query = self._format_query(request)
                opik_tracer = OpikTracer(
                    graph=supervisor.get_graph(xray=True),
                    tags=["multi-agent", "marag"],
                    metadata={"environment": "development", "version": "1.0"}
                )
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
                if chunk is not None:
                    final_message_history = chunk["supervisor"]["messages"]
                    final_answer = final_message_history[-1].content if final_message_history else "No answer generated"
                else:
                    final_answer = "No output from supervisor."
                execution_time = time.time() - start_time
                metadata = {
                    "agents_used": ["retriever_query_agent", "critique_agent", "supervisor"],
                    "execution_time_seconds": round(execution_time, 2),
                    "collection_name": request.collection_name,
                    "k_results": request.k,
                    "total_chunks": len(messages),
                    "tools_available": len(tools)
                }
                validation_result = None
                if request.enable_validation and self.ragas_validator and self.agent_output_processor:
                    logger.info("Validation: RAGAS started")
                    try:
                        agent_outputs = {
                            "messages": final_message_history,
                            "supervisor_result": final_answer
                        }
                        ragas_input = self.agent_output_processor.prepare_ragas_input(
                            query=request.query_text,
                            agent_outputs=agent_outputs
                        )
                        validation = await self.ragas_validator.validate_response(ragas_input)
                        logger.info("Validation: RAGAS completed")
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
                logger.info("Pipeline: Completed")
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


# Global pipeline instance
_pipeline_instance = None

async def get_pipeline() -> SupervisorPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = SupervisorPipeline()
        await _pipeline_instance.initialize()
    return _pipeline_instance
