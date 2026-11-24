# Serverless checklist (abridged from the Well-Architected Serverless Lens)

## Reliability
- [ ] Timeouts set explicitly; API-facing functions ≤ 29 s
- [ ] SQS visibility timeout ≥ 6 × function timeout
- [ ] DLQ / on-failure destination for async invokes, SQS, EventBridge targets
- [ ] Partial batch response enabled for SQS/Kinesis/DynamoDB streams
- [ ] Idempotency keys for at-least-once sources
- [ ] Reserved concurrency for functions protecting downstream systems

## Security
- [ ] One IAM role per function, least privilege, no `*` data-plane actions
- [ ] Secrets from Secrets Manager / SSM, never env-var plaintext
- [ ] API auth (IAM, Cognito, Lambda authorizer) on every route
- [ ] Encryption at rest with KMS for queues/tables holding PII

## Performance & cost
- [ ] Memory tuned (Lambda Power Tuning) — not left at 128 MB by default
- [ ] arm64 (Graviton) where dependencies allow
- [ ] Log retention set (not "never expire")
- [ ] DynamoDB on-demand vs provisioned chosen deliberately

## Operations
- [ ] Structured logs with request IDs (Powertools for AWS Lambda)
- [ ] Alarms on errors, throttles, DLQ depth, iterator age
- [ ] X-Ray / OpenTelemetry tracing enabled
