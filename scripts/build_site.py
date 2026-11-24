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
    "AI-first SaaS",
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


SCENARIO_FIELDS = ["id", "title", "tagline", "domain", "complexity", "personas", "trigger", "steps",
                   "guardrails", "outcome", "metrics", "labs", "services", "diagram"]


def validate_scenarios(lab_ids: set[str]) -> int:
    path = SITE_SRC / "data" / "scenarios.json"
    if not path.exists():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    errors, seen = [], set()
    for sc in data["scenarios"]:
        sid = sc.get("id", "?")
        missing = [f for f in SCENARIO_FIELDS if f not in sc]
        if missing:
            errors.append(f"{sid}: missing {missing}")
        if sid in seen:
            errors.append(f"{sid}: duplicate id")
        seen.add(sid)
        if sc.get("domain") not in data["domains"]:
            errors.append(f"{sid}: unknown domain {sc.get('domain')!r}")
        if sc.get("complexity") not in ("Advanced", "Expert"):
            errors.append(f"{sid}: complexity must be Advanced or Expert")
        for lab in sc.get("labs", []):
            if lab not in lab_ids:
                errors.append(f"{sid}: references unknown lab {lab}")
        for st in sc.get("steps", []):
            if st.get("kind") not in ("agent", "human", "system"):
                errors.append(f"{sid}: step kind must be agent|human|system")
            if not st.get("checkpoint"):
                errors.append(f"{sid}: happy-path step '{st.get('actor')}' needs a checkpoint")
            for t in st.get("troubleshoot", []):
                if set(t) != {"symptom", "cause", "fix"}:
                    errors.append(f"{sid}: troubleshoot entries need symptom/cause/fix")
        path_ids = set()
        for path in sc.get("paths", []):
            pid = path.get("id", "?")
            if pid in path_ids or pid == "happy":
                errors.append(f"{sid}/{pid}: duplicate or reserved path id")
            path_ids.add(pid)
            if path.get("type") not in ("alternate", "failure", "edge"):
                errors.append(f"{sid}/{pid}: type must be alternate|failure|edge")
            if not (1 <= int(path.get("branchesAt", 0)) <= len(sc.get("steps", [])) + 1):
                errors.append(f"{sid}/{pid}: branchesAt out of range")
            for k in ("name", "when", "steps", "outcome"):
                if not path.get(k):
                    errors.append(f"{sid}/{pid}: missing {k}")
            for st in path.get("steps", []):
                if st.get("kind") not in ("agent", "human", "system") or not st.get("checkpoint"):
                    errors.append(f"{sid}/{pid}: each step needs kind and checkpoint")
    if errors:
        print("Scenario errors:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)
    return len(data["scenarios"])


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
    n_scen = validate_scenarios({l["id"] for l in labs})
    print(f"Built {len(labs)} labs and {n_scen} scenarios into {OUT.relative_to(ROOT)}/")


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
