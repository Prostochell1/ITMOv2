#!/usr/bin/env python3
"""
Run post-fix verification scenarios and write HTTP dumps to evidence/after.
This script performs the same cases as Stage 3 but expects secure outcomes.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError


BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "evidence" / "after"
BASEURL = "http://127.0.0.1:8066"


def dump(method: str, url: str, out_rel: str, body: dict | None = None, headers: dict | None = None):
    out = OUT / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    req_headers = {"Accept": "application/json", "User-Agent": "mini-dumper/1.0"}
    if headers:
        req_headers.update(headers)
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=req_headers, method=method)
    try:
        with urlopen(req, timeout=5) as r:
            resp = {
                "status": r.status,
                "headers": dict(r.headers.items()),
                "body": r.read().decode("utf-8", "replace"),
            }
    except HTTPError as e:
        resp = {
            "status": e.code,
            "headers": dict(e.headers.items()),
            "body": e.read().decode("utf-8", "replace"),
            "error": "HTTPError",
        }
    out.write_text(json.dumps({
        "request": {"method": method, "url": url, "headers": req_headers, "body": body},
        "response": resp,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out_rel)


def login(username: str, password: str) -> dict:
    req = Request(BASEURL + "/login", data=json.dumps({"username": username, "password": password}).encode(),
                  headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=5) as r:
        token = json.loads(r.read().decode())["token"]
    return {"X-Token": token}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    alice = login("alice", "learn-alice")
    staff = login("staff", "learn-staff")

    # 1 SQLi (should be blocked or benign)
    dump("GET", f"{BASEURL}/profile?id=1%20OR%201%3D1", "sqli/profile-or.json", headers=alice)
    dump("GET", f"{BASEURL}/search?q=%27%20OR%20%271%27%3D%271", "sqli/search-or.json")
    dump("GET", f"{BASEURL}/assistant/context?order_id=1%20OR%201%3D1", "sqli/assistant-context-or.json", headers=alice)

    # 2 BAC
    dump("GET", f"{BASEURL}/profile?id=2", "bac/profile-2.json", headers=alice)
    dump("GET", f"{BASEURL}/orders", "bac/orders.json", headers=alice)

    # 3 X-Role escalation blocked
    dump("GET", f"{BASEURL}/admin/export", "role/admin-export-as-alice.json", headers=alice)

    # 4 Price tampering ignored
    dump("POST", f"{BASEURL}/orders", "price/order-alice.json", body={"product": "lamp", "price": 1}, headers=alice)

    # 5 Files restrictions
    dump("GET", f"{BASEURL}/files?user=alice&path=../bob/receipt.txt", "path/files-bob.json", headers=alice)
    dump("GET", f"{BASEURL}/files?user=bob&path=receipt.txt", "path/files-bob-own.json", headers=alice)
    dump("GET", f"{BASEURL}/files?user=alice&path=../private/operator-note.txt", "path/files-operator.json", headers=alice)

    # 6 XSS escaped
    dump("POST", f"{BASEURL}/reviews", "xss/review-post.json", body={"product": "chair", "text": "<script>alert('xss')</script>"}, headers=alice)
    dump("GET", f"{BASEURL}/reviews/view", "xss/review-view.json", headers=alice)

    # 7 Assistant policy
    dump("POST", f"{BASEURL}/assistant/execute", "assistant/execute-export-profiles.json", body={"decision": {"tool": "export_profiles"}}, headers=alice)
    dump("POST", f"{BASEURL}/assistant/execute", "assistant/execute-delete-tree.json", body={"decision": {"tool": "delete_tree", "arguments": {"path": "."}}}, headers=alice)
    dump("POST", f"{BASEURL}/assistant/execute", "assistant/execute-read-own.json", body={"decision": {"tool": "read_file", "arguments": {"path": "files/alice/receipt.txt"}}}, headers=alice)

    # 8 Logs
    dump("GET", f"{BASEURL}/debug/logs", "logs/debug-logs-alice.json", headers=alice)
    dump("GET", f"{BASEURL}/debug/logs", "logs/debug-logs-staff.json", headers=staff)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
