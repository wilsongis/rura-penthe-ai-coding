# Rura Penthe - Feature TODOs

## High Priority
- [ ] **CLI vs MCP Migration (Progressive Disclosure)**:
  - Migrate away from bloated MCP servers to a 3-layer CLI progressive disclosure framework (Prompt Metadata, 800-token Skill guides, File System routing for context protection).
  - Add native skills for `gh` (GitHub), `psql` (Postgres schemas), `ogr2ogr` (GIS), `curl` (API Testing), and `uv`/`just` (Builds).
  - Explicitly restrict giant stdout payloads by routing large outputs to `/tmp/analysis.csv` or `.json`.

## Medium Priority
- [ ] **Obsidian Vault Integration (`rura-intel`)**: Develop a CLI tool or module (`rura_penthe/context/obsidian_search.py`) to connect directly to the user's Obsidian Vault. If the agent needs to know the architectural plan for a specific project, it can run this command to extract just the relevant markdown notes instead of feeding the entire vault.
- [ ] **Local SQLite Symbol Indexing (Persisted AST)**: Parse repositories once with Tree-sitter and serialize the extracted symbols, signatures, and byte-offsets into a local SQLite database for sub-millisecond retrieval, avoiding continuous filesystem parsing. Code analysis queries like `find_importers()` or `get_class_hierarchy()` can be executed natively.
- [ ] **Model Context Protocol (MCP) Server Layer**: Wrap `rura-penthe` AST parsing and token-optimized logic into an MCP server. This allows IDEs (Cursor, Claude Desktop) and agents to dynamically consume Rura Penthe's structural tools without relying strictly on bespoke CLI prompt-drop files.
- [ ] **Cumulative Diff Sandbox (State Machine)**: Build a sandbox environment for agent "Batch-wave processing". Instead of immediately writing generated feature scaffolds directly to the disk/branch, queue them in a state machine where they can be linted (`ruff`/`pyright`) and optionally reviewed or auto-fixed before final application to the working tree.

## Backlog / Completed
- [x] **Roo Code `.roomodes` Integration**: Automatically generate a `.roomodes` configuration file during `specify init` to enforce Cost Optimized Model Ladders inside the Roo Code IDE. Created an `Architect` mode (premium models) and a `Rura Coder` mode (fast/cheap open-router models) to split complex tasks from execution tasks, including automated `git switch -c` branch enforcement.
- [x] **Token-Optimized Execution Protocols**: Explicitly documented and enforced the progressive disclosure execution loop (e.g. outputting schemas to `/tmp/analysis.csv` and verifying with `head`).
- [x] **Stack Enforcement (`rura-enforce`)**: Re-use `just lint` and the Warden compliance profile.
- [x] **Repository Context Window Parsing**: Re-use `repo_map.py` to prevent large file pollution.
