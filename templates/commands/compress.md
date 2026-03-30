---
description: Hardware-accelerated LLMLingua context compression to shrink oversized repository artifacts.
scripts:
  sh: uv run .specify/scripts/python/compress.py {ARGS}
  ps: uv run .specify/scripts/python/compress.py {ARGS}
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are the Context Compressor (`/warden.compress`).
The user invokes this command to semantically compress a file or payload before feeding it to other subagents, saving significant LLM tokens.

### 1. Identify Target

Parse the target file or command string provided in `$ARGUMENTS`.
If no target is specified, immediately ask the user to provide a path to a file they wish to compress.

### 2. Execute Compression Daemon

Run the following command exactly as generated for your environment, replacing `{ARGS}` with `$ARGUMENTS` in your execution if not already substituted:

`{SCRIPT}`

*Note*: The `compress.py` script uses PEP 723 to automatically download its Torch/LLMLingua dependencies inside a temporary `uv` environment. The first execution may take a while depending on network conditions.

### 3. Output Processing

Read the results of the script.
If the user did not pass an `--output` argument, the script will print the compressed text to stdout. 
You should capture this output and optionally save it to a reasonably named file in `.specify/memory/` (e.g. `compressed_<filename>`) if it's very large, or present it back to the user if requested.

### 4. Provide Summary

Once done, report:
- Original size
- Compressed size
- Theoretical Percentage Saved (from the script output)
- Where the compressed artifact is now located.
