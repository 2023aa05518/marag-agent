import os
import asyncio
import json
from datetime import datetime
from typing import Any, Dict, Union
from dotenv import load_dotenv
import sys

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
# Removed unused ChatOpenAI import
from langchain_google_genai import ChatGoogleGenerativeAI
# from mcp import ClientSession
from langchain_mcp_adapters.client import MultiServerMCPClient

# Load environment variables from .env file
load_dotenv()

def convert_response_to_json(response: Any) -> str:
    """
    Convert agent response to valid JSON string.
    Handles various response types including LangGraph agent responses.
    """
    try:
        # If response is already a string, try to parse and re-serialize
        if isinstance(response, str):
            try:
                parsed = json.loads(response)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                # If not valid JSON, wrap it in a JSON object
                return json.dumps({"content": response}, indent=2, ensure_ascii=False)
        
        # If response is a dict-like object
        if hasattr(response, '__dict__') or isinstance(response, dict):
            response_dict = response.__dict__ if hasattr(response, '__dict__') else response
            return json.dumps(response_dict, indent=2, ensure_ascii=False, default=json_serializer)
        
        # For other types, convert to string and wrap
        return json.dumps({"response": str(response)}, indent=2, ensure_ascii=False)
        
    except Exception as e:
        # Fallback: create error response
        return json.dumps({
            "error": f"Failed to serialize response: {str(e)}",
            "original_response": str(response),
            "timestamp": datetime.now().isoformat()
        }, indent=2, ensure_ascii=False)

def json_serializer(obj: Any) -> Any:
    """
    Custom JSON serializer for objects that aren't natively JSON serializable.
    """
    if hasattr(obj, 'isoformat'):  # datetime objects
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):  # custom objects
        return obj.__dict__
    elif hasattr(obj, 'to_dict'):  # objects with to_dict method
        return obj.to_dict()
    elif isinstance(obj, (set, tuple)):  # collections
        return list(obj)
    else:
        return str(obj)

def extract_agent_response_content(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract meaningful content from LangGraph agent response.
    """
    extracted = {
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }
    
    # Extract messages if available
    if "messages" in response:
        messages = response["messages"]
        if messages:
            last_message = messages[-1] if isinstance(messages, list) else messages
            if hasattr(last_message, 'content'):
                extracted["content"] = last_message.content
            elif isinstance(last_message, dict) and "content" in last_message:
                extracted["content"] = last_message["content"]
            else:
                extracted["content"] = str(last_message)
        
        # Include all messages for context
        extracted["all_messages"] = [
            {
                "type": getattr(msg, 'type', 'unknown'),
                "content": getattr(msg, 'content', str(msg))
            } for msg in (messages if isinstance(messages, list) else [messages])
        ]
    
    # Include any other relevant fields
    for key, value in response.items():
        if key not in ["messages"] and not key.startswith("_"):
            extracted[key] = value
    
    return extracted

def get_llm():
    # Get Google API key from environment variable
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=google_api_key,
    )
    return llm

# def get_openai_llm():
#     openai_api_key = os.getenv("OPENAI_API_KEY")
#     if not openai_api_key:
#         raise ValueError("OPENAI_API_KEY environment variable is not set")

#     llm = ChatOpenAI(
#         model="gpt-3.5-turbo",
#         temperature=0,
#         max_tokens=None,
#         timeout=None,
#         max_retries=2,
#         api_key=openai_api_key,
#     )
#     return llm

async def main(query):
    try:
        llm = get_llm()
        # llm = get_openai_llm()
        
        # Initialize MultiServerMCPClient
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
                
                print("Creating agent...")
                agent = create_react_agent(model=llm, tools=tools)
                
                print("Invoking agent...")
                # response = await agent.ainvoke({"messages": "what's (30 + 5) x 2?"})
                response = await agent.ainvoke({"messages": query})
                
                # Convert response to JSON
                print("Converting response to JSON...")
                
                # Method 1: Extract meaningful content and convert to JSON
                extracted_content = extract_agent_response_content(response)
                json_response = convert_response_to_json(extracted_content)
                
                print("=== EXTRACTED CONTENT AS JSON ===")
                print(json_response)
                
                # Method 2: Convert full response to JSON (for debugging)
                full_json_response = convert_response_to_json(response)
                print("\n=== FULL RESPONSE AS JSON ===")
                print(full_json_response)
                
                # Method 3: Save to file
                with open("agent_response.json", "w", encoding="utf-8") as f:
                    f.write(json_response)
                print("\n=== JSON saved to agent_response.json ===")
                
                return json_response
                
        except Exception as e:
            print(f"Error during session: {str(e)}")
            raise
                
    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise


def get_query():
    
    # query = "do nothing"
    # query = "Give me list of collection for tenants umtest and databases testdb use chroma list collection "
    #Note:  create a new database is not supported.   This is a good test to see that ai is not doing anything unexpected.
  
    # query = "create a new database umeshdb " 
    
    # query = "create a collection with name professional_services. add a document with name 'test' and content 'this is a test document' to the collection professional_services"
    
    # query =  "give list of collection in database umeshdb"
    
    query ="how many documents are in the collection professional_services in database umeshdb"

    # query = "give me a sample question  to test the leadership  capabilities using  database docs"
    # query = "delete collection leadership_test_cases"
    # query = "give me few behavioral questions from tenent ptc and database docs"
    # query = "how many documents are in the collection pdf_chunks in database docs"
    
    
    return query

if __name__ == "__main__":
    try:
        
        asyncio.run(main(query=get_query()))
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)
