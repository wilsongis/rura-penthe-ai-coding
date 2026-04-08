# Warden: Safety-Critical Profiles for Spec Kit

## Overview

This document explains the **tiered profile system** for Specify projects. Safety constraints are opt-in, with three distinct profiles:

- **Vanilla Profile** (default): Standard Python best practices. No Power of 11 constraints. Upstream compatibility maintained.
- **Warden Profiles** (opt-in): Projects that declare `[tool.specify] profile = "warden"` adopt Power of 11 constraints. Further subdivided by deployment context:
  - **Warden Profile A (Edge):** High-level mission compute (CPython 3.11+, C-extensions permitted)
  - **Warden Profile B (Embedded):** Low-level bare-metal control (MicroPython, pure Python only)

This design preserves upstream compatibility with vanilla Specify projects while enabling safety-critical systems to opt into rigorous constraints.

---

## Profile Selection

When initializing a project, declare one of two profiles in `pyproject.toml`:

### Vanilla Profile (Default)

**When to use:** Standard web applications, data processing tools, utilities, services that do not operate in safety-critical environments.

```toml
[tool.specify]
profile = "vanilla"
```

**Characteristics:**
- Follows Python best practices (PEP 8, Pylint, standard linting)
- Supports dynamic features: `pickle`, floating dependency versions, metaprogramming
- Exceptions may be used as control flow (with caveats)
- Standard Python object model: no `__slots__` requirement
- `pip install` permitted; `uv` recommended but not mandatory
- Upstream Specify projects may be freely imported/vendored without modification

**Ruff Configuration:** Standard rule set (E, F, W, and key security rules S*)

---

### Warden Profile (Opt-in)

**When to use:** Aerospace flight controllers, automotive ECUs, medical devices, financial systems, or any system where uncontrolled execution could cause harm.

```toml
[tool.specify]
profile = "warden"
warden_target = "edge"  # or "embedded" for bare-metal
```

**Characteristics (all Warden):**
- Enforces **Power of 11** rules (see [Power of 11 Research](./research/The%20Power%20of%2011_%20Adapting%20the%20Power%20of%20Ten%20for%20Safety-Critical%20Python.md))
- Forbids: `pickle`, floating versions, metaprogramming (`eval`, `exec`, `globals()`, dynamic `getattr`/`setattr`)
- Strict assertions: `assert` banned outright; use explicit guards or Pydantic validation
- No pickle; `safetensors` only for ML artifacts
- Mandatory `uv` with cryptographic pinning (`uv.lock`)
- Mandatory `pip-audit` in CI/CD; zero tolerance for CVE violations
- Google Style Docstrings with exhaustive `Raises:` and side-effect documentation
- Pyright: `strict` mode, no `Any` type allowed
- Ruff: Aggressive rule set (C901, PLR0915, S*, ASYNC, TRY, etc.)

#### Warden Profile A: Edge / Mission Compute
- **Target Runtime:** CPython 3.11+
- **Target Hardware:** Mission computers, Ground stations, NVIDIA Jetson, Raspberry Pi Compute Modules
- **Allowed:** Vetted C-extensions (NumPy, Pydantic)
- **Memory Allocation:** Pre-allocated with NumPy arrays
- **Exception Handling:** Bounded try/except permitted at architectural boundaries
- Use case: High-level telemetry, data routing, AI execution on edge devices

#### Warden Profile B: Embedded / Bare-Metal Control
- **Target Runtime:** MicroPython / CircuitPython
- **Target Hardware:** Bare-metal microcontrollers (ARM Cortex-M, ESP32), ECUs, flight controller loops
- **Allowed:** Native MicroPython and pure Python ONLY. Zero C-Extensions
- **Memory Allocation:** Manual control via `array` module; explicit `gc.disable()` for critical sections
- **Exception Handling:** Exceptions forbidden for expected control flow; return explicit `Result` tuples instead
- Use case: Hard real-time sensor fusion, hardware interrupts, actuator control loops

---

## Specification of Profiles in pyproject.toml

The `[tool.specify]` table controls the active profile and related metadata:

```toml
[project]
name = "my-app"
version = "0.1.0"
description = "..."
requires-python = ">=3.11"
dependencies = []

[tool.specify]
# Declare which safety profile this project targets
profile = "vanilla"  # or "warden"

# For Warden projects, specify deployment context
warden_target = "edge"  # or "embedded" for bare-metal

# Optional: Document target deployment environment
deployment_environment = "web-service"  # or "flight-controller", "ecu", "edge-compute"

[tool.pyright]
# Vanilla: standard OK; Warden: strict required
typeCheckingMode = "strict"  # vanilla: "standard" OK; warden: "strict" required
reportMissingImports = true

[tool.ruff]
# Profile-specific configuration
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = [
    # Vanilla & Warden shared
    "E",       # pycodestyle errors
    "F",       # pyflakes
    
    # Warden-only additions include:
    # "C90",   # mccabe complexity
    # "S",     # bandit (security)
    # "PLR",   # pylint refactor (complexity)
    # "ASYNC", # async safety
    # "TRY",   # exception handling
]
```

---

## Import and Dependency Management

### Profile A (Vanilla)

**Upstream compatibility is paramount.**

```bash
# Standard pip workflow
pip install numpy pandas requests

# Dependencies float; upgrade at will
# requirements.txt: numpy>=2.0.0

# Downstream projects can safely import and vendor your code without modification
import my_vanilla_app
```

**No requirements to validate vs Warden constraints.**

### Profile B (Warden)

**All dependencies must be cryptographically pinned and audited.**

```bash
# MANDATORY: Use uv for reproducible builds
uv add numpy pandas requests
# Automatically generates uv.lock with SHA-256 hashes

# CI/CD MANDATORY: Validate lockfile hasn't drifted
uv sync --locked

# MANDATORY: Run pip-audit to catch CVEs
pip-audit  # Fails on High/Critical vulnerabilities

# Downstream projects must acknowledge they're importing Warden code
# (Can still be done but requires explicit validation step)
```

**uv.lock enforces:**
- Exact versions for all transitive dependencies
- Cryptographic hashes for all packages
- Build reproducibility across machines/time

---

## Dependency Vetting Checklist (Profile B)

Before adding a library to a Warden project:

- [ ] **Test Coverage**: ≥80% coverage; check via GitHub/package metadata
- [ ] **Maintenance Health**: Updated in last 12 months; ≥2 active maintainers
- [ ] **License**: Compatible with project license (avoid GPL in proprietary contexts)
- [ ] **Security**: No High/Critical CVEs; passes `pip-audit`
- [ ] **Bus Factor**: Source code publicly available; not dependent on single maintainer
- [ ] **Size**: Avoid "micro-packages" that add attack surface without value
- [ ] **Documentation**: Comprehensive docstrings + README; maintainable for handover

---

## Warden Import Validation (For Consuming Projects)

If your Warden project imports code from an upstream Specify (vanilla) project:

```python
# ❌ PROBLEM: Vanilla code might use forbidden patterns
from upstream.vanilla_app import process_data  # Could internally use eval(), pickle, etc.

# ✅ SOLUTION: Validate before consuming
# 1. Use static analysis on imported code
#    semgrep --config p/security-audit upstream/
#
# 2. Document the boundary as "untrusted_external"
#    Layer a validation function around imported code
#
# 3. Check if upstream uses Power of 11 compliant patterns:
#    ruff check upstream/ --select S,C90,PLR0915
```

**Warden projects may consume vanilla code; just ensure the boundary is explicit and validated.**

---

## Documentation Standards by Profile

### Profile A (Vanilla)

**Minimum:** PEP 257 docstrings for public APIs.

```python
def calculate_total(prices: list[float]) -> float:
    """Calculate total from a list of prices.
    
    Args:
        prices: List of price values.
    
    Returns:
        Sum of all prices.
    """
```

### Profile B (Warden)

**Mandatory:** Google Style Docstrings with explicit `Raises:` and side-effect documentation.

```python
def calculate_total(prices: list[float]) -> float:
    """Calculate total from a list of prices with mutation guards.
    
    Computes the sum of all price values. This function does NOT mutate
    the input list and guarantees O(n) time complexity.
    
    Args:
        prices: Immutable sequence of price values (float). Must not be
            empty; will raise ValueError if empty.
    
    Returns:
        Sum of all prices as a float.
    
    Raises:
        ValueError: If prices list is empty.
        TypeError: If any element is not a numeric type (static check fails).
    
    Side Effects:
        None. This function is pure and does not modify global state,
        perform I/O, or mutate its inputs.
    
    Time Complexity: O(n) where n = len(prices)
    Space Complexity: O(1)
    """
    if not prices:
        raise ValueError("Cannot calculate total of empty price list")
    return sum(prices)
```

---

## Toolchain Validation by Profile

### Profile A (Vanilla)

```bash
# Recommended but optional
ruff check .
pyright .

# Testing
pytest tests/
```

### Profile B (Warden)

```bash
# MANDATORY in CI/CD
ruff check . --select E,F,C90,S,PLR,ASYNC,TRY
pyright . --outputjson  # strict mode, zero Any

# MANDATORY: Dependency audit
uv sync --locked
pip-audit

# MANDATORY: Deep taint analysis
semgrep --config p/security-audit .

# Testing with memory profiling
pytest tests/ --profile-memory

# Linting with zero-tolerance
just lint  # Fails if any warnings

just test  # Fails if any tests fail or coverage <100%
```

---

## Warden: CI/CD Pipeline Integration

For Warden projects, the CI/CD pipeline enforces:

```yaml
# .github/workflows/warden-compliance.yml
name: Warden Compliance

on: [push, pull_request]

jobs:
  warden-check:
    runs-on: ubuntu-latest
    steps:
      # 1. Validate profile declaration
      - name: Check Profile
        run: |
          grep 'profile = "warden"' pyproject.toml || exit 1

      # 2. Lock file validation
      - name: Verify Lockfile
        run: uv sync --locked

      # 3. Security audit
      - name: Audit Dependencies
        run: pip-audit

      # 4. Ruff with Warden rules
      - name: Ruff Check
        run: ruff check . --select E,F,C90,S,PLR,ASYNC,TRY
      
      # 5. Pyright strict
      - name: Type Check
        run: pyright . --strict

      # 6. Taint analysis
      - name: Semgrep
        run: semgrep --config p/security-audit .

      # 7. Tests
      - name: Tests
        run: just test

      # 8. Memory profiling
      - name: Memory Profile
        run: pytest tests/ --profile-memory
```

---

## Migration Guide: Vanilla → Warden

If you want to upgrade a vanilla project to Warden safety constraints:

1. **Declare Profile B**
   ```toml
   [tool.specify]
   profile = "warden"
   ```

2. **Migrate to uv**
   ```bash
   # Export existing dependencies
   pip freeze > requirements.txt
   
   # Recreate with uv
   uv pip install -r requirements.txt
   uv pip compile requirements.txt -o uv.lock
   
   # Or manually add key dependencies
   uv add numpy pydantic pyright
   ```

3. **Update Ruff config** (enable aggressive rules)

4. **Search and eliminate**
   - `assert` statements → replace with `if not X: raise ValueError(...)`
   - `pickle` → use `safetensors` or JSON
   - `eval`/`exec` → refactor with static dispatch
   - Floating versions → pin with hashes

5. **Add documentation** (Google Style + Raises/Side Effects blocks)

6. **Set up CI/CD** (Warden compliance pipeline)

---

## FAQ

### Can a Warden project import vanilla code?

**Yes, but validate the boundary.** Wrap the imported code in a validation layer that sanitizes inputs/outputs.

```python
# In Warden project
from external.vanilla import risky_function

def safe_wrapper(data):
    # Validate external code's output
    if not isinstance(data, dict):
        raise ValueError("External function must return dict")
    return data

result = safe_wrapper(risky_function(x))
```

### Can a vanilla project import Warden code?

**Yes, freely.** Warden code is a strict superset of Python best practices; it's safe to consume.

```python
# In Vanilla project
from safety_critical_lib import calculate_total  # Perfectly safe
```

### What about MicroPython (Profile C)?

**Future extension.** Profile B currently targets CPython 3.11+. MicroPython support would be a distinct Profile C with additional constraints (no exceptions for control flow, explicit `gc.disable()`, etc.).

### How do I check if a project is Warden-compliant?

```bash
# Quick check script
if grep -q 'profile = "warden"' pyproject.toml; then
    echo "✓ Declared as Warden"
    ruff check . --select S,C90,PLR0915
    pyright . --strict
else
    echo "ⓘ Vanilla profile (no enforcement)"
fi
```

---

## References

- [Power of 11: Adapting the Power of Ten for Safety-Critical Python](./research/The%20Power%20of%2011_%20Adapting%20the%20Power%20of%20Ten%20for%20Safety%20Critical%20Python.md)
- [NASA JPL: The Power of Ten](https://en.wikipedia.org/wiki/The_Power_of_Ten_Software_Development_Rules) — Original rules for C
- [Specification-Driven Development](./spec-driven.md)
- [AGENTS.md](./AGENTS.md) — Agent integration and CLI command reference
