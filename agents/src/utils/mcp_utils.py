
import asyncio
import logging
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

logger = logging.getLogger(__name__)


def get_mcp_server_config():
    logger.debug("Creating MCP server configuration")
    
    server_config = {
        "chroma": {
            "url": "http://localhost:8000/sse", 
            "transport": "sse",
            # "tenant": "stp",
            # "database": "support"
        }
    }
    
    return server_config
