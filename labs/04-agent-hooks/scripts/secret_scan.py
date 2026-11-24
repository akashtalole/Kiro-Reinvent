#!/usr/bin/env python3
"""PreToolUse secret scan for file writes. Blocks content that looks like credentials."""
import json
import re
import sys

event = json.load(sys.stdin)
blob = json.dumps(event.get("tool_input", {}))
PATTERNS = {
    "AWS access key id": r"\b(AKIA|ASIA)[0-9A-Z]{16}\b",
    "private key": r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "GitHub token": r"\bgh[pousr]_[A-Za-z0-9]{36,}\b",
    "Slack token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",
}
hits = [name for name, rx in PATTERNS.items() if re.search(rx, blob)]
if hits:
    print("Refusing write: looks like it contains " + ", ".join(hits) +
          ". Use Secrets Manager / SSM parameters instead.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
