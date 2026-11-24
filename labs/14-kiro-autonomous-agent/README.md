---
id: 14
title: The Kiro autonomous agent — issue to PR
category: Automate & scale
level: Intermediate
duration: 40 min
summary: Delegate GitHub issues to Kiro's frontier autonomous agent — label or mention it, let it work in an isolated sandbox across repos, and review the pull requests it opens.
services: [Kiro autonomous agent, Kiro Web, GitHub]
tags: [frontier agent, delegation, sandbox, multi-repo, async]
---

# Lab 14 · The Kiro autonomous agent — issue to PR

> **Outcome:** Well-scoped issues delegated to the autonomous agent with the `kiro` label or `/kiro` mention, sandbox network rules set, and its PRs reviewed against your standards.

## Scenario

Announced at re:Invent 2025 as one of AWS's three **frontier agents** (with AWS Security Agent and AWS DevOps Agent), the Kiro autonomous agent works **asynchronously** on longer tasks: it plans, spins up subagents, runs in an isolated sandbox per task, keeps context across sessions, learns from your review feedback, and delivers pull requests. It can run multiple tasks concurrently.

```mermaid
flowchart LR
  I[GitHub issue] -->|label: kiro<br/>or comment /kiro| A[Kiro autonomous agent]
  A --> SB[Isolated sandbox per task<br/>domain allow-list]
  SB --> R1[(repo A)] & R2[(repo B)]
  A -->|subagents| P[Plan · implement · test]
  P --> PR[Pull request(s)]
  PR --> H{Human review}
  H -->|feedback| A
```

## How it works

| Aspect | Detail |
| --- | --- |
| **Assigning work** | Add the `kiro` label to an issue, or mention `/kiro` in a comment; or start a task from Kiro Web |
| **Execution** | Isolated sandbox per task; configure internet access via domain allow-lists |
| **Scope** | Can work across multiple repositories in one task |
| **Memory** | Persistent context across sessions; learns from PR review feedback |
| **Configuration** | Reads your repo's steering, skills and (on Web) MCP servers, custom agents and hooks |
| **Availability** | Preview, rolling out to paid tiers — check your Kiro plan |

## Step 1 — Connect GitHub

In Kiro Web, connect your GitHub account/org and select the repositories the agent may access. Prefer a **pilot repo** first.

## Step 2 — Make repos agent-ready

Agents succeed when the repo explains itself:

- `.kiro/steering/` + `AGENTS.md` (Lab 02) — stack, structure, test commands
- A one-command test run (`npm test`, `make test`) that passes on `main`
- Skills for recurring procedures (Lab 07)
- Branch protection + required reviews (the agent opens PRs; humans merge)

## Step 3 — Write delegable issues

Use the template in [`issue-template.md`](issue-template.md): context, acceptance criteria (EARS works great), constraints, out-of-scope.

Good first delegations:

- "Upgrade all Lambda functions from `nodejs18.x` to `nodejs22.x`; update CDK, fix breaking changes, keep tests green." (multi-file, verifiable)
- "Add pagination (`limit`, `cursor`) to `GET /todos` per our API conventions."
- "Replace `console.log` with Powertools structured logging in `src/`."

## Step 4 — Delegate and watch

Label the issue `kiro`. Follow progress in Kiro Web (and on mobile). Review the PR like a human's: tests, scope creep, conventions. Leave review comments — the agent incorporates feedback into future work.

## Step 5 — Set network rules

Restrict sandbox internet to what builds need (package registries, your artifact store, AWS docs). Deny everything else.

## Choosing the right async tool

| | Autonomous agent | Kiro Crew bots | Headless CLI in CI |
| --- | --- | --- | --- |
| Unit of work | Issue → PR | Recurring responsibility | One pipeline step |
| Runs where | AWS-managed sandbox | Your machine / server | Your CI runner |
| Best for | Feature/maintenance tasks | Triage, monitoring, review | Gates, reports, fixes in pipeline |

## Learn more

- [Introducing the Kiro autonomous agent](https://kiro.dev/blog/introducing-kiro-autonomous-agent/) · [Kiro Web](https://kiro.dev/blog/introducing-kiro-web/)
- Next: [Lab 15 — AWS MCP Server](../15-aws-mcp-server/README.md)
