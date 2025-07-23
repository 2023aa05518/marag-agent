from typing import List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from pydantic import BaseModel
import json
import logging

logger = logging.getLogger(__name__)

class RAGASInput(BaseModel):
    question: str
    contexts: List[str]
    answer: str
    ground_truth: Optional[str] = None

class MessageParser:
    """Parser to extract structured data from LangGraph agent message exchanges"""
    
    def extract_question(self, messages: List[BaseMessage]) -> str:
        """Extract the original user question from the first HumanMessage"""
        for message in messages:
            if isinstance(message, HumanMessage):
                return message.content
        return "No question found"
    
    def extract_contexts(self, messages: List[BaseMessage]) -> List[str]:
        """Extract retrieved document contexts from ToolMessage responses"""
        contexts = []
        
        def flatten_to_strings(item):
            """Recursively flatten nested structures to strings"""
            if isinstance(item, str):
                return [item] if item.strip() else []
            elif isinstance(item, list):
                flattened = []
                for subitem in item:
                    flattened.extend(flatten_to_strings(subitem))
                return flattened
            else:
                # Convert other types to string
                return [str(item)] if str(item).strip() else []
        
        for message in messages:
            if isinstance(message, ToolMessage):
                # Skip handoff messages (they're not actual document content)
                if "transferred" in message.content.lower():
                    continue
                    
                # Parse tool response for document content
                try:
                    # Handle JSON responses from MCP tools
                    if message.content.startswith('{') or message.content.startswith('['):
                        tool_data = json.loads(message.content)
                        
                        # Extract documents from common MCP response formats
                        if isinstance(tool_data, dict):
                            if 'documents' in tool_data:
                                # Flatten documents array
                                flattened = flatten_to_strings(tool_data['documents'])
                                contexts.extend(flattened)
                            elif 'content' in tool_data:
                                flattened = flatten_to_strings(tool_data['content'])
                                contexts.extend(flattened)
                        elif isinstance(tool_data, list):
                            # Handle list responses - flatten them properly
                            flattened = flatten_to_strings(tool_data)
                            contexts.extend(flattened)
                    else:
                        # Handle plain text responses
                        if message.content.strip():
                            contexts.append(message.content.strip())
                            
                except json.JSONDecodeError:
                    # If not JSON, treat as plain text
                    if message.content.strip():
                        contexts.append(message.content.strip())
        
        return contexts
    
    def extract_answer(self, messages: List[BaseMessage]) -> str:
        """Extract the final answer from the supervisor's last substantial AIMessage"""
        # Look for the last AIMessage from supervisor with substantial content
        for message in reversed(messages):
            if isinstance(message, AIMessage):
                # Skip messages with only tool calls
                if message.tool_calls:
                    continue
                # Return first substantial content found
                if message.content and len(message.content.strip()) > 20:
                    return message.content
        return "No answer found"
    
    def to_ragas_input(self, messages: List[BaseMessage], ground_truth: Optional[str] = None) -> RAGASInput:
        """Convert message history to RAGASInput format"""
        question = self.extract_question(messages)
        contexts = self.extract_contexts(messages)
        answer = self.extract_answer(messages)
        
        return RAGASInput(
            question=question,
            contexts=contexts,
            answer=answer,
            ground_truth=ground_truth
        )