"""Pattern 2 — graph: a deterministic DAG with a conditional edge (a content pipeline with a quality gate).

research → draft → review ──(approved)──► publish_summary
                     └─(needs work)─► revise → review   (bounded by max node executions)

Best when: you know the steps, want parallelism/conditions, and need predictable, auditable flow.
    python graph_pipeline.py "Write a 300-word internal guide: when to use SQS vs EventBridge"
"""
import sys

from strands import Agent
from strands.multiagent import GraphBuilder

MODEL = "global.anthropic.claude-sonnet-4-6"


def mk(name: str, prompt: str) -> Agent:
    return Agent(name=name, model=MODEL, system_prompt=prompt, callback_handler=None)


research = mk("research", "List the 6 most important facts for the topic, each with an AWS docs URL.")
draft = mk("draft", "Write the requested guide using only the provided facts. Markdown, with a decision table.")
review = mk("review", "Review the draft for accuracy and clarity. Reply starting with exactly APPROVED or NEEDS_WORK, then reasons.")
revise = mk("revise", "Revise the draft to address every review comment. Return the full revised guide.")
publish = mk("publish_summary", "Return the final guide unchanged, followed by a 2-line TL;DR.")


def approved(state) -> bool:
    out = state.results.get("review")
    return bool(out) and str(out.result).strip().upper().startswith("APPROVED")


def needs_work(state) -> bool:
    return not approved(state)


b = GraphBuilder()
for agent in (research, draft, review, revise, publish):
    b.add_node(agent, agent.name)
b.add_edge("research", "draft")
b.add_edge("draft", "review")
b.add_edge("review", "publish_summary", condition=approved)
b.add_edge("review", "revise", condition=needs_work)
b.add_edge("revise", "review")
b.set_entry_point("research")
b.reset_on_revisit(True)
b.set_max_node_executions(8)     # hard stop on review/revise loops
graph = b.build()

if __name__ == "__main__":
    result = graph(" ".join(sys.argv[1:]) or "Write a 300-word internal guide: when to use SQS vs EventBridge")
    print("status:", result.status, "| order:", [n.node_id for n in result.execution_order])
    print(result.results["publish_summary"].result if "publish_summary" in result.results else "not published")
