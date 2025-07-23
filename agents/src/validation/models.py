
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class RAGASInput(BaseModel):
    """Input model for RAGAS evaluation"""
    question: str
    contexts: List[str]
    answer: str
    ground_truth: Optional[str] = None


class ValidationResult(BaseModel):
    """Result of validation evaluation"""
    passed: bool
    overall_score: float
    metrics: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    should_retry: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationConfig(BaseModel):
    """Configuration for validation thresholds"""
    faithfulness_threshold: float = 0.7
    answer_relevancy_threshold: float = 0.7
    context_precision_threshold: float = 0.6
    context_recall_threshold: float = 0.6
    overall_threshold: float = 0.65
    max_retries: int = 2
    enabled: bool = True