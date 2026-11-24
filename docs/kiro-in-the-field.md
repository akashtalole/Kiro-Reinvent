# Kiro in the field: use cases from the AWS Machine Learning Blog

This guide analyzes **every post in the AWS ML Blog's Kiro category** ([category page](https://aws.amazon.com/blogs/machine-learning/category/artificial-intelligence/kiro/)): nine posts from February to October 2026, read in full from the category feed on 24 Nov 2026. For each post it covers what was built, *how Kiro was used*, the reusable pattern, and the lab in this repo that turns the pattern into a hands-on build.

## At a glance

| # | Post (date) | Domain | How Kiro is used | Pattern | Lab |
| --- | --- | --- | --- | --- | --- |
| 1 | [Repeatable PHP-to-Java migration engine](https://aws.amazon.com/blogs/machine-learning/build-a-repeatable-php-to-java-migration-engine-with-kiro/) (Oct 29) | Modernization | **Skills + steering** encode an 8-phase migration methodology with approval gates; the same skills drive **AWS Transform** at portfolio scale | Methodology-as-skills, parity harness as referee | [39](../labs/39-skill-driven-migration-engine/README.md), [36](../labs/36-e2e-legacy-modernization/README.md) |
| 2 | [Workflow context with Smartsheet MCP](https://aws.amazon.com/blogs/machine-learning/workflow-context-for-ai-agents-with-smartsheet-mcp-on-aws/) (Oct 20) | Project / work management | **Remote MCP** in `mcp.json`; specs generated from roadmap rows; a **hook** updates task status on commit | Business-system context in the dev loop | [42](../labs/42-work-management-mcp-in-the-dev-loop/README.md) |
| 3 | [HCLS reasoning with open-source agent skills](https://aws.amazon.com/blogs/machine-learning/improving-hcls-ai-reasoning-with-open-source-agent-skills/) (Sep 16) | Healthcare & life sciences | **Kiro CLI multi-agent**: a skill-free coordinator plus 8 domain specialists loading only their skills; installer ships Kiro agents | Domain skills at scale, with context engineering | [41](../labs/41-domain-skills-at-scale/README.md), [07](../labs/07-agent-skills/README.md) |
| 4 | [AI as accessibility for neurodivergent professionals](https://aws.amazon.com/blogs/machine-learning/when-your-brain-works-differently-ai-isnt-a-luxury-its-accessibility/) (Jul 13) | Personal productivity | Kiro used to **build a custom MCP server** (Outlook, calendar, Asana) whose triage rules live in Markdown; consumed by AWS Quick desktop | Build-your-own MCP; rules-as-markdown | [40](../labs/40-kiro-cli-persistent-memory/README.md) (MCP server build), [09](../labs/09-mcp-servers-in-kiro/README.md) |
| 5 | [How AWS ProServe became a frontier team](https://aws.amazon.com/blogs/machine-learning/built-from-the-inside-out-how-aws-professional-services-became-a-frontier-team-first/) (Jun 12) | Professional services delivery | **Specs as source of truth**, **steering** for codified standards, parallel agents; part of the ProServe Delivery Agent with AgentCore and Strands | AI-DLC operating model | [38](../labs/38-e2e-governed-agent-platform/README.md), [06](../labs/06-subagents-and-parallel-work/README.md) |
| 6 | [Research assistants with Strands](https://aws.amazon.com/blogs/machine-learning/from-idea-to-ai-app-creating-intelligent-research-assistants-with-strands/) (May 26) | Agent development | **Strands power** for accurate scaffolding; Kiro generates a Streamlit + Strands app from a detailed prompt | Powers to ground agent code | [21](../labs/21-strands-first-agent/README.md), [08](../labs/08-build-a-kiro-power/README.md) |
| 7 | [Conversational memory in Kiro CLI with AgentCore Memory](https://aws.amazon.com/blogs/machine-learning/extending-conversational-memory-in-kiro-cli-using-amazon-bedrock-agentcore-memory/) (May 19) | Developer productivity | **Custom MCP server + custom agent + hooks** give Kiro CLI memory across sessions | Durable memory for the coding agent | [40](../labs/40-kiro-cli-persistent-memory/README.md), [28](../labs/28-agentcore-memory/README.md) |
| 8 | [Agent-guided model customization in SageMaker AI](https://aws.amazon.com/blogs/machine-learning/agent-guided-workflows-to-accelerate-model-customization-in-amazon-sagemaker-ai/) (May 4) | ML engineering | Kiro **pre-configured over ACP** in SageMaker Studio JupyterLab; 9 model-customization **skills** auto-loaded | Kiro embedded in another product via ACP + skills | [44](../labs/44-kiro-in-sagemaker-model-customization/README.md), [11](../labs/11-acp-editor-integration/README.md) |
| 9 | [Full-stack starter template for AgentCore (FAST)](https://aws.amazon.com/blogs/machine-learning/accelerate-agentic-application-development-with-a-full-stack-starter-template-for-amazon-bedrock-agentcore/) (Feb 9) | Agent application delivery | Template ships **steering docs** and feature guides so Kiro (and other assistants) extend it correctly | Repos designed for AI-assisted development | [43](../labs/43-fullstack-agentcore-starter/README.md), [34](../labs/34-e2e-agentic-customer-support/README.md) |

## Which Kiro features show up where

| Kiro capability | Posts | Frequency |
| --- | --- | --- |
| **Skills** (Agent Skills format) | 1, 3, 8 (and Quick/Strands/AgentCore in 3) | ●●● |
| **Steering** | 1, 5, 9 | ●●● |
| **MCP servers** (consume or build) | 2, 4, 7, 8 | ●●●● |
| **Specs / spec-driven development** | 1, 2, 5 | ●●● |
| **Hooks** | 2, 7 | ●● |
| **Custom agents / multi-agent** | 3, 7, 5 | ●●● |
| **Powers** | 2 (mentioned), 6 | ●● |
| **Kiro CLI** | 3, 7, 8 | ●●● |
| **ACP embedding** | 8 | ● |
| **Integration with other AWS agents/services** | 1 (AWS Transform), 2 & 4 (AWS Quick), 3 (AgentCore harness, Quick Desktop), 5 (AgentCore, Strands), 8 (SageMaker AI) | ●●●●● |

The headline finding is that **knowledge-as-files** (skills and steering) is the most-used lever. In posts 1, 3, 5, 8 and 9 the value sits in versioned Markdown that both humans and agents read, and the same files often power several tools: Kiro, AWS Transform, AWS Quick, Strands, the AgentCore harness, Claude Code and Codex.

## Post-by-post notes

### 1 · PHP → Java migration engine (modernization)

- **Problem.** A port that compiles can still behave differently, because rules hide in Eloquent traits, `$hidden` lists and XML mappings.
- **How Kiro is used:**
  - The repo root carries a shared `.kiro/` with two skills, `php-model-discovery` (the scanner) and `php-to-java-migration` (the 8-phase playbook), plus a `core-workflow.md` steering file.
  - Per-project specs live under `.kiro/specs/`.
  - Kiro walks the phases with explicit approval gates.
- **Principles:**
  - Discovery comes before translation: a token-only scanner produces a JSON manifest with `flags[]` as the human review queue.
  - The judge is built before the code: the parity harness must fail on injected breakage.
  - Fix the loop, not the code: amend `RULEBOOK.md` and regenerate.
  - One shared brain serves many projects.
- **Scale.** AWS Transform integrates natively with Kiro and can run the *same skill files* agentically across a portfolio. A rulebook fix in either tool improves both.
- **Honesty worth copying.** The sample states that only 4 of 37 models were ported and that the parity harness wasn't built for that slice ("the single biggest gap").
- **Repo.** [aws-samples/sample-php-to-java-migration](https://github.com/aws-samples/sample-php-to-java-migration) · **Lab:** 39.

### 2 · Smartsheet MCP (work management)

- **Problem.** Plans and code live in different tools, and status drifts.
- **How Kiro is used:**
  - Remote MCP server (`https://mcp.smartsheet.com`; EU and AU endpoints also exist) is added to `.kiro/settings/mcp.json` with a bearer token. OAuth is recommended for production.
  - Prompts like *"check the Backend API sheet for open bugs and generate a prioritized fix list"* and *"pull the Q3 Roadmap sheet and create a spec for features marked In Progress."*
  - **A Kiro hook updates the row to Complete when the fix is committed.**
- **Two audiences.** AWS Quick (pre-built connector, OAuth, org-wide) serves PMs and operations. Kiro (config file and token) serves developers.
- **Governance.**
  - Agents get user-level permissions only.
  - Admins have AI on/off switches and can restrict write tools by group.
  - Firewall allow-listing is by FQDN.
  - No prompt storage.
- **Lab:** 42.

### 3 · HCLS agent skills (healthcare & life sciences)

- **Problem.** Models cite the right framework (ACMG/AMP, CMS-HCC) but misapply it. These are silent failures with patient-safety and regulatory consequences.
- **Solution.** 38 MIT-0 skills across 11 domains, split into *reasoning* skills (methodology) and *pipeline* skills (exact commands and parameters).
- **Results.** Skill-equipped agents won **70–86 %** of head-to-head comparisons, and **78–85 %** on critical thinking (d = 0.65–1.03).
- **How Kiro is used:**
  - `./install.sh --target kiro` installs the skills and a pre-configured agent (`/agent hcls`).
  - `--mode multiagent` gives a **coordinator plus 8 specialists** (`/agent hcls-multiagent`).
  - Loading all 38 skills costs about 80K tokens. Specialists cost about 15K each, which solves both attention dilution and the "which skill do I invoke?" problem.
- **Also runs on** Strands, the AgentCore harness, AWS Quick Desktop, Claude Code and Codex.
- **Verification note.** The post's Strands snippet uses `from strands.skills import AgentSkills`, `Agent(skills=...)` and `MultiAgentOrchestrator`. In `strands-agents` 1.66 the working form is `from strands import Agent, AgentSkills` with `Agent(plugins=[AgentSkills(skills=...)])`, plus agents-as-tools for routing (verified in Lab 41). The post's install line names `awslabs/hcls-agent-skills`, while its links point to `aws-samples/sample-hcls-agent-skills`.
- **Lab:** 41.

### 4 · AI as accessibility (personal productivity)

- **Problem.** For a neurodivergent (AuDHD) architect, organizing work costs far more executive function than the technical work itself, and every productivity tool eventually lapsed into disuse.
- **How Kiro is used:**
  - The author **built a custom MCP server with Kiro** that connects AWS Quick desktop to Outlook, calendar and Asana.
  - Triage rules, priority logic ("Do First / Do Next / If Time") and communication style live in **Markdown files read fresh each session**, so changing a rule needs no redeploy.
- **Outcomes (personal, not benchmarks):**
  - Inbox scans take 6–13 minutes instead of more than 45.
  - Zero follow-ups were dropped in a month.
  - It is the author's longest-ever streak of sticking with a workflow system.
- **Pattern.** Use Kiro to build the integration (the MCP server), put the behaviour in editable Markdown, and keep the cost of starting near zero.
- **Labs:** the MCP server build in 40; rules-as-markdown follows the same idea as steering and skills.

### 5 · AWS ProServe as a frontier team (delivery operating model)

- **Problem.** Most of each engagement went to documentation, coordination and scaffolding.
- **How Kiro is used.** Kiro is one of the tools in the stack with AgentCore and Strands, inside the **ProServe Delivery Agent**: a supervisor with sub-agents for requirements, architecture, implementation, security, testing and deployment. It implements **AI-DLC**, the AI-Driven Development Lifecycle.
- **Five practices:**
  1. Slow down to speed up.
  2. Invest heavily in agent context. Steering files are first-order artifacts.
  3. Feed agents instead of babysitting them: run them in parallel on a backlog of well-scoped tasks.
  4. Use specs as the source of truth.
  5. Shift testing left.
- **Outcome quoted.** LexisNexis reported that weeks of backlog creation became hours and code delivery was 60 % faster.
- **Lesson.** *"The workflow is the constant. Tools are enablers."*
- **Labs:** 38 (platform), 06 (parallel agents), 03 (specs), 02 (steering).

### 6 · Research assistant with Strands (agent development)

- **How Kiro is used:**
  - The **"Build an agent with Strands" power** ([kirodotdev/powers/strands](https://github.com/kirodotdev/powers/tree/main/strands)) gives Kiro SDK docs search and correct API patterns.
  - A detailed natural-language prompt generates a Streamlit + Strands research app of about 30 lines.
- **Note.** The post says there are "over 50 curated powers". Kiro's own one-year retrospective later cites 100+.
- **Pattern.** Ground code generation in a power for the SDK you're using, and be explicit in prompts about the requirements.
- **Labs:** 21 and 08.

### 7 · Kiro CLI + AgentCore Memory (developer productivity)

- **Problem.** The IDE forgets everything between sessions.
- **How Kiro is used.** A custom stdio **MCP server** exposes 10 memory tools (store, search, history, sessions, stats, delete). A **custom agent** (`kiro_memory`) is set as the default with `{"chat.defaultAgent": "kiro_memory"}`. **Hooks** cache the prompt, load preferences and store each conversation.
- **Retrieval.** Semantic search via `retrieve_memory_records` falls back to scanning raw events, so fresh conversations are findable before extraction finishes. Timeframes are supported ("last night").
- **Actor id.** Either the user id (personal) or a project id (team isolation).
- **Repo.** [aws-samples/sample-amazon-bedrock-agentcore-memory-mcp-server](https://github.com/aws-samples/sample-amazon-bedrock-agentcore-memory-mcp-server) · **Lab:** 40 (a compact MCP 2.x version).

### 8 · Model customization in SageMaker AI (ML engineering)

- **How Kiro is used:**
  - Kiro is **pre-configured in the SageMaker Studio JupyterLab chat panel over ACP**.
  - Sign-in is `kiro-cli login --use-device-flow`.
  - The space auto-loads **9 model-customization skills**: use case, planning, fine-tuning setup, dataset evaluation and transformation, fine-tuning, evaluation and deployment.
  - Other ACP agents (Claude Code via `@zed-industries/claude-agent-acp`, Codex, Gemini, OpenCode) get the same skills.
- **Flow.** The agent *plans first*, chooses SFT, DPO or RLVR, generates editable notebooks, evaluates with LLM-as-judge and deploys to SageMaker or Bedrock.
- **Pattern.** Products embed Kiro through ACP and specialize it with skills, with no new agent to build.
- **Lab:** 44.

### 9 · FAST full-stack AgentCore template (agent apps)

- **What.** A CDK template wiring a React app (Amplify Hosting), Cognito, AgentCore Runtime (Strands or LangGraph pattern), Gateway (Lambda tool), Memory, Code Interpreter and Observability.
- **How Kiro is used.** The repo is **"designed for AI-assisted development"**. Steering documents, feature guides and READMEs mean Kiro and other assistants follow the documented patterns when you ask for changes.
- **Pattern.** Make the repo itself the agent's onboarding: put conventions in steering and procedures in guides.
- **Repo.** [awslabs/fullstack-solution-template-for-agentcore](https://github.com/awslabs/fullstack-solution-template-for-agentcore) · **Lab:** 43.

## Cross-cutting lessons

1. **Put expertise in files, not prompts.** Skills and steering are portable, auditable, diffable and shared across tools (posts 1, 3, 5, 8, 9).
2. **Route, then load.** With more than a handful of skills, a skill-free coordinator plus scoped specialists beats one agent holding everything (post 3).
3. **Gate the human judgment early, then let loops run.** Discovery, the referee and the rulebook come first, and phases 4–8 run themselves (post 1). Humans set intent, AI creates, humans verify (post 5).
4. **Build the judge before the work.** Parity harnesses (1), A/B judges (3) and LLM-as-judge evaluations (8) all define "done" in advance.
5. **MCP connects business systems to engineering.** Plans (2), inboxes (4) and memory (7) all arrive as MCP servers, and hooks keep them in sync automatically (2, 7).
6. **Kiro is often one component of a larger AWS agentic system**, alongside AWS Transform, AWS Quick, SageMaker AI and the AgentCore-based Delivery Agent. Shared skill files are what tie them together.
7. **Design repos for agents.** Templates that ship steering get correct AI-assisted changes for free (9).

## Use-case catalogue by role

| Role | Use cases from these posts |
| --- | --- |
| Application developer | Pull tasks and create specs from the project plan (2) · persistent memory in Kiro CLI (7) · scaffold Strands agents with a power (6) |
| Modernization lead | Repeatable, parity-verified language migration; hand off to AWS Transform at scale (1) |
| Domain expert (HCLS, finance, …) | Encode procedures as reasoning and pipeline skills; coordinator-plus-specialist routing (3) |
| ML engineer | Agent-guided SFT / DPO / RLVR with evaluation and deployment from JupyterLab (8) |
| Agent builder | Start from FAST and extend it with Kiro following the template's steering (9) |
| Engineering leader | The AI-DLC operating model: specs, steering, parallel agents, shift-left testing (5) |
| Individual knowledge worker | Build a personal MCP server with Kiro; triage rules in Markdown (4) |
