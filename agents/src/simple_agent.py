# from langchain_mcp_adapters.tools import load_mcp_tools
# from langgraph.prebuilt import create_react_agent
# from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
# import asyncio
# import os
# from dotenv import load_dotenv
# from mcp import ClientSession, StdioServerParameters, stdio_client

# # Load environment variables from .env file
# load_dotenv()


# def get_llm():
#         # Get Google API key from environment variable
#     google_api_key = os.getenv("GOOGLE_API_KEY")
#     if not google_api_key:
#         raise ValueError("GOOGLE_API_KEY environment variable is not set")

#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.0-flash",
#         temperature=0,
#         max_tokens=None,
#         timeout=None,
#         max_retries=2,
#         api_key=google_api_key,
       
#     )
#     return llm
# def get_mcp_server():
#     mcp = StdioServerParameters(
#         command='uvx',
#         args=['src/chroma-mcp/src/chroma_mcp/server.py'] 
#     )
#     return mcp

# async def main():

#     llm = get_llm()
#     mcp = get_mcp_server()

#     async with stdio_client(mcp) as (read,write):
#         async with ClientSession() as session:
#             await session.initialize()
#             tools = await load_mcp_tools(session=session)
#             agent = create_react_agent(model=llm,tools=tools)
#             response = await agent.ainvoke({"messages":"get list of tools"})
#             print (f"response : {response}")

#     # # Create the agent
#     # agent = create_react_agent(llm, mcp)

#     # # Invoke the agent
#     # result = await agent.invoke({"input": "Give me list of tools available"})

#     # print(result)

# if __name__ == "__main__":
#     # Run the async main function
#     asyncio.run(main())


import os
import asyncio
from dotenv import load_dotenv
import sys
from pathlib import Path
import traceback
import subprocess
import time

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
# Removed unused ChatOpenAI import
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from mcp import ClientSession, StdioServerParameters, stdio_client
from mcp.shared.exceptions import McpError

# Load environment variables from .env file
load_dotenv()

# def get_google_llm():
#     # Get Google API key from environment variable
#     google_api_key = os.getenv("GOOGLE_API_KEY")
#     if not google_api_key:
#         raise ValueError("GOOGLE_API_KEY environment variable is not set")
    
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.0-flash",
#         temperature=0,
#         max_tokens=None,
#         timeout=None,
#         max_retries=2,
#         api_key=google_api_key,
#     )
#     return llm

def get_openai_llm():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=openai_api_key,
    )
    return llm
# def get_mcp_server():
#     mcp = StdioServerParameters(
#         command='python',
#         # args=['src/chroma-mcp/src/chroma_mcp/server.py'] 
#         args=['.\loader\simple_server.py'] 
#     )
#     return mcp

def get_server_path():
    # Get the current script's directory
    current_dir = Path(__file__).parent.absolute()
    # Construct path to simple_server.py
    server_path = current_dir / "simple_server.py"
    if not server_path.exists():
        raise FileNotFoundError(f"Server script not found at: {server_path}")
    return str(server_path)

def verify_server_process(server_path: str) -> bool:
    """Verify that the server process can be started"""
    try:
        # Try to start the server process
        process = subprocess.Popen(
            [sys.executable, server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(1)
        
        # Check if process is still running
        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            print(f"Server process failed to start. Exit code: {process.returncode}")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False
            
        # Process is running, terminate it
        process.terminate()
        process.wait()
        return True
    except Exception as e:
        print(f"Error verifying server process: {str(e)}")
        return False

async def initialize_session(session: ClientSession):
    """Initialize the MCP session with retries"""
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            print(f"Initializing session (attempt {attempt + 1}/{max_retries})...")
            await session.initialize()
            print("Session initialized successfully")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Session initialization failed: {str(e)}")
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print("Session initialization failed after all retries")
                raise

async def main():
    try:
        llm = get_openai_llm()
        server_path = get_server_path()
        
        print(f"Verifying server at: {server_path}")
        if not verify_server_process(server_path):
            raise RuntimeError("Server process verification failed")
        
        print(f"Starting server from: {server_path}")
        mcp = StdioServerParameters(
            command=sys.executable,  # Use the current Python interpreter
            args=[server_path],
        )

        async with stdio_client(mcp) as (read_stream, write_stream):
            try:
                async with ClientSession(read_stream=read_stream, write_stream=write_stream) as session:
                    # Initialize session with retries
                    await initialize_session(session)
                    
                    print("Loading tools...")
                    tools = await load_mcp_tools(session=session)
                    print(f"Loaded {len(tools)} tools")
                    
                    print("Creating agent...")
                    agent = create_react_agent(model=llm, tools=tools)
                    
                    print("Invoking agent...")
                    response = await agent.ainvoke({"input": "what is 4 + 2"})
                    print(f"Response: {response}")
            except McpError as e:
                print(f"MCP Error: {str(e)}")
                print("Stack trace:")
                traceback.print_exc()
                raise
            except Exception as e:
                print(f"Error during session: {str(e)}")
                print("Stack trace:")
                traceback.print_exc()
                raise
    except Exception as e:
        print(f"Error in main: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
        sys.exit(1)
