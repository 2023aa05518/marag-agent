from typing import Any, List
from ragas import SingleTurnSample
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextRecall
from src.agents.test_message_extractor import RAGASInput
import logging

logger = logging.getLogger(__name__)

def ragas_input_to_single_turn_sample(ragas_input: RAGASInput) -> SingleTurnSample:
    """Convert RAGASInput to RAGAS SingleTurnSample format"""
    return SingleTurnSample(
        user_input=ragas_input.question,
        retrieved_contexts=ragas_input.contexts,
        response=ragas_input.answer
    )

async def evaluate_rag_metrics(single_turn_sample: SingleTurnSample) -> dict:
    try:
        from src.utils.llm_utils import get_llm
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from langchain_community.embeddings import HuggingFaceEmbeddings
        
        llm = get_llm()
        ragas_llm = LangchainLLMWrapper(llm)
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        ragas_embeddings = LangchainEmbeddingsWrapper(embeddings)
        
        faithfulness = Faithfulness()
        answer_relevancy = AnswerRelevancy()
        # Note: ContextRecall requires reference answer, so we'll skip it for now
        
        faithfulness.llm = ragas_llm
        answer_relevancy.llm = ragas_llm
        answer_relevancy.embeddings = ragas_embeddings
        
        results = {}
        
        # Evaluate Faithfulness (doesn't require reference)
        try:
            results['faithfulness'] = await faithfulness.single_turn_ascore(single_turn_sample)
        except Exception as e:
            logger.error(f"Error evaluating faithfulness: {e}")
            results['faithfulness'] = 0.0
            
        # Evaluate Answer Relevancy (doesn't require reference)
        try:
            results['answer_relevancy'] = await answer_relevancy.single_turn_ascore(single_turn_sample)
        except Exception as e:
            logger.error(f"Error evaluating answer relevancy: {e}")
            results['answer_relevancy'] = 0.0
            
        # Skip Context Recall for now since it requires reference answer
        results['context_recall'] = 'skipped - requires reference answer'
        
        return results
    except Exception as e:
        logger.error(f"Error evaluating RAG metrics: {e}")
        return {
            'faithfulness': 0.0,
            'answer_relevancy': 0.0,
            'context_recall': 0.0,
            'error': str(e)
        }

async def comprehensive_evaluation(ragas_input: RAGASInput) -> dict:
    try:
        print("Starting comprehensive evaluation...")
        print("--------------------------------------------------------------------------")
        print(f"Question: {ragas_input.question}")
        print(f"Contexts: {ragas_input.contexts}")
        print(f"Answer: {ragas_input.answer}")
        
        print("--------------------------------------------------------------------------")
        single_turn_sample = ragas_input_to_single_turn_sample(ragas_input)
        rag_metrics = await evaluate_rag_metrics(single_turn_sample)
        
        return {
            'parsed_data': ragas_input,
            'single_turn_sample': single_turn_sample,
            'rag_metrics': rag_metrics
        }
    except Exception as e:
        logger.error(f"Error in comprehensive evaluation: {e}")
        return {'error': str(e)}

def show_results(results: dict) -> None:
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
    
    print("="*50)
    print("RAGAS EVALUATION RESULTS")
    print("="*50)
    
    if 'rag_metrics' in results:
        print("\nRAG METRICS:")
        for metric, score in results['rag_metrics'].items():
            print(f"  {metric}: {score}")
    
    if 'single_turn_sample' in results:
        sample = results['single_turn_sample']
        print(f"\nQUESTION: {sample.user_input}")
        print(f"CONTEXTS: {len(sample.retrieved_contexts)} contexts")
        print(f"ANSWER: {sample.response[:100]}...")
    
    print("="*50)


