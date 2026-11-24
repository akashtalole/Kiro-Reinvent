---
inclusion: auto
name: security-review
description: Security review checklist for handlers, auth, input validation and secrets. Use when reviewing or writing code that handles requests, credentials or user data.
---
# Security review checklist

1. Validate and bound every input (size, type, enum).
2. No secrets in code, logs or test fixtures — use AWS Secrets Manager / SSM.
3. AuthZ check happens before any data access.
4. Log request IDs, never request bodies containing PII.
