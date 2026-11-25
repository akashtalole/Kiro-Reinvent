# Reference architecture diagrams

Drawn with the [archify-aws](https://github.com/akashtalole/archify-aws) skill using official AWS Architecture Icons. The `*.spec.json` files are the source. HTML, SVG, PNG and draw.io files are generated from them.

| Diagram | Source | Outputs |
| --- | --- | --- |
| Multi-tenant runtime with AI features | `ai-first-saas-runtime.spec.json` | `.html` (interactive), `.svg`, `.png`, `.drawio` |
| Build and operate with Kiro | `ai-first-saas-delivery.spec.json` | `.html` (interactive), `.svg`, `.png`, `.drawio` |
| Kiro IDE and CLI: one agent harness | `kiro-harness.spec.json` | `.html` (interactive), `.svg`, `.png`, `.drawio` |
| Kiro Crew components | `kiro-crew-architecture.spec.json` | `.html` (interactive), `.svg`, `.png`, `.drawio` |
| Kiro Crew message flow (sequence) | `kiro-crew-message-flow.spec.json` | `.html` (interactive), `.svg`, `.png`, `.drawio` |

Regenerate from the archify-aws skill directory:

```bash
node bin/archify-aws.mjs finalize <repo>/docs/diagrams/ai-first-saas-runtime.spec.json -o <repo>/docs/diagrams/ai-first-saas-runtime.html
node bin/archify-aws.mjs finalize <repo>/docs/diagrams/ai-first-saas-delivery.spec.json -o <repo>/docs/diagrams/ai-first-saas-delivery.html
node bin/archify-aws.mjs finalize <repo>/docs/diagrams/kiro-harness.spec.json -o <repo>/docs/diagrams/kiro-harness.html
node bin/archify-aws.mjs finalize <repo>/docs/diagrams/kiro-crew-architecture.spec.json -o <repo>/docs/diagrams/kiro-crew-architecture.html
node bin/archify-aws.mjs finalize <repo>/docs/diagrams/kiro-crew-message-flow.spec.json -o <repo>/docs/diagrams/kiro-crew-message-flow.html
```

Notes:
- The published copies set `"review": false`. The Well-Architected review is advisory and kept out of the public site. Set it to `true` locally to see it.
- Kiro, Kiro Crew, GitHub, GitHub Actions and the AWS MCP Server have no official AWS icon, so they use generic icons with honest labels.
- The main flow in each diagram is aligned on one line. The column spacers in the specs are computed from the layout engine's anchor rule, so keep them when editing.
- The cost tab is an indicative list-price estimate with default usage. Bedrock model inference and Knowledge Bases are not estimated until you add token volumes. Confirm costs with the AWS Pricing Calculator.
- The Kiro Crew diagrams show local processes, not AWS services, so they use generic icons. They are based on `kirodotdev/KiroCrew` `docs/architecture/overview.md` (commit `967a2fad`). See `docs/kiro-crew-internals.md`.
- The Kiro harness diagram is based on kiro.dev docs (Nov 2026); see `docs/kiro-ide-cli-internals.md`. Kiro usage is billed in Kiro credits, so its cost tab shows $0 for the AWS account.
