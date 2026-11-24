"""Deterministic guardrails for a Strands agent using hooks.

* BeforeToolCallEvent: block refunds above a limit (cancel_tool) and require a ticket id pattern
* AfterToolCallEvent:  audit every tool call as a JSON line
* BeforeInvocationEvent: cheap prompt screening before the model is called
"""
from __future__ import annotations

import json
import re
import time

from strands.hooks import (AfterToolCallEvent, BeforeInvocationEvent, BeforeToolCallEvent, HookProvider,
                           HookRegistry)

REFUND_LIMIT_USD = 100.0
INJECTION = re.compile(r"ignore (all|previous) instructions|you are now|system prompt", re.I)


class SupportGuardrails(HookProvider):
    def __init__(self, audit_path: str = "audit.jsonl") -> None:
        self.audit_path = audit_path

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        registry.add_callback(BeforeInvocationEvent, self.screen_prompt)
        registry.add_callback(BeforeToolCallEvent, self.enforce_refund_policy)
        registry.add_callback(AfterToolCallEvent, self.audit)

    def screen_prompt(self, event: BeforeInvocationEvent) -> None:
        last = event.agent.messages[-1] if event.agent.messages else None
        text = " ".join(c.get("text", "") for c in (last or {}).get("content", []) if isinstance(c, dict))
        if INJECTION.search(text):
            event.agent.state.set("flagged_injection", True)

    def enforce_refund_policy(self, event: BeforeToolCallEvent) -> None:
        tool = event.tool_use
        if tool["name"].endswith("issue_refund"):   # also matches gateway names like orders___issue_refund
            amount = float(tool["input"].get("amount", 0))
            if amount > REFUND_LIMIT_USD:
                event.cancel_tool = (f"Refunds over ${REFUND_LIMIT_USD:.0f} need a human. "
                                     "Tell the customer a specialist will follow up within 1 business day.")
            if event.agent.state.get("flagged_injection"):
                event.cancel_tool = "Refund blocked: the conversation was flagged for possible prompt injection."

    def audit(self, event: AfterToolCallEvent) -> None:
        with open(self.audit_path, "a") as f:
            f.write(json.dumps({
                "ts": time.time(),
                "tool": event.tool_use["name"],
                "input": event.tool_use["input"],
                "status": (event.result or {}).get("status"),
            }) + "\n")
