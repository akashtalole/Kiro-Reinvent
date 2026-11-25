---
name: draw-aws-diagram
description: Draw an AWS architecture diagram for a lab or doc with official AWS icons (archify-aws), with a numbered main flow, an indicative cost tab and an advisory Well-Architected review kept out of published copies. Use when asked for an architecture diagram, reference architecture or flow picture.
license: MIT
---
# Draw an AWS diagram

1. Identify the main flow (entry → compute → data → model or delivery) and put it on one row; put identity, security and observability above or below their neighbour.
2. Write a typed JSON spec (archify-aws format) in `.archify-aws/<slug>-<date>/spec.json`. Use real service icon ids; use generic icons only for non-AWS components and label them honestly.
3. Run `finalize`. Open the PNG and fix crossing labels, step markers on borders and edges that share a line.
4. Publish to `docs/diagrams/` with `"review": false` and no `meta.output`.
5. Report node and edge counts, the indicative monthly cost with what was not priced, and the review findings by risk, saying the review is advisory and inferred from the drawing.
