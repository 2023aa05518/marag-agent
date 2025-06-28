
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
# from mcp_utils import ClientSession


def get_mcp_server_config():
    server_config ={
            "chroma": {
                "url": "http://localhost:8000/sse", 
                "transport": "sse",
                # "tenant": "stp",
                # "database": "support"
            }
    }
    
    return server_config


# asyncio.run( get_mcp_tools())