import logging
from typing import Dict, List
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy, 
    context_precision,
    context_recall
)
from datasets import Dataset

from .models import RAGASInput, ValidationResult, ValidationConfig

logger = logging.getLogger(__name__)


class RAGASValidator:
    def __init__(self, config: ValidationConfig = None):
        self.config = config or ValidationConfig()
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
        logger.debug("RAGASValidator initialized")
    
    async def validate_response(self, validation_input: RAGASInput) -> ValidationResult:
        try:
            logger.info(f"Starting RAGAS validation for question: {validation_input.question[:50]}...")
            
            dataset = Dataset.from_dict({
                "question": [validation_input.question],
                "contexts": [validation_input.contexts],
                "answer": [validation_input.answer],
                "ground_truth": [validation_input.ground_truth] if validation_input.ground_truth else [None]
            })
            
            result = evaluate(dataset, metrics=self.metrics)
            
            metrics = {
                "faithfulness": result["faithfulness"],
                "answer_relevancy": result["answer_relevancy"],
                "context_precision": result["context_precision"],
                "context_recall": result["context_recall"]
            }
            
            overall_score = sum(metrics.values()) / len(metrics)
            passed = self._check_validation_passed(metrics, overall_score)
            recommendations = self._generate_recommendations(metrics)
            
            validation_result = ValidationResult(
                passed=passed,
                overall_score=overall_score,
                metrics=metrics,
                recommendations=recommendations,
                should_retry=not passed and overall_score > 0.4
            )
            
            logger.info(f"RAGAS validation completed: passed={passed}, score={overall_score:.3f}")
            return validation_result
            
        except Exception as e:
            logger.error(f"RAGAS validation failed: {e}", exc_info=True)
            return ValidationResult(
                passed=False,
                overall_score=0.0,
                recommendations=[f"Validation error: {str(e)}"],
                should_retry=True
            )
    
    def _check_validation_passed(self, metrics: Dict[str, float], overall_score: float) -> bool:
        return (
            metrics["faithfulness"] >= self.config.faithfulness_threshold and
            metrics["answer_relevancy"] >= self.config.answer_relevancy_threshold and
            metrics["context_precision"] >= self.config.context_precision_threshold and
            metrics["context_recall"] >= self.config.context_recall_threshold and
            overall_score >= self.config.overall_threshold
        )
    
    def _generate_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        recommendations = []
        
        if metrics["faithfulness"] < self.config.faithfulness_threshold:
            recommendations.append("Improve answer faithfulness - ensure claims are supported by context")
        
        if metrics["answer_relevancy"] < self.config.answer_relevancy_threshold:
            recommendations.append("Improve answer relevancy - address the question more directly")
        
        if metrics["context_precision"] < self.config.context_precision_threshold:
            recommendations.append("Improve context precision - retrieve more relevant context")
        
        if metrics["context_recall"] < self.config.context_recall_threshold:
            recommendations.append("Improve context recall - retrieve more comprehensive context")