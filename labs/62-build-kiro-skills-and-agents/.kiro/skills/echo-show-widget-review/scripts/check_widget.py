#!/usr/bin/env python3
"""Lint an Alexa+ add-on widget (MCP Apps ui:// HTML) against the Echo Show design rules.

  check_widget.py widget.html [--meta tool-meta.json]
Exit 1 if any FAIL. WARN lines are advice. Static checks only: run the Local Inspector and a real device too.
"""
from __future__ import annotations

import json
import re
import sys
from urllib.parse import urlparse

TYPE_TOKENS = {48, 40, 32, 28, 24, 20, 18, 16, 14, 12, 10, 8}
FORBIDDEN = {
    "window.parent": r"\bwindow\.parent\b",
    "localStorage": r"\blocalStorage\b",
    "sessionStorage": r"\bsessionStorage\b",
    "document.cookie": r"\bdocument\.cookie\b",
}


def hosts(urls):
    return {urlparse(u).netloc for u in urls if u.startswith(("http://", "https://"))}


def check(html: str, meta: dict | None) -> list[tuple[str, str, str]]:
    out = []

    def add(ok, name, detail="", warn=False):
        out.append(("PASS" if ok else ("WARN" if warn else "FAIL"), name, detail))

    for name, rx in FORBIDDEN.items():
        add(not re.search(rx, html), f"sandbox: no {name}")
    ext_scripts = re.findall(r"<script[^>]+src=[\"']([^\"']+)", html, re.I)
    ext_css = re.findall(r"<link[^>]+rel=[\"']stylesheet[\"'][^>]*href=[\"']([^\"']+)", html, re.I)
    add(not ext_scripts and not ext_css, "single HTML file (no external scripts or stylesheets)",
        ", ".join(ext_scripts + ext_css))
    add(bool(re.search(r"addEventListener\(\s*[\"']message[\"']", html)), "listens on the postMessage bridge")
    add("hostContext" in html, "reads hostContext")
    add("host-context-changed" in html, "re-resolves on host-context-changed")
    add("deviceClass" in html, "uses deviceClass (authoritative)")
    add(bool(re.search(r"\b768\b", html)) and bool(re.search(r"\b480\b", html)), "authored at the 768x480 base canvas")
    add(bool(re.search(r"\bzoom\b", html)), "applies one root scale (zoom)", warn=True)
    sizes = {int(x) for x in re.findall(r"font-size\s*:\s*(\d+)px", html)}
    bad = sorted(sizes - TYPE_TOKENS)
    add(not bad, "font sizes use type tokens", "off-token: " + ", ".join(map(str, bad)) if bad else "")
    add(bool(re.search(r"prefers-color-scheme|theme", html)), "handles light and dark")
    imgs = re.findall(r"<img[^>]+src=[\"']([^\"']+)", html, re.I) + re.findall(r"url\([\"']?(https?://[^)\"']+)", html)
    add(all(u.startswith("https://") or u.startswith("data:") for u in imgs), "images are https or inline",
        ", ".join(u for u in imgs if not u.startswith(("https://", "data:"))))
    add(bool(re.search(r"aria-label|role=", html)), "has accessible labels/roles for VoiceView", warn=True)

    if meta is not None:
        ui = (meta.get("_meta") or {}).get("ui") or {}
        uri = ui.get("resourceUri", "")
        add(uri.startswith("ui://"), "_meta.ui.resourceUri is a ui:// URI", uri)
        add(bool(re.search(r"-[0-9a-f]{6,}\.html$", uri)), "resource URI is versioned (…-<hash>.html)", uri, warn=True)
        csp = ui.get("csp") or {}
        declared = set(csp.get("connectDomains", [])) | set(csp.get("resourceDomains", []))
        declared_hosts = {urlparse(d).netloc or d for d in declared}
        used = hosts(imgs) | hosts(re.findall(r"fetch\(\s*[\"'](https?://[^\"']+)", html))
        missing = sorted(used - declared_hosts)
        add(not missing, "every external domain is declared in _meta.ui.csp", ", ".join(missing))
    return out


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__, file=sys.stderr)
        return 2
    html = open(argv[0], encoding="utf-8").read()
    meta = json.load(open(argv[argv.index("--meta") + 1], encoding="utf-8")) if "--meta" in argv else None
    results = check(html, meta)
    for status, name, detail in results:
        print(f"{status} {name}" + (f" — {detail}" if detail else ""))
    return 1 if any(s == "FAIL" for s, _, _ in results) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
