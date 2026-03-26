#!/usr/bin/env bash
# Rura Penthe — Auto-generate CHANGELOG.md from semantic wave commits.
# Usage: ./scripts/bash/generate-changelog.sh [--append]
# Run after completing a set of waves to produce release notes.

set -euo pipefail

CHANGELOG="CHANGELOG.md"
APPEND=false

for arg in "$@"; do
    case "$arg" in
        --append) APPEND=true ;;
    esac
done

DATE=$(date +%Y-%m-%d)
VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "unreleased")

# Collect wave commits
WAVE_COMMITS=$(git log --oneline --grep="^feat(wave-" | head -50)
CHORE_COMMITS=$(git log --oneline --grep="^chore(" | head -20)
FIX_COMMITS=$(git log --oneline --grep="^fix(" | head -20)

generate_section() {
    local header="$1"
    local commits="$2"
    if [ -n "$commits" ]; then
        echo "### $header"
        echo ""
        echo "$commits" | while read -r line; do
            echo "- $line"
        done
        echo ""
    fi
}

ENTRY="## [$VERSION] - $DATE

$(generate_section "🌊 Waves" "$WAVE_COMMITS")
$(generate_section "🐛 Fixes" "$FIX_COMMITS")
$(generate_section "🔧 Chores" "$CHORE_COMMITS")"

if [ "$APPEND" = true ] && [ -f "$CHANGELOG" ]; then
    # Insert after the first line (# Changelog)
    TEMP=$(mktemp)
    head -1 "$CHANGELOG" > "$TEMP"
    echo "" >> "$TEMP"
    echo "$ENTRY" >> "$TEMP"
    tail -n +2 "$CHANGELOG" >> "$TEMP"
    mv "$TEMP" "$CHANGELOG"
    echo "✅ Appended entry to $CHANGELOG"
else
    echo "# Changelog" > "$CHANGELOG"
    echo "" >> "$CHANGELOG"
    echo "$ENTRY" >> "$CHANGELOG"
    echo "✅ Generated $CHANGELOG"
fi
