"""Lab 22 — a Strands "AWS solutions architect" agent that uses MCP servers as tools.

* AWS Knowledge MCP (remote, streamable HTTP, no auth) for current docs
* AWS Pricing MCP (local stdio via uvx) for real prices
* Local @tool functions alongside MCP tools

    pip install -r requirements.txt     # plus `uv` on PATH for uvx
    python agent.py "Design a low-cost way to send 2M push notifications/month and price it in eu-west-1"
"""
import os
import sys

from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient

knowledge = MCPClient(
    url="https://knowledge-mcp.global.api.aws",
    prefix="docs",                       # tools appear as docs_<name> — avoids clashes between servers
    startup_timeout=60,
)

pricing = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-pricing-mcp-server@latest"],
            env={**os.environ, "AWS_REGION": "us-east-1", "FASTMCP_LOG_LEVEL": "ERROR"},
        )
    ),
    prefix="pricing",
    # Only expose what this agent needs; everything else stays out of the context window.
    tool_filters={"rejected": ["generate_cost_report"]},
)


@tool
def monthly_cost(unit_price_usd: float, units_per_month: float) -> dict:
    """Multiply a unit price by monthly volume. Use for every cost line instead of mental math.

    Args:
        unit_price_usd: Price per unit in USD, as returned by the pricing tools.
        units_per_month: Number of billable units per month.
    """
    return {"monthly_usd": round(unit_price_usd * units_per_month, 2)}


SYSTEM = """You are an AWS solutions architect.
1. Research options with the docs_* tools and cite the URLs you used.
2. Fetch real prices with the pricing_* tools — never invent prices.
3. Use monthly_cost for arithmetic. Present a comparison table, then a recommendation."""

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Compare SNS mobile push vs Pinpoint-style alternatives for 2M pushes/month in eu-west-1."
    # Passing MCPClient objects directly lets the Agent manage their lifecycle (start on first use, stop on cleanup).
    agent = Agent(system_prompt=SYSTEM, tools=[knowledge, pricing, monthly_cost])
    agent(question)
    print("\n\ntools used:", sorted({name for name in agent.event_loop_metrics.tool_metrics}))
