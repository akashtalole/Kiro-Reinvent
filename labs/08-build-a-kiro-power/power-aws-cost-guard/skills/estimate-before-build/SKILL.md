---
name: estimate-before-build
description: Produce a monthly AWS cost estimate for a design, spec or CDK/CloudFormation/Terraform project before it is deployed. Use when asked "how much will this cost", when a spec design is approved, or before adding new AWS resources.
---
# Estimate before build

1. Inventory resources: from `design.md`, or `npx cdk synth --json` → `python3 scripts/inventory.py <template.json>`.
2. Ask the user for usage drivers you can't infer (requests/month, GB stored, hours on). State every assumption.
3. Use the `aws-pricing` MCP tools to fetch on-demand prices for the target region. Never guess a price.
4. Output a table: `service | driver | unit price | monthly qty | monthly cost`, a total, and the top 3 savings levers (Graviton, Savings Plans, storage tiering, right-sizing).
5. Append the estimate to the spec's design.md under `## Cost estimate`.
