# Tenant-scoped CloudWatch Logs Insights queries

Use them in CloudWatch / CloudWatch Omni, or let Kiro run them (`aws logs start-query`). Replace `t-acme01`.

## Errors for one tenant (last hour)
```
fields @timestamp, @message, TenantId, Feature, requestId
| filter TenantId = "t-acme01" and (level = "ERROR" or statusCode >= 500)
| sort @timestamp desc | limit 100
```

## Noisy neighbours: share of requests per tenant (5-minute buckets)
```
filter ispresent(TenantId) and ispresent(Requests)
| stats sum(Requests) as req by TenantId, bin(5m) as t
| sort req desc | limit 20
```

## AI tokens per tenant per feature (billing check)
```
filter ispresent(AITokens)
| stats sum(AITokens) as tokens by TenantId, Feature
| sort tokens desc
```

## p95 latency by tier (is premium actually faster?)
```
filter ispresent(LatencyMs)
| stats pct(LatencyMs, 95) as p95 by Tier, Feature
```

## Agent traces for one tenant (spans carry tenant.id)
```
fields traceId, name, durationNano/1e6 as ms, attributes.`tenant.id` as tenant
| filter attributes.`tenant.id` = "t-acme01"
| sort ms desc | limit 50
```
(Run against `aws/spans`.)
