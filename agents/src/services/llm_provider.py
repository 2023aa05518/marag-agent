import os
import logging
from typing import Any, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from .schemas.llm_schemas import LLMProviderConfig, LLMProviderEnum

load_dotenv()
logger = logging.getLogger(__name__)


class LLMProvider:
    
    def __init__(self, config: Optional[LLMProviderConfig] = None):
        self.config = config or LLMProviderConfig()
        
    def get(self, provider: Optional[str] = None) -> Any:
        provider_enum = self._resolve_provider(provider)
        return self._create_llm(provider_enum)
    
    def _resolve_provider(self, provider: Optional[str]) -> LLMProviderEnum:
        if provider is None:
            return self.config.default_provider
        
        provider_lower = provider.lower()
        provider_map = {p.value: p for p in LLMProviderEnum}
        
        if provider_lower not in provider_map:
            available = ", ".join(provider_map.keys())
            raise ValueError(f"Unknown provider '{provider}'. Available: {available}")
        
        return provider_map[provider_lower]
    
    def _create_llm(self, provider: LLMProviderEnum) -> Any:
        creators = {
            LLMProviderEnum.GEMINI: self._create_gemini,
            LLMProviderEnum.OPENAI: self._create_openai,
        }
        
        creator = creators.get(provider)
        if not creator:
            raise ValueError(f"No creator for provider: {provider.value}")
        
        try:
            return creator()
        except Exception as e:
            logger.error(f"Failed to create {provider.value} LLM: {e}")
            raise
    
    def _create_gemini(self) -> ChatGoogleGenerativeAI:
        config = self.config.gemini
        api_key = os.getenv(config.api_key_env)
        
        if not api_key:
            raise ValueError(f"{config.api_key_env} not set")
        
        return ChatGoogleGenerativeAI(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries,
            api_key=api_key,
        )
    
    def _create_openai(self) -> ChatOpenAI:
        config = self.config.openai
        api_key = os.getenv(config.api_key_env)
        
        if not api_key:
            raise ValueError(f"{config.api_key_env} not set")
        
        return ChatOpenAI(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries,
            api_key=api_key,
        )
