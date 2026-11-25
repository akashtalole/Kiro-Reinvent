---
inclusion: always
---
# Repository structure

| Path | What lives there | Source of truth for |
| --- | --- | --- |
| `labs/NN-slug/README.md` | One lab per folder, YAML front matter + body, runnable assets beside it | The labs catalog (`_site/data/labs.json` is generated) |
| `site/` | Static HTML/CSS/JS, no framework, no bundler | Pages, filters, navigation |
| `site/data/catalog.json` | Learning paths, use cases, field stories, home architecture | Paths and use cases |
| `site/data/scenarios.json` | Advanced scenarios with happy and alternate paths | Scenarios (`docs/advanced-scenarios.md` is generated from it) |
| `docs/*.md` | Long-form guides rendered by `site/doc.html` | Reference docs |
| `docs/diagrams/` | archify-aws diagrams: `*.spec.json` is the source, HTML/SVG/PNG/draw.io are generated | Architecture diagrams |
| `scripts/build_site.py` | Builds `_site/`, validates front matter and scenarios, derives products, writes pretty-URL stubs | The build |
| `tests/` | Hypothesis property tests + data integrity tests | Build correctness |
| `.kiro/` | Steering, specs, custom agents, hooks, MCP, skills used to build this repo | How agents work here |

Never edit generated files (`_site/`, `docs/advanced-scenarios.md`); change the source and rebuild.
