"""
Test pipeline with environmental query from supervisor.py
"""

import asyncio
from src.agents.pipeline import SupervisorPipeline
from src.validation.ragas_validator import RAGASValidator
from src.services.llm_provider import LLMProvider
from src.validation.agent_output_processor import AgentOutputProcessor
from src.api.models import QueryRequest
from src.utils.pretty_print import pretty_print_messages
from src.utils.logging_config import setup_logging

# Setup logging to see debug messages
setup_logging()


async def main_pipeline():
    """
    Legacy main pipeline function for backward compatibility.
    Now uses the new SupervisorPipeline class with validation.
    """
    # Create validation components
    llm_provider = LLMProvider()
    ragas_validator = RAGASValidator(llm_provider=llm_provider)
    agent_output_processor = AgentOutputProcessor()
    
    # Create pipeline with validation
    pipeline = SupervisorPipeline(
        llm_provider=llm_provider,
        ragas_validator=ragas_validator,
        agent_output_processor=agent_output_processor
    )
    
    # Example query - can be modified for testing
    query_request = QueryRequest(
        query_text="What are the primary environmental challenges India is facing?",
        collection_name="docs",
        k=2,
        enable_validation=True
    )
    
    print(f"Processing query: {query_request.query_text}")
    print(f"Collection: {query_request.collection_name}")
    print(f"Results count (k): {query_request.k}")
    print("-" * 50)
    
    # Process the query
    result = await pipeline.process_query(query_request)
    
    # Print results
    print(f"Status: {result.status}")
    print(f"Execution time: {result.metadata.get('execution_time_seconds', 0)}s")
    print(f"Agents used: {result.metadata.get('agents_used', [])}")
    print("-" * 50)
    print("Result:")
    print(result.result)
    
    # Print validation scores if available
    if result.validation:
        print("-" * 50)
        print("RAGAS Validation:")
        print(f"Passed: {result.validation.get('passed', 'N/A')}")
        print(f"Overall Score: {result.validation.get('overall_score', 'N/A')}")
        if 'metrics' in result.validation:
            print("Metrics:")
            for metric, score in result.validation['metrics'].items():
                print(f"  {metric}: {score:.3f}")
    else:
        print("-" * 50)
        print("RAGAS Validation: Not available")
    
    return result


def main():
    """Main entry point for the supervisor script"""
    asyncio.run(main_pipeline())


# For backward compatibility and direct testing
if __name__ == "__main__":
    main()
