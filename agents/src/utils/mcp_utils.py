
import asyncio
import logging
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
# from mcp_utils import ClientSession

# Setup logging
logger = logging.getLogger(__name__)


def get_mcp_server_config():
    """
    Get MCP server configuration for ChromaDB.
    
    Returns:
        dict: Server configuration dictionary
    """
    logger.debug("Creating MCP server configuration")
    
    server_config = {
        "chroma": {
            "url": "http://localhost:8000/sse", 
            "transport": "sse",
            # "tenant": "stp",
            # "database": "support"
        }
    }
    
    logger.debug(f"MCP server config created: {server_config}")
    return server_config


# asyncio.run( get_mcp_tools())