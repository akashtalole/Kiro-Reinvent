# Useful CloudWatch Logs Insights queries for agents

Traces/spans from AgentCore (and any OTel-instrumented agent sending to CloudWatch) land in `aws/spans`.

## Slowest tool calls (last 24 h)
```
fields @timestamp, attributes.`gen_ai.tool.name` as tool, durationNano / 1e6 as ms
| filter ispresent(attributes.`gen_ai.tool.name`)
| stats avg(ms) as avg_ms, pct(ms, 95) as p95_ms, count() as calls by tool
| sort p95_ms desc
```

## Token usage per session
```
fields attributes.`session.id` as session, attributes.`gen_ai.usage.input_tokens` as tin, attributes.`gen_ai.usage.output_tokens` as tout
| filter ispresent(tin)
| stats sum(tin) as input_tokens, sum(tout) as output_tokens by session
| sort input_tokens desc | limit 20
```

## Tool errors
```
fields @timestamp, attributes.`gen_ai.tool.name` as tool, status.code, status.message
| filter status.code = "ERROR" and ispresent(tool)
| stats count() by tool, status.message
```

Attribute names follow the OpenTelemetry GenAI semantic conventions; verify them against a sample span in your account.
