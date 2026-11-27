# Ideas: skills and custom agents to build for Kiro

A catalogue of 39 skills and custom agents worth building, how to decide which form each idea should take, a design recipe, and how to test and ship them. Eight of the ideas are already built and tested in [Lab 62](../labs/62-build-kiro-skills-and-agents/README.md): the five device skills and three device agents marked **(built)**.

## 1. Pick the right form first

| If the idea is… | Build a… | Why |
| --- | --- | --- |
| Always true about this project (stack, conventions, "never do X") | **Steering** file (`always` or `fileMatch`) | Always in context, or whenever matching files are touched |
| A procedure you repeat ("review a webhook", "pre-flight a deploy") | **Skill** | Loads only when its description matches; can carry scripts and references |
| A procedure plus tools (MCP servers) others should install | **Power** | Skills + MCP packaged and keyword-activated ([Lab 08](../labs/08-build-a-kiro-power/README.md)) |
| A role with its own permissions, tools and model | **Custom agent** | Least privilege, a narrow prompt, agent-local MCP ([Lab 05](../labs/05-custom-agents/README.md)) |
| Something that must happen every time (block secrets, run tests) | **Hook** | Deterministic; doesn't depend on the model remembering |
| A schedule, watcher or shared team tool | **Kiro Crew app or cron** | Runs while you're away; installable by teammates ([Lab 54](../labs/54-crew-build-your-first-app/README.md)) |

Most good ideas combine two of these: an **agent** that owns a job and the **skills** it uses, guarded by a **hook**.

## 2. Design recipe (works for every idea below)

1. **Write the description first.** It is the router. Start with a verb, list concrete nouns the user will say, and end with "Use when …". Write three prompts that should trigger it and two near-misses that shouldn't.
2. **Script the deterministic parts.** Validation, signing, parsing and limits go in `scripts/`. Each script prints compact PASS/FAIL lines and exits non-zero on failure, so agents, hooks and Crew jobs can all use it.
3. **Prose only for judgement.** Keep `SKILL.md` short. Long checklists and specs go in `references/`, and templates in `assets/`.
4. **Least privilege for agents.** Allow the commands the job needs, deny the dangerous ones, and set `ask` on anything irreversible. Agent-local MCP servers rather than the whole workspace set.
5. **Test.** Lint every skill (name equals folder, description length, "Use when", links, scripts compile), run routing evals, and add property tests for the scripts.
6. **Ship.** Commit `.kiro/` for the team, import from GitHub, package as a power, or wrap in a Crew app.

## 3. The catalogue

Legend: **S** skill · **A** custom agent · **P** power · **H** hook.

### Amazon devices (Alexa+, Bee, Ring, Fire TV)

| Idea | Type | What it does | Guard rail |
| --- | --- | --- | --- |
| `ring-webhook-verifier` **(built)** | S | Sign and verify `X-Signature`, replay saved deliveries, review endpoint code against the Ring checklist | Key read from the environment only; never printed |
| `alexa-addon-preflight` **(built)** | S | Validate `addon.json` limits and probe the MCP endpoint (401 with no `WWW-Authenticate`) before `alexa-ai deploy` | Runs before every deploy; deploy itself is `ask` |
| `bee-to-spec` **(built)** | S | Bee conversation → EARS `requirements.md` with transcript citations → a Bee todo | Only conversations the user points at; asks before writing to Bee |
| `vega-tv-ui-review` **(built)** | S | 10-foot UI and D-pad review, plus a remote-only walkthrough on the Vega Virtual Device | Doesn't guess platform APIs; uses Amazon's docs |
| `echo-show-widget-review` **(built)** | S | Lint an Alexa+ widget for Echo Show (sandbox rules, hostContext, 768×480 canvas, type tokens, light/dark, CSP, versioned `ui://` URI) and check that speech and screen match | Static checks first; the Local Inspector and a real device have the final say |
| `echo-show-widget-builder` | A | Builds List, Carousel, Card and Map widgets from a tool's data, runs the widget review and the Local Inspector | Can write only `widgets/`; deploy is `ask` |
| `voice-visual-parity` | S | Compares each tool's spoken text with what its widget shows and flags contradictions or screen-only facts | Read-only |
| `alexa-latency-budget` | S | Measure each MCP tool's p95 latency against the 500 ms rule and propose caching | Read-only against production |
| `ring-event-replayer` | S | Turn real webhook captures into signed, anonymised test fixtures | Strips account IDs and URLs |
| `bee-privacy-filter` | S | Remove bystander speech and personal data from transcripts before any model call | Runs before every Bee-derived prompt |
| `ring-integrator` **(built)** · `alexa-addon-builder` **(built)** · `bee-builder` **(built)** | A | One owner per platform, each with only its skill and MCP server | Can't read keys; asks before deploying or writing to Bee |
| `demo-director` | A | Writes and rehearses the demo script, and checks each runtime-hook proof file exists | Read-only on code |

### Build and operate on AWS

| Idea | Type | What it does | Guard rail |
| --- | --- | --- | --- |
| `iam-least-privilege-review` | S | Scan synthesised CloudFormation for wildcard actions and resources; propose scoped policies | Never applies changes |
| `cost-diff` | S + P | Monthly cost delta of an IaC change, using the AWS Pricing MCP server | Labels prices as indicative |
| `incident-commander` | A | Read-only CloudWatch/CloudTrail MCP; builds a timeline and hypotheses, writes the post-incident review | No write tools at all |
| `architecture-diagrammer` | S | Draws AWS diagrams with official icons, plus cost and Well-Architected tabs | Review stays local |
| `bedrock-model-picker` | S | Compares models on your own eval set for quality, latency and cost | Uses your data only with consent |
| `migration-wave-planner` | A | Splits a legacy migration into module waves with parity tests ([Lab 39](../labs/39-skill-driven-migration-engine/README.md)) | Never deploys |

### SDLC and code quality

| Idea | Type | What it does | Guard rail |
| --- | --- | --- | --- |
| `ears-to-properties` | S | Turns EARS acceptance criteria into property-based tests (Hypothesis or fast-check) | Each property cites its requirement |
| `flaky-test-triager` | S | Classifies failures as flaky or real from CI history, with evidence | Quarantine expires automatically |
| `pr-narrator` | S | Writes the PR description from the diff and the spec | Never claims tests it didn't see run |
| `release-notes` | S | Release notes from merged PRs, grouped for users | Links every line to a PR |
| `api-contract-guard` | H + S | Blocks a save that breaks the OpenAPI contract without a version bump | Stop hook |
| `dependency-upgrade-planner` | A | Plans and executes major upgrades step by step on a branch | Force approval before merge |

### AI engineering

| Idea | Type | What it does | Guard rail |
| --- | --- | --- | --- |
| `prompt-eval-author` | S | Builds eval cases from real failures and support tickets | Scrubs personal data |
| `guardrail-red-team` | A | Attacks agent prompts and tools with injection payloads in a sandbox | Sandbox account only |
| `mcp-tool-designer` | S | Reviews MCP tool names, descriptions and schemas for model-friendliness | Read-only |
| `rag-eval` | S | Measures retrieval hit rate and grounding on a fixed question set | Fixed seed and question set |
| `model-migration` | A | Replays traces against a new model and reports diffs by route | Human signs off per model family |

### Kiro Crew operations

| Idea | Type | What it does | Guard rail |
| --- | --- | --- | --- |
| `cron-designer` | S | Chooses script vs minimal-context vs full-agent jobs, and writes the `kirocrew cron add` line | Never changes a job on its own |
| `bot-charter-writer` | S | Turns a recurring chore into a bot charter: inputs, sources, hand-off, stop conditions ([Lab 13](../labs/13-kiro-crew-bots/README.md)) | Starts bots comment-only |
| `crew-app-packager` | S | Packages agents, skills and crons into a valid `app.json` ([Lab 54](../labs/54-crew-build-your-first-app/README.md)) | Declares `"cron": true` when crons exist |
| `crew-governance-auditor` | A | Checks sandbox tier, denied commands, policy and audit-chain status ([Lab 58](../labs/58-crew-governance-for-teams/README.md)) | Read-only |
| `workflow-author` | S | Writes fan-out and judge-and-verify workflows for the Workflows app | Script is validated before it runs |

### Team and knowledge

| Idea | Type | What it does | Guard rail |
| --- | --- | --- | --- |
| `runbook-from-incident` | S | Turns a resolved incident chat into a runbook in your template | Human reviews before merge |
| `onboarding-guide` | S | Generates a first-week guide from the repo, steering and knowledge library | Cites every source |
| `docs-drift-checker` | S + H | Finds commands and flags in docs that no longer match the code | Opens issues; never edits silently |
| `fact-checker` | A | Checks product claims against official sources ([this repo's agent](kiro-features-in-this-repo.md)) | No writes, no shell |

## 4. Agent team patterns

| Pattern | Shape | Use for |
| --- | --- | --- |
| **Specialist + reviewer** | A builder agent and a read-only reviewer on a different model | Anything that ships to users |
| **Orchestrator + subagents** | One agent decomposes and delegates to specialists in isolated contexts | Multi-platform work (one subagent per device track) |
| **Read-only verifier** | Can build, test and browse, but never edit | The last step before "done" |
| **Human gate** | `ask` on deploy, publish, delete, or writes to customer data | Irreversible actions |
| **Always-on owner** | A Kiro Crew bot with a charter, a schedule and a stop condition | Recurring chores |

## 5. Test and measure

- **Lint** every skill on save. Lab 62's [`check_skills.py`](../labs/62-build-kiro-skills-and-agents/evals/check_skills.py) checks name = folder, description length and "Use when", links and that scripts compile. It caught a weak description on its first run.
- **Routing evals:** for each skill, keep prompts that should and shouldn't trigger it ([example](../labs/62-build-kiro-skills-and-agents/evals/trigger-evals.yaml)). Track precision (it loaded only when right) and recall (it loaded every time it should). When routing is wrong, fix the description, not the body.
- **Script tests:** property tests for anything that parses, signs or validates. For example, `verify(sign(body)) == true`, and flipping any byte makes it false.
- **Outcome metrics:** task success rate with and without the skill, human corrections per task, and tokens per task (skills should *reduce* context, not grow it).

## 6. Ship and share

| Audience | How |
| --- | --- |
| Your team, this repo | Commit `.kiro/skills` and `.kiro/agents` |
| Every repo you work on | `~/.kiro/skills` and `~/.kiro/agents` |
| Other teams | Import from a GitHub URL, or package as a **power** with its MCP servers |
| Teams on Kiro Crew | Wrap agents, skills and crons in a Crew **app**, installable from git |
| Other agents | Agent Skills is an open format; the same folder works in other skill-aware agents |

## Sources

- Kiro docs:
  - [Skills](https://kiro.dev/docs/skills/)
  - [Custom agents](https://kiro.dev/docs/custom-agents/)
  - [Permissions](https://kiro.dev/docs/permissions/)
  - [Hooks](https://kiro.dev/docs/hooks/types/)
  - [Powers](https://kiro.dev/docs/powers/)
  - [Kiro Crew apps](https://kiro.dev/docs/crew/apps/)
- Related labs and guides:
  - [Lab 62 starter pack](../labs/62-build-kiro-skills-and-agents/README.md)
  - [Amazon devices build plan](amazon-devices-build-plan.md)
  - [Kiro features in this repo](kiro-features-in-this-repo.md)

Ideas not marked **(built)** are proposals: build them with the recipe above and test them before relying on them.
