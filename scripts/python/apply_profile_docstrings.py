"""Apply Profile A docstrings to Python modules missing Power-of-11 declarations.

Deployment Profile: Profile A (Edge / Mission Compute)

Scans src/ and scripts/python/ for Python files that either:
  1. Have no module docstring at all → inserts a new Profile A docstring.
  2. Have a docstring but no Profile A/B tag → appends the Profile A tag.

Usage:
    uv run scripts/python/apply_profile_docstrings.py [--dry-run]

Args:
    --dry-run: Print changes without writing files.
"""

import ast
import os
import sys
from pathlib import Path

PROFILE_A_TAG = "\n\nDeployment Profile: Profile A (Edge / Mission Compute)"

# Maps relative file paths to context-appropriate module descriptions.
# Files not in this map will get a generic description derived from their path.
MODULE_DESCRIPTIONS: dict[str, str] = {
    "scripts/python/compress.py": (
        "Warden Context Compressor (LLMLingua-2).\n\n"
        "Hardware-accelerated token compression pipeline for reducing\n"
        "agent context window payloads via the LLMLingua-2 model."
    ),
    "scripts/python/telemetry.py": (
        "Warden Telemetry Dashboard.\n\n"
        "Reads and reports compression telemetry metrics from the\n"
        "local SQLite database (~/.rura/telemetry.db)."
    ),
    "src/rura_penthe/optimizer/base.py": (
        "Token Optimization Base Classes.\n\n"
        "Defines the abstract interfaces (TokenOptimizer, ContextCompressor)\n"
        "and the InterceptorMiddleware for LLMLingua compression pipelines."
    ),
    "src/rura_penthe/optimizer/context_compressor.py": (
        "Advanced Context Optimizer.\n\n"
        "Implements advanced context-window compression strategies\n"
        "for reducing token payloads in agent prompt generation."
    ),
    "src/rura_penthe/optimizer/execution_boundary.py": (
        "Execution Boundary Compressor.\n\n"
        "Compresses execution result payloads at process boundaries\n"
        "to minimize token consumption in agent feedback loops."
    ),
    "src/rura_penthe/optimizer/file_modifier.py": (
        "Modifier Constraint Enforcer.\n\n"
        "Enforces file modification constraints and guards to ensure\n"
        "safe, bounded mutations during agent-driven code generation."
    ),
    "src/rura_penthe/optimizer/memory_anchor.py": (
        "Memory Anchor Protocol.\n\n"
        "Implements the memory anchoring protocol for persistent context\n"
        "retention across agent session boundaries."
    ),
}


def _derive_description(rel_path: str) -> str:
    """Derive a generic module description from the file path.

    Args:
        rel_path: Relative path of the Python file.

    Returns:
        A generic description string.
    """
    stem = Path(rel_path).stem
    parent = Path(rel_path).parent.name
    return f"{stem.replace('_', ' ').title()} module ({parent} package)."


def apply_profile_docstrings(project_root: Path, *, dry_run: bool = False) -> list[str]:
    """Apply Profile A docstrings to all Python files missing declarations.

    Args:
        project_root: Absolute path to the project root.
        dry_run: If True, print changes without writing files.

    Returns:
        List of relative paths that were modified.
    """
    directories_to_check = [
        project_root / "src",
        project_root / "scripts" / "python",
    ]

    modified_files: list[str] = []

    for directory in directories_to_check:
        if not directory.exists():
            continue

        for root, _, files in os.walk(directory):
            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(project_root))

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                try:
                    tree = ast.parse(content)
                except SyntaxError:
                    continue

                docstring = ast.get_docstring(tree)

                if docstring is None:
                    # Case 1: No docstring at all — insert a new one
                    description = MODULE_DESCRIPTIONS.get(
                        rel_path, _derive_description(rel_path)
                    )
                    new_docstring = f'"""{description}{PROFILE_A_TAG}\n"""'
                    new_content = _insert_docstring(content, new_docstring)
                    action = "INSERTED"

                elif "profile a" not in docstring.lower() and "profile b" not in docstring.lower():
                    # Case 2: Has docstring but no Profile tag — append tag
                    new_content = _append_profile_tag(content, docstring)
                    action = "APPENDED"

                else:
                    # Already has a Profile declaration
                    continue

                if dry_run:
                    print(f"  [DRY-RUN] {action} Profile A → {rel_path}")
                else:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"  [APPLIED] {action} Profile A → {rel_path}")

                modified_files.append(rel_path)

    return modified_files


def _insert_docstring(content: str, docstring: str) -> str:
    """Insert a module docstring at the top of a Python file.

    Handles files that start with comments (shebangs, script metadata blocks)
    by inserting the docstring after the leading comment block.

    Args:
        content: Original file content.
        docstring: The triple-quoted docstring to insert.

    Returns:
        Modified file content with docstring inserted.
    """
    lines = content.split("\n")

    # Find the insertion point: skip shebangs, encoding declarations,
    # and PEP 723 script metadata blocks (# /// script ... # ///)
    insert_idx = 0
    in_script_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Handle PEP 723 script metadata blocks
        if stripped == "# /// script":
            in_script_block = True
            insert_idx = i + 1
            continue
        if in_script_block:
            insert_idx = i + 1
            if stripped == "# ///":
                in_script_block = False
            continue

        # Skip shebangs and encoding declarations
        if i == 0 and stripped.startswith("#!"):
            insert_idx = 1
            continue
        if i <= 1 and stripped.startswith("# -*-"):
            insert_idx = i + 1
            continue

        # Skip blank lines after comments
        if stripped == "" and i == insert_idx:
            insert_idx = i + 1
            continue

        # If we hit a comment that's part of a file header (like # src/...)
        if stripped.startswith("#") and i == insert_idx:
            insert_idx = i + 1
            continue

        break

    # Insert the docstring
    lines.insert(insert_idx, docstring)
    return "\n".join(lines)


def _append_profile_tag(content: str, existing_docstring: str) -> str:
    """Append the Profile A tag to an existing module docstring.

    Finds the closing triple-quote of the module docstring and inserts
    the Profile A tag line before it.

    Args:
        content: Original file content.
        existing_docstring: The current docstring text (without quotes).

    Returns:
        Modified file content with Profile A tag appended.
    """
    # Find the module docstring in the raw content
    # Look for the closing triple-quote of the first docstring
    tree = ast.parse(content)
    first_node = tree.body[0] if tree.body else None

    if not isinstance(first_node, ast.Expr) or not isinstance(first_node.value, ast.Constant):
        return content

    # Get the end line of the docstring
    end_line = first_node.end_lineno
    if end_line is None:
        return content

    lines = content.split("\n")
    # end_line is 1-indexed
    closing_line_idx = end_line - 1
    closing_line = lines[closing_line_idx]

    # The closing line should contain the closing triple-quotes
    # Insert the profile tag before the closing quotes
    if closing_line.strip() == '"""' or closing_line.strip() == "'''":
        # Closing quotes on their own line — insert tag before it
        indent = closing_line[: len(closing_line) - len(closing_line.lstrip())]
        tag_line = f"\nDeployment Profile: Profile A (Edge / Mission Compute)"
        lines.insert(closing_line_idx, tag_line)
    elif closing_line.rstrip().endswith('"""'):
        # Closing quotes at end of content line
        pre = closing_line.rstrip()[:-3]
        lines[closing_line_idx] = (
            pre + "\n\nDeployment Profile: Profile A (Edge / Mission Compute)\n" + '"""'
        )
    elif closing_line.rstrip().endswith("'''"):
        pre = closing_line.rstrip()[:-3]
        lines[closing_line_idx] = (
            pre + "\n\nDeployment Profile: Profile A (Edge / Mission Compute)\n" + "'''"
        )
    else:
        return content

    return "\n".join(lines)


def main() -> None:
    """Entry point for the Profile A docstring application script."""
    dry_run = "--dry-run" in sys.argv

    project_root = Path(__file__).resolve().parent.parent.parent
    print(f"Project root: {project_root}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")
    print()

    modified = apply_profile_docstrings(project_root, dry_run=dry_run)

    print(f"\nTotal files {'would be ' if dry_run else ''}modified: {len(modified)}")
    if dry_run and modified:
        print("\nRe-run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
