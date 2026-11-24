---
inclusion: always
---
# Kiro Reinvent Labs — repository rules

- Labs live in `labs/NN-slug/` with a front-matter README. `scripts/build_site.py` builds the GitHub Pages site from them; there is no other registry except `site/data/catalog.json` for paths and use cases.
- The site is static HTML/CSS/JS in `site/`. Don't add a framework or build step. External scripts load only from cdnjs or jsdelivr, with pinned versions.
- Prefer official sources and mark preview features. Never invent CLI flags or API fields. Verify them against installed SDKs or docs.
- Agent-facing code is least-privilege by default and never deploys to production.
- Run `python scripts/build_site.py` before finishing any change.
