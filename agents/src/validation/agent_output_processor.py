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
        Extract contexts from agent messages, handling structured responses and legacy formats.
        """
        contexts = []
        
        for message in agent_messages:
            if message.get("name") == "retriever_agent":
                # Try structured response first (new format)
                if "structured_response" in message:
                    response = message["structured_response"]
                    if isinstance(response, dict):
                        # Extract sources from structured response
                        sources = response.get("sources", [])
                        if sources:
                            contexts.extend([self._clean_text(source) for source in sources])
                        
                        # Also include the reasoning as context
                        reasoning = response.get("reasoning", "")
                        if reasoning:
                            contexts.append(self._clean_text(reasoning))
                        
                        continue
                
                content = message.get("content", "")
                
                # Try to parse as JSON (legacy format)
                try:
                    parsed_content = json.loads(content)
                    if isinstance(parsed_content, dict):
                        # Extract sources from JSON structure
                        sources = parsed_content.get("sources", [])
                        if sources:
                            contexts.extend([self._clean_text(source) for source in sources])
                        
                        # Also include the reasoning as context
                        reasoning = parsed_content.get("reasoning", "")
                        if reasoning:
                            contexts.append(self._clean_text(reasoning))
                        
                        continue
                except (json.JSONDecodeError, TypeError):
                    # Not JSON, fall back to legacy processing
                    pass
                
                # Legacy format processing
                if "context" in content.lower() or "document" in content.lower():
                    contexts.append(self._clean_text(content))
        
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