# Authoring guide

Every lab is a folder, `labs/NN-kebab-name/`, containing a `README.md` that starts with front matter, plus any runnable assets. The site is generated from those folders. There is no second place to update.

## Front matter

```yaml
---
id: 39                                  # unique, two digits
title: Short imperative title
category: AgentCore                     # one of the categories below
level: Intermediate                     # Beginner | Intermediate | Advanced
duration: 45 min                        # "N min", "N h", or "1 day"
summary: One sentence on what the learner builds and why it matters.
services: [AgentCore Gateway, Strands Agents]
tags: [mcp, oauth]
popular: false                          # true puts it in "Popular labs" (keep ≤ 8)
---
```

Categories: `Kiro foundations`, `Customize Kiro`, `Automate & scale`, `AWS MCP servers`, `Strands Agents`, `AgentCore`, `End-to-end solutions`.

## README structure

1. `# Lab NN · Title`, then a `> **Outcome:**` line
2. `## Scenario`: the problem, followed by a mermaid diagram
3. `## How it works`: concepts, a config table, file paths
4. `## Step N — …`: copy-ready commands and Kiro prompts. Link the lab's files with relative paths
5. `## Verify`: checkboxes
6. `## Clean up` for anything that bills
7. `## Learn more`: official docs, then a link to the next lab

## Rules

- **Run it.** Import-check Python, synth CDK, and validate JSON. Say what you verified.
- **Prefer official sources**, and mark preview features.
- **Least privilege by default.** Read-only first. Never deploy from an agent without a human.
- **No secrets** in files. Use `.gitignore` for generated credential files.
- Link other labs as `../NN-name/README.md`. The site rewrites those links.

## Use the lab-creator skill

This repo ships a Kiro skill in `.kiro/skills/lab-creator/`. In Kiro:

```text
> /lab-creator AgentCore Payments: give an agent a wallet with spending limits
```

## Build and preview

```bash
python scripts/build_site.py --serve
```

The build fails on missing or invalid front matter or duplicate ids. CI runs the same build on every PR.
