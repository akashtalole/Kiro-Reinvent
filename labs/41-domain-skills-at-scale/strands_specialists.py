"""The same coordinator → specialists architecture in Strands, using the AgentSkills plugin.

Strands 1.6x loads skills as a plugin: Agent(plugins=[AgentSkills(skills="./skills/<domain>/")]).
Each specialist sees only its domain's skills; the coordinator sees none and routes via agents-as-tools.

    python strands_specialists.py "Review this: SELECT * FROM orders o JOIN items i ON i.order_id=o.id WHERE date(o.created_at)=current_date"
"""
import sys

from strands import Agent, AgentSkills

MODEL = "global.anthropic.claude-sonnet-4-6"


def specialist(domain: str, description: str) -> Agent:
    return Agent(
        name=f"{domain}_specialist",
        description=description,
        model=MODEL,
        system_prompt=f"You are the {domain} specialist. Activate and follow the relevant skill. Name the skill you used.",
        plugins=[AgentSkills(skills=f"./skills/{domain}/")],
        callback_handler=None,
    )


security = specialist("security", "Threat modelling, authN/Z, secrets, abuse cases.")
data = specialist("data", "SQL correctness/performance/safety, schemas, migrations.")
cloud = specialist("cloud", "AWS serverless, IaC, reliability and cost reviews.")

coordinator = Agent(
    name="coordinator",
    model=MODEL,
    system_prompt=("Route each request to the right specialist tool(s); delegate multi-domain requests to several. "
                   "Never answer domain questions yourself. Merge answers and resolve conflicts."),
    tools=[security.as_tool(), data.as_tool(), cloud.as_tool()],
)

if __name__ == "__main__":
    coordinator(" ".join(sys.argv[1:]) or "We expose an SQS-triggered Lambda that writes orders to Aurora. Threats and SQL risks?")
