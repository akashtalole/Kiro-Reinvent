#!/usr/bin/env python3
"""Generate docs/advanced-scenarios.md from site/data/scenarios.json (single source of truth).

    python scripts/gen_scenarios_md.py          # write
    python scripts/gen_scenarios_md.py --check  # CI: fail if the doc is stale
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "site" / "data" / "scenarios.json"
DST = ROOT / "docs" / "advanced-scenarios.md"
ICON = {"agent": "🤖", "human": "🧑", "system": "⚙️"}


def lab_index() -> dict:
    out = {}
    for readme in (ROOT / "labs").glob("*/README.md"):
        slug = readme.parent.name
        title = next((l.split(":", 1)[1].strip().strip('"') for l in readme.read_text().splitlines() if l.startswith("title:")), slug)
        out[slug[:2]] = (slug, title)
    return out


def render() -> str:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    labs = lab_index()
    lines = [
        "# Advanced use cases and scenarios",
        "",
        "> Generated from `site/data/scenarios.json` by `scripts/gen_scenarios_md.py`. Edit the JSON, not this file.",
        "",
        "End-to-end stories showing how an AI-first, multi-tenant SaaS team uses Kiro, skills, MCP, the AWS CLI, "
        "Bedrock, AgentCore and CloudWatch Omni when things get hard. Each scenario lists the trigger, who does "
        "what (🤖 agent · 🧑 human · ⚙️ system), the guardrails, the outcome, the metrics to track, and the labs that "
        "teach every piece. The metrics are what to measure, not promised results.",
        "",
        "| Scenario | Domain | Complexity | Personas |",
        "| --- | --- | --- | --- |",
    ]
    for sc in data["scenarios"]:
        lines.append(f"| [{sc['title']}](#{sc['id']}) | {sc['domain']} | {sc['complexity']} | {', '.join(sc['personas'])} |")
    for sc in data["scenarios"]:
        lines += ["", f'<a id="{sc["id"]}"></a>', "", f"## {sc['title']}", "",
                  f"*{sc['domain']} · {sc['complexity']} · {', '.join(sc['personas'])}*", "", sc["tagline"], "",
                  f"**Trigger:** {sc['trigger']}", "", "```mermaid", sc["diagram"], "```", "", "| # | Who | Does | With |",
                  "| --- | --- | --- | --- |"]
        for i, st in enumerate(sc["steps"], 1):
            lines.append(f"| {i} | {ICON[st['kind']]} {st['actor']} | {st['action']} | {', '.join(st.get('tools', [])) or '—'} |")
        lines += ["", "**Guardrails:** " + " · ".join(sc["guardrails"]), "", f"**Outcome:** {sc['outcome']}", "",
                  "**Metrics to track:** " + " · ".join(sc["metrics"]), "",
                  "**Labs:** " + " · ".join(f"[{l} {labs[l][1]}](../labs/{labs[l][0]}/README.md)" for l in sc["labs"] if l in labs),
                  "", "**AWS & Kiro services:** " + ", ".join(sc["services"])]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    text = render()
    if "--check" in sys.argv:
        if not DST.exists() or DST.read_text(encoding="utf-8") != text:
            sys.exit("docs/advanced-scenarios.md is stale: run python scripts/gen_scenarios_md.py")
        print("advanced-scenarios.md up to date")
    else:
        DST.write_text(text, encoding="utf-8")
        print(f"wrote {DST.relative_to(ROOT)}")
