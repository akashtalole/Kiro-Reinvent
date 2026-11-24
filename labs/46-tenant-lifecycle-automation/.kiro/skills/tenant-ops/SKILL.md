---
name: tenant-ops
description: Operate the tenant lifecycle of the multi-tenant SaaS — onboard, change tier, suspend, resume, offboard, and check status — using scripts/tenantctl.sh with dry runs and approval gates. Use for any request about creating, upgrading, suspending, deleting or inspecting a tenant.
metadata: { persona: tenant-operations }
---
# Tenant operations

1. **Identify the request.** Get the tenant id (`t-…`), the action, and a ticket or request reference. If the ticket is missing, ask for it.
2. **Check state.** Run `scripts/tenantctl.sh status <tenant>` and summarise it.
3. **Dry run.** Run `DRY_RUN=1 scripts/tenantctl.sh <action> …` and show the planned AWS calls.
4. **Approval gate.**
   - `onboard`, `suspend` and `resume` need the requester's confirmation in chat.
   - `offboard` needs a ticket id *and* an explicit `CONFIRM=<tenant-id>`. The PreToolUse hook enforces this.
5. **Execute.** Run the real command and capture the JSON log lines on stderr.
6. **Verify.** Run `status` again. For onboarding, also confirm the inference profile exists (`aws bedrock list-inference-profiles --type-equals APPLICATION`) and that the API key is attached to the tier's usage plan.
7. **Record.** Post a summary to the ticket: what changed, when, and by whom (the agent plus the approving human).

Never edit tenant data tables directly. Every change goes through `tenantctl.sh`, so it stays idempotent and audited.
