"""
FastAPI dependencies for multi-agent MARAG system.
Centralized dependency creation and management.
"""

import logging
from fastapi import Depends
from src.agents.pipeline import SupervisorPipeline
from src.validation.ragas_validator import RAGASValidator
from src.validation.agent_output_processor import AgentOutputProcessor

# Setup logging
logger = logging.getLogger(__name__)


async def get_ragas_validator() -> RAGASValidator:
    """
    Create and return a RAGASValidator instance.
    
    This dependency function handles the creation and initialization
    of the RAGAS validator for response validation.
    
    Returns:
        RAGASValidator: Ready-to-use validator instance
        
    Raises:
        Exception: If validator creation fails
    """
    try:
        logger.debug("Creating RAGASValidator instance")
        
        # Create validator instance with default config
        validator = RAGASValidator()
        
        logger.debug("RAGASValidator created successfully")
        return validator
        
    except Exception as e:
        logger.error(f"Failed to create RAGASValidator: {str(e)}")
        raise Exception(f"Validator creation failed: {str(e)}")


async def get_agent_output_processor() -> AgentOutputProcessor:
    """
    Create and return an AgentOutputProcessor instance.
    
    This dependency function handles the creation of the agent output
    processor for extracting contexts and answers from agent responses.
    
    Returns:
        AgentOutputProcessor: Ready-to-use processor instance
        
    Raises:
        Exception: If processor creation fails
    """
    try:
        logger.debug("Creating AgentOutputProcessor instance")
        
        # Create processor instance
        processor = AgentOutputProcessor()
        
        logger.debug("AgentOutputProcessor created successfully")
        return processor
        
    except Exception as e:
        logger.error(f"Failed to create AgentOutputProcessor: {str(e)}")
        raise Exception(f"Processor creation failed: {str(e)}")


async def get_supervisor_pipeline(
    ragas_validator: RAGASValidator = Depends(get_ragas_validator),
    agent_output_processor: AgentOutputProcessor = Depends(get_agent_output_processor)
) -> SupervisorPipeline:
    """
    Create and return a SupervisorPipeline instance with validation dependencies.
    
    This dependency function handles the creation and initialization
    of the supervisor pipeline with RAGAS validation capabilities.
    
    Args:
        ragas_validator: RAGAS validator instance for response validation
        agent_output_processor: Processor for extracting contexts and answers
    
    Returns:
        SupervisorPipeline: Ready-to-use pipeline instance with validation
        
    Raises:
        Exception: If pipeline creation or initialization fails
    """
    try:
        logger.debug("Creating SupervisorPipeline instance with validation dependencies")
        
        # Create pipeline instance with validation dependencies
        pipeline = SupervisorPipeline(
            ragas_validator=ragas_validator,
            agent_output_processor=agent_output_processor
        )
        
        # Initialize if needed (the pipeline handles session-per-query internally)
        await pipeline.initialize()
        
        logger.debug("SupervisorPipeline with validation created successfully")
        return pipeline
        
    except Exception as e:
        logger.error(f"Failed to create SupervisorPipeline with validation: {str(e)}")
        raise Exception(f"Pipeline creation failed: {str(e)}")
