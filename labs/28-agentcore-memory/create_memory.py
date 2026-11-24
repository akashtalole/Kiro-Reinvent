"""Create an AgentCore Memory resource with four long-term strategies.

    python create_memory.py            # prints MEMORY_ID; export it for agent_with_memory.py
"""
from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name="us-east-1")
memory = client.create_memory_and_wait(
    name="AcmeSupportMemory",
    description="Short-term turns + long-term facts, preferences, summaries and episodes for Acme support",
    event_expiry_days=30,                                   # raw conversation events (short-term memory)
    strategies=[
        {"semanticMemoryStrategy": {"name": "facts", "namespaces": ["/support/{actorId}/facts"]}},
        {"userPreferenceMemoryStrategy": {"name": "preferences", "namespaces": ["/support/{actorId}/preferences"]}},
        {"summaryMemoryStrategy": {"name": "summaries", "namespaces": ["/support/{actorId}/{sessionId}/summary"]}},
        {"episodicMemoryStrategy": {"name": "episodes", "namespaces": ["/support/{actorId}/episodes"]}},
    ],
)
print("MEMORY_ID=" + memory.get("id", memory.get("memoryId")))
