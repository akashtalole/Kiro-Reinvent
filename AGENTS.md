# AGENTS.md

Instructions for coding agents (Kiro, Claude Code, Copilot, …) working in this repo.

- Labs: `labs/NN-slug/README.md` with YAML front matter (see `docs/authoring.md`). Use the `lab-creator` skill in `.kiro/skills/`.
- Site: static files in `site/`; build with `python scripts/build_site.py` (output `_site/`, git-ignored); preview with `--serve`.
- Verify code you add (import/compile checks, `cdk synth`, JSON/YAML parse) and say what you verified.
- Never commit credentials or generated `gateway.json` / `policy-state.json` files.
- Run `python -m pytest tests -q` (Hypothesis property tests) after changing `scripts/build_site.py`. Kiro config lives in `.kiro/` (steering, agents, hooks, specs, MCP); see `docs/kiro-features-in-this-repo.md`.
