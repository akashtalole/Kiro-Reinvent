---
name: adr-writer
description: Write an Architecture Decision Record in docs/adr using the team template. Use when a design decision is made or the user asks to record, document or justify an architectural choice.
---
# ADR writer

1. Find the next number: list `docs/adr/` and increment the highest `NNNN`.
2. Copy [assets/template.md](assets/template.md) to `docs/adr/NNNN-<kebab-title>.md`.
3. Fill every section. Options must include at least two real alternatives with trade-offs.
4. Status starts as `Proposed`. Link related ADRs.

Invoke directly with `/adr-writer <decision title>`; in the CLI the title is available as `$ARGUMENTS`.
