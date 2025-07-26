import asyncio
import os
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio
from src.utils.mcp_utils import get_mcp_server_config
from src.services import LLMProvider
from src.loader.doc_loader import loader_pipeline
import  json
from chromadb.config import Settings


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
    # settings = Settings(tenant="default", database="default")
    client = MultiServerMCPClient(get_mcp_server_config())

    async with client.session("chroma") as session:
        tools = await load_mcp_tools(session)
 
        llm_provider = LLMProvider()
        llm = llm_provider.get("gemini")
        agent = create_react_agent(llm, tools)
 
        # Example flow:
        # 1. Instantiate collection
        # resp=await agent.ainvoke({"messages":[{"role":"user",
        #                                   "content":"create_collection name=docs .  once created get the list of collection "}
        #                                 ]
        #                     })
 
        # # # 2. Add docs
        # doc_collection = loader_pipeline()
        # if doc_collection["ids"]:
        #     content_str = f"add documents in database = default_database   collection  name=docs ids={doc_collection['ids']!r} docs={doc_collection['documents']!r} metadatas={doc_collection['metadatas']!r}"
        #     resp=await agent.ainvoke({"messages":[{"role":"user","content": f" check for  collection name   if exist  delete it and recreate {content_str}"}]})
        #     print(resp)
 
        # 3. Query docs
        # resp = await agent.ainvoke({"messages":[{"role":"user","content":
        #     "query collection name=docs query_text=\"What are the primary environmental challenges facing India\" k=2"}]})
 
        # print(resp)
        print ("======================================================\n")
        # prprint(resp)
 
if __name__ == "__main__":
    asyncio.run(main())