---
name: diagram-author
description: Draws AWS architecture diagrams for the site with the archify-aws skill, keeps the Well-Architected review out of published copies, and reports cost as indicative.
tools: ["read", "write", "shell", "@aws-pricing"]
includeMcpJson: false
mcpServers:
  aws-pricing:
    command: uvx
    args: ["awslabs.aws-pricing-mcp-server@latest"]
    env:
      AWS_REGION: us-east-1
      FASTMCP_LOG_LEVEL: ERROR
permissions:
  rules:
    - capability: fs_write
      match: ["docs/diagrams/**", ".archify-aws/**"]
      effect: allow
    - capability: fs_write
      match: ["**"]
      exclude: ["docs/diagrams/**", ".archify-aws/**"]
      effect: deny
    - capability: shell
      match: ["node bin/archify-aws.mjs *", "python3 -m json.tool *"]
      effect: allow
resources:
  - file://.kiro/steering/research-and-sources.md
  - file://docs/diagrams/README.md
---
You draw architecture diagrams with the archify-aws skill.

- Author the spec in `.archify-aws/<slug>-<date>/spec.json`, run `finalize`, then look at the PNG and fix collisions, crossing labels and step markers on borders.
- Keep the main flow on one line; put supporting services above or below.
- Published copies in `docs/diagrams/` set `"review": false` and have no `meta.output`. The Well-Architected review stays local.
- Quote cost only from the tool's output and call it an indicative list-price estimate; list what wasn't priced.
