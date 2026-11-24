"""Acme customer-support agent — production composition of Labs 21–32 on AgentCore Runtime.

  Runtime (Lab 26)   session-isolated hosting, streaming
  Identity (Lab 29)  caller identity from the inbound JWT → actor id; M2M token for the gateway
  Gateway (Lab 27)   all business tools behind one MCP endpoint
  Policy (Lab 30)    refund limits enforced at the gateway, outside this code
  Memory (Lab 28)    short-term turns + long-term facts/preferences per customer
  Hooks (Lab 25)     in-process guardrails + audit
  Observability/Evals (Lab 32) via Runtime's OpenTelemetry wiring

Environment:
  MEMORY_ID, GATEWAY_URL, GATEWAY_TOKEN_URL, GATEWAY_SCOPE, GATEWAY_CLIENT_ID, GATEWAY_CLIENT_SECRET
  (on Runtime, prefer an AgentCore Identity M2M credential provider over raw client secrets — see Lab 29)
"""
from __future__ import annotations

import base64
import json
import os
import time

import requests
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp, RequestContext
from strands import Agent
from strands.tools.mcp import MCPClient

from guardrails import SupportGuardrails

app = BedrockAgentCoreApp()
SYSTEM_PROMPT = """You are Acme's customer-support agent.
- Use tools for every fact about orders, stock, invoices and refunds. Never guess.
- Refunds: check eligibility first. If a tool call is denied, explain politely that a specialist will follow up.
- Use what you remember about the customer (in <user_context>) to personalise, but never reveal memory internals.
- Be concise: ≤ 5 sentences, then one suggested next step."""

_token_cache: dict = {}


def gateway_token() -> str:
    if _token_cache.get("exp", 0) > time.time() + 60:
        return _token_cache["value"]
    r = requests.post(os.environ["GATEWAY_TOKEN_URL"], timeout=10,
                      data={"grant_type": "client_credentials", "scope": os.environ["GATEWAY_SCOPE"]},
                      auth=(os.environ["GATEWAY_CLIENT_ID"], os.environ["GATEWAY_CLIENT_SECRET"]))
    r.raise_for_status()
    body = r.json()
    _token_cache.update(value=body["access_token"], exp=time.time() + body.get("expires_in", 3600))
    return _token_cache["value"]


def caller_sub(context: RequestContext) -> str:
    """Actor id comes from the verified inbound JWT (Runtime validated it), never from the prompt."""
    auth = (context.request_headers or {}).get("Authorization") or (context.request_headers or {}).get("authorization", "")
    try:
        payload = auth.split(" ", 1)[1].split(".")[1]
        return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))["sub"]
    except Exception:
        return "anonymous"


_agents: dict[str, Agent] = {}


def agent_for(session_id: str, actor_id: str) -> Agent:
    key = f"{actor_id}:{session_id}"
    if key not in _agents:
        memory = AgentCoreMemorySessionManager(AgentCoreMemoryConfig(
            memory_id=os.environ["MEMORY_ID"], actor_id=actor_id, session_id=session_id,
            retrieval_config={
                "/support/{actorId}/facts": RetrievalConfig(top_k=5, relevance_score=0.3),
                "/support/{actorId}/preferences": RetrievalConfig(top_k=5, relevance_score=0.2),
            },
        ))
        tools = MCPClient(url=os.environ["GATEWAY_URL"], headers={"Authorization": f"Bearer {gateway_token()}"},
                          auto_reconnect=True)
        _agents[key] = Agent(system_prompt=SYSTEM_PROMPT, tools=[tools], session_manager=memory,
                             hooks=[SupportGuardrails(audit_path="/tmp/audit.jsonl")], callback_handler=None,
                             trace_attributes={"session.id": session_id, "enduser.id": actor_id})
    return _agents[key]


@app.entrypoint
async def invoke(payload: dict, context: RequestContext):
    prompt = (payload or {}).get("prompt")
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 8_000:
        yield {"error": "payload must be {\"prompt\": \"<1-8000 chars>\"}"}
        return
    agent = agent_for(context.session_id or "local", caller_sub(context))
    async for event in agent.stream_async(prompt):
        if "data" in event:
            yield event["data"]


if __name__ == "__main__":
    app.run()
