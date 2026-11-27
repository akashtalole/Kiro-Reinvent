#!/usr/bin/env python3
"""Alexa+ add-on pre-flight.

  check_addon.py addon.json          validate manifest limits (exit 1 on any FAIL)
  check_addon.py --probe URL         unauthenticated probe: expect 401 and no WWW-Authenticate
The manifest is walked generically, so field paths that differ slightly still get checked.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request

ICON_SIZES = {72, 64, 88, 126, 180, 241}
IMG_RX = re.compile(r"^https://.+\.(png|jpe?g|webp)(\?.*)?$", re.I)


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, node


def check_manifest(m: dict) -> list[tuple[str, bool, str]]:
    leaves = list(walk(m))
    out = []

    def find(rx):
        return [(p, v) for p, v in leaves if re.search(rx, p, re.I)]

    for path, v in find(r"(^|\.)name(\.value)?$"):
        if isinstance(v, str):
            out.append(("name ≤ 30", len(v) <= 30, f"{path}: {len(v)} chars"))
    for path, v in find(r"shortDescription"):
        if isinstance(v, str):
            out.append(("shortDescription ≤ 123", len(v) <= 123, f"{path}: {len(v)} chars"))
    for path, v in find(r"fullDescription"):
        if isinstance(v, str):
            out.append(("fullDescription ≤ 4000", len(v) <= 4000, f"{path}: {len(v)} chars"))
    phrases = [v for p, v in find(r"examplePhrases\[\d+\]") if isinstance(v, str)]
    if phrases:
        out.append(("3–4 example phrases", 3 <= len(phrases) <= 4, f"{len(phrases)} phrases"))
        out.append(("example phrase ≤ 200", all(len(x) <= 200 for x in phrases), "longest " + str(max(map(len, phrases)))))
    images = [(p, v) for p, v in leaves if isinstance(v, str) and re.search(r"(icon|carousel|banner|image)", p, re.I) and v.startswith(("http://", "https://"))]
    for p, v in images:
        out.append(("image is HTTPS png/jpg/webp", bool(IMG_RX.match(v)), p))
    sizes = {int(n) for p, v in leaves for n in re.findall(r"(\d{2,3})", p) if re.search(r"icon", p, re.I)}
    if sizes:
        missing = sorted(ICON_SIZES - sizes)
        out.append(("all six icon sizes", not missing, "missing " + ", ".join(map(str, missing)) if missing else "ok"))
    return out


def probe(url: str) -> list[tuple[str, bool, str]]:
    req = urllib.request.Request(url, data=b'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}',
                                 headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    try:
        urllib.request.urlopen(req, timeout=10)
        return [("unauthenticated request is rejected", False, "got 2xx without a token")]
    except urllib.error.HTTPError as e:
        return [("status 401", e.code == 401, str(e.code)),
                ("no WWW-Authenticate header", "WWW-Authenticate" not in e.headers, str(e.headers.get("WWW-Authenticate")))]


def main(argv: list[str]) -> int:
    if argv[:1] == ["--probe"] and len(argv) == 2:
        results = probe(argv[1])
    elif len(argv) == 1:
        results = check_manifest(json.load(open(argv[0], encoding="utf-8")))
    else:
        print(__doc__, file=sys.stderr)
        return 2
    for name, ok, detail in results:
        print(("PASS " if ok else "FAIL ") + f"{name} — {detail}")
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
