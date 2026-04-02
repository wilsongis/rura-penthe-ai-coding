# src/rura_penthe/optimizer/file_modifier.py
"""Modifier Constraint Enforcer.

Enforces file modification constraints and guards to ensure
safe, bounded mutations during agent-driven code generation.

Deployment Profile: Profile A (Edge / Mission Compute)
"""
from typing import Dict, Any

class ModifierConstraintEnforcer:
    """
    Relies on standard JSON tool schemas to modify code, 
    eliminating the overhead of custom string parsers.
    """
    
    TOOL_SCHEMA = {
        "type": "function",
        "function": {
            "name": "apply_unified_diff",
            "description": "Applies a standard unified patch to modify an existing file. This should be prioritized over full-file overrides.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Absolute path to the target file."},
                    "unified_diff_content": {"type": "string", "description": "The unified diff containing the modifications."}
                },
                "required": ["file_path", "unified_diff_content"]
            }
        }
    }

    @classmethod
    def enforce_tools(cls, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Injects the tool schema into the dispatch queue without modifying spec-kit internals.
        """
        tools = request_payload.get("tools", [])
        tools.append(cls.TOOL_SCHEMA)
        request_payload["tools"] = tools
        return request_payload
