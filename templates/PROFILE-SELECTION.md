# Profile Selection Guide

Use this guide to choose the right Specify profile for your project.

## Quick Decision Tree

```
Does your project operate in a safety-critical environment?
(e.g., aerospace flight control, automotive ECU, medical device, financial transaction core)

  YES → Use WARDEN Profile
         ├─ Deployed on standard Linux/RTOS? → Use Warden Profile A (Edge)
         └─ Bare-metal microcontroller? → Use Warden Profile B (Embedded)

  NO → Use VANILLA Profile (Default)
```

## Profile Comparison

| Aspect | Vanilla | Warden A (Edge) | Warden B (Embedded) |
|--------|---------|-----------------|-------------------|
| **Default Python Safety** | ✅ Yes (PEP 8) | ✅✅ Power of 11 | ✅✅ Power of 11 |
| **Floating Versions** | ✅ Allowed | ❌ Forbidden | ❌ Forbidden |
| **Pickle** | ✅ Allowed | ❌ Forbidden | ❌ Forbidden |
| **Eval/Exec** | ✅ Allowed (use cautiously) | ❌ Forbidden | ❌ Forbidden |
| **Package Manager** | pip or uv | ✅ uv (mandatory) | ✅ uv (mandatory) |
| **Type Checking** | "standard" | strict | strict |
| **Ruff Rules** | Standard | Aggressive (Power of 11) | Aggressive (Power of 11) |
| **Dependency Audit** | Recommended | ✅ Mandatory (pip-audit) | ✅ Mandatory (pip-audit) |
| **Assertions** | ✅ Allowed | Pydantic/explicit guards | Explicit guards only |
| **Exceptions** | ✅ Standard use | Boundary-only | Forbidden for control flow |
| **NumPy** | ✅ Optional | ✅ Pre-allocation required | ❌ Forbidden |
| **Recursion** | ✅ Allowed | ❌ Forbidden | ❌ Forbidden |
| **Function Length (max)** | 100+ lines | 50 statements | 50 statements |
| **Cyclomatic Complexity** | No strict limit | Max 10 (McCabe) | Max 10 (McCabe) |
| **Google Docstrings** | Recommended | ✅ Mandatory | ✅ Mandatory |

---

## Decision Scenarios

### Scenario 1: Web Application (REST API + Database)
```
Profile: VANILLA
Reasoning: Web applications operate in non-critical environments (worst case: service downtime).
          Standard Python practices sufficient. Upstream Spec Kit compatibility desired.
Declare: profile = "vanilla"
```

### Scenario 2: Data Processing Pipeline (ETL, Analytics)
```
Profile: VANILLA
Reasoning: Batch processing; errors are recoverable. Standard Python tools (pandas, NumPy, etc.) 
          freely available. No hard real-time constraints.
Declare: profile = "vanilla"
```

### Scenario 3: Autonomous Vehicle Sensor Fusion (High-Level)
```
Profile: WARDEN Profile A (Edge)
Reasoning: Safety-critical (human lives at risk). High-end computing (Linux, Jetson).
          Supports NumPy/Pydantic for data processing. Strict exceptions at boundaries.
Declare: profile = "warden"
         warden_target = "edge"
```

### Scenario 4: Flight Controller Firmware (Hard Real-Time)
```
Profile: WARDEN Profile B (Embedded)
Reasoning: Safety-critical. Bare-metal microcontroller (ESP32, STM32). Hard real-time 
          constraints. Cannot use C-extensions. Must manually manage garbage collection.
Declare: profile = "warden"
         warden_target = "embedded"
Uses: MicroPython
```

### Scenario 5: Financial Risk Engine (Transaction Core)
```
Profile: WARDEN Profile A (Edge)
Reasoning: Financial systems are safety-critical (fraud, data corruption, compliance violations).
          Runs on enterprise servers. Strict constraints prevent logic errors and vulnerability chains.
Declare: profile = "warden"
         warden_target = "edge"
```

### Scenario 6: Machine Learning Model Inference
```
Profile: VANILLA (if consumer-facing, non-critical)
         WARDEN Profile A (if safety-critical, e.g., autonomous driving decision)
         
Reasoning: Depends on consequences of incorrect predictions. Consumer recommendations: Vanilla.
          Autonomous vehicle decisions: Warden Profile A.
Declare: Choose based on consequence analysis.
```

---

## Migration Path

### From Vanilla → Warden

If your project starts as Vanilla but later requires safety guarantees:

1. **Update pyproject.toml:**
   ```toml
   [tool.specify]
   profile = "warden"
   warden_target = "edge"  # or "embedded"
   ```

2. **Run compliance check:**
   ```bash
   ruff check . --select C90,S,PLR0915
   pyright . --strict
   ```

3. **Address violations:**
   - Remove assertions → use `if not X: raise ValueError(...)`
   - Migrate pickle → use JSON or safetensors
   - Remove eval/exec → use static dispatch
   - Limit function size, complexity
   - Add Google-style docstrings

4. **Set up uv.lock (if not already done):**
   ```bash
   uv add <packages>  # Re-add dependencies to generate lock
   pip-audit  # Verify no CVEs
   ```

5. **Update CI/CD** to enforce Power of 11 checks (see WARDEN.md)

---

## FAQ

**Q: Can I start with Vanilla and later switch to Warden?**
A: Yes, absolutely. Many projects start Vanilla and transition when safety requirements increase.

**Q: Can a Warden project consume Vanilla code?**
A: Yes, but validate the boundary. Wrap external code in a sanitization layer.

**Q: Can a Vanilla project consume Warden code?**
A: Yes, freely. Warden code is a strict superset of Python best practices.

**Q: What if my system has mixed concerns (some real-time, some not)?**
A: Use two separate projects/modules. Real-time components: Warden Profile B. High-level logic: Warden Profile A or Vanilla. Communicate via serialized bus (CAN, UART, SPI).

**Q: Is Warden Profile B (embedded) required for IoT devices?**
A: Not necessarily. If your IoT device runs Linux and isn't safety-critical, use Vanilla or Warden Profile A. Profile B is strictly for hard real-time / bare-metal systems.

---

## References

- [WARDEN.md](../WARDEN.md) — Detailed profile documentation
- [Power of 11 Research](../research/The%20Power%20of%2011_%20Adapting%20the%20Power%20of%20Ten%20for%20Safety-Critical%20Python.md) — Scientific basis
- [AGENTS.md](../AGENTS.md) — Agent integration
