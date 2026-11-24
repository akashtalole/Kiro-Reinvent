import pytest

from router import call_with_fallback, in_canary, release_gate, resolve


def test_tier_routing_and_wildcard():
    assert resolve("support-answer", "basic", "t-a").model_chain[0].startswith("us.amazon.nova-lite")
    assert resolve("support-answer", "enterprise", "t-a").max_tokens == 2500
    assert resolve("summarize-ticket", "premium", "t-a").max_tokens == 400


def test_canary_is_deterministic_and_roughly_sized():
    assert in_canary("t-acme01", "support-answer", 10) == in_canary("t-acme01", "support-answer", 10)
    share = sum(in_canary(f"t-{i:05d}", "support-answer", 10) for i in range(5000)) / 5000
    assert 0.07 < share < 0.13


def test_prompt_version_follows_canary():
    versions = {resolve("support-answer", "premium", f"t-{i:05d}").prompt_version for i in range(300)}
    assert versions == {"v2", "v3"}


def test_fallback_chain():
    calls = []

    def invoke(model):
        calls.append(model)
        if len(calls) == 1:
            raise RuntimeError("ThrottlingException")
        return "ok"

    model, out = call_with_fallback(resolve("support-answer", "premium", "t-a"), invoke)
    assert out == "ok" and model == calls[1] and len(calls) == 2


def test_release_gate():
    ok, problems = release_gate("support-answer", "v3")
    assert ok, problems


def test_every_route_has_a_registered_prompt():
    import json, pathlib
    root = pathlib.Path(__file__).parent
    policy = json.loads((root / "model_policy.json").read_text())
    registry = json.loads((root / "prompts" / "registry.json").read_text())
    assert set(policy["routes"]) <= set(registry), "every routed use case needs a prompt in the registry"
    for uc, entry in registry.items():
        for v in entry["versions"].values():
            assert (root / "prompts" / v["file"]).exists() and (root / v["eval"]).exists()
