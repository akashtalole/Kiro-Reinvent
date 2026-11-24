#!/usr/bin/env python3
"""PermissionRequest hook: auto-allow read-only AWS API calls, defer everything else."""
import json
import re
import sys

event = json.load(sys.stdin)
args = json.dumps(event.get("tool_input", {})).lower()
READ_ONLY = re.compile(r"\b(describe|get|list|head|lookup|search|batch-get)-[a-z0-9-]+")
WRITE = re.compile(r"\b(create|put|update|delete|terminate|modify|attach|detach|run|start|stop)-")
if READ_ONLY.search(args) and not WRITE.search(args):
    print(json.dumps({"hookSpecificOutput": {"decision": {"behavior": "allow"}}}))
sys.exit(0)  # no output → the normal approval prompt is shown
