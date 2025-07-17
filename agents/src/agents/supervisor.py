"""
Legacy supervisor module - now refactored to use the pipeline.
This module can still be used for direct testing or legacy compatibility.
"""

import asyncio
from src.agents.pipeline import SupervisorPipeline
from src.api.models import QueryRequest
from src.utils.pretty_print import pretty_print_messages


async def main_pipeline():
    """
    Legacy main pipeline function for backward compatibility.
    Now uses the new SupervisorPipeline class.
    """
    pipeline = SupervisorPipeline()
    
    # Example query - can be modified for testing
    query_request = QueryRequest(
        query_text="What are the primary environmental challenges India is facing?",
        collection_name="docs",
        k=2
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
    
    return result


def main():
    """Main entry point for the supervisor script"""
    asyncio.run(main_pipeline())


# For backward compatibility and direct testing
if __name__ == "__main__":
    main()