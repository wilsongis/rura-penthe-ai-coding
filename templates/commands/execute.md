---
description: Execute the next pending XML wave from tasks.md using a strict state machine.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Strict State Machine Execution

You operate as a Strict State Machine executing XML `<wave>` chunks from `tasks.md`.
To maintain pristine context and prevent codebase mutilation, you must process exactly **ONE** pending `<wave>` at a time.

### 1. Context Acquisition
- Run `{SCRIPT}` to ensure prerequisites.
- Parse `tasks.md` and identify the FIRST `<wave>` block with `status="pending"`.
- Read `STACK.md` to ensure you adhere to strict Negative Constraints (e.g., do not use pip if uv is enforced).
- Read `plan.md` and `spec.md` only as necessary for the tasks within this specific wave.

### 2. Execution Loop
For the pending `<wave>` you identified:
1. Examine the internal `<task>` elements.
2. Formulate your execution strategy based on the `<action>` tags.
3. Apply the necessary code changes across the `<files>` specified.
4. Ensure your implementation adheres to project linters and formatters.

### 3. Verification & Commit Gate (CRITICAL)
Before you are allowed to complete this wave or move to the next:
1. Run the command specified in the wave's `<verify>` tag (e.g., `just test && just lint`).
2. If the verification **FAILS**:
   - You are trapped in a fix loop.
   - Analyze the error.
   - Modify the code to fix the problem.
   - Rerun the `<verify>` command.
   - You MUST NOT proceed until the verification passes. Do not touch other waves.
3. If the verification **PASSES**:
   - Stage the changes: `git add .`
   - Create a semantic git commit: `git commit -m "feat(wave-{id}): implementation of wave tasks"`
   - Open `tasks.md` and change this wave's status from `status="pending"` to `status="completed"`.

### 4. Handoff
After successfully committing the wave:
- Report the successful completion of the wave.
- Do NOT automatically start the next wave.
- Stop and instruct the user that the wave is securely committed, and they may run `/warden.execute` again to process the next wave.
