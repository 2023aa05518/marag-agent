import json
import logging
from typing import List, Dict, Any
from .models import RAGASInput

logger = logging.getLogger(__name__)


class AgentOutputProcessor:
    """
    Enhanced agent output processor that handles JSON-structured agent responses.
    Compatible with both legacy and new structured output formats.
    """
    
    def extract_contexts(self, agent_messages: List[Dict[str, Any]]) -> List[str]:
        """
        Extract contexts from LangChain messages using ToolMessage pattern.
        """
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
                return [str(item)] if str(item).strip() else []
        
        for message in agent_messages:
            # Use the working pattern: check for ToolMessage type
            if hasattr(message, '__class__') and message.__class__.__name__ == 'ToolMessage':
                # Skip handoff messages
                if hasattr(message, 'content') and "transferred" in message.content.lower():
                    continue
                    
                # Parse tool response for document content
                try:
                    if message.content.startswith('{') or message.content.startswith('['):
                        tool_data = json.loads(message.content)
                        
                        if isinstance(tool_data, dict):
                            if 'documents' in tool_data:
                                flattened = flatten_to_strings(tool_data['documents'])
                                contexts.extend([self._clean_text(item) for item in flattened])
                            elif 'content' in tool_data:
                                flattened = flatten_to_strings(tool_data['content'])
                                contexts.extend([self._clean_text(item) for item in flattened])
                        elif isinstance(tool_data, list):
                            flattened = flatten_to_strings(tool_data)
                            contexts.extend([self._clean_text(item) for item in flattened])
                    else:
                        if message.content.strip():
                            contexts.append(self._clean_text(message.content))
                            
                except json.JSONDecodeError:
                    if message.content.strip():
                        contexts.append(self._clean_text(message.content))
        
        return contexts
    
    def extract_final_answer(self, supervisor_result: str) -> str:
        """
        Extract final answer, handling structured responses and legacy formats.
        """
        if not supervisor_result:
            return ""
        
        # Try to parse as structured response first (new format)
        if isinstance(supervisor_result, dict) and "content" in supervisor_result:
            return self._clean_text(supervisor_result["content"])
        
        # Try to parse as JSON (legacy format)
        try:
            parsed_result = json.loads(supervisor_result)
            if isinstance(parsed_result, dict):
                # Extract answer from JSON structure
                answer = parsed_result.get("content", "")
                if answer:
                    return self._clean_text(answer)
        except (json.JSONDecodeError, TypeError):
            # Not JSON, fall back to legacy processing
            pass
        
        # Legacy format processing
        lines = supervisor_result.split('\n')
        answer_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('Action:') and not line.startswith('Observation:'):
                answer_lines.append(line)
        
        return self._clean_text(' '.join(answer_lines))
    
    def prepare_ragas_input(self, query: str, agent_outputs: Dict[str, Any]) -> RAGASInput:
        """
        Prepare RAGAS input from agent outputs, handling both legacy and structured formats.
        """
        agent_messages = agent_outputs.get("messages", [])
        supervisor_result = agent_outputs.get("supervisor_result", "")
        
        # LOG 2: AgentOutputProcessor received data
        logger.debug(f"AgentOutputProcessor received: {len(agent_messages)} messages, "
                    f"supervisor result: {len(supervisor_result)} chars")
        
        # Extract contexts from structured messages
        contexts = self.extract_contexts(agent_messages)
        
        # If no contexts found in messages, try to extract from contexts field
        if not contexts:
            contexts = agent_outputs.get("contexts", [])
        
        # Extract final answer
        answer = self.extract_final_answer(supervisor_result)
        
        logger.debug(f"Prepared RAGAS input: {len(contexts)} contexts, answer length: {len(answer)}")
        
        return RAGASInput(
            question=query,
            contexts=contexts,
            answer=answer,
            ground_truth=None
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        return text.strip().replace('\n', ' ').replace('\r', ' ')