from src.utils.llm_utils import get_llm
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from src.utils.pretty_print import pretty_print_messages
import asyncio
from src.utils.mcp_utils import get_mcp_server_config
from langchain.schema import HumanMessage
# from chromadb.config import Settings
# from IPython.display import display, Image
# MODEL = get_llm()
# Your supervisor would become:
from opik.integrations.langchain import OpikTracer

# Create tracer with graph visualization

async  def main_pipeline():
    # settings = settings()
    # settings.te
    client = MultiServerMCPClient(get_mcp_server_config())
    async with client.session("chroma") as session:
        tools = await load_mcp_tools(session)

        retriever_query_agent = create_react_agent(
            name="retriever_query_agent",
            model=get_llm(),
            tools=tools,
            prompt=(
                "You are a document retriever agent. your job is to query collection and return  the relevant records\n\n"
                
                "INSTRUCTIONS:\n"
                "- extract the collection name from query text . if not present then return with valid reason and ask for collection information."
                "- query collection name  using  given query_text "
                "- Return tenent and database name along with collection name in the response to supervisor"
                "- Assist ONLY with retrieving query results related to vector database, DO NOT do any other activity\n"
                "- After you're done with your tasks, respond to the supervisor directly\n"
                "- Respond ONLY with the results of your work, do NOT include ANY other text."
            )
        )

        doc_count_agent = create_react_agent(
            name="doc_count_agent",
            model=get_llm(),
            tools=tools,
            prompt=(
                "You are a document count agent. your job is to count the documents from collection\n\n"
                "INSTRUCTIONS:\n"
                "- extract the collection name from query text . if not present then return with valid reason and ask for collection information."
                "- Assist ONLY with getting document counts, DO NOT do any other activity\n"
                "- After you're done with your tasks, respond to the supervisor directly\n"
                "- Respond ONLY with the results of your work, do NOT include ANY other text."
            )
        )

        critique_agent = create_react_agent(
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

        supervisor = create_supervisor(
            model=get_llm(),
            agents=[retriever_query_agent, critique_agent],
            # agents=[retriever_query_agent],
            prompt=(
                "You are a supervisor managing agents:\n"
                "- A retriever agent for document queries.\n"
                # "- A doc count agent for counting documents.\n"
                "- A critique agent (judge) to check for hallucination and completeness.\n"
                "Workflow:\n"
                "1. Assign the query to the retriever agent.\n"
                "2. Pass the retriever's answer and context to the critique agent.\n"
                "3. If the critique agent requests more context, re-run the retriever agent with an expanded query.\n"
                "4. Repeat process only one  time the critique agent approves the answer.\n"
                "Do not do any work yourself. Assign work to one agent at a time."
            ),
            add_handoff_back_messages=True,
            output_mode="full_history",
        ).compile()

        chunk = None
        query = """
                query_text=  What are the primary environmental challenges india is facing. Fetch results k=2.
                from collection name=docs .  
                Format the resutls in human readable form and generate output in separate rows.


                """
        opik_tracer = OpikTracer(
            graph=supervisor.get_graph(xray=True),
            tags=["multi-agent", "marag"],
            metadata={"environment": "development", "version": "1.0"}
        )
        async for chunk in supervisor.astream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"{query}",
                        # HumanMessage(content=query)
                    }
                ]
            },config={"callbacks":[opik_tracer]}
        ):
            pretty_print_messages(chunk, last_message=True)

        if chunk is not None:
            final_message_history = chunk["supervisor"]["messages"]
            # print(final_message_history)
        else:
            print("No output from supervisor.")

# display(Image(supervisor.get_graph().draw_mermaid_png()))

# To run:
if __name__ == "__main__":
    asyncio.run(main_pipeline())