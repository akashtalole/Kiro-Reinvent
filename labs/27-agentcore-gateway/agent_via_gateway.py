"""A Strands agent that gets ALL its tools from one AgentCore Gateway endpoint.

    python agent_via_gateway.py "Is order A-1002 delivered and is SKU-2 in stock?"
"""
import json
import sys

import requests
from strands import Agent
from strands.tools.mcp import MCPClient

cfg = json.load(open("gateway.json"))


def access_token() -> str:
    r = requests.post(cfg["tokenUrl"], data={"grant_type": "client_credentials", "scope": cfg["scope"]},
                      auth=(cfg["clientId"], cfg["clientSecret"]), timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


gateway = MCPClient(url=cfg["gatewayUrl"], headers={"Authorization": f"Bearer {access_token()}"})

agent = Agent(
    system_prompt="You are Acme support. Use the gateway tools; never guess order or stock data.",
    tools=[gateway],
)

if __name__ == "__main__":
    agent(" ".join(sys.argv[1:]) or "Is order A-1002 delivered and is SKU-2 in stock?")
