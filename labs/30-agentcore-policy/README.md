---
id: 30
title: AgentCore Policy — deterministic tool control with Cedar
category: AgentCore
level: Advanced
duration: 50 min
summary: Write tool-call rules in plain English, generate Cedar policies, test them in log-only mode, then enforce them at the gateway — so refund limits hold no matter what the model decides.
services: [AgentCore Policy, AgentCore Gateway, AgentCore Identity, Cedar]
tags: [policy, Cedar, authorization, governance, log-only, enforcement]
popular: true
---

# Lab 30 · AgentCore Policy — deterministic tool control with Cedar

> **Outcome:** A policy engine attached to the Lab 27 gateway that allows `issue_refund` only within role-based limits and order-id rules — generated from natural language, reviewed, trialled in `LOG_ONLY`, then `ENFORCE`d.

## Scenario

Prompts can be jailbroken; hooks live in code someone can change. Compliance teams want **controls outside the agent**: a central, auditable rule that says *who* may call *which tool* with *which arguments*. **AgentCore Policy** evaluates every tool call that passes through AgentCore Gateway against **Cedar** policies (also authorable in natural language), using the tool's input and the caller's OAuth claims.

```mermaid
flowchart LR
  A[Agent] -->|tools/call issue_refund {order_id, amount}<br/>+ JWT role=support-agent| GW[AgentCore Gateway]
  GW --> PE{Policy engine<br/>Cedar}
  PE -->|permit| T[Lambda target]
  PE -->|deny| X[error to agent]
  PE --> L[(decision logs)]
  NL[policies/requirements.txt<br/>plain English] -->|StartPolicyGeneration| PE
```

## How it works

| Piece | Detail |
| --- | --- |
| **Policy engine** | Container of policies; attached to a gateway with `policyEngineConfiguration {arn, mode}` |
| **Modes** | `LOG_ONLY` (record decisions, don't block) → `ENFORCE` |
| **Authoring** | Cedar directly, or **natural language → generated policies** (`StartPolicyGeneration`) that you review and promote |
| **Schema** | Generated from the gateway's tool input schemas; policies are validated against it (`validationMode: FAIL_ON_ANY_FINDINGS`) |
| **Inputs to decisions** | Principal (OAuth user + claims/tags), action (the tool), resource (the gateway), `context.input` (tool arguments) |
| **Default** | Cedar is deny-by-default; `forbid` overrides `permit` |

## Step 1 — Prerequisites

Lab 27 gateway deployed (it includes the `issue_refund` tool). Add a `role` claim to your tokens — for Cognito M2M, use a pre-token-generation Lambda or separate app clients per role.

## Step 2 — Write the rules in English

[`policies/requirements.txt`](policies/requirements.txt):

```text
The issue_refund tool may only be called when the amount is less than or equal to 100,
and only by users whose "role" claim is "support-agent" or "support-lead".
Users whose "role" claim is "support-lead" may call issue_refund for amounts up to 1000.
Nobody may call issue_refund for an order id that does not start with "A-".
```

## Step 3 — Generate, review, create, attach (LOG_ONLY)

```bash
cd labs/30-agentcore-policy
python create_policies.py --gateway-id <gateway-id>
```

[`create_policies.py`](create_policies.py) creates the engine, generates candidate policies from the text, shows each with its findings, creates only the ones you approve, and attaches the engine in `LOG_ONLY`. Compare the generated Cedar with the hand-written illustration in [`policies/refunds.cedar`](policies/refunds.cedar) — the generated one has the exact entity/action names for your gateway.

## Step 4 — Test the matrix

| Caller role | Call | Expected |
| --- | --- | --- |
| support-agent | refund A-1002 $59.90 | permit |
| support-agent | refund A-1002 $500 | deny |
| support-lead | refund A-1002 $500 | permit |
| support-lead | refund B-77 $10 | deny (forbid) |
| (no role) | get_order A-1001 | permit |

Run each through Lab 27's agent and check the decision logs. When every row matches, enforce:

```bash
python create_policies.py --gateway-id <gateway-id> --enforce
```

## Step 5 — Let Kiro maintain policies

```text
> Our refund policy changed: leads may refund up to 2000, and refunds on orders older
  than 90 days need a "finance" role. Update policies/requirements.txt, regenerate,
  and write a test matrix like the one in the README.
```

## Where policy fits

Kiro **permissions & hooks** (Labs 04–05) govern your *coding* agent. Strands **hooks** (Lab 25) are in-process guardrails. **AgentCore Policy** governs *deployed* agents' tool calls centrally — independent of framework or prompt.

## Learn more

- [AgentCore adds quality evaluations and policy controls](https://aws.amazon.com/blogs/aws/amazon-bedrock-agentcore-adds-quality-evaluations-and-policy-controls-for-deploying-trusted-ai-agents/) · [Cedar](https://www.cedarpolicy.com/)
- Next: [Lab 31 — Code Interpreter and Browser](../31-agentcore-code-interpreter-browser/README.md)
