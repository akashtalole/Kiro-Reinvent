#!/usr/bin/env python3
"""PreToolUse guard for shell commands. Reads hook JSON on stdin.
Exit 2 (with a reason on stderr) blocks the tool call; exit 0 allows it."""
import json
import re
import sys

event = json.load(sys.stdin)
cmd = json.dumps(event.get("tool_input", {}))

BLOCK = [
    (r"rm\s+-rf\s+(/|~|\$HOME|\.\s)", "recursive delete of a root/home/cwd path"),
    (r"git\s+push\s+.*--force(?!-with-lease)", "force push without lease"),
    (r"cdk\s+deploy\s+.*[Pp]rod", "production CDK deploy"),
    (r"terraform\s+(apply|destroy)\s+.*-auto-approve", "unattended terraform apply/destroy"),
    (r"aws\s+\S+\s+delete-", "AWS delete-* API call"),
]
for pattern, why in BLOCK:
    if re.search(pattern, cmd):
        print(f"Blocked by guardrail hook: {why}. Ask a human to run it.", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
