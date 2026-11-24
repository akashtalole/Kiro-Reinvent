"""Create the AgentCore Memory resource used by the Kiro memory MCP server.

    python setup_memory.py      # prints: export MEMORY_ID=...
"""
from bedrock_agentcore.memory import MemoryClient

m = MemoryClient(region_name="us-east-1").create_memory_and_wait(
    name="KiroCliMemory",
    description="Long-term memory for Kiro CLI sessions",
    event_expiry_days=90,
    strategies=[
        {"semanticMemoryStrategy": {"name": "facts", "namespaces": ["/kiro/{actorId}/facts"]}},
        {"userPreferenceMemoryStrategy": {"name": "preferences", "namespaces": ["/kiro/{actorId}/preferences"]}},
    ],
)
print("export MEMORY_ID=" + m.get("id", m.get("memoryId")))
