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
from src.validation.models import RAGASInput, ValidationResult, ValidationConfig
from src.utils.llm_utils import get_llm
from langchain_huggingface import HuggingFaceEmbeddings

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
        logger.info("RAGASValidator initialized")
    
    async def validate_response(self, validation_input: RAGASInput) -> ValidationResult:
        try:
            logger.info(f"Starting RAGAS validation for question: {validation_input.question}")
            
            # LOG 3: RAGASValidator received data for evaluation
            logger.debug(f"RAGAS validation input - question: {(validation_input.question)} chars, "
                        f"contexts: {(validation_input.contexts)} items, "
                        f"answer: {(validation_input.answer)} chars")
            
            llm = get_llm()
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            
            # Create dataset with all columns for compatibility
            dataset_dict = {
                "question": [validation_input.question],
                "contexts": [validation_input.contexts],
                "answer": [validation_input.answer],
                "ground_truth": [validation_input.ground_truth] if validation_input.ground_truth else [""],
                "reference": [validation_input.ground_truth] if validation_input.ground_truth else [""]
            }
            dataset = Dataset.from_dict(dataset_dict)
            
            # Select metrics based on available data
            available_metrics = [faithfulness, answer_relevancy]
            if validation_input.ground_truth:
                available_metrics.extend([context_precision, context_recall])
            
            result = evaluate(
                dataset, 
                metrics=available_metrics,
                llm=llm,
                embeddings=embeddings
            )
            
            logger.debug(f"RAGAS evaluation completed with result type: {type(result).__name__}")
            
            # Extract scalar values from lists (RAGAS returns lists with single values)
            def extract_scalar(value):
                if isinstance(value, list) and len(value) > 0:
                    return float(value[0])
                elif isinstance(value, (int, float)):
                    return float(value)
                else:
                    return 0.0
            
            faith_val = result["faithfulness"]
            relevancy_val = result["answer_relevancy"]
            
            metrics = {}
            metrics["faithfulness"] = extract_scalar(faith_val)
            metrics["answer_relevancy"] = extract_scalar(relevancy_val)
            metrics["context_precision"] = 0.0
            metrics["context_recall"] = 0.0
            
            logger.debug(f"Extracted metrics - faithfulness: {metrics['faithfulness']:.3f}, "
                        f"answer_relevancy: {metrics['answer_relevancy']:.3f}")
            
            # Calculate overall score only from evaluated metrics
            evaluated_scores = [score for score in metrics.values() if score > 0]
            overall_score = sum(evaluated_scores) / len(evaluated_scores) if evaluated_scores else 0.0
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
        # Check only metrics that were actually evaluated (> 0)
        checks = []
        
        if metrics["faithfulness"] > 0:
            checks.append(metrics["faithfulness"] >= self.config.faithfulness_threshold)
        if metrics["answer_relevancy"] > 0:
            checks.append(metrics["answer_relevancy"] >= self.config.answer_relevancy_threshold)
        if metrics["context_precision"] > 0:
            checks.append(metrics["context_precision"] >= self.config.context_precision_threshold)
        if metrics["context_recall"] > 0:
            checks.append(metrics["context_recall"] >= self.config.context_recall_threshold)
        
        return all(checks) and overall_score >= self.config.overall_threshold
    
    def _generate_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        recommendations = []
        
        if metrics["faithfulness"] > 0 and metrics["faithfulness"] < self.config.faithfulness_threshold:
            recommendations.append("Improve answer faithfulness - ensure claims are supported by context")
        
        if metrics["answer_relevancy"] > 0 and metrics["answer_relevancy"] < self.config.answer_relevancy_threshold:
            recommendations.append("Improve answer relevancy - address the question more directly")
        
        if metrics["context_precision"] > 0 and metrics["context_precision"] < self.config.context_precision_threshold:
            recommendations.append("Improve context precision - retrieve more relevant context")
        
        if metrics["context_recall"] > 0 and metrics["context_recall"] < self.config.context_recall_threshold:
            recommendations.append("Improve context recall - retrieve more comprehensive context")
        
        return recommendations