import os
from langchain_google_genai import ChatGoogleGenerativeAI
# from mcp_utils import ClientSession
# from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

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