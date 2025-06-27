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

# from IPython.display import display, Image
# MODEL = get_llm()

async  def main_pipeline():
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


        supervisor = create_supervisor(
            model=get_llm(),
            # model=init_chat_model(get_llm()),
            # agents=[retriever_query_agent ],
            agents=[retriever_query_agent ,  doc_count_agent],
            prompt=(
                "You are a supervisor managing agents:\n"
                "- a retriever agent. Assign document query retrieval related tasks to this agent\n"
                "-  a doc count agent. assign count related task to  this agent"
                "Assign work to one agent at a time, do not call agents in parallel.\n"
                "Do not do any work yourself."
            ),
            add_handoff_back_messages=True,
            output_mode="full_history",
        ).compile()

        chunk = None
        query = """
                query_text=  What are the primary environmental challenges india is facing. Fetch results k=2 from collection name=my_docs .  
                Get the total doucment in the collection.
                Format the resutls in human readable form and generate output in separate rows.


                """
        async for chunk in supervisor.astream(
            {
                "messages": [
                    {
                        # "role": "user",
                        # "content": f"{query}",
                        HumanMessage(content=query)
                    }
                ]
            }
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