import asyncio
import os
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio
from src.utils.mcp_utils import get_mcp_server_config
from src.utils.llm_utils import get_llm
from src.loader.doc_loader import main_pipeline
import  json
from src.agents.pretty_print import pretty_print_messages


def prprint(resp, indent=0):
    """Pretty print agent responses, parsing nested JSON strings if possible."""
    prefix = " " * indent
    if isinstance(resp, str):
        # Try to parse as JSON
        try:
            parsed = json.loads(resp)
            prprint(parsed, indent=indent)
        except (json.JSONDecodeError, TypeError):
            print(prefix + resp)
    elif isinstance(resp, dict):
        for k, v in resp.items():
            print(f"{prefix}{k}:")
            prprint(v, indent=indent + 2)
    elif isinstance(resp, list):
        for i, item in enumerate(resp):
            print(f"{prefix}- [{i}]")
            prprint(item, indent=indent + 2)
    else:
        print(prefix + str(resp))


async def main():

    client = MultiServerMCPClient(get_mcp_server_config())

    async with client.session("chroma") as session:
        tools = await load_mcp_tools(session)
 
        llm = get_llm()
        agent = create_react_agent(llm, tools)
 
        # Example flow:
        # 1. Instantiate collection
        # await agent.ainvoke({"messages":[{"role":"user",
        #                                   "content":"create_collection name=my_docs .  once created get the list of collection "}
        #                                 ]
        #                     })
 
        # # 2. Add docs
        # doc_collection = main_pipeline()
        # if doc_collection["ids"]:
        #     content_str = f"add documents incollection  name=my_docs ids={doc_collection['ids']!r} docs={doc_collection['documents']!r} metadatas={doc_collection['metadatas']!r}"
        #     await agent.ainvoke({"messages":[{"role":"user","content": content_str}]})
 
        # 3. Query docs
        resp = await agent.ainvoke({"messages":[{"role":"user","content":
            "query collection name=my_docs query_text=\"What are the primary environmental challenges facing India\" k=2"}]})
 
        print(resp)
        print ("======================================================\n")
        prprint(resp)
 
if __name__ == "__main__":
    asyncio.run(main())