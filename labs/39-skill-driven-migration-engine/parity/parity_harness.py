#!/usr/bin/env python3
"""Parity harness: replay recorded HTTP cases against the legacy app and the port, and diff the responses.

    python parity_harness.py --cases cases.json --legacy http://localhost:8000 --target http://localhost:8080
    python parity_harness.py --self-test     # proves the harness detects injected breakage (Phase 1 gate)

cases.json: [{"id": "books-list", "method": "GET", "path": "/api/books", "body": null,
              "ignore": ["$.meta.generated_at"]}]
Exit code 0 = parity, 1 = mismatches (report printed as JSON lines).
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from typing import Any


def fetch(base: str, case: dict) -> tuple[int, Any]:
    data = json.dumps(case["body"]).encode() if case.get("body") is not None else None
    req = urllib.request.Request(base.rstrip("/") + case["path"], data=data, method=case.get("method", "GET"),
                                 headers={"content-type": "application/json", "accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, raw.decode(errors="replace")


def strip(obj: Any, ignore: list[str], path: str = "$") -> Any:
    if path in ignore:
        return "<ignored>"
    if isinstance(obj, dict):
        return {k: strip(v, ignore, f"{path}.{k}") for k, v in sorted(obj.items())}
    if isinstance(obj, list):
        return [strip(v, ignore, f"{path}[]") for v in obj]
    return obj


def diff(a: Any, b: Any, path: str = "$") -> list[str]:
    if type(a) is not type(b):
        return [f"{path}: type {type(a).__name__} != {type(b).__name__}"]
    if isinstance(a, dict):
        out = [f"{path}.{k}: missing in target" for k in a.keys() - b.keys()]
        out += [f"{path}.{k}: extra in target" for k in b.keys() - a.keys()]
        for k in a.keys() & b.keys():
            out += diff(a[k], b[k], f"{path}.{k}")
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} != {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in diff(x, y, f"{path}[{i}]")]
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


def compare(cases: list[dict], legacy, target) -> list[dict]:
    """legacy/target are callables case -> (status, body)."""
    results = []
    for case in cases:
        (s1, b1), (s2, b2) = legacy(case), target(case)
        ign = case.get("ignore", [])
        problems = ([f"status {s1} != {s2}"] if s1 != s2 else []) + diff(strip(b1, ign), strip(b2, ign))
        results.append({"id": case["id"], "ok": not problems, "problems": problems[:20]})
    return results


def self_test() -> int:
    """A harness that can't see injected breakage is not trusted (Phase 1 gate)."""
    cases = [{"id": "book", "method": "GET", "path": "/b/1", "ignore": ["$.generated_at"]}]
    good = lambda c: (200, {"id": 1, "title": "Dune", "hidden": None, "generated_at": "t1"})
    same = lambda c: (200, {"id": 1, "title": "Dune", "hidden": None, "generated_at": "t2"})
    broken = lambda c: (200, {"id": 1, "title": "dune", "hidden": None, "generated_at": "t2"})
    leaky = lambda c: (200, {"id": 1, "title": "Dune", "hidden": None, "generated_at": "t2", "password": "x"})
    checks = {
        "passes on identical behaviour (ignoring volatile fields)": all(r["ok"] for r in compare(cases, good, same)),
        "fails on changed value": not compare(cases, good, broken)[0]["ok"],
        "fails on leaked extra field": not compare(cases, good, leaky)[0]["ok"],
        "fails on status change": not compare(cases, good, lambda c: (500, None))[0]["ok"],
    }
    for name, ok in checks.items():
        print(("PASS " if ok else "FAIL ") + name)
    return 0 if all(checks.values()) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases")
    ap.add_argument("--legacy")
    ap.add_argument("--target")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.cases and a.legacy and a.target):
        ap.error("--cases, --legacy and --target are required (or use --self-test)")
    results = compare(json.load(open(a.cases)), lambda c: fetch(a.legacy, c), lambda c: fetch(a.target, c))
    for r in results:
        print(json.dumps(r))
    passed = sum(r["ok"] for r in results)
    print(json.dumps({"summary": f"{passed}/{len(results)} cases at parity"}))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
