# The Kiro + AWS agentic landscape (November 2026)

A research briefing on every piece this lab series uses: what it is, where it fits, and how the pieces combine into end-to-end solutions. Facts were checked against official docs, the installed SDKs (`strands-agents` 1.66, `bedrock-agentcore` 1.27, `@aws/agentcore` CLI 1.2) and live endpoints on 24 Nov 2026. Preview features are marked. This space moves monthly, so check the linked docs before you rely on a detail.

## TL;DR

| Layer | Product | One-liner |
| --- | --- | --- |
| **Build with agents** | **Kiro IDE** | Agentic IDE built around specs, steering, hooks, powers and skills |
| | **Kiro CLI** | The same agent harness (V3) in the terminal, headless in CI, or behind any ACP editor |
| | **Kiro Web / Mobile** | Cloud sessions in the browser (preview) and steering them from your phone |
| | **Kiro autonomous agent** | Frontier agent (preview): issue → PR, runs asynchronously in a sandbox, works across repos |
| | **Kiro Crew** | Open-source (Apache-2.0) persistent workspace: many kiro-cli agents over ACP, schedules, heartbeats, channels, **bots** (GA Nov 2026) |
| **Connect agents to AWS** | **AWS MCP Server** (managed, preview) | Remote MCP server: AWS APIs + docs + agent SOPs, SigV4/IAM |
| | **awslabs/mcp** | 60+ open-source MCP servers: IaC, serverless, data, cost, observability, AI/ML, healthcare |
| **Build agents** | **Strands Agents** | Model-driven SDK (Python, TypeScript 1.0): tools, MCP, multi-agent, A2A, hooks, evals, bidi voice |
| **Run agents** | **Amazon Bedrock AgentCore** | Runtime, Harness, Gateway, Identity, Memory, Code Interpreter, Browser, Observability, Evaluations, Optimization, Policy, Registry, Payments |

## 1 · Kiro

### 1.1 One harness, many surfaces

Since Kiro CLI 3.0 the **V3 agent harness** is the default everywhere: IDE, CLI and Web share one agent loop and one configuration model. Local clients talk to it over stdio. Web and Mobile talk to a sandboxed harness over WebSocket. Anything you configure (steering, skills, custom agents, hooks, MCP, permissions) applies on every surface. One exception: Mobile reads only steering and skills.

| Surface | Strength | Lab |
| --- | --- | --- |
| IDE | Visual specs, diff review, hooks UI, property-based tests from specs | 03, 04 |
| CLI | Terminal, `--no-interactive` headless for CI (API-key auth), `kiro-cli acp` for editors | 01, 10, 11 |
| Web (preview) | Specs in the browser, multi-repo sessions, GitHub/GitLab | 14 |
| Autonomous agent (preview) | Label `kiro` or `/kiro` on an issue → PR; sandbox per task; learns from review | 14 |
| Crew | Long-running, scheduled, multi-agent, channel-driven | 12, 13 |

### 1.2 The configuration model (`.kiro/`)

| Primitive | Path | What it's for |
| --- | --- | --- |
| **Steering** | `.kiro/steering/*.md`, `~/.kiro/steering/`, `AGENTS.md` | Durable project facts and rules. Inclusion: `always`, `fileMatch`, `auto` (description-matched), `manual`. Can embed `#[[file:…]]` |
| **Specs** | `.kiro/specs/<name>/` | `requirements.md` (EARS) → `design.md` → `tasks.md`. Variants: requirements-first, design-first, bugfix (`bugfix.md`), quick spec |
| **Hooks** | `.kiro/hooks/*.json` | `version: v1`; triggers such as `SessionStart`, `PreToolUse`, `PostToolUse`, `PermissionRequest`, `PreCompact`, `PostFileSave`, `Stop`; `command` or `agent` actions; exit 2 blocks |
| **Custom agents** | `.kiro/agents/*.json` or `.md` | Prompt, `tools`, `permissions.rules` (allow/ask/deny, deny wins), `resources` (`file://`, `skill://`, knowledge bases), `mcpServers`, inline `hooks`, `model` |
| **Subagents** | via the `subagent` tool | Parallel delegation with separate context windows and task dependencies |
| **Skills** | `.kiro/skills/<name>/SKILL.md` | Open Agent Skills format; loaded on demand by description; `scripts/`, `references/`, `assets/` |
| **Powers** | `plugin.json` + `mcp.json` + `skills/` | Agent Plugins format; keyword-activated bundles of MCP + skills; installable from folder or GitHub; partner marketplace |
| **MCP** | `.kiro/settings/mcp.json`, `~/.kiro/settings/mcp.json` | stdio or remote (`url`, `headers`, `oauth`), `autoApprove`, `disabledTools`; enterprise IdP sign-in |

**How the pieces divide the work.** Steering holds what is always true. A skill is how to do one thing. A power is how to do it plus the tools to do it. A hook is what must always happen. A custom agent is who does the job and what they're allowed to touch.

### 1.3 Kiro Crew

Kiro Crew started inside Amazon as *MeshClaw* and was open-sourced on 4 Aug 2026 at [`kirodotdev/KiroCrew`](https://github.com/kirodotdev/KiroCrew). It's a personal or team agent workspace that drives `kiro-cli` through the **Agent Client Protocol**, and it reuses your existing `.kiro` configuration. It includes:

- Desktop app, web dashboard and CLI (`kirocrew setup | doctor | gateway`)
- Channels for Slack, Teams, Discord, Telegram, Webex, WeCom and WeChat
- Parallel background agents, scheduled jobs, and heartbeats that stay silent until something needs attention
- Knowledge folders that are indexed and embedded
- Safety controls: OS sandbox, deny-by-default commands, credential redaction, and a signed audit log
- **Bots** (GA 5 Nov 2026): long-running agents with a single responsibility, each with its own memory and git tree. AWS's examples are intake, build-health, code-review and release-readiness bots.

Coverage notes that Crew can use credits faster than interactive CLI use.

### 1.4 Frontier agents

At re:Invent 2025 AWS announced three **frontier agents**: the **Kiro autonomous agent**, the **AWS Security Agent** and the **AWS DevOps Agent**. All three run long tasks asynchronously, with their own context and sandboxes. They complement the self-hosted patterns in Labs 13, 19 and 35.

## 2 · MCP on AWS

- **AWS MCP Server** (managed remote, preview). Combines API access across AWS services, current docs and knowledge, and agent SOPs for multi-step tasks. Clients authenticate with SigV4 through `mcp-proxy-for-aws`, so IAM is the guardrail and CloudTrail is the audit log. Managed **EKS**, **ECS** and **SageMaker** MCP servers launched alongside it.
- **AWS Knowledge MCP** (`https://knowledge-mcp.global.api.aws`, remote, no auth). Tools: `search_documentation`, `read_documentation`, `list_regions`, `get_regional_availability`, `retrieve_skill` (verified live).
- **awslabs/mcp** (open source). See the [catalog](aws-mcp-catalog.md). The highlights for this series are IaC, Serverless, Lambda Tool, Pricing, Billing & Cost Management, CloudWatch, Application Signals, CloudTrail, DynamoDB, Aurora, S3 Tables, Bedrock KB Retrieval and the AgentCore MCP server.

MCP shows up in three places in an end-to-end build:

1. **Kiro → AWS.** Developers and CI use MCP (Labs 09 and 15–20).
2. **Your agent → tools.** Strands `MCPClient` (Lab 22).
3. **Gateway → everything.** AgentCore Gateway exposes Lambda, OpenAPI, Smithy, API Gateway and MCP servers as one governed MCP endpoint (Lab 27).

## 3 · Strands Agents

| Capability | API (Python 1.66) |
| --- | --- |
| Agent | `Agent(model, system_prompt, tools, hooks, session_manager, …)`. The default model is `global.anthropic.claude-sonnet-4-6` on Bedrock |
| Tools | `@tool` (docstring + type hints become the schema); vended tools in `strands.vended_tools` |
| Structured output | `agent(prompt, structured_output_model=Model).structured_output` |
| MCP | `MCPClient(url=…, headers=…, prefix=…, tool_filters=…)` or a stdio transport, passed directly in `tools` |
| Multi-agent | `agent.as_tool()`, `GraphBuilder` (conditional edges, bounded cycles), `Swarm` (hand-offs, limits), A2A (`A2AServer`, `A2AAgent`) |
| Hooks | `HookProvider` with `BeforeToolCallEvent.cancel_tool`, `AfterToolCallEvent`, invocation, model and multi-agent events |
| Sessions / memory | File, S3 and repository session managers; AgentCore Memory integration |
| Evals | `strands-agents-evals`: `Case`, `Experiment`, LLM judges, trajectory and tool evaluators, simulators, red-teaming |
| Voice | `BidiAgent` (Python) with Nova Sonic, Gemini Live, OpenAI Realtime |
| TypeScript | SDK 1.0, with agents-as-tools, Graph, Swarm and MCP |

Note: `strands-agents-tools` 0.9 **removed** its `code_interpreter` and `browser` tools. Use the AgentCore SDK clients instead (Lab 31).

## 4 · Amazon Bedrock AgentCore

| Service | Purpose | Lab |
| --- | --- | --- |
| **Runtime** | Serverless, session-isolated microVM hosting for any framework. Supports HTTP, MCP, A2A and AG-UI protocols, long sessions, and WebSocket bidirectional streaming | 26 |
| **Harness** | A managed agent loop: model, prompt and tools declared as config | 26 |
| **Gateway** | APIs, Lambda, OpenAPI, Smithy and MCP servers exposed as MCP tools. Inbound JWT/IAM, outbound credentials, semantic tool search, interceptors, rate limits | 27 |
| **Identity** | Workload identities, a token vault, OAuth 3LO / M2M / on-behalf-of, API keys | 29 |
| **Memory** | Short-term events plus long-term semantic, preference, summary, episodic and custom strategies, organised by namespace | 28 |
| **Code Interpreter / Browser** | Managed sandboxes for code and Chromium | 31 |
| **Observability** | OpenTelemetry traces in CloudWatch GenAI observability | 32 |
| **Evaluations** | Built-in and custom evaluators, run on demand or online on sampled live traffic | 32 |
| **Optimization** | Prompt and tool-description recommendations and A/B tests from evals and traces | 32 |
| **Policy** | Cedar (or natural-language → generated) rules on Gateway tool calls. `LOG_ONLY` → `ENFORCE` | 30 |
| **Registry** | Catalog of agents, MCP servers, tools and skills | 38 |
| **Payments** | x402 / MPP micropayments with wallets and spending limits | — |

**Tooling.** The `@aws/agentcore` CLI covers `create`, `add`, `dev`, `build`, `deploy`, `status`, `invoke`, `logs`, `traces` and `eval`. It deploys with CDK from `agentcore/agentcore.json`. The older Starter Toolkit samples now live under `legacy/` in [agentcore-samples](https://github.com/awslabs/agentcore-samples).

## 5 · How to combine them

The labs build up as follows:

1. **Ground** Kiro with steering, skills and MCP (Labs 02, 07, 09).
2. **Specify** with EARS specs before code (Lab 03).
3. **Constrain** with permissions and hooks (Labs 04, 05).
4. **Build** infrastructure and services through AWS MCP servers (Labs 15–20).
5. **Build agents** with Strands (Labs 21–25).
6. **Run** them on AgentCore with identity, gateway, memory and policy (Labs 26–31).
7. **Measure** with traces and evals (Labs 25, 32).
8. **Automate** the loop with headless CI, Crew bots and the autonomous agent (Labs 10–14).
9. **Govern** at org scale (Lab 38).

## 6 · Open questions and caveats

- The AWS MCP Server and the Kiro autonomous agent were still **preview** at the time of writing. Kiro Web is preview.
- Some hook trigger identifiers (prompt submit, file create/delete, task execution) vary by version. Use the hook editor or the [trigger reference](https://kiro.dev/docs/hooks/types/).
- Cedar entity and action names for AgentCore Policy come from your gateway's tool schema. Generate policies from natural language first, then read the output.
- Third-party adoption figures for Crew (for example "39,000 internal developers") come from secondary sources.

## Sources

- Kiro: [docs](https://kiro.dev/docs/) · [CLI](https://kiro.dev/docs/cli/) · [custom agents](https://kiro.dev/docs/custom-agents/) · [hooks](https://kiro.dev/docs/hooks/) · [steering](https://kiro.dev/docs/steering/) · [specs](https://kiro.dev/docs/specs/) · [skills](https://kiro.dev/docs/skills/) · [powers](https://kiro.dev/docs/powers/) · [MCP](https://kiro.dev/docs/mcp/) · [One agent, every surface](https://kiro.dev/blog/one-agent/) · [Kiro CLI 3](https://kiro.dev/blog/cli-3/)
- Kiro Crew: [Introducing Kiro Crew](https://kiro.dev/blog/introducing-kiro-crew/) · [GitHub](https://github.com/kirodotdev/KiroCrew) · [InfoQ](https://www.infoq.com/news/2026/08/kiro-crew-coding-agents/) · [Getting started (Builder Center)](https://builder.aws.com/content/3HYByHPgtbAQqGjoelhwVLzem7j/getting-started-with-kiro-crew) · [Bots (The Letter Two)](https://thelettertwo.com/2026/11/05/aws-kiro-bots-kiro-crew)
- Frontier agents: [Introducing the Kiro autonomous agent](https://kiro.dev/blog/introducing-kiro-autonomous-agent/) · [re:Invent 2025 breakdown](https://builder.aws.com/content/36aKe6ujF5lvU4HFgAcIvs3A51M/reinvent-2025-frontier-agents-are-here-the-complete-breakdown)
- MCP: [AWS MCP Server preview](https://aws.amazon.com/about-aws/whats-new/2025/11/aws-mcp-server/) · [IAM for managed MCP](https://aws.amazon.com/blogs/security/understanding-iam-for-managed-aws-mcp-servers/) · [awslabs/mcp](https://awslabs.github.io/mcp/)
- Strands: [strandsagents.com](https://strandsagents.com/) · [multi-agent patterns](https://strandsagents.com/docs/user-guide/sdk/multi-agent/multi-agent-patterns/) · [TypeScript 1.0](https://strandsagents.com/blog/strands-agents-typescript-v1/)
- AgentCore: [What is AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) · [Policy & Evaluations](https://aws.amazon.com/blogs/aws/amazon-bedrock-agentcore-adds-quality-evaluations-and-policy-controls-for-deploying-trusted-ai-agents/) · [Gateway concepts](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-core-concepts.html) · [samples](https://github.com/awslabs/agentcore-samples)
