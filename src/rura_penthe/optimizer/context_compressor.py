# src/rura_penthe/optimizer/context_compressor.py
"""Advanced Context Optimizer.

Implements advanced context-window compression strategies
for reducing token payloads in agent prompt generation.

Deployment Profile: Profile A (Edge / Mission Compute)
"""
from typing import List, Dict, Any

class AdvancedContextOptimizer:
    def __init__(self, llmlingua_client=None):
        self.compressor = llmlingua_client
        
    def order_for_prompt_caching(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Pushes system instructions, API documentation, and static protocol rules to the top of the array
        to maximize prompt caching hit rates on cloud inference backends.
        """
        static_messages = [m for m in messages if m.get("role") == "system"]
        dynamic_messages = [m for m in messages if m.get("role") != "system"]
        
        # Keep static config at the absolute beginning of the prompt block
        return static_messages + dynamic_messages

    def compress_large_context(self, content: str) -> str:
        """
        Uses LLMLingua to semantically digest large code blocks without breaking scope boundaries.
        """
        if not self.compressor or len(content) < 2000:
            return content
            
        return self.compressor.compress_prompt(
            content,
            instruction="Retain all functional code logic, class structures, and imports.",
            target_token=1000
        )
