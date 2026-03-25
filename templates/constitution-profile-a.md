# [PROJECT_NAME] Constitution (Profile A: Edge / Mission Compute)

## Core Principles

### I. Safety-Critical Control Flow (Power of 11: Rules 1 & 2)
Prohibit all recursion, deep nested generators, and exception-based control flow loops. All loops must have fixed, preset upper bounds. Exceptions must strictly report errors, never dictate logic. Bounded `try/except` constructs are permitted at architectural boundaries.

### II. Deterministic Memory Management (Power of 11: Rule 3)
Dynamic memory allocation after initialization is strictly prohibited. Pre-allocate collections, enforce `__slots__` on all classes. NumPy pre-allocation is permitted.

### III. Cognitive Bounding (Power of 11: Rule 4)
Limit all functions to a maximum of 50 statements (`Ruff PLR0915`). Refactor complex logic into smaller, independently testable helper functions. Maximum McCabe complexity is 10 (`Ruff C901`).

### IV. Structural Validation & Data Hiding (Power of 11: Rules 5 & 6)
No native `assert` statements (`Ruff S101`). Explicitly mandate **Pydantic** for rigid structural validation and schema enforcement at system boundaries. Variables must be scoped minimally; `global` and `nonlocal` keywords are forbidden. Mutable default arguments are forbidden.

### V. Strict Verification & No Metaprogramming (Power of 11: Rules 7 & 8)
Mandate strict typing (Pyright Strict), explicitly using `TypeIs` for boundary validation. Ensure return values are continuously checked. No dynamic execution: `eval`, `exec`, `globals()`, and dynamic monkey-patching are strictly banned (`Ruff S102`, `S307`).

### VI. Immutable Data & Zero-Tolerance Linting (Power of 11: Rules 9 & 10)
Restrict reference aliasing by enforcing deep immutable data structures (`frozen` dataclasses, tuples). All code must compile with zero warnings using `uv run ruff check` continuously. Semgrep must run for taint analysis. 

### VII. Secure Supply Chain (Power of 11: Rule 11)
Pin all dependencies to cryptographic hashes using `uv.lock`. Avoid floating versions. All dependencies must be vetted via `pip-audit`.

## Architecture Profile: A (Edge / High-Level Compute)
**Target**: CPython 3.11+
**Hardware**: Mission computers, Ground stations, Jetson, Raspberry Pi
**Allowed**: Vetted C-extensions (NumPy, Pydantic), soft real-time execution.

## AI Security Guardrails (OWASP GenAI)
- **Agentic Isolation:** LLM executions must be containerized (gVisor). Direct host file system access is forbidden.
- **Model Integrity:** Use `safetensors` exclusively. `pickle` serialization is strictly banned.
- **MCP Gateways:** Third-party MCP interactions must pass through secure gateways.
- **Guardrails:** Utilize input/output safety constraints (e.g., NeMo-Guardrails) to intercept Prompt Injections.

## Documentation Standard
Google Style docstrings are strictly enforced for every module, class, and function. All inputs, outputs, `Raises:`, and side effects must be exhaustively detailed. Type hints complement—but do not replace—docstrings.

## Governance
All PRs/reviews must verify compliance with the Power of 11 Profile A constraints.

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
