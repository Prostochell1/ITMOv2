#!/usr/bin/env bash
set -euo pipefail

# Run A/B experiments for questions q1,q2,q4,q5,q6 with warm-up and 3 repeats each.
# Requirements: run inside WSL where both `ollama serve` and `opencode` are available.
# Fixed params: model=ollama/itmo-agent, temperature=0.2, seed=42, think=false (via model/config), same context and limits.

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
  local variant_dir="$1"
  local qid="$2"
  local label="$3" # A or B
  local prompt="$4"
  local tag="$5"   # r1/r2/r3 or warm
  ( set +e; cd "$variant_dir" && \
    timeout 120 opencode run --standalone --agent local-guide --model ollama/itmo-agent --format json \
      "$prompt" > "$RES_DIR/${qid}.${tag}.${label}.jsonl"; exit 0 ) || true
}

for Q in q1 q2 q4 q5 q6; do
  echo "== $Q warm-up A/B =="
  run_one "$DEMO_A" "$Q" A "${PROMPTS[$Q]}" warm || true
  run_one "$DEMO_B" "$Q" B "${PROMPTS[$Q]}" warm || true

  echo "== $Q repeats A =="
  run_one "$DEMO_A" "$Q" A "${PROMPTS[$Q]}" r1 || true
  run_one "$DEMO_A" "$Q" A "${PROMPTS[$Q]}" r2 || true
  run_one "$DEMO_A" "$Q" A "${PROMPTS[$Q]}" r3 || true

  echo "== $Q repeats B =="
  run_one "$DEMO_B" "$Q" B "${PROMPTS[$Q]}" r1 || true
  run_one "$DEMO_B" "$Q" B "${PROMPTS[$Q]}" r2 || true
  run_one "$DEMO_B" "$Q" B "${PROMPTS[$Q]}" r3 || true
done

echo "Done. Results in $RES_DIR"
