---
name: tenant-cost-report
description: Produce per-tenant and per-tier cost and unit economics (infra + AI inference) and flag unprofitable tenants or features. Use for FinOps reviews, pricing decisions, margin questions or "what does tenant X cost us".
metadata: { persona: finops }
---
# Tenant cost report

1. **AI cost**: Cost Explorer grouped by the `tenantId` cost-allocation tag on Bedrock application inference profiles, for the period.
2. **Shared infra**: allocate pooled costs by usage share, using the `TenantUsage` metrics (requests, storage GB, compute ms) from CloudWatch.
3. **Revenue**: plan price by tier, from the billing system or the tenant table.
4. Output a table `tenant | tier | revenue | AI cost | infra cost | margin % | trend`, then the top 5 negative-margin tenants with their drivers, and pricing or limit recommendations.
5. State the allocation method and its assumptions. This skill is read-only.
