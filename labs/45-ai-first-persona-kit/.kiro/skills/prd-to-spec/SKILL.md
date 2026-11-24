---
name: prd-to-spec
description: Turn a product requirement, customer request or PRD into a Kiro spec (EARS requirements) with tenant impact, tier gating, success metrics and rollout plan. Use when a product manager shares a feature idea, PRD, customer ask or roadmap item.
metadata: { persona: product-manager }
---
# PRD → spec

1. Restate the problem, the target personas and the **tenant tiers** affected (basic / premium / enterprise).
2. Write requirements in EARS. Every feature needs at least:
   - one requirement per tier difference ("WHERE the tenant tier is premium THE SYSTEM SHALL …");
   - one isolation requirement ("THE SYSTEM SHALL NOT expose tenant A's data to tenant B");
   - one metering requirement (what usage is billable, emitted as `TenantUsage`).
3. Add **success metrics** (adoption per tier, latency SLO, cost per tenant per month) and a **feature flag / rollout plan** (internal → 5 % of tenants → GA).
4. List open questions for engineering. Don't invent answers.
5. Save the result as `.kiro/specs/<feature>/requirements.md`, and link the source (ticket, sheet row or doc).
