#!/usr/bin/env python3
"""Kiro PostFileSave hook: every JSON file in labs/, site/, docs/diagrams/ and .kiro/ must parse.

Exit 1 with the failing paths on stderr so the agent sees what to fix.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = {"node_modules", "_site", ".git"}


def bad_json_files(root: Path = ROOT) -> list[str]:
    bad = []
    for base in ("labs", "site", "docs/diagrams", ".kiro"):
        for path in (root / base).rglob("*.json"):
            if SKIP & set(path.parts):
                continue
            try:
                json.loads(path.read_text(encoding="utf-8-sig"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                bad.append(f"{path.relative_to(root)}: {exc}")
    return bad


if __name__ == "__main__":
    problems = bad_json_files()
    for p in problems:
        print(p, file=sys.stderr)
    sys.exit(1 if problems else 0)
