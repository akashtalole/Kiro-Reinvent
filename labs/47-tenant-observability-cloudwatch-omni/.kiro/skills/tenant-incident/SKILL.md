---
name: tenant-incident
description: Investigate a production problem scoped to one tenant, one tier or a noisy neighbour, using CloudWatch / CloudWatch Omni telemetry, tenant-tagged logs, metrics and traces. Use when a customer reports an issue, an alarm names a tenant or tier, or someone asks "is tenant X affected".
metadata: { persona: sre }
---
# Tenant incident investigation

1. **Scope.** Is it one tenant, one tier or everyone? Compare the tenant's error rate and p95 with its tier (queries in `ops/tenant_queries.md`).
2. **Noisy neighbour check.** Find the top tenants by Requests and AITokens in the window. Did one tenant's spike line up with others' latency?
3. **Traces.** Filter spans by `tenant.id`. For agent features, open the agent trace in CloudWatch Omni to see each model call and tool call.
4. **Changes.** Check deployments and config or IAM changes in the window (CloudTrail), and whether the tenant was onboarded, upgraded or suspended recently (`tenantctl.sh status`).
5. **Root cause.** If the cause isn't obvious within 15 minutes, start an AWS DevOps Agent investigation (built into Omni) and attach your findings.
6. **Output.** Write an impact statement (tenants and tiers affected, start and end time), the evidence, a mitigation (a throttle via the usage plan beats a global change), and a customer-safe status update. Hand off to `runbook-from-incident`.

Read-only: never change throttles, tenants or infrastructure from this skill.
