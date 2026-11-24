"""Support agent with a refund tool, protected by hook-based guardrails."""
from strands import Agent, tool

from guardrails import SupportGuardrails
from orders_tools import check_refund_eligibility, get_order, list_orders


@tool
def issue_refund(order_id: str, amount: float) -> dict:
    """Issue a refund. Only call after check_refund_eligibility returned eligible=true.

    Args:
        order_id: Order identifier.
        amount: Refund amount in USD (must equal the eligible amount).
    """
    return {"refund_id": f"RF-{order_id}", "amount": amount, "status": "ISSUED"}


def build_agent(**kwargs) -> Agent:
    return Agent(
        name="acme-support",
        system_prompt=("You are Acme's order-support agent. Always use tools; never guess. "
                       "Refunds: check eligibility, then issue_refund for exactly the eligible amount. "
                       "If a tool is blocked, explain the reason to the customer politely."),
        tools=[get_order, list_orders, check_refund_eligibility, issue_refund],
        hooks=[SupportGuardrails()],
        **kwargs,
    )


if __name__ == "__main__":
    import sys
    build_agent()(" ".join(sys.argv[1:]) or "Please refund order A-1002")
