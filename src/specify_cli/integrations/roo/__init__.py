"""Roo Code integration.

Deployment Profile: Profile A (Edge / Mission Compute)
"""

from ..base import MarkdownIntegration


class RooIntegration(MarkdownIntegration):
    key = "roo"
    config = {
        "name": "Roo Code",
        "folder": ".roo/",
        "commands_subdir": "commands",
        "install_url": None,
        "requires_cli": False,
    }
    registrar_config = {
        "dir": ".roo/commands",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": ".md",
    }
    context_file = ".roo/rules/specify-rules.md"
