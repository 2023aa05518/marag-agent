import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
# from mcp_utils import ClientSession
# from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

def get_llm():
    """
    Create and return a ChatGoogleGenerativeAI instance.
    
    Returns:
        ChatGoogleGenerativeAI: Configured LLM instance
        
    Raises:
        ValueError: If GOOGLE_API_KEY is not set
        Exception: If LLM creation fails
    """
    try:
        logger.debug("Creating LLM instance")
        
        # Get Google API key from environment variable
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.error("GOOGLE_API_KEY environment variable is not set")
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        logger.debug("Google API key found, creating ChatGoogleGenerativeAI instance")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=google_api_key,
        )
        
        logger.debug("LLM instance created successfully")
        return llm
        
    except Exception as e:
        logger.error(f"Failed to create LLM instance: {e}", exc_info=True)
        raise