"""Pattern 1 — agents as tools: an orchestrator routes to specialists it calls like functions.

Best when: one conversation, the orchestrator stays in charge, specialists are stateless helpers.
    python agents_as_tools.py "Our checkout API p95 doubled after yesterday's deploy. What should we check?"
"""
import sys

from strands import Agent

MODEL = "global.anthropic.claude-sonnet-4-6"

security = Agent(name="security_reviewer", model=MODEL,
                 description="Assesses security impact: authn/z, data exposure, secrets, injection.",
                 system_prompt="You are an application security engineer. Answer in ≤6 bullets with severity.",
                 callback_handler=None)
performance = Agent(name="performance_engineer", model=MODEL,
                    description="Diagnoses latency, throughput and cost-performance problems on AWS.",
                    system_prompt="You are a performance engineer for AWS serverless and containers. Give a ranked checklist.",
                    callback_handler=None)
writer = Agent(name="tech_writer", model=MODEL,
               description="Turns technical findings into a short, clear update for stakeholders.",
               system_prompt="Write crisp stakeholder updates: headline, impact, next steps. ≤120 words.",
               callback_handler=None)

lead = Agent(
    name="tech_lead",
    model=MODEL,
    system_prompt=("Route the request to the right specialist tools (possibly several), "
                   "combine their answers, resolve contradictions, and finish with a stakeholder update from tech_writer."),
    tools=[security.as_tool(), performance.as_tool(), writer.as_tool()],
)

if __name__ == "__main__":
    lead(" ".join(sys.argv[1:]) or "Our checkout API p95 doubled after yesterday's deploy. What should we check?")
