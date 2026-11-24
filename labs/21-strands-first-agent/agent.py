"""Lab 21 — a first Strands agent: model + system prompt + tools, with streaming and structured output.

    pip install -r requirements.txt
    python agent.py "Where is order A-1001?"
"""
import sys

from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel

from orders_tools import check_refund_eligibility, get_order, list_orders

SYSTEM_PROMPT = """You are Acme's order-support agent.
- Always look orders up with tools; never guess status, dates or amounts.
- Refunds: call check_refund_eligibility first and quote its reason.
- Be brief: at most 4 sentences, then offer one next step."""

model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-6",  # Strands default; any Bedrock model with tool use works
    region_name="us-west-2",
    temperature=0.2,
)

agent = Agent(
    name="acme-support",
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_order, list_orders, check_refund_eligibility],
)


class TicketSummary(BaseModel):
    """Structured hand-off for a human agent."""
    intent: str = Field(description="what the customer wanted")
    order_ids: list[str]
    resolved: bool
    next_action: str


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "Customer c-42 wants a refund for their delivered order. Can they get one?"
    result = agent(prompt)                       # streams to stdout via the default callback handler
    print("\n\n--- metrics ---")
    print(result.metrics.get_summary()["accumulated_usage"])

    handoff = agent("Summarise this conversation for the ticket system.", structured_output_model=TicketSummary)
    print(handoff.structured_output.model_dump_json(indent=2))
