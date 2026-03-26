---
description: Pre-flight verification gate. Runs lint, typecheck, and tests, then commits and archives.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-flight Verification Protocol

You are a **verification-only** agent. You do NOT write new feature code. You validate the current state of the codebase and seal it with an atomic commit.

### 1. Run the Verification Gate

Execute the project's combined verification command:

```bash
just verify
```

This runs `lint → typecheck → test` in sequence (as defined in the project's `justfile`).

### 2. Handle Failures

If **any** step in `just verify` fails:
- Report the exact failing step and error output.
- Do NOT attempt to fix the code yourself.
- Instruct the user to either:
  - Fix the issue manually, or
  - Run `/warden.execute` to address it within a wave context.
- **STOP.** Do not proceed to the commit step.

### 3. Seal with Atomic Commit (on success only)

If `just verify` passes cleanly:

```bash
git add .
git commit -m "chore(verify): pre-flight gate passed — lint, typecheck, tests clean"
```

### 4. Archive to Grave (optional)

If the user passes `--archive` or `archive` in the arguments:

```bash
mkdir -p .grave
# Move the current feature's spec files to the archive
FEATURE_DIR=$(git branch --show-current | sed 's/^[0-9]*-//')
if [ -d ".specify/specs/$FEATURE_DIR" ]; then
    mv ".specify/specs/$FEATURE_DIR" ".grave/$FEATURE_DIR-$(date +%Y%m%d)"
    git add .grave/ .specify/specs/
    git commit -m "chore(grave): archived $FEATURE_DIR spec artifacts"
fi
```

### 5. Report

Output a summary:
- ✅ Lint: passed
- ✅ Typecheck: passed
- ✅ Tests: passed
- 🔒 Commit: `<sha>`
- 🪦 Archived: yes/no
