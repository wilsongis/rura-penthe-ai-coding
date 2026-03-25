# [PROJECT_NAME] Constitution (Profile B: Embedded / Low-Level Control)

## Core Principles

### I. Safety-Critical Control Flow (Power of 11: Rules 1 & 2)
Prohibit all recursion, deep nested generators, and exception-based control flow loops. All loops must have fixed, preset upper bounds. Exceptions for expected control flow are forbidden; `raise` is reserved exclusively for catastrophic hardware panics. 

### II. Deterministic Memory Management (Power of 11: Rule 3)
Dynamic memory allocation after initialization is strictly prohibited. Pre-allocate collections, enforce `__slots__` on all classes. Utilize Python's native `array` module for contiguous buffers. Garbage collection must be disabled (`gc.disable()`) before critical loops and run manually only during idle windows.

### III. Cognitive Bounding (Power of 11: Rule 4)
Limit all functions to a maximum of 50 statements. Refactor complex logic into smaller helper functions. Maximum McCabe complexity is 10.

### IV. Structural Validation & Data Hiding (Power of 11: Rules 5 & 6)
No native `assert` statements. **Pydantic and NumPy are explicitly forbidden**. Use manual guard clauses rejecting invalid state immediately. Variables must be scoped minimally; `global` and `nonlocal` keywords are forbidden.

### V. Strict Verification & Result Tuple Unpacking (Power of 11: Rules 7 & 8)
Mandate strict typing (Pyright Strict). Functions must return explicit `Result` objects (e.g., `(success_bool, value, error_code)`) unpacked via Python 3.10+ `match / case` structural pattern matching. No dynamic execution (`eval`, `exec`, `globals()`, decorators) or dynamic importing. 

### VI. Immutable Data & Zero-Tolerance Linting (Power of 11: Rules 9 & 10)
Restrict reference aliasing by enforcing deep immutable data structures (`frozen` dataclasses, tuples). All code must compile with zero warnings using `uv run ruff check` continuously. 

### VII. Secure Supply Chain (Power of 11: Rule 11)
Pin all dependencies to cryptographic hashes using `uv.lock`. Avoid floating versions. All dependencies must be vetted via `pip-audit`.

## Architecture Profile: B (Embedded / Hardware Loop)
**Target**: MicroPython / CircuitPython
**Hardware**: Cortex-M, ESP32, ECUs, bare-metal microcontrollers
**Allowed**: Native MicroPython and pure Python ONLY. Zero C-Extensions. Hard real-time determinism.

## AI Security Guardrails (OWASP GenAI)
- **Model Integrity:** Use `safetensors` exclusively. `pickle` serialization is strictly banned.

## Documentation Standard
Google Style docstrings are strictly enforced for every module, class, and function. All inputs, outputs, `Raises:`, and side effects must be exhaustively detailed. Type hints complement—but do not replace—docstrings.

## Governance
All PRs/reviews must verify compliance with the Power of 11 Profile B constraints.

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
