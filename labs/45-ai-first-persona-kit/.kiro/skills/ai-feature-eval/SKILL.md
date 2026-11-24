---
name: ai-feature-eval
description: Define and run the evaluation gate for an AI feature (prompt, agent, RAG, model change) before release — golden set, judges, tenant-isolation probes, cost and latency budgets. Use when building or changing any LLM or agent feature.
metadata: { persona: ai-engineer }
---
# AI feature eval gate

1. Build the **golden set**: 30–100 cases from real (anonymized) usage, covering each tier and each language, plus adversarial cases (prompt injection, out-of-scope requests, a cross-tenant probe).
2. Pick evaluators: correctness/faithfulness judges, tool-selection accuracy, deterministic checks (citations present, no other-tenant ids in the output).
3. Set budgets: p95 latency, tokens per request, cost per 1k requests per tier.
4. Compare candidate vs baseline. Ship only if quality ≥ baseline and the budgets hold. Record the result in the spec.
5. After release, run online evaluation (AgentCore Evaluations / CloudWatch Omni) on sampled sessions.
