"""Acme support agent packaged for Amazon Bedrock AgentCore Runtime.

The Runtime gives each session an isolated microVM, scales to zero, supports long-running
sessions and streams responses. Locally, `agentcore dev` (or `python main.py`) serves the same
HTTP contract on :8080 (POST /invocations, GET /ping).
"""
from __future__ import annotations

import logging

from bedrock_agentcore.runtime import BedrockAgentCoreApp, RequestContext
from strands import Agent

from orders_tools import check_refund_eligibility, get_order, list_orders

log = logging.getLogger("acme-support")
app = BedrockAgentCoreApp()

SYSTEM_PROMPT = ("You are Acme's order-support agent. Always use tools; never guess status, dates or amounts. "
                 "Refunds: check eligibility first and quote the reason. Be brief.")

_agents: dict[str, Agent] = {}   # one agent per Runtime session (the microVM is already per-session)


def agent_for(session_id: str) -> Agent:
    if session_id not in _agents:
        _agents[session_id] = Agent(
            system_prompt=SYSTEM_PROMPT,
            tools=[get_order, list_orders, check_refund_eligibility],
            callback_handler=None,
            trace_attributes={"session.id": session_id, "service.name": "acme-support"},
        )
    return _agents[session_id]


@app.entrypoint
async def invoke(payload: dict, context: RequestContext):
    """Payload: {"prompt": "..."} → streams text chunks back to the caller (SSE)."""
    prompt = (payload or {}).get("prompt")
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 8_000:
        yield {"error": "payload must be {\"prompt\": \"<non-empty string up to 8000 chars>\"}"}
        return
    session_id = context.session_id or "local"
    log.info("invoke session=%s", session_id)
    async for event in agent_for(session_id).stream_async(prompt):
        if "data" in event:
            yield event["data"]


if __name__ == "__main__":
    app.run()
