#!/usr/bin/env python3
"""
Simple HTTP dumper using only the standard library.
Usage:
  python3 scripts/dump_http.py <METHOD> <URL> <OUTPUT_JSON> [<BODY_JSON>|@<BODY_FILE>] [<HEADERS_JSON>|@<HEADERS_FILE>]

Writes a JSON with fields:
  {
    "timestamp": "ISO-8601",
    "request": { method, url, headers, body },
    "response": { status, headers, body }
  }
Notes:
- BODY/HEADERS can be passed inline as JSON or via @file path.
- Default headers include Accept and User-Agent; when BODY is set, Content-Type: application/json is also added.
"""
import json
import sys
from urllib.request import Request, urlopen
from datetime import datetime, timezone


def _parse_json_arg(arg: str | None):
    if not arg:
        return None
    if arg == "-":
        return None
    if arg.startswith("@"):
        with open(arg[1:], "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(arg)


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        print("Usage: dump_http.py <METHOD> <URL> <OUTPUT_JSON> [<BODY_JSON>|@<BODY_FILE>] [<HEADERS_JSON>|@<HEADERS_FILE>]", file=sys.stderr)
        return 2
    _, method, url, out_path, *rest = argv
    body = _parse_json_arg(rest[0]) if len(rest) >= 1 else None
    extra_headers = _parse_json_arg(rest[1]) if len(rest) >= 2 else None

    req_headers = {
        "Accept": "application/json",
        "User-Agent": "mini-dumper/1.0",
    }
    if body is not None:
        req_headers["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    else:
        data = None
    if extra_headers:
        req_headers.update({str(k): str(v) for k, v in extra_headers.items()})

    request = Request(url, data=data, method=method, headers=req_headers)
    try:
        with urlopen(request, timeout=10) as resp:
            response = {
                "status": resp.status,
                "headers": dict(resp.headers.items()),
                "body": resp.read().decode("utf-8", errors="replace"),
            }
    except Exception as exc:
        response = {
            "status": None,
            "headers": {},
            "body": str(exc),
            "error": type(exc).__name__,
        }
    # urllib adds Host automatically; reflect it in the dump
    req_dump = {
        "method": method,
        "url": url,
        "headers": {**req_headers, "Host": Request(url).host},
        "body": body,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request": req_dump,
            "response": response,
        }, f, ensure_ascii=False, indent=2)
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
