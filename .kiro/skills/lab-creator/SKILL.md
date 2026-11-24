---
name: lab-creator
description: Create a new hands-on lab for the Kiro Reinvent Labs repository (labs/NN-name/README.md with front matter, diagram, steps, verify, clean up, plus runnable assets). Use when asked to add, scaffold, or write a lab, tutorial or workshop module for Kiro, AWS MCP servers, Strands Agents or AgentCore.
license: MIT
metadata:
  author: kiro-reinvent-labs
  version: "1.0"
---
# Lab creator

1. **Pick the id and slug.** List `labs/`, take the next free two-digit id, and use the slug `NN-kebab-title`.
2. **Research first.** Use the AWS Knowledge MCP server and official docs (kiro.dev, strandsagents.com, docs.aws.amazon.com/bedrock-agentcore). Note anything in preview.
3. **Copy** [assets/lab-template.md](assets/lab-template.md) to `labs/<slug>/README.md`. Fill every section and follow `docs/authoring.md`.
4. **Write runnable assets** next to the README: `.kiro/` configs, Python/TS code, IaC. Keep them minimal and least-privilege.
5. **Verify** them: `python -m py_compile` / import checks, `cdk synth`, JSON/YAML parse, and any script dry runs. Record what you verified in the README.
6. **Wire it in.** If it fits a learning path or use case, add it to `site/data/catalog.json`.
7. **Build** with `python scripts/build_site.py`. It must succeed.
