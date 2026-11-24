"""Pattern 3 — swarm: autonomous hand-offs through shared context (an incident war-room).

Agents decide who goes next with the built-in handoff tool. Best when the path isn't known up front.
    python swarm_incident.py "Orders API 5xx rate 12% since 02:10 UTC in eu-west-1"
"""
import sys

from strands import Agent
from strands.multiagent import Swarm

MODEL = "global.anthropic.claude-sonnet-4-6"

triage = Agent(name="triage", model=MODEL, callback_handler=None, system_prompt=(
    "You are incident commander. Classify severity, list hypotheses, then hand off to the most relevant specialist. "
    "When specialists have reported, hand off to comms."))
infra = Agent(name="infra", model=MODEL, callback_handler=None, system_prompt=(
    "You investigate infrastructure: capacity, throttling, deployments, networking. Report evidence-based findings, then hand back to triage."))
app = Agent(name="app", model=MODEL, callback_handler=None, system_prompt=(
    "You investigate application errors: exceptions, dependency timeouts, bad config. Report findings, then hand back to triage."))
comms = Agent(name="comms", model=MODEL, callback_handler=None, system_prompt=(
    "Write the status-page update and the internal summary. You are the last agent; do not hand off."))

swarm = Swarm(
    [triage, infra, app, comms],
    entry_point=triage,
    max_handoffs=12,
    max_iterations=16,
    execution_timeout=600,
    node_timeout=180,
    repetitive_handoff_detection_window=6,
    repetitive_handoff_min_unique_agents=2,
)

if __name__ == "__main__":
    result = swarm(" ".join(sys.argv[1:]) or "Orders API 5xx rate 12% since 02:10 UTC in eu-west-1")
    print("status:", result.status)
    print("path:", " → ".join(n.node_id for n in result.node_history))
