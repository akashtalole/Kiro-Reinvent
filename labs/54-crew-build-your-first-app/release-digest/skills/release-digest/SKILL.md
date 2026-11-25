---
description: How to write the team's weekday release digest for one GitHub repository
always: false
---

# Release digest

Repository: `owner/repo` (edit this line for your team).

## Gather (read-only)

1. `gh pr list --repo owner/repo --state merged --search "merged:>=$(date -d yesterday +%F)" --json number,title,url,author`
2. `gh pr list --repo owner/repo --state open --label blocked --json number,title,url`
3. `gh run list --repo owner/repo --branch main --limit 5 --json name,conclusion,url`

## Decide what is risky

A merged PR is **risky** if it touches database migrations, IAM or auth code, feature flags defaults, or has no linked issue.

## Write

- **Shipped** — up to 5 merged PRs, one line each, with links.
- **Blocked** — open PRs labelled `blocked`, with the blocker in five words.
- **Risky** — merged PRs that match the rule above, and why.
- **Main branch** — the latest CI conclusion with a link.

Never include secrets, tokens or customer data in the digest.
