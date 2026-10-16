#!/usr/bin/env python3
import json, os, re, sys
from glob import glob

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
GOLD_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 'gold.json')

q_re = re.compile(r"^q(?P<q>[12456])\.(?P<tag>warm|r[123])\.(?P<variant>[AB])\.jsonl$")
main_re = re.compile(r"^q(?P<q>[12456])\.(?P<variant>[AB])\.jsonl$")

def load_gold():
    with open(GOLD_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    gold = {}
    for item in data.get('questions', []):
        gold[item['id']] = item['gold']
    return gold

def parse_answer_and_reads(path):
    answer = None
    reads = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith('{'):
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            # collect read tool events
            if obj.get('type') == 'tool_use':
                part = obj.get('part') or {}
                if part.get('tool') == 'read':
                    state = (part.get('state') or {}).get('input') or {}
                    p = state.get('path') or state.get('filePath')
                    if p:
                        reads.append(p)
            # try to extract final/assistant content
            if obj.get('type') in ('final','message','assistant','answer'):
                text = obj.get('text') or obj.get('content')
                if isinstance(text, str) and text.strip():
                    answer = text.strip()
            # Roo/OpenCode variants: top-level part has type 'assistant'
            part = obj.get('part') or {}
            if part.get('type') in ('assistant','final'):
                txt = part.get('text') or part.get('content')
                if isinstance(txt, str) and txt.strip():
                    answer = txt.strip()
    return answer, reads

def main():
    # Prefer main files qN.A.jsonl / qN.B.jsonl; fallback to r3 if main missing
    files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('.jsonl')]
    pairs = {}
    for f in files:
        m = main_re.match(f)
        if m:
            q = 'q' + m.group('q')
            var = m.group('variant')
            pairs.setdefault(q, {})[var] = f
    # fill missing with r3 where available
    for f in files:
        m = q_re.match(f)
        if m and m.group('tag') == 'r3':
            q = 'q' + m.group('q')
            var = m.group('variant')
            pairs.setdefault(q, {})
            pairs[q].setdefault(var, f)

    gold = load_gold()
    out = {'evaluations': []}
    for q, by_var in sorted(pairs.items()):
        for var in ('A','B'):
            fname = by_var.get(var)
            if not fname:
                out['evaluations'].append({
                    'question': q,
                    'variant': var,
                    'status': 'missing',
                })
                continue
            path = os.path.join(RESULTS_DIR, fname)
            ans, reads = parse_answer_and_reads(path)
            out['evaluations'].append({
                'question': q,
                'variant': var,
                'file': fname,
                'answer_present': bool(ans),
                'answer_preview': (ans[:200] + '…') if ans and len(ans)>200 else ans,
                'read_calls': reads,
            })

    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
