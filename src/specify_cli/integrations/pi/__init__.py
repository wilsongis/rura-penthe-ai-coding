"""Pi Coding Agent integration.

Deployment Profile: Profile A (Edge / Mission Compute)
"""

from ..base import MarkdownIntegration


class PiIntegration(MarkdownIntegration):
    key = "pi"
    config = {
        "name": "Pi Coding Agent",
        "folder": ".pi/",
        "commands_subdir": "prompts",
        "install_url": "https://www.npmjs.com/package/@mariozechner/pi-coding-agent",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".pi/prompts",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": ".md",
    }
    context_file = "AGENTS.md"
