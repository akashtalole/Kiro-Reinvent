---
name: explain-the-bill
description: Explain AWS spend and cost anomalies for a period using Billing and Cost Management data. Use when asked why the bill went up, for month-over-month cost breakdowns, or for rightsizing and savings recommendations.
---
# Explain the bill

1. Use `aws-billing` MCP tools for cost and usage grouped by service, then by usage type for the top 3 services, for the requested period and the prior period.
2. Compute deltas; attribute ≥ 80% of the change to specific usage types.
3. Pull cost anomalies and rightsizing / Savings Plans recommendations if available.
4. Answer in this order: headline (one sentence), top drivers table, actions ranked by $ impact.
Read-only: never change budgets, commitments or resources.
