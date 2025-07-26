from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class LLMProviderEnum(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"


class LLMConfig(BaseModel):
    model_name: str
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None
    max_retries: int = Field(default=2, ge=0, le=10)
    api_key_env: str


class LLMProviderConfig(BaseModel):
    gemini: LLMConfig = Field(
        default=LLMConfig(
            model_name="gemini-2.0-flash",
            api_key_env="GOOGLE_API_KEY"
        )
    )
    openai: LLMConfig = Field(
        default=LLMConfig(
            model_name="gpt-4",
            api_key_env="OPENAI_API_KEY"
        )
    )
    default_provider: LLMProviderEnum = LLMProviderEnum.GEMINI
