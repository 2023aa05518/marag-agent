"""
Pydantic schemas for structured agent responses.
Ensures consistent, type-safe communication between agents.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class RetrieverResponse(BaseModel):
    """Structured response from retriever agent"""
    content: str = Field(description="The main answer or response")
    sources: List[str] = Field(description="List of source documents or contexts")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of how the answer was derived")
    next_action: Literal["complete", "retry", "continue"] = Field(description="Recommended next action")


class CritiqueResponse(BaseModel):
    """Structured response from critique agent"""
    content: str = Field(description="Evaluation summary and feedback")
    confidence: float = Field(description="Confidence in the critique", ge=0.0, le=1.0)
    reasoning: str = Field(description="Detailed reasoning for the critique")
    next_action: Literal["complete", "retry", "continue"] = Field(description="Recommended next action")
    issues_found: List[str] = Field(default_factory=list, description="Specific issues identified")
