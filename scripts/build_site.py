#!/usr/bin/env python3
"""Build the static GitHub Pages site for Kiro Reinvent Labs.

Single source of truth: every lab is a folder under ``labs/`` with a README.md
that starts with a small YAML front-matter block. This script:

1. copies ``site/`` into ``_site/``
2. copies every lab folder into ``_site/labs/<slug>/``
3. parses front matter and writes ``_site/data/labs.json``
4. copies ``docs/*.md`` into ``_site/docs/`` (rendered client-side)

No third-party dependencies, so it runs anywhere Python 3.9+ exists.

    python scripts/build_site.py            # build into _site/
    python scripts/build_site.py --serve    # build and serve on :8000
"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_SRC = ROOT / "site"
LABS_SRC = ROOT / "labs"
DOCS_SRC = ROOT / "docs"
OUT = ROOT / "_site"

REQUIRED = ["id", "title", "category", "level", "duration", "summary"]
CATEGORIES = [
    "Kiro foundations",
    "Customize Kiro",
    "Automate & scale",
    "AWS MCP servers",
    "Strands Agents",
    "AgentCore",
    "End-to-end solutions",
]
LEVELS = ["Beginner", "Intermediate", "Advanced"]


def parse_scalar(raw: str):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [parse_scalar(x) for x in inner.split(",")] if inner else []
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    meta: dict = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = parse_scalar(value)
    return meta, body


def first_heading(body: str) -> str:
    m = re.search(r"^#\s+(.+)$", body, re.M)
    return m.group(1).strip() if m else ""


def collect_labs() -> list[dict]:
    labs, errors = [], []
    for readme in sorted(LABS_SRC.glob("*/README.md")):
        slug = readme.parent.name
        meta, body = parse_front_matter(readme.read_text(encoding="utf-8"))
        missing = [k for k in REQUIRED if k not in meta]
        if missing:
            errors.append(f"{slug}: missing front matter {missing}")
            continue
        if meta["category"] not in CATEGORIES:
            errors.append(f"{slug}: unknown category {meta['category']!r}")
        if meta["level"] not in LEVELS:
            errors.append(f"{slug}: unknown level {meta['level']!r}")
        files = sorted(
            str(p.relative_to(readme.parent)).replace("\\", "/")
            for p in readme.parent.rglob("*")
            if p.is_file() and p.name != "README.md"
        )
        labs.append(
            {
                "slug": slug,
                "id": str(meta["id"]).zfill(2),
                "title": meta["title"],
                "category": meta["category"],
                "level": meta["level"],
                "duration": meta["duration"],
                "summary": meta["summary"],
                "services": meta.get("services", []),
                "tags": meta.get("tags", []),
                "popular": str(meta.get("popular", "")).lower() == "true",
                "files": files,
                "heading": first_heading(body),
            }
        )
    if errors:
        print("Front-matter errors:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)
    ids = [l["id"] for l in labs]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        print(f"Duplicate lab ids: {sorted(dupes)}", file=sys.stderr)
        sys.exit(1)
    return sorted(labs, key=lambda l: l["id"])


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SITE_SRC, OUT)
    labs = collect_labs()
    for lab in labs:
        shutil.copytree(LABS_SRC / lab["slug"], OUT / "labs" / lab["slug"])
    (OUT / "docs").mkdir(exist_ok=True)
    for md in DOCS_SRC.glob("*.md"):
        shutil.copy2(md, OUT / "docs" / md.name)
    (OUT / "data").mkdir(exist_ok=True)
    (OUT / "data" / "labs.json").write_text(
        json.dumps({"categories": CATEGORIES, "levels": LEVELS, "labs": labs}, indent=2),
        encoding="utf-8",
    )
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(labs)} labs into {OUT.relative_to(ROOT)}/")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true", help="serve _site on localhost")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    build()
    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        print(f"Serving http://localhost:{args.port}/")
        http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler).serve_forever()


if __name__ == "__main__":
    main()
