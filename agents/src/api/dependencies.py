"""
FastAPI dependencies for multi-agent MARAG system.
Centralized dependency creation and management.
"""

import logging
from fastapi import Depends
from src.agents.pipeline import SupervisorPipeline
from src.validation.ragas_validator import RAGASValidator
from src.validation.agent_output_processor import AgentOutputProcessor
from src.services import LLMProvider, LLMProviderConfig

logger = logging.getLogger(__name__)


def get_llm_config() -> LLMProviderConfig:
    return LLMProviderConfig()

async def get_llm_provider(
    config: LLMProviderConfig = Depends(get_llm_config)
) -> LLMProvider:
    try:
        provider = LLMProvider(config)
        logger.info("Dependencies: Injected LLMProvider")
        return provider
    except Exception as e:
        logger.error(f"LLMProvider creation failed: {e}")
        raise


async def get_gemini_llm(llm_provider: LLMProvider = Depends(get_llm_provider)):
    try:
        gemini = llm_provider.get("gemini")
        logger.info("Dependencies: Injected Gemini LLM object")
        return gemini
    except Exception as e:
        logger.error(f"Gemini LLM creation failed: {e}")
        raise


async def get_openai_llm(llm_provider: LLMProvider = Depends(get_llm_provider)):
    try:
        openai = llm_provider.get("openai")
        logger.info("Dependencies: Injected OpenAI LLM object")
        return openai
    except Exception as e:
        logger.error(f"OpenAI LLM creation failed: {e}")
        raise


async def get_ragas_validator(
    llm_provider: LLMProvider = Depends(get_llm_provider)
) -> RAGASValidator:
    try:
        validator = RAGASValidator(llm_provider=llm_provider)
        logger.info("Dependencies: Injected RAGASValidator")
        return validator
    except Exception as e:
        logger.error(f"RAGASValidator creation failed: {e}")
        raise


async def get_agent_output_processor() -> AgentOutputProcessor:
    try:
        processor = AgentOutputProcessor()
        logger.info("Dependencies: Injected AgentOutputProcessor")
        return processor
    except Exception as e:
        logger.error(f"AgentOutputProcessor creation failed: {e}")
        raise


async def get_supervisor_pipeline(
    llm_provider: LLMProvider = Depends(get_llm_provider),
    ragas_validator: RAGASValidator = Depends(get_ragas_validator),
    agent_output_processor: AgentOutputProcessor = Depends(get_agent_output_processor)
) -> SupervisorPipeline:
    try:
        pipeline = SupervisorPipeline(
            llm_provider=llm_provider,
            ragas_validator=ragas_validator,
            agent_output_processor=agent_output_processor
        )
        logger.info("Dependencies: Injected SupervisorPipeline")
        await pipeline.initialize()
        return pipeline
    except Exception as e:
        logger.error(f"SupervisorPipeline creation failed: {e}")
        raise
