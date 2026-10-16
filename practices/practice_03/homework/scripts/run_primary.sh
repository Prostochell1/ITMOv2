#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HW_DIR="$ROOT_DIR/practices/practice_03/homework"
RES_DIR="$HW_DIR/results"
DEMO_A="$ROOT_DIR/practices/practice_03/lab/demo"
DEMO_B="$ROOT_DIR/practices/practice_03/homework/demo_b"

mkdir -p "$RES_DIR"

declare -A PROMPTS
PROMPTS["q1"]='Как запустить проверку артефактов Практики 1? Укажи file:line.'
PROMPTS["q2"]='Какие файлы проверяет цель make test в Практике 1? Приведи список и file:line.'
PROMPTS["q4"]='В каком разделе зафиксированы метрики проекта? Укажи file:line.'
PROMPTS["q5"]='Какая CI‑система настроена для запуска тестов? Если сведений нет — скажи об этом. Укажи file:line.'
PROMPTS["q6"]='В Makefile Практики 1 явно вызывается pytest — в какой строке? Если предпосылка неверна, скажи об этом. Укажи file:line.'

run_one() {
  local variant_dir="$1"; shift
  local qid="$1"; shift
  local label="$1"; shift # A or B
  local prompt="$1"; shift
  (
    set +e
    cd "$variant_dir" || exit 0
    for attempt in 1 2; do
      timeout 240 opencode run --agent local-guide --model ollama/itmo-agent --format json \
        "$prompt" > "$RES_DIR/${qid}.${label}.jsonl"
      # success heuristic: non-empty file
      if [ -s "$RES_DIR/${qid}.${label}.jsonl" ]; then
        break
      fi
      sleep 2
    done
    exit 0
  ) || true
}

for Q in q1 q2 q4 q5 q6; do
  echo "== PRIMARY $Q A/B =="
  run_one "$DEMO_A" "$Q" A "${PROMPTS[$Q]}"
  run_one "$DEMO_B" "$Q" B "${PROMPTS[$Q]}"
done

echo "Primary A/B runs stored in $RES_DIR"
