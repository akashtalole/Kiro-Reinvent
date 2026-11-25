# Every Kiro feature, used on this repo

This repository now carries a working Kiro setup for building the site itself:
- steering;
- four custom agents;
- hooks;
- two specs, one finished and one ready to run;
- workspace MCP servers;
- property-based tests;
- a power;
- a headless Kiro CLI job in CI.

This page maps each feature to its files, shows how to use it from Kiro IDE, CLI, Web and Crew, and records what it has done for the project so far.

> **How this page was produced.** The site, labs and this `.kiro/` setup were written with an AI coding agent working against official Kiro and AWS docs. Everything listed as "verified" below was run in this repository. Anything about *your* experience in Kiro (how it felt, what changed for you) is yours to add after you run the steps in [Try it](#try-it-a-feature-tour-on-a-real-spec). Don't present those parts as done until you have.

## At a glance

| Feature | Where | Verified here |
| --- | --- | --- |
| Steering | `.kiro/steering/` (6 files: `always`, `fileMatch`, `auto`) | Front matter parses as YAML |
| Custom agents | `.kiro/agents/` (`lab-author`, `fact-checker`, `site-verifier`, `diagram-author`) | JSON and YAML front matter parse; permissions are least-privilege |
| Hooks | `.kiro/hooks/build-site.json`, `.kiro/hooks/quality.json` | Hook scripts tested: the secret scan blocks an AWS key and a Crew webhook token, and allows clean writes |
| Specs | `.kiro/specs/site-catalog/` (done), `.kiro/specs/product-chips-everywhere/` (ready to run) | Requirements in EARS form, each linked to tasks and properties |
| MCP | `.kiro/settings/mcp.json` + agent-local servers | JSON parses |
| Property-based tests | `tests/test_build_site_properties.py` (Hypothesis) | 8 tests pass; **one real bug found and fixed** |
| Powers | `powers/power-kiro-reinvent-authoring/` | JSON parses; skills follow the Agent Skills format |
| Kiro CLI headless | `.github/workflows/kiro-review.yml` | YAML parses; skips cleanly without `KIRO_API_KEY` |

## 1. Kiro IDE, CLI, Web and Crew: which to use for what

All four read the same `.kiro/` folder. The IDE and CLI drive the same V3 agent harness ([how they relate](kiro-ide-cli-internals.md)).

| Surface | Best for in this repo | How |
| --- | --- | --- |
| **Kiro IDE** | Running the `product-chips-everywhere` spec with visual task tracking and inline diffs. Reviewing a lab's markdown and mermaid | Open the repo, open the spec, run tasks one by one or in waves |
| **Kiro CLI** | Fast single tasks and headless CI | `kiro-cli --agent lab-author`; `/spec` for spec mode; `kiro-cli chat --no-interactive --agent fact-checker "…"` in CI |
| **Kiro Web** *(preview)* | A long spec run that should keep going after you close the laptop (cloud session in us-east-1) | `kiro-cli --cloud --repo akashtalole/Kiro-Reinvent`, or start it from the web app |
| **Kiro Crew** | Recurring upkeep: a nightly fact-check, a weekly link check, PR babysitting | A cron job such as `kirocrew cron add "nightly-fact-check" "Use the fact-checker agent on labs changed in the last 24 h" --cron "0 2 * * *" --timezone "Europe/London" --agent fact-checker` ([Lab 51](../labs/51-crew-scheduling-heartbeats-webhooks/README.md)) |

**How they differ** (from Kiro's docs):
- The IDE uses editor APIs for file edits and has the checkpoint UI.
- The CLI adds headless runs with `stream-json` output and the `code` tool.
- Web runs the harness in a managed cloud sandbox.
- Crew is a gateway that runs many CLI sessions over ACP, with schedules, memory and its own policy gate.

## 2. Custom agents

| Agent | Can | Can't | Use it for |
| --- | --- | --- | --- |
| `lab-author` (Markdown) | Write `labs/**`, `docs/**`, the catalog; run the build and tests; query the AWS Knowledge MCP server | Push, deploy, run `aws`, touch `.env`, `.kiro/settings` or `.github` | New labs via the `lab-creator` skill |
| `fact-checker` (JSON) | Read, fetch from official domains only, use AWS Knowledge MCP | Write files, run shell | Pre-publish checks; runs in CI |
| `site-verifier` (JSON) | Build, run tests, drive a browser through Playwright MCP | Edit source files | "Is this change done?" checks at desktop and 390 px |
| `diagram-author` (Markdown) | Write `docs/diagrams/**`, run archify-aws, use the AWS Pricing MCP server | Write anywhere else | Architecture diagrams |

**What they're for:** each agent has a narrow prompt, only the MCP servers its job needs, and permissions that make the wrong action impossible rather than unlikely. For example, `fact-checker` cannot edit what it checks, and `diagram-author` can only write diagrams.

**Use:** `kiro-cli --agent fact-checker`, `/agent swap lab-author`, or pick from the IDE agent selector.

## 3. Agent hooks

| Hook | Trigger | Automates |
| --- | --- | --- |
| Rebuild site after lab edits | File save on `labs/**/README.md`, `site/**`, `docs/**.md` | Front-matter validation and a full site build on every save |
| Session briefing | Session start | `git status` and the last 5 commits go into context |
| No secrets in a public repo | Pre tool use (`write`) | Blocks AWS keys, private keys, GitHub/Slack tokens, Kiro Crew webhook tokens and Kiro API keys (exit code 2) |
| Regenerate the scenarios doc | Save `site/data/scenarios.json` | Keeps the generated `docs/advanced-scenarios.md` in sync |
| JSON must parse | Save any `.json` | Validates every JSON file under `labs/`, `site/`, `docs/diagrams/`, `.kiro/` |
| Property tests on builder changes | Save `scripts/build_site.py` or `tests/*.py` | Reruns the Hypothesis properties |
| Use cases must match their lab | Save `site/data/catalog.json` | **Agent hook:** checks each changed use case against the lab it links to |
| Done means green | Agent stop | Build + scenario-doc check + tests before the agent may finish |

**What they improve:** checks that used to be "remember to run X" now run on every save, and the agent can't declare a task done while the build or tests are red. The CI pipeline runs the same commands, so local and CI results match.

## 4. Spec-driven development

- **`site-catalog` (done)** records the product filter and build behaviour as four requirements in EARS form (`WHEN … THE SYSTEM SHALL …`). It also has a design with six named correctness properties (P1–P6) and a task list. Each property maps to a test in `tests/test_build_site_properties.py`.
- **`product-chips-everywhere` (not implemented)** covers product chips on lab pages, product search in ⌘K, and product counts on the home page. Its design has three properties to check with Playwright. Run it in Kiro to experience spec mode end to end.

**Spec-driven vs vibe coding, in this repo.** The product filter was first built conversationally; the spec was written afterwards. Writing it turned two behaviours that only existed implicitly in the code into explicit requirements, each now checked by a property:
- AgentCore services must not imply Amazon Bedrock (requirement 2.3);
- adding services never removes a product (requirement 2.4).

Writing requirement 1.3 (quote-aware lists) prompted the property that found the parser bug in section 7. A conversational build had no place where that edge case would have been written down.

## 5. Steering

| File | Inclusion | Why |
| --- | --- | --- |
| `product.md` | always | Audience, voice, "truthfulness beats completeness", safety defaults |
| `structure.md` | always | Source of truth for each kind of content; never edit generated files |
| `repo.md` | always | Existing repo rules |
| `lab-authoring.md` | `fileMatch: labs/**/*` | Lab structure, front-matter rules (quote list items with commas), the Mermaid pitfall, verification duties. Pulls in `docs/authoring.md` with `#[[file:…]]` |
| `site-frontend.md` | `fileMatch: site/**/*` | No frameworks, escape all data, no nested links, URL-kept filter state, 390 px rule |
| `research-and-sources.md` | `auto` (by description) | Source order, quoting, preview labels, prices only from the Pricing MCP server |

**The strategy that matters most:** turn every mistake that actually happened into a rule. Two `fileMatch` rules came straight from bugs fixed in this repo:
- the Mermaid dotted-edge label that broke lab 61;
- the nested link on the home page.

`fileMatch` keeps those rules out of context until the agent touches the files they apply to.

## 6. MCP

| Server | Scope | What it enabled |
| --- | --- | --- |
| AWS Knowledge (remote) | Workspace, `lab-author`, `fact-checker`, power | Current AWS docs, API references and What's New posts inside the agent loop, so claims are checked against sources instead of model memory |
| AWS Pricing (uvx) | Workspace, `diagram-author`, power | List prices from the AWS Price List for indicative cost tabs; no hand-computed prices |
| Playwright | Workspace, `site-verifier` | Real-browser checks of filters, mobile width and console errors under the `/Kiro-Reinvent/` prefix |
| GitHub (remote, disabled by default) | Workspace | PRs and issues from the agent, with `merge_pull_request`, `delete_file` and `push_files` disabled |

**What would be hard without MCP:**
- verifying 60+ labs' commands against live docs;
- pricing every diagram from the public price list;
- catching mobile-layout and JavaScript regressions that only show in a browser.

## 7. Property-based testing

`tests/test_build_site_properties.py` uses Hypothesis, the same technique Kiro uses when it extracts properties from spec requirements.

| Property | Requirement | Result |
| --- | --- | --- |
| P1 Front matter round-trips for any ints, strings and lists, including `:`, `,`, `#`, `[]` | 1.1–1.4 | **Failed first, found a real bug** |
| P2 Products are known, unique and canonically ordered | 2.1 | Pass |
| P3 Explicit products override and keep order | 2.2 | Pass |
| P4 AgentCore alone never yields Amazon Bedrock | 2.3 | Pass |
| P5 Products are monotonic in services | 2.4 | Pass |
| P6 Redirect stubs resolve to the intended page at any depth | 3.1 | Pass |
| E1 Every path and use case points at a real lab; every lab has a product | 4.1–4.2 | Pass |

**The bug PBT caught:**
- **Symptom:** Hypothesis shrank a failure to `{'_': [',']}`. A quoted list item containing a comma, such as `services: ["Amazon Bedrock, Claude"]`, was split into two broken items, `'"Amazon Bedrock'` and `'Claude"'`.
- **Why unit tests missed it:** no existing lab had a comma inside a list item, so example-based tests and the build never hit it. One lab author writing a service name with a comma would have produced wrong filter chips silently.
- **Fix:** a quote-aware `split_list` in `scripts/build_site.py`.

The tests run in CI (`pages.yml`) and in the "Done means green" hook.

## 8. Powers

`powers/power-kiro-reinvent-authoring/` is an Agent Plugins–format power. It bundles the AWS Knowledge and AWS Pricing MCP servers with two skills: `fact-check-a-lab` and `draw-aws-diagram`. It activates on keywords such as *lab*, *fact check*, *architecture diagram* and *aws pricing*, so the MCP tools enter context only when the topic comes up.

Install it in Kiro from the folder, or from GitHub. **Check after installing:** the remote MCP entry uses `"type": "http"`, which this repo hasn't confirmed against the Agent Plugins schema. If Kiro rejects it, use the URL-only form from `.kiro/settings/mcp.json`.

**Third-party powers:** browse Kiro's power catalog from the IDE and add the integrations your project needs. List the ones you actually installed and what each changed in your answer. This repo doesn't assume any.

## Try it: a feature tour on a real spec

Run these in Kiro to get first-hand answers for every question above.

1. **Steering:** open any `labs/*/README.md` and ask *"What rules apply to this file?"* The `lab-authoring` fileMatch steering should be in context; in a `site/` file you should see `site-frontend` instead.
2. **Spec (IDE):** open `.kiro/specs/product-chips-everywhere/` and run task 1. Compare the diff with what you'd have got from *"add product chips to lab pages"* without a spec.
3. **Hooks:** save `site/data/catalog.json` after a small edit and watch the JSON hook and the use-case agent hook run. Then try writing a fake `AKIA…` key into a file and see the secret-scan hook block it.
4. **Custom agents (CLI):** run `kiro-cli --agent fact-checker`, then *"Fact-check labs/57-crew-24x7-on-aws/README.md"*. Then ask it to fix something and watch the write get denied.
5. **MCP:** run `kiro-cli --agent site-verifier`, then *"Check labs.html?product=Kiro+Crew at 390 px and report console errors."*
6. **PBT:** run task 4 of the new spec, adding P1–P3 as tests, and break something on purpose to watch the shrinker produce a minimal counterexample.
7. **Power:** install `powers/power-kiro-reinvent-authoring`, then say *"draw an architecture diagram for lab 56"* and check that the skill and the Pricing MCP server activate.
8. **Web and Crew:** start task 2 as a cloud session from the CLI (`--cloud`), close the laptop, and resume it later. Add the nightly fact-check cron to Crew.

## Sources

- [Steering](https://kiro.dev/docs/steering/)
- [Custom agents](https://kiro.dev/docs/custom-agents/)
- [Hook types](https://kiro.dev/docs/hooks/types/)
- [Specs](https://kiro.dev/docs/specs/)
- [Spec correctness and PBT](https://kiro.dev/docs/specs/correctness/)
- [MCP](https://kiro.dev/docs/mcp/)
- [Powers](https://kiro.dev/docs/powers/)
- [Headless CLI](https://kiro.dev/docs/cli/headless/)
- [Cloud sessions](https://kiro.dev/docs/cloud-sessions/)
- [Kiro Crew](https://kiro.dev/docs/crew/)
- [Hypothesis](https://hypothesis.readthedocs.io/)
