---
name: serverless-review
description: Review AWS serverless code and IaC (Lambda, API Gateway, SQS, EventBridge, DynamoDB, Step Functions) against Well-Architected serverless best practices. Use when reviewing or writing Lambda handlers, CDK/SAM/CloudFormation for serverless apps, or when asked about timeouts, retries, idempotency, concurrency or cold starts.
license: MIT
metadata:
  author: kiro-reinvent-labs
  version: "1.0"
---
# Serverless review

## When invoked
1. Run `python3 <this skill folder>/scripts/scan_template.py <path-to-synthesized-template.json>` if a CloudFormation/CDK template exists (`npx cdk synth --json > /tmp/t.json` first for CDK).
2. Read the handler code for each function the script lists.
3. Check every item in [references/checklist.md](references/checklist.md). Only report items that fail or are unknown.

## Output
A table: `severity | resource / file:line | finding | fix`, then a 3-line summary.
Severity: **blocker** (data loss, security), **major** (reliability, cost), **minor** (style).

## Rules of thumb
- SQS → Lambda: visibility timeout ≥ 6× function timeout; use `ReportBatchItemFailures`.
- Every async path needs a DLQ or on-failure destination.
- Idempotency for anything triggered by at-least-once delivery.
- Never `*` in IAM actions for data-plane access.
