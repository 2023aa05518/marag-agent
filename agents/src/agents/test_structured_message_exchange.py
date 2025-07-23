from typing import Any, List
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.utils.llm_utils import get_llm
from src.utils.mcp_utils import get_mcp_server_config
from src.api.models import QueryRequest
from src.agents.ragas_integration import comprehensive_evaluation, show_results
from src.agents.test_message_extractor import MessageParser

import logging


logger = logging.getLogger(__name__)


def _create_retriever_agent(tools: List[Any]) -> Any:
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

def _create_supervisor_agent(agents: List[Any]) -> Any:
    """Create a supervisor agent for coordination"""
    return create_supervisor(
        model=get_llm(),
        agents=agents,
        prompt=(
            "You are a supervisor managing agents:\n"
            "- A retriever agent for document queries.\n"
            "Workflow:\n"
            "1. Assign the query to the retriever agent to get relevant information.\n"
            "2. Once the retriever agent returns results, analyze and synthesize the information.\n"
            "3. Provide a comprehensive final answer based on the retrieved information.\n"
            "4. Format the answer in a clear, human-readable way.\n"
            "Your goal is to ensure the user gets a complete and well-formatted response to their query."
        ),
        add_handoff_back_messages=True,
        output_mode="full_history",
    ).compile()

def _format_query(request: QueryRequest) -> str:
    """Format user query for agents"""
    return f"query_text= {request.query_text}. Fetch results k={request.k}. from collection name={request.collection_name}. Format the results in human readable form and generate output in separate rows."


query_request = QueryRequest(
    query_text="What are the primary environmental challenges India is facing?"
)

async def pipeline() -> Any:  # FIXED: Simplified parameters, removed unused ones
    try:
        client = MultiServerMCPClient(get_mcp_server_config())
        async with client.session("chroma") as session:
            tools = await load_mcp_tools(session)
            
            retriever_agent = _create_retriever_agent(tools)  # FIXED: Removed 'self'
            supervisor = _create_supervisor_agent([retriever_agent])
            
            messages = []  # FIXED: Initialize messages list
            chunk = None   # FIXED: Initialize chunk
            
            logger.info("Starting supervisor agent pipeline")
            async for chunk in supervisor.astream(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": _format_query(query_request),  # FIXED: Use QueryRequest object
                        }
                    ]
                },
                # config={"callbacks": [opik_tracer]}
            ):
                if chunk:
                    messages.append(chunk)
            
            if chunk is not None:
                final_message_history = chunk["supervisor"]["messages"]
                ragas_input = MessageParser().to_ragas_input(final_message_history)
                evaluation_results = await comprehensive_evaluation(ragas_input)
                return evaluation_results
            else:
                return {"error": "No output from supervisor."}
            
    except Exception as e:
        logger.error(f"Error in pipeline: {e}", exc_info=True)
        return {"error": str(e)}

def show(results: dict) -> None:
    show_results(results)

async def main():
    result = await pipeline()
    if 'error' in result:
        print(f"Error: {result['error']}")
    elif 'parsed_data' in result:
        parsed = result['parsed_data']
        print(f"Question: {parsed.question}")
        print(f"Contexts: {parsed.contexts}")
        print(f"Answer: {parsed.answer}")
        print("\n" + "="*50)
        show_results(result)
    else:
        print("Unexpected result format")
        print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
