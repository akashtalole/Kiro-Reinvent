#!/usr/bin/env python3
"""Check a Bee-derived requirements.md: every acceptance criterion is EARS-shaped and cites the transcript.

  check_citations.py requirements.md   -> exit 1 and a list of offending lines if any criterion fails
"""
from __future__ import annotations

import re
import sys

CITE = re.compile(r"\[bee:[A-Za-z0-9_-]+@\d{1,3}:[0-5]\d\]\s*$")
EARS = re.compile(r"\b(WHEN|IF|WHILE|WHERE)\b.*\bSHALL\b|^THE SYSTEM SHALL\b", re.I)
CRITERION = re.compile(r"^\s*\d+\.\s+(.*)$")


def problems(text: str) -> list[str]:
    out, in_criteria = [], False
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("#"):
            in_criteria = "acceptance criteria" in line.lower()
            continue
        m = CRITERION.match(line)
        if in_criteria and m:
            body = m.group(1)
            if not EARS.search(body):
                out.append(f"{n}: not EARS — {body[:70]}")
            if not CITE.search(body):
                out.append(f"{n}: missing [bee:<id>@mm:ss] citation — {body[:70]}")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    found = problems(open(sys.argv[1], encoding="utf-8").read())
    print("\n".join(found) if found else "ok: every criterion is EARS and cited")
    sys.exit(1 if found else 0)
