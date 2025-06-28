
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
# from mcp_utils import ClientSession

async def get_mcp_tools():
    try:
      

        client = MultiServerMCPClient(
            {
                "mcp_server": {
                    "url": "http://localhost:8000/sse", 
                    "transport": "sse"
                }
            }
        )
        
        try:
            print("Getting session...")
            async with client.session("mcp_server") as session:
                print("Loading tools...")
                tools = await load_mcp_tools(session=session)
                print(f"Loaded {len(tools)} tools")
                print(f"Available tools :")
                for  tool in tools:
                    print(f"\t  {tool.name}")
                
                return tools
                
        except Exception as e:
            print(f"Error during session: {str(e)}")
            raise
                
    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise

# asyncio.run( get_mcp_tools())


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