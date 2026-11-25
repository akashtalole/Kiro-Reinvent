#!/usr/bin/env python3
"""Kiro PreToolUse hook: block file writes whose content looks like a credential.

Reads the hook event JSON on stdin. Exit 2 (reason on stderr) blocks the write; exit 0 allows it.
Kiro Crew webhook tokens, Slack/GitHub tokens and AWS keys must never land in this public repo.
"""
import json
import re
import sys

PATTERNS = {
    "AWS access key id": r"\b(AKIA|ASIA)[0-9A-Z]{16}\b",
    "private key": r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "GitHub token": r"\bgh[pousr]_[A-Za-z0-9]{36,}\b",
    "Slack token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",
    "Kiro Crew webhook token": r"\bkc_whk_[A-Za-z0-9_-]{16,}\b",
    "Kiro API key in env assignment": r"KIRO_API_KEY\s*=\s*['\"]?[A-Za-z0-9_-]{20,}",
}


def findings(blob: str) -> list[str]:
    return [name for name, rx in PATTERNS.items() if re.search(rx, blob)]


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # not a tool event we understand; don't block
    hits = findings(json.dumps(event.get("tool_input", {})))
    if hits:
        print("Refusing write: it looks like it contains " + ", ".join(hits) +
              ". Keep secrets in the Kiro Crew vault, Secrets Manager or environment variables.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
