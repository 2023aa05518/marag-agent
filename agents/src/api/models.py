"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query_text: str = Field(..., description="The query text to process")
    collection_name: str = Field(default="docs", description="ChromaDB collection name")
    k: int = Field(default=2, description="Number of results to fetch")
    enable_validation: bool = Field(default=False, description="Enable RAGAS validation of the response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_text": "What are the primary environmental challenges India is facing?",
                "collection_name": "docs",
                "k": 2,
                "enable_validation": True
            }
        }


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    status: str = Field(..., description="Status of the request (success/error)")
    result: str = Field(..., description="The processed result from agents")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "result": "Environmental challenges in India include air pollution, water scarcity...",
                "metadata": {
                    "agents_used": ["retriever_query_agent", "critique_agent"],
                    "execution_time_seconds": 5.2,
                    "tokens_used": 1250
                },
                "timestamp": "2025-07-07T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now)
