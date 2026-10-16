#!/usr/bin/env python3
import json, os, re, statistics
from glob import glob

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')

run_re = re.compile(r"^q(?P<q>[12456])\.r(?P<rep>[123])\.(?P<variant>[AB])\.jsonl$")

def parse_line_times(obj):
    # Returns (start_ms, end_ms) if available; else None
    t = obj.get('part', {}).get('time') or obj.get('time')
    if isinstance(t, dict) and 'start' in t and 'end' in t:
        try:
            return int(t['start']), int(t['end'])
        except Exception:
            return None
    return None

def parse_file(path):
    first, last = None, None
    first_ts, last_ts = None, None
    total = 0
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or not line.startswith('{'):
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            se = parse_line_times(obj)
            if se:
                s,e = se
                if first is None or s < first:
                    first = s
                if last is None or e > last:
                    last = e
                if e >= s:
                    total += (e - s)
            # Fallback: use top-level timestamp field if present
            ts = obj.get('timestamp')
            if isinstance(ts, (int, float)):
                ts = int(ts)
                if first_ts is None or ts < first_ts:
                    first_ts = ts
                if last_ts is None or ts > last_ts:
                    last_ts = ts
    wall = None
    if first is not None and last is not None:
        wall = (last - first)/1000.0
    elif first_ts is not None and last_ts is not None:
        wall = (last_ts - first_ts)/1000.0
    total_s = total/1000.0 if total>0 else None
    return {
        'wall_seconds': wall,
        'total_seconds': total_s,
        'decode_tokens_per_second': None
    }

def median(values):
    vs = [v for v in values if v is not None]
    return statistics.median(vs) if vs else None

def main():
    runs = {}
    for fname in os.listdir(RESULTS_DIR):
        m = run_re.match(fname)
        if not m:
            continue
        q = 'q'+m.group('q')
        var = m.group('variant')
        path = os.path.join(RESULTS_DIR, fname)
        metrics = parse_file(path)
        runs.setdefault(q, {}).setdefault(var, []).append({
            'file': fname,
            **metrics
        })

    med = {}
    for q, variants in runs.items():
        med[q] = {}
        for var, arr in variants.items():
            ws = median([x['wall_seconds'] for x in arr])
            ts = median([x['total_seconds'] for x in arr])
            dps = median([x.get('decode_tokens_per_second') for x in arr])
            med[q][var] = {
                'wall_seconds_median': ws,
                'total_seconds_median': ts,
                'decode_tokens_per_second_median': dps
            }

    out = {
        'runs': runs,
        'medians': med,
        'units': {
            'time': 'seconds',
            'speed': 'tokens/second'
        }
    }
    with open(os.path.join(RESULTS_DIR, 'metrics.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Wrote {os.path.join(RESULTS_DIR, 'metrics.json')}")

if __name__ == '__main__':
    main()
