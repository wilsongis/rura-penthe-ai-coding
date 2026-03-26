"""
Specify CLI Configuration

Contains decentralized, environment-driven constants used across the CLI and plugin systems.
"""
import os
import json

def _resolve_command_namespace() -> str:
    """
    Cascading config loader to shield against VS Code environment variable inheritance failures.
    1. Reads .rura/config.json if present
    2. Reads [tool.rura] in pyproject.toml if present
    3. Falls back to SPEC_COMMAND_NAMESPACE env var
    4. Defaults to 'warden'
    """
    cwd = os.getcwd()
    
    # 1. Check for .rura/config.json
    try:
        rura_config_path = os.path.join(cwd, ".rura", "config.json")
        if os.path.exists(rura_config_path):
            with open(rura_config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "command_namespace" in data:
                    return str(data["command_namespace"])
    except Exception:
        pass

    # 2. Check for pyproject.toml
    try:
        pyproject_path = os.path.join(cwd, "pyproject.toml")
        if os.path.exists(pyproject_path):
            import tomllib
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                namespace = data.get("tool", {}).get("rura", {}).get("command_namespace")
                if namespace:
                    return str(namespace)
    except Exception:
        pass

    # 3 & 4. Environment variable or explicit default
    return os.getenv("SPEC_COMMAND_NAMESPACE", "warden")

COMMAND_NAMESPACE = _resolve_command_namespace()
