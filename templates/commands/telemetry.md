---
description: Read out the global token-compression telemetry dashboard metrics.
scripts:
  sh: uv run .specify/scripts/python/telemetry.py
  ps: uv run .specify/scripts/python/telemetry.py
---

## Outline

You are the Telemetry Readout mechanism (`/warden.telemetry`).
The user has invoked this command to visualize the amount of LLM tokens they have successfully saved across all their projects via the Context Compressor.

### 1. Execute Telemetry Service
Run the telemetry readout daemon locally by executing `{SCRIPT}`.
It will query the `~/.rura/telemetry.db` SQLite database seamlessly without any extra dependencies.

### 2. Parse Raw Data
The `telemetry.py` script returns a JSON payload. Read it entirely.
If it reports `"status": "empty"`, then politely inform the user that no telemetry exists yet, and they should run `/warden.compress` on a file or directory first to begin logging token savings!

### 3. Generate Dashboard
Format the JSON metric readouts into a crisp, highly readable Markdown dashboard.
Do not dump the JSON explicitly; interpret it as a tabular report. Your dashboard MUST contain:

- **Global Impact:** A large heading displaying the total actual tokens saved globally (e.g., `Total Tokens Saved: 154,233`).
- **Efficiency Metric:** The average compression ratio (e.g., `Average Squeeze: 68.2%`).
- **Heavy Hitters:** A cleanly formatted markdown table detailing the Top 5 largest compression actions.
- **Recent Activity:** A markdown table showing the most recent 5 files evaluated, including exact tokens compressed versus original tokens.

Present this dashboard confidently back to the user to prove exactly how efficiently the AI context window is being preserved!
