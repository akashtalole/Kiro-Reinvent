"""Team "Billing" publishes its agent over A2A. Other teams discover it via its Agent Card.

    python billing_agent_server.py            # serves http://127.0.0.1:9000 (card at /.well-known/agent-card.json)
"""
from strands import Agent, tool
from strands.multiagent.a2a import A2AServer

_INVOICES = {"c-42": [{"id": "INV-9", "amount": 129.00, "status": "PAID"}, {"id": "INV-11", "amount": 59.90, "status": "REFUND_PENDING"}]}


@tool
def list_invoices(customer_id: str) -> list[dict]:
    """List invoices and their payment status for a customer.

    Args:
        customer_id: Customer identifier such as "c-42".
    """
    return _INVOICES.get(customer_id, [])


def make_agent(context_id: str) -> Agent:
    # One agent per A2A context: isolates conversations and is where you'd attach a per-context session manager.
    return Agent(
        name="billing-agent",
        description="Answers questions about invoices, payments and refund status for Acme customers.",
        system_prompt="You are Acme Billing. Use tools; never reveal card numbers; amounts in USD.",
        tools=[list_invoices],
        callback_handler=None,
    )


if __name__ == "__main__":
    A2AServer(agent_factory=make_agent, host="127.0.0.1", port=9000, version="1.0.0").serve()
