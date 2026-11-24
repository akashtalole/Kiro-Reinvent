"""MCP server (stdio) that gives Kiro CLI long-term memory backed by Amazon Bedrock AgentCore Memory.

Tools: remember_turn, recall, recent_turns, list_sessions, memory_stats.
Retrieval cascades: semantic long-term records first, then raw event scan of recent sessions,
so fresh conversations are findable before asynchronous extraction has finished.

Environment:
  MEMORY_ID            AgentCore Memory id (create with setup_memory.py)
  AWS_REGION           default us-east-1
  KIRO_MEMORY_ACTOR    actor id; default = $USER (personal). Use a project id for team-shared memory.
"""
from __future__ import annotations

import datetime as dt
import os

from bedrock_agentcore.memory import MemoryClient
from mcp.server.mcpserver import MCPServer

MEMORY_ID = os.environ["MEMORY_ID"]
ACTOR = os.environ.get("KIRO_MEMORY_ACTOR") or os.environ.get("USER", "kiro-user")
NAMESPACE = f"/kiro/{ACTOR}/facts"
client = MemoryClient(region_name=os.environ.get("AWS_REGION", "us-east-1"))
server = MCPServer(
    name="kiro-agentcore-memory",
    instructions=("Long-term memory for this developer across Kiro sessions. Call recall at the start of a task "
                  "that may relate to earlier work; call remember_turn after answering anything worth keeping "
                  "(decisions, preferences, project facts). Never store secrets."),
)


def _today_session() -> str:
    return "kiro-" + dt.date.today().isoformat()


@server.tool(description="Store one user/assistant exchange (and optional explicit facts) in long-term memory.")
def remember_turn(user_message: str, assistant_summary: str, session_id: str | None = None) -> dict:
    sid = session_id or _today_session()
    client.create_event(memory_id=MEMORY_ID, actor_id=ACTOR, session_id=sid,
                        messages=[(user_message[:8000], "USER"), (assistant_summary[:8000], "ASSISTANT")])
    return {"stored": True, "session_id": sid, "actor_id": ACTOR}


@server.tool(description="Search past conversations and extracted facts. Use natural queries like 'what did we decide about the auth service'.")
def recall(query: str, top_k: int = 5) -> dict:
    records = client.retrieve_memories(memory_id=MEMORY_ID, namespace=NAMESPACE, query=query, top_k=top_k)
    hits = [{"source": "long-term", "text": r.get("content", {}).get("text"), "score": r.get("score")} for r in records]
    if not hits:  # fallback: scan raw events from the last 7 days of sessions
        terms = [t for t in query.lower().split() if len(t) > 3]
        for days_ago in range(7):
            sid = "kiro-" + (dt.date.today() - dt.timedelta(days=days_ago)).isoformat()
            for ev in client.list_events(memory_id=MEMORY_ID, actor_id=ACTOR, session_id=sid, max_results=50):
                for p in ev.get("payload", []):
                    text = p.get("conversational", {}).get("content", {}).get("text", "")
                    if text and any(t in text.lower() for t in terms):
                        hits.append({"source": f"event:{sid}", "text": text[:600]})
            if len(hits) >= top_k:
                break
    return {"query": query, "results": hits[:top_k]}


@server.tool(description="Return the last k exchanges of a session (default: today's).")
def recent_turns(k: int = 5, session_id: str | None = None) -> list:
    turns = client.get_last_k_turns(memory_id=MEMORY_ID, actor_id=ACTOR, session_id=session_id or _today_session(), k=k)
    return [[m.get("content", {}).get("text", "")[:600] for m in turn] for turn in turns]


@server.tool(description="List which of the last N days have stored sessions.")
def list_sessions(days: int = 14) -> list:
    found = []
    for d in range(days):
        sid = "kiro-" + (dt.date.today() - dt.timedelta(days=d)).isoformat()
        if client.list_events(memory_id=MEMORY_ID, actor_id=ACTOR, session_id=sid, max_results=1, include_payload=False):
            found.append(sid)
    return found


@server.tool(description="Show memory configuration for this server.")
def memory_stats() -> dict:
    return {"memory_id": MEMORY_ID, "actor_id": ACTOR, "namespace": NAMESPACE,
            "strategies": [s.get("name") for s in client.get_memory_strategies(MEMORY_ID)]}


if __name__ == "__main__":
    server.run("stdio")
