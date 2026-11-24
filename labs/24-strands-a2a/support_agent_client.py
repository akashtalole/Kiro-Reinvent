"""Team "Support" consumes Billing's agent over A2A as just another tool.

    python billing_agent_server.py &      # in another terminal
    python support_agent_client.py "Has customer c-42's refund been processed?"
"""
import sys

from strands import Agent, tool
from strands.agent.a2a_agent import A2AAgent

billing = A2AAgent(endpoint="http://127.0.0.1:9000", timeout=120)


@tool
def ask_billing(question: str) -> str:
    """Ask the Billing team's agent about invoices, payments or refund status.

    Args:
        question: A self-contained question including the customer id.
    """
    return str(billing(question))


support = Agent(
    name="support-agent",
    system_prompt="You are Acme Support. For anything about money, ask_billing. Summarise for the customer in ≤3 sentences.",
    tools=[ask_billing],
)

if __name__ == "__main__":
    support(" ".join(sys.argv[1:]) or "Has customer c-42's refund been processed?")
