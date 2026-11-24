#!/usr/bin/env python3
"""SessionStart hook: print recent preferences/facts so they enter the agent's context (stdout → context)."""
import os
import sys

try:
    from bedrock_agentcore.memory import MemoryClient
    actor = os.environ.get("KIRO_MEMORY_ACTOR") or os.environ.get("USER", "kiro-user")
    c = MemoryClient(region_name=os.environ.get("AWS_REGION", "us-east-1"))
    lines = []
    for ns, q in ((f"/kiro/{actor}/preferences", "coding preferences and conventions"),
                  (f"/kiro/{actor}/facts", "current projects and recent decisions")):
        for r in c.retrieve_memories(memory_id=os.environ["MEMORY_ID"], namespace=ns, query=q, top_k=5):
            text = r.get("content", {}).get("text")
            if text:
                lines.append(f"- {text}")
    if lines:
        print("Remembered from previous sessions (verify before relying on it):\n" + "\n".join(lines))
except Exception as e:  # never block a session because memory is unavailable
    print(f"(memory unavailable: {type(e).__name__})", file=sys.stderr)
sys.exit(0)
