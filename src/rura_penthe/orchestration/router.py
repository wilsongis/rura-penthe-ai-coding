"""
Rura Penthe Task Router.

Utilizes `litellm` to dynamically route LLM tasks based on configured profiles.
Implements the "Model Ladder" concept:
- Parse/Plan tasks hit fast/cheap models (e.g. gemini-flash, llama-3 via openrouter)
- Coding/Implementation tasks hit premium models (e.g. claude-3.5-sonnet)
"""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

try:
    import litellm
except ImportError:
    litellm = None

logger = logging.getLogger(__name__)

@dataclass
class TaskProfile:
    complexity: str
    tags: list[str]

class ModelRouter:
    """Dynamically routes tasks to the most cost-effective and capable model."""

    # Default model ladder mapping
    STATIC_LADDER = {
        "low": "openrouter/meta-llama/llama-3-8b-instruct",       # Cheap, fast
        "medium": "gemini/gemini-1.5-flash",                      # High context, cheap
        "high": "anthropic/claude-3.5-sonnet-20240620",           # Premium, coding
        "architect": "anthropic/claude-3-opus-20240229"           # Max reasoning
    }

    def __init__(self, custom_ladder: Optional[Dict[str, str]] = None):
        self.ladder = custom_ladder or self.STATIC_LADDER
        if litellm is None:
            logger.warning("litellm is not installed. Routing may fallback to string parsing only.")

    def determine_model(self, profile: TaskProfile) -> str:
        """Determines the appropriate model string based on task complexity and tags."""
        
        # If specific tags override complexity
        if "architect" in profile.tags:
            return self.ladder["architect"]
            
        if profile.complexity in self.ladder:
            return self.ladder[profile.complexity]
            
        # Fallback
        return self.ladder["medium"]

    def completion(self, profile: TaskProfile, messages: list[dict], **kwargs) -> Any:
        """
        Executes a completion call via LiteLLM to the routed model.
        """
        if litellm is None:
            raise ImportError("litellm must be installed to execute completions via Router.")
            
        model = self.determine_model(profile)
        logger.info(f"Routing task (complexity: {profile.complexity}) to model: {model}")
        
        # Invoke LiteLLM
        response = litellm.completion(
            model=model,
            messages=messages,
            **kwargs
        )
        return response

# Example usage:
# router = ModelRouter()
# profile = TaskProfile(complexity="low", tags=["parser"])
# # router.completion(profile, [{"role": "user", "content": "List files."}])
