---
name: tenancy-review
description: Review a design, spec or IaC change for multi-tenant SaaS concerns — isolation model (silo/pool/bridge), tenant context propagation, noisy neighbours, tiering, data residency, metering and tenant lifecycle. Use when reviewing architecture, design.md, new services or data stores in a SaaS product.
metadata: { persona: architect }
---
# Tenancy review

Check each item and report only the failures, as `severity | where | issue | fix`:

1. **Tenant context**: `tenantId` comes from the verified identity (JWT claim or authorizer context), never from the request body, and it propagates to logs, metrics, traces (`tenant.id`) and async messages.
2. **Isolation**: the pool model uses `dynamodb:LeadingKeys` / row-level security / per-tenant prefixes with IAM session tags. The silo model uses one resource or account per tenant. **AI paths count too**: retrieval filters, memory namespaces and tool authorization must all be scoped per tenant.
3. **Noisy neighbour**: per-tenant throttles (usage plans, token budgets), with no shared unbounded queues per tier.
4. **Tiering**: limits and features read from the tenant record, not hard-coded.
5. **Metering**: every billable action emits `TenantUsage`. Bedrock calls go through a per-tenant application inference profile, or are logged with tenant metadata.
6. **Lifecycle**: onboarding, suspension, offboarding and data export/delete are automated and idempotent.
7. **Residency**: the tenant's region is pinned, with no cross-region replication of its data unless the contract allows it.
