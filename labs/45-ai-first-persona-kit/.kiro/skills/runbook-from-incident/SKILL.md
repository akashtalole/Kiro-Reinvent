---
name: runbook-from-incident
description: Turn an incident (alarm, timeline, postmortem, chat thread) into a runbook, a missing alarm, a regression test and a backlog item. Use after incidents, game days or when on-call asks "how do we handle X".
metadata: { persona: sre }
---
# Runbook from incident

1. Extract the following: trigger (which alarm or symptom), blast radius (**which tenants and tiers**), detection gap (minutes from first error to alarm), and the fix that worked.
2. Write `docs/runbooks/<slug>.md` with: Symptoms → Triage queries (CloudWatch / Omni, filtered by `tenant.id`) → Mitigations (safe first) → Escalation → Verification.
3. Propose the missing alarm as IaC (metric, threshold, period), and the regression test.
4. Open backlog items for each of them. Never change production resources from this skill.
