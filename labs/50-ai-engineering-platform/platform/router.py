"""Tier-aware model routing, prompt versioning with deterministic canaries, and a release gate.

Kept deliberately small: one JSON policy (model_policy.json) and one prompt registry are the
control plane; changing either is a reviewed PR that must pass `release_gate()`.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).parent


@dataclass(frozen=True)
class Route:
    model_chain: tuple[str, ...]
    max_tokens: int
    guardrail: str
    prompt_version: str
    prompt: str


def _load(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def in_canary(tenant_id: str, use_case: str, percent: int) -> bool:
    """Deterministic per-tenant bucketing: a tenant sees the same version on every request."""
    bucket = int(hashlib.sha256(f"{use_case}:{tenant_id}".encode()).hexdigest(), 16) % 100
    return bucket < percent


def resolve(use_case: str, tier: str, tenant_id: str, policy: dict | None = None, registry: dict | None = None) -> Route:
    policy = policy or _load("model_policy.json")
    registry = registry or _load("prompts/registry.json")
    routes = policy["routes"][use_case]
    r = routes.get(tier) or routes.get("*")
    if r is None:
        raise KeyError(f"no route for {use_case}/{tier}")
    entry = registry[use_case]
    version = entry["stable"]
    canary = policy.get("canary", {}).get(use_case)
    if canary and in_canary(tenant_id, use_case, canary["percent"]):
        version = canary["prompt_version"]
    prompt = (ROOT / "prompts" / entry["versions"][version]["file"]).read_text()
    return Route((r["primary"], *r["fallbacks"]), r["max_tokens"], r["guardrail"], version, prompt)


def call_with_fallback(route: Route, invoke) -> tuple[str, object]:
    """invoke(model_id) -> result; falls through the chain on throttling/unavailability."""
    last = None
    for model_id in route.model_chain:
        try:
            return model_id, invoke(model_id)
        except Exception as e:  # narrow to ThrottlingException / ServiceUnavailable in production
            last = e
    raise RuntimeError(f"all models failed for route; last error: {last}")


def release_gate(use_case: str, candidate: str, registry: dict | None = None, *, max_cost_increase=0.15,
                 max_latency_increase=0.20) -> tuple[bool, list[str]]:
    """A prompt/model version may go to canary or stable only if its eval beats the stable baseline
    on quality, passes every tenant-isolation probe, and stays within cost and latency budgets."""
    registry = registry or _load("prompts/registry.json")
    entry = registry[use_case]
    base = _load(entry["versions"][entry["stable"]]["eval"])
    cand = _load(entry["versions"][candidate]["eval"])
    problems = []
    if cand["pass_rate"] < base["pass_rate"]:
        problems.append(f"pass_rate {cand['pass_rate']} < baseline {base['pass_rate']}")
    if cand["isolation_probes_passed"] < cand["isolation_probes"]:
        problems.append("failed tenant-isolation probes")
    if cand["cost_per_1k_usd"] > base["cost_per_1k_usd"] * (1 + max_cost_increase):
        problems.append("cost budget exceeded")
    if cand["p95_ms"] > base["p95_ms"] * (1 + max_latency_increase):
        problems.append("latency budget exceeded")
    return (not problems), problems
