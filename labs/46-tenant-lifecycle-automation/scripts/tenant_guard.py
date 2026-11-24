#!/usr/bin/env python3
"""PreToolUse guard for tenant operations (exit 2 = block)."""
import json
import re
import sys

cmd = json.dumps(json.load(sys.stdin).get("tool_input", {}))
if re.search(r"tenantctl\.sh\s+offboard", cmd):
    m = re.search(r"offboard\s+(t-[a-z0-9]+)\s+(\S+)", cmd)
    if not m or f"CONFIRM={m.group(1)}" not in cmd:
        print("Offboarding needs a ticket id and CONFIRM=<tenant-id> on the same command.", file=sys.stderr)
        sys.exit(2)
if re.search(r"dynamodb\s+(delete-item|batch-write-item|delete-table)", cmd):
    print("Direct deletes on tenant data are blocked; use tenantctl.sh.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
