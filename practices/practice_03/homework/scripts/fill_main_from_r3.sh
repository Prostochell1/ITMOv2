#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
RES_DIR="$ROOT_DIR/practices/practice_03/homework/results"

fix_one() {
  local qid="$1"   # q1/q2/q4/q5/q6
  local label="$2" # A or B
  local main="$RES_DIR/${qid}.${label}.jsonl"
  local r3="$RES_DIR/${qid}.r3.${label}.jsonl"
  # If main missing or lacks any read tool call, and r3 exists with read, copy r3 to main
  if [ ! -s "$main" ] || ! grep -q '"tool":"read"' "$main" 2>/dev/null; then
    if [ -s "$r3" ] && grep -q '"tool":"read"' "$r3" 2>/dev/null; then
      cp -f "$r3" "$main"
      echo "Filled $main from $(basename "$r3")"
    fi
  fi
}

for Q in q1 q2 q4 q5 q6; do
  for L in A B; do
    fix_one "$Q" "$L"
  done
done

echo "Done filling missing mains from r3 where applicable."
