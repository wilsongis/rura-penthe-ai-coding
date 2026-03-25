"""
Specify CLI Configuration

Contains decentralized, environment-driven constants used across the CLI and plugin systems.
"""
import os

# To decouple the command namespace for forks/custom tooling, define the namespace.
# Upstream default is 'speckit', user/fork default is 'warden'.
COMMAND_NAMESPACE = os.getenv("SPEC_COMMAND_NAMESPACE", "warden")
