"""Support agent that remembers customers across sessions via AgentCore Memory.

    export MEMORY_ID=...                 # from create_memory.py
    python agent_with_memory.py c-42 s-1 "Hi, I'm Dana. Please always email me, never call. Where's A-1001?"
    python agent_with_memory.py c-42 s-2 "Any update on my order? You know how I like to be contacted."
"""
import os
import sys

from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from strands import Agent

from orders_tools import check_refund_eligibility, get_order, list_orders

actor_id, session_id, prompt = sys.argv[1], sys.argv[2], " ".join(sys.argv[3:])

config = AgentCoreMemoryConfig(
    memory_id=os.environ["MEMORY_ID"],
    actor_id=actor_id,          # the customer — long-term memory is scoped per actor
    session_id=session_id,      # the conversation — short-term memory is scoped per session
    retrieval_config={
        "/support/{actorId}/facts": RetrievalConfig(top_k=5, relevance_score=0.3),
        "/support/{actorId}/preferences": RetrievalConfig(top_k=5, relevance_score=0.2),
        "/support/{actorId}/episodes": RetrievalConfig(top_k=3, relevance_score=0.4),
    },
)

agent = Agent(
    system_prompt=("You are Acme support. Use remembered facts and preferences about the customer when relevant "
                   "(they appear in <user_context>). Never reveal memory internals. Use tools for order data."),
    tools=[get_order, list_orders, check_refund_eligibility],
    session_manager=AgentCoreMemorySessionManager(config, region_name="us-east-1"),
)

if __name__ == "__main__":
    agent(prompt)
