"""See what long-term memory extracted for a customer (extraction is asynchronous — allow ~1 minute).

    python inspect_memory.py c-42 "contact preference"
"""
import os
import sys

from bedrock_agentcore.memory import MemoryClient

actor, query = sys.argv[1], " ".join(sys.argv[2:]) or "customer"
client = MemoryClient(region_name="us-east-1")
for ns in ("facts", "preferences", "episodes"):
    print(f"--- {ns}")
    for rec in client.retrieve_memories(memory_id=os.environ["MEMORY_ID"], namespace=f"/support/{actor}/{ns}", query=query, top_k=5):
        print("•", rec.get("content", {}).get("text"))
