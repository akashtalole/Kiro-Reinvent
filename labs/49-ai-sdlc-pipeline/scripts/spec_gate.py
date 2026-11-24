#!/usr/bin/env python3
"""Spec traceability gate: every PR must cite the spec task it implements, and that task must be ticked.

Accepted references (PR body or commit messages):   Implements: <spec-name>#<task-number>   e.g. Implements: tenant-onboarding#2.1
Checks: .kiro/specs/<spec-name>/tasks.md exists, task <n> exists, and is checked ([x]) in the PR head.
Exempt with the label/keyword "spec-exempt: <reason>" (e.g. dependency bumps).

    python spec_gate.py --text "$PR_BODY $(git log --format=%B origin/main..HEAD)" --root .
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REF = re.compile(r"Implements:\s*([a-z0-9][a-z0-9-]*)#(\d+(?:\.\d+)?)", re.I)
EXEMPT = re.compile(r"spec-exempt:\s*\S+", re.I)


def find_task(tasks_md: str, number: str) -> bool | None:
    """True if ticked, False if present but unticked, None if missing."""
    rx = re.compile(r"^\s*-\s*\[( |x|X)\]\s*" + re.escape(number) + r"[.\s]", re.M)
    m = rx.search(tasks_md)
    return None if not m else m.group(1).lower() == "x"


def check(text: str, root: pathlib.Path) -> tuple[bool, list[str]]:
    if EXEMPT.search(text):
        return True, ["spec-exempt: " + EXEMPT.search(text).group(0)]
    refs = REF.findall(text)
    if not refs:
        return False, ["No 'Implements: <spec>#<task>' reference found in the PR body or commits."]
    msgs, ok = [], True
    for spec, task in sorted(set(refs)):
        path = root / ".kiro" / "specs" / spec / "tasks.md"
        if not path.exists():
            ok = False
            msgs.append(f"{spec}#{task}: {path} not found")
            continue
        state = find_task(path.read_text(), task)
        if state is None:
            ok = False
            msgs.append(f"{spec}#{task}: task not in tasks.md")
        elif not state:
            ok = False
            msgs.append(f"{spec}#{task}: task not ticked — finish it or update tasks.md")
        else:
            msgs.append(f"{spec}#{task}: ok")
    return ok, msgs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    ok, msgs = check(a.text, pathlib.Path(a.root))
    print("\n".join(msgs))
    sys.exit(0 if ok else 1)
