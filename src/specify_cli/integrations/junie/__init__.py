"""Junie integration (JetBrains).

Deployment Profile: Profile A (Edge / Mission Compute)
"""

from ..base import MarkdownIntegration


class JunieIntegration(MarkdownIntegration):
    key = "junie"
    config = {
        "name": "Junie",
        "folder": ".junie/",
        "commands_subdir": "commands",
        "install_url": "https://junie.jetbrains.com/",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".junie/commands",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": ".md",
    }
    context_file = ".junie/AGENTS.md"
