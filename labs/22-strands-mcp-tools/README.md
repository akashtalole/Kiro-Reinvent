---
id: 22
title: Strands agents with MCP tools
category: Strands Agents
level: Intermediate
duration: 30 min
summary: Give a Strands agent remote (streamable HTTP) and local (stdio) MCP servers — AWS Knowledge and AWS Pricing — with prefixes, tool filters and managed lifecycle.
services: [Strands Agents, AWS Knowledge MCP, AWS Pricing MCP, Amazon Bedrock]
tags: [MCP, MCPClient, tool filters, streamable HTTP, stdio]
---

# Lab 22 · Strands agents with MCP tools

> **Outcome:** An "AWS solutions architect" agent that researches with the AWS Knowledge MCP server, prices with the AWS Pricing MCP server, and computes with a local tool — the same MCP servers Kiro uses, now inside *your* agent.

## Scenario

Every MCP server you configured for Kiro is also a tool library for agents you build. Strands' `MCPClient` connects to any MCP server; the agent sees MCP tools exactly like `@tool` functions.

```mermaid
flowchart LR
  A[Strands Agent] --> L[monthly_cost<br/>@tool]
  A --> K[MCPClient url=… prefix=docs<br/>streamable HTTP]
  A --> P[MCPClient stdio uvx … prefix=pricing<br/>tool_filters]
  K --> KS[(AWS Knowledge MCP<br/>knowledge-mcp.global.api.aws)]
  P --> PS[(AWS Pricing MCP<br/>local process)]
```

## How it works

```python
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

remote = MCPClient(url="https://knowledge-mcp.global.api.aws", prefix="docs")
local  = MCPClient(lambda: stdio_client(StdioServerParameters(command="uvx", args=["awslabs.aws-pricing-mcp-server@latest"])),
                   prefix="pricing", tool_filters={"rejected": ["generate_cost_report"]})

agent = Agent(tools=[remote, local, my_tool])     # agent manages the clients' lifecycle
```

| Option | Why |
| --- | --- |
| `url=` / `headers=` / `auth=` | Streamable HTTP servers, with headers or OAuth credentials |
| `prefix=` | Namespaces tools (`docs_…`, `pricing_…`) so two servers can't collide |
| `tool_filters={"allowed": [...], "rejected": [...]}` | Keep context lean; hide dangerous tools |
| `auto_reconnect=True` | Long-running agents survive server restarts |
| `with client: client.list_tools_sync()` | Manual lifecycle when you need it |

## Step 1 — Install and list tools

```bash
cd labs/22-strands-mcp-tools && pip install -r requirements.txt
python - <<'PY'
from strands.tools.mcp import MCPClient
with MCPClient(url="https://knowledge-mcp.global.api.aws", prefix="docs") as c:
    print([t.tool_name for t in c.list_tools_sync()])
PY
```

Expected (Nov 2026): `docs_aws___search_documentation`, `docs_aws___read_documentation`, `docs_aws___list_regions`, `docs_aws___get_regional_availability`, `docs_aws___retrieve_skill`.

## Step 2 — Run the agent

```bash
python agent.py "Design a low-cost way to send 2M push notifications/month and price it in eu-west-1"
```

Read [`agent.py`](agent.py): the system prompt forces docs citations, real prices and tool-based arithmetic.

## Step 3 — Put AgentCore Gateway in front

In production you won't spawn `uvx` processes per agent. Lab 27 puts tools behind **AgentCore Gateway** — the agent then needs exactly one `MCPClient(url=<gateway>, auth=...)` regardless of how many targets sit behind it.

## Step 4 — TypeScript variant

```ts
import { Agent, McpClient } from "@strands-agents/sdk";
const docs = new McpClient({ url: "https://knowledge-mcp.global.api.aws" });
const agent = new Agent({ tools: [docs] });
await agent.invoke("What's the max message size for SQS?");
```

(Check the [TypeScript SDK docs](https://strandsagents.com/) for the exact class names in your version.)

## Learn more

- [Strands MCP tools](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-tools/) · [AWS Knowledge MCP](https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server/)
- Next: [Lab 23 — Multi-agent patterns](../23-strands-multi-agent/README.md)
