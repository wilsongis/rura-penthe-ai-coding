# [PROJECT_NAME] Constitution (Vanilla Profile)

> **This constitution applies to Vanilla Profile projects.** Vanilla projects declare `profile = "vanilla"` in `pyproject.toml`. For safety-critical systems, use Warden Profile instead. See [WARDEN.md](../WARDEN.md).

## Core Principles

### I. Standard Python Best Practices
Follow PEP 8 and standard Python conventions. Code should be readable, maintainable, and follow community best practices.

### II. Testing and Documentation
Maintain adequate test coverage (≥70%). Use docstrings for public APIs. Type hints are recommended but not mandatory.

### III. Dependency Management
Use `uv` as the preferred package manager for reproducibility. Floating versions are permitted but should be reviewed during dependency updates.

### IV. Code Quality
Use standard linters: `ruff`, `pylint`, or similar. Fix warnings and maintain consistent code style across the project.

### V. Architecture
- **Framework Liberty:** Choose appropriate frameworks for your use case (Django, FastAPI, Flask, etc.)
- **Design Patterns:** Use standard design patterns; no special constraints
- **Language Features:** Full Python expressiveness permitted (pickle, eval in constrained contexts, metaprogramming where beneficial)

## Documentation Standard
Use docstrings following PEP 257 conventions. For larger projects, Google Style is recommended but not mandatory. Document:
- Function parameters and return values
- Raised exceptions (if any)
- Usage examples for complex functions

## Testing Strategy
- Unit tests for core logic
- Integration tests for major workflows
- Follow standard test discovery patterns (pytest, unittest)

## Governance
Code reviews should verify general code quality, test coverage, and adherence to project style guide.

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
