---
name: fact-check-a-lab
description: Check every factual claim in a lab or doc (product status, commands, flags, config keys, limits, prices) against official sources and report Verified, Contradicted or Unverified with links. Use before publishing or when a reader reports an error.
license: MIT
---
# Fact-check a lab

1. Read the file and list each claim that could be wrong: product names and release status (GA, preview), commands and flags, config keys and file paths, limits and defaults, prices and quoted numbers.
2. For each claim, search in this order: the product's official docs, its source repository (for open-source tools such as Kiro Crew), the AWS Knowledge MCP server (`aws-knowledge`), official blogs.
3. For prices use the `aws-pricing` MCP server; never compute a price by hand.
4. Output a table — claim | status | source URL | short quote or correction — then the three most important fixes.
5. Do not edit the file unless asked. When asked, change only contradicted claims and keep a list of what you changed.
