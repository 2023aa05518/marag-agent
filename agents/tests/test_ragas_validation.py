"""
Test RAGAS validation: message history → RAGASInput → validation
"""
import asyncio
import pytest
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from src.validation.ragas_validator import RAGASValidator
from src.validation.agent_output_processor import AgentOutputProcessor
from src.validation.models import ValidationConfig


@pytest.mark.asyncio
async def test_message_history_to_validation():
    """Test complete flow: message history → RAGASInput → validation"""
    
    # Sample message history using proper LangChain message types
    messages = [
        HumanMessage(content='What are the benefits of renewable energy?'),
        AIMessage(content='Renewable energy offers environmental benefits by reducing carbon emissions, economic benefits through job creation, and energy independence.'),
        ToolMessage(content='Context: Solar and wind power are clean energy sources that help combat climate change.', tool_call_id='tool_1')
    ]
    
    # Process messages to RAGASInput
    processor = AgentOutputProcessor()
    question = "What are the benefits of renewable energy?"
    ragas_input = processor.prepare_ragas_input_from_messages(question, messages)
    
    # Validate structure
    assert ragas_input.question == question
    assert ragas_input.answer is not None
    assert len(ragas_input.contexts) > 0
    
    # Run validation
    config = ValidationConfig(enabled=True, overall_threshold=0.3)
    validator = RAGASValidator(config)
    result = await validator.validate_response(ragas_input)
    
    # Check results
    assert result is not None
    assert isinstance(result.passed, bool)
    assert isinstance(result.overall_score, (float, int))
    assert len(result.metrics) == 4
    assert 'faithfulness' in result.metrics
    assert 'answer_relevancy' in result.metrics
    assert 'context_precision' in result.metrics
    assert 'context_recall' in result.metrics
    
    print(f"✅ Validation completed - Passed: {result.passed}, Score: {result.overall_score:.3f}")
    return result


# Manual test runner
async def run_manual_test():
    """Quick manual test"""
    print("Testing RAGAS validation...")
    
    messages = [
        HumanMessage(content='What is Python?'),
        AIMessage(content='Python is a programming language known for simplicity and readability.'),
        ToolMessage(content='Context: Python was created by Guido van Rossum in 1991.', tool_call_id='tool_1')
    ]
    
    try:
        processor = AgentOutputProcessor()
        validator = RAGASValidator(ValidationConfig(enabled=True, overall_threshold=0.3))
        
        ragas_input = processor.prepare_ragas_input_from_messages("What is Python?", messages)
        result = await validator.validate_response(ragas_input)
        
        print(f"✅ Test completed - Passed: {result.passed}, Score: {result.overall_score:.3f}")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_manual_test())
    exit(0 if success else 1)
