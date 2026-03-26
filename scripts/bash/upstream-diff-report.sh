#!/usr/bin/env bash
# Rura Penthe — Upstream Diff Reporter
# Shows which fork-sensitive files have changed in upstream before you merge.
# Usage: ./scripts/bash/upstream-diff-report.sh
# Prerequisites: git remote add upstream https://github.com/github/spec-kit.git

set -euo pipefail

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Files that are known to diverge in the fork
WATCHED_FILES=(
    "src/specify_cli/config.py"
    "src/specify_cli/agents.py"
    "src/specify_cli/__init__.py"
    "src/specify_cli/extensions.py"
    "src/specify_cli/presets.py"
    "README.md"
    "templates/commands/execute.md"
    "templates/commands/tasks.md"
    "templates/commands/implement.md"
    "templates/commands/verify.md"
    "templates/commands/constitution.md"
    "templates/pyproject-template.toml"
)

# Ensure upstream remote exists
if ! git remote | grep -q "^upstream$"; then
    echo -e "${RED}Error: 'upstream' remote not found.${NC}"
    echo "Run: git remote add upstream https://github.com/github/spec-kit.git"
    exit 1
fi

echo -e "${CYAN}Fetching upstream...${NC}"
git fetch upstream --quiet

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Upstream Diff Report: main ↔ upstream/main${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Get full diff stat
CHANGED_FILES=$(git diff main..upstream/main --name-only 2>/dev/null || true)

if [ -z "$CHANGED_FILES" ]; then
    echo -e "${GREEN}✅ No upstream changes detected. You are up to date.${NC}"
    exit 0
fi

TOTAL=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
echo -e "Total files changed upstream: ${YELLOW}${TOTAL}${NC}"
echo ""

# Check watched files
CONFLICTS=0
echo "Fork-sensitive files:"
echo "─────────────────────"
for watched in "${WATCHED_FILES[@]}"; do
    if echo "$CHANGED_FILES" | grep -q "^${watched}$"; then
        echo -e "  ${RED}⚠ CHANGED${NC}  $watched"
        CONFLICTS=$((CONFLICTS + 1))
    else
        echo -e "  ${GREEN}✓ clean${NC}    $watched"
    fi
done

echo ""
echo "─────────────────────"
if [ "$CONFLICTS" -eq 0 ]; then
    echo -e "${GREEN}✅ No fork-sensitive files changed. Safe to merge.${NC}"
else
    echo -e "${YELLOW}⚠  ${CONFLICTS} fork-sensitive file(s) changed. Manual review needed during merge.${NC}"
    echo ""
    echo "Merge strategy:"
    echo "  git checkout main"
    echo "  git checkout -b merge/upstream-sync"
    echo "  git merge upstream/main"
    echo "  # Resolve conflicts, keeping YOUR versions of fork-sensitive files"
    echo "  uv tool install specify-cli --force --from ."
    echo "  specify check"
fi

echo ""
echo "Full diff stat:"
git diff main..upstream/main --stat | tail -5
