# Troubleshooting

## Kiro

| Symptom | Fix |
| --- | --- |
| Custom agent ignores steering or skills | Custom agents don't inherit them. Add `"resources": ["file://.kiro/steering/**/*.md", "skill://.kiro/skills/*/SKILL.md"]` |
| CLI V3 skips an old agent profile | It uses `allowedTools` / `toolsSettings`. Run `/upgrade-agent` |
| Hook never fires | Hooks load at session start, so restart. Check the `trigger` spelling against the [trigger reference](https://kiro.dev/docs/hooks/types/) and test the `matcher` regex |
| Hook blocks everything | Your script exits 2 on every input. Pipe sample JSON into it by hand |
| Skill not discovered | The folder name must equal `name`, and `SKILL.md` must sit in a subfolder of `.kiro/skills/`. Make the description say "Use when …" |
| Power never activates | Its `keywords` are too specific or never appear in chat |
| MCP server shows as failed | Run `/mcp` to see the error. Check that `uvx` is on PATH, the credentials/profile, and `timeout` |
| Headless run hangs | A tool needs approval. Use `--trust-tools` or an agent with explicit `permissions` |

## AWS MCP

| Symptom | Fix |
| --- | --- |
| `AccessDenied` from AWS MCP Server | Your IAM principal lacks the action. That's expected for read-only roles |
| Duplicate tools | Remove the local `aws-api` / `aws-knowledge` servers when you use the managed AWS MCP Server |
| Serverless MCP can't deploy | Start it with `--allow-write` (dev only) |

## Strands / AgentCore

| Symptom | Fix |
| --- | --- |
| `AccessDeniedException` on model invoke | Enable model access in the Bedrock console for your region. Check the model or inference-profile id |
| `ModuleNotFoundError: a2a` | `pip install 'strands-agents[a2a]'` |
| `code_interpreter was removed` | Use `bedrock_agentcore.tools.code_interpreter_client` (Lab 31) |
| Runtime invoke 4xx | `runtimeSessionId` must be ≥ 33 chars, and the payload must be JSON bytes. For JWT runtimes, send a bearer token |
| Gateway 401 | Token audience or client isn't in the authorizer's `allowedClients`, or the token expired |
| Memory returns nothing | Long-term extraction is asynchronous, so wait about a minute. Namespace templates must match those used at creation |
| Policy denies everything | Cedar is deny-by-default. Start in `LOG_ONLY` and check the generated entity and action names |
