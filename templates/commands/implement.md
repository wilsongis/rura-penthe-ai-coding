---
description: REDIRECT. This command has been replaced by warden.execute. Use warden.execute to process XML waves one at a time.
handoffs:
  - label: Execute Waves
    agent: warden.execute
    prompt: Start the XML wave state machine
    send: true
---

## ⚠️ Command Relocated

**`/warden.implement`** has been replaced by **`/warden.execute`**.

The new `/warden.execute` command operates as a **strict state machine**, processing one XML `<wave>` at a time instead of running the entire implementation monolithically.

### To proceed:

Run `/warden.execute` to begin processing the next pending wave.
