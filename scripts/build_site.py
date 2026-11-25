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


STUB = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Kiro Reinvent Labs</title><meta name="robots" content="noindex">
<link rel="canonical" href="{target}"><meta http-equiv="refresh" content="0; url={target}">
<script>location.replace("{target}" + location.hash);</script>
<style>body{{font:16px system-ui,sans-serif;margin:3rem auto;max-width:40rem;padding:0 1rem;color:#17151c;background:#fbfaf8}}</style>
</head><body><p>Opening <a href="{target}">{title}</a>…</p></body></html>
"""


def write_stub(rel_dir: str, target_from_root: str, title: str) -> None:
    """Pretty URL (e.g. /labs/03-spec-driven-development/) → real page, like the Azure labs site's folder URLs."""
    depth = len([p for p in rel_dir.strip("/").split("/") if p])
    target = "../" * depth + target_from_root
    out = OUT / rel_dir / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(STUB.format(target=target, title=title.replace("<", "&lt;")), encoding="utf-8")


def write_pretty_urls(labs: list[dict]) -> int:
    n = 0
    write_stub("labs", "labs.html", "All labs"); n += 1
    for lab in labs:
        write_stub(f"labs/{lab['slug']}", f"lab.html?id={lab['slug']}", f"Lab {lab['id']}: {lab['title']}")
        write_stub(f"labs/{lab['id']}", f"lab.html?id={lab['slug']}", f"Lab {lab['id']}: {lab['title']}")
        write_stub(f"lab/{lab['id']}", f"lab.html?id={lab['slug']}", f"Lab {lab['id']}: {lab['title']}")
        n += 3
    scen = SITE_SRC / "data" / "scenarios.json"
    if scen.exists():
        write_stub("scenarios", "scenarios.html", "Advanced scenarios"); n += 1
        for sc in json.loads(scen.read_text(encoding="utf-8"))["scenarios"]:
            write_stub(f"scenarios/{sc['id']}", f"scenarios.html?id={sc['id']}", sc["title"]); n += 1
    for md in DOCS_SRC.glob("*.md"):
        write_stub(f"docs/{md.stem}", f"doc.html?doc={md.stem}", md.stem.replace("-", " ").title()); n += 1
    cat = json.loads((SITE_SRC / "data" / "catalog.json").read_text(encoding="utf-8"))
    for path in cat.get("paths", []):
        write_stub(f"paths/{path['id']}", f"labs.html?path={path['id']}", path["title"]); n += 1
    aliases = {"quickstart": "lab.html?id=01-kiro-cli-quickstart", "playbook": "doc.html?doc=ai-first-saas-playbook",
               "field": "doc.html?doc=kiro-in-the-field", "landscape": "doc.html?doc=landscape", "paths": "index.html#paths",
               "use-cases": "use-cases.html", "internals": "doc.html?doc=kiro-ide-cli-internals", "usecases": "use-cases.html", "site": "index.html"}
    for k, v in aliases.items():
        write_stub(k, v, k.replace("-", " ").title()); n += 1
    return n


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
    diagrams = DOCS_SRC / "diagrams"
    if diagrams.is_dir():  # archify-aws diagrams: interactive HTML, SVG, PNG, draw.io (receipts stay local)
        shutil.copytree(diagrams, OUT / "docs" / "diagrams", ignore=shutil.ignore_patterns("*.receipt.json"))
    (OUT / "data").mkdir(exist_ok=True)
    (OUT / "data" / "labs.json").write_text(
        json.dumps({"categories": CATEGORIES, "levels": LEVELS, "labs": labs}, indent=2),
        encoding="utf-8",
    )
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    n_scen = validate_scenarios({l["id"] for l in labs})
    n_urls = write_pretty_urls(labs)
    print(f"Built {len(labs)} labs, {n_scen} scenarios and {n_urls} pretty URLs into {OUT.relative_to(ROOT)}/")


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
