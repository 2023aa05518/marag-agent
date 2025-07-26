
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
import time
import uuid
from typing import Dict, Any

from src.api.models import QueryRequest, QueryResponse, ErrorResponse
from src.agents.pipeline import SupervisorPipeline
from src.api.dependencies import get_supervisor_pipeline

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Multi-Agent Query"])

@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Process Query with Multi-Agent System",
    description="Submit a query to be processed by the retriever and critique agents"
)
async def process_query(
    request: QueryRequest,
    pipeline: SupervisorPipeline = Depends(get_supervisor_pipeline)
) -> QueryResponse:
   
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        logger.info(f"[{request_id}] Starting query processing")
        
        result = await pipeline.process_query(request)
        
        execution_time = time.time() - start_time
        
        if result.status == "success":
            logger.info(f"[{request_id}] Query processed successfully in {execution_time:.2f}s")
        else:
            logger.warning(f"[{request_id}] Query processing failed after {execution_time:.2f}s: {result.result}")
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"[{request_id}] Unexpected error processing query after {execution_time:.2f}s: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the multi-agent system is healthy and ready"
)
async def health_check(
    pipeline: SupervisorPipeline = Depends(get_supervisor_pipeline)
) -> Dict[str, Any]:

    health_check_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        logger.debug(f"[{health_check_id}] Performing health check")
        
        await pipeline.initialize()
        
        execution_time = time.time() - start_time
        logger.info(f"[{health_check_id}] Health check passed in {execution_time:.3f}s")
        
        return {
            "status": "healthy",
            "service": "multi-agent-marag",
            "pipeline_initialized": pipeline._initialized,
            "response_time_ms": round(execution_time * 1000, 2),
            "message": "Multi-agent system is ready to process queries"
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"[{health_check_id}] Health check failed after {execution_time:.3f}s: {str(e)}", exc_info=True)
        
        return {
            "status": "unhealthy",
            "service": "multi-agent-marag",
            "response_time_ms": round(execution_time * 1000, 2),
            "error": str(e),
            "message": "Multi-agent system is not ready"
        }


@router.get(
    "/",
    summary="API Information",
    description="Get information about the multi-agent API"
)
async def api_info() -> Dict[str, Any]:

    return {
        "service": "Multi-Agent MARAG System",
        "version": "1.0.0",
        "description": "RESTful API for document retrieval and analysis using multi-agent system",
        "endpoints": {
            "POST /api/v1/query": "Process query with multi-agent system",
            "GET /api/v1/health": "Health check endpoint",
            "GET /api/v1/": "API information"
        },
        "agents": [
            "retriever_query_agent - Retrieves relevant documents from ChromaDB",
            "critique_agent - Validates responses for hallucinations"
        ]
    }


@router.get(
    "/metrics",
    summary="Performance Metrics",
    description="Get performance and operational metrics for monitoring"
)
async def get_metrics(
    pipeline: SupervisorPipeline = Depends(get_supervisor_pipeline)
) -> Dict[str, Any]:

    metrics_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        logger.debug(f"[{metrics_id}] Collecting metrics")
        
        pipeline_metrics = pipeline.get_performance_metrics()
        
        execution_time = time.time() - start_time
        
        metrics = {
            "timestamp": time.time(),
            "service": "multi-agent-marag",
            "version": "1.0.0",
            "metrics_collection_time_ms": round(execution_time * 1000, 2),
            "pipeline": pipeline_metrics,
            "endpoints": {
                "total_requests": "N/A",  
                "active_requests": "N/A",
                "error_rate": "N/A"
            }
        }
        
        logger.debug(f"[{metrics_id}] Metrics collected in {execution_time:.3f}s")
        return metrics
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"[{metrics_id}] Failed to collect metrics after {execution_time:.3f}s: {str(e)}", exc_info=True)
        
        return {
            "timestamp": time.time(),
            "service": "multi-agent-marag",
            "status": "error",
            "error": str(e),
            "collection_time_ms": round(execution_time * 1000, 2)
        }
