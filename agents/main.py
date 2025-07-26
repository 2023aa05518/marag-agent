"""
FastAPI application for multi-agent MARAG system.
Provides RESTful API endpoints for document retrieval and analysis.
"""

import os
import sys
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import time
import uuid

# Add project root to path for imports
# sys.path.append(os.path.dirname(__file__))

from src.api.router import router
from src.utils.logging_config import setup_logging

# Setup centralized logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Multi-Agent MARAG API...")
    logger.info("Pipeline will be initialized per request")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-Agent MARAG API...")


# Create FastAPI app
app = FastAPI(
    title="Multi-Agent MARAG API",
    description="RESTful API for document retrieval and analysis using multi-agent system with ChromaDB",
    version="1.0.0",
    lifespan=lifespan
)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses"""
    logger.info("API: Received query request")
    response = await call_next(request)
    logger.info("API: Responded to query")
    return response


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Multi-Agent MARAG API is running",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_endpoints": "/api/v1/",
        "health": "/api/v1/health"
    }


def main():
    """Main entry point for running the FastAPI application"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8100,
        # reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()

# Run the application with Uvicorn using below command on command prompt:

# uvicorn main:app --host 0.0.0.0 --port 8100 --reload