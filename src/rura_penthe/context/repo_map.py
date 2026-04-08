"""
Rura Penthe AST Repository Mapper.

Uses `tree-sitter` and `grep-ast` to build a structural map of the repository,
identifying important class and function definitions to serve as a low-token
context map for AI agents.
"""

import os
from pathlib import Path
import logging

try:
    from grep_ast import TreeContext
    from tree_sitter_languages import get_language, get_parser
except ImportError:
    TreeContext = None

logger = logging.getLogger(__name__)

class RepositoryMap:
    """Generates an AST-driven token-efficient repository map."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.max_map_tokens = 2000

    def get_map(self, target_dirs: list[str] = None) -> str:
        """
        Scans target directories (or entire root) and returns an AST summary map.
        """
        if TreeContext is None:
            logger.warning("grep-ast or tree-sitter-languages not installed. Falling back to basic tree.")
            return "Note: AST mapping disabled due to missing dependencies. Use `uv add grep-ast tree-sitter-languages`."

        if not target_dirs:
            target_dirs = ["."]
            
        map_output = []
        map_output.append(f"Repository Map for root: {self.root_dir}\n")
        
        # Discover all supported source files
        supported_exts = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.go': 'go', '.rs': 'rust'}
        
        files_to_parse = []
        for tdir in target_dirs:
            full_dir = self.root_dir / tdir
            if not full_dir.exists():
                continue
            for root, _, files in os.walk(full_dir):
                if '.git' in root or '__pycache__' in root or 'node_modules' in root or '.venv' in root:
                    continue
                for f in files:
                    ext = Path(f).suffix
                    if ext in supported_exts:
                        files_to_parse.append(Path(root) / f)

        # For simplicity, extract all top-level definitions to form a skeleton of the files
        for file_path in files_to_parse:
            try:
                rel_path = file_path.relative_to(self.root_dir)
                code = file_path.read_text(encoding="utf-8")
                
                # A lightweight representation showing the "skeleton" of the file
                # `grep-ast` TreeContext can show structural elements given relevant lines.
                # To show the skeleton, we can just request line 1 to be the line of interest, 
                # but with show_top_of_file_parent_scope=True it shows the tree outline.
                # However, directly printing the module structure is best.
                ctx = TreeContext(
                    filename=str(rel_path),
                    code=code,
                    color=False,
                    line_number=True,
                    child_context=True,
                    last_line=False,
                    margin=0,
                    mark_lois=False,
                    loi_pad=0,
                    show_top_of_file_parent_scope=True,
                )
                
                # If we don't add specific lines of interest, it might be blank.
                # To show definitions (class/def), we can use a naive AST parse or TreeContext.
                # Let's add line 1, which usually captures the top-level structure.
                ctx.add_lines_of_interest([1]) 
                ctx.add_context()
                
                file_summary = ctx.format()
                if file_summary.strip():
                    map_output.append(f"--- {rel_path} ---")
                    map_output.append(file_summary)
                    
            except Exception as e:
                logger.debug(f"Failed to parse {file_path}: {e}")

        final_map = "\n".join(map_output)
        return final_map

# Example usage:
# repo_map = RepositoryMap(".")
# print(repo_map.get_map(["src"]))
