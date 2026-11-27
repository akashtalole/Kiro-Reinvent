---
name: ring-webhook-verifier
description: Verify, replay and debug Ring Partner API webhooks — check the X-Signature HMAC-SHA256 over the raw body, dedupe on meta.request_id, and explain why a delivery was rejected. Use when building or debugging a Ring webhook endpoint, writing tests for it, or replaying a saved delivery.
license: MIT
---
# Ring webhook verifier

Ring signs each webhook with HMAC-SHA256 over the **raw request body** using your app's signing key, sent as `X-Signature: sha256=<hex>`. You must verify before parsing, answer within 5 seconds, and dedupe on `meta.request_id` (Ring retries up to 6 times).

1. **Verify a saved delivery** (body file + header value, key from the environment, never from chat):
   `RING_SIGNING_KEY=… python3 scripts/verify.py samples/body.json "sha256=<hex>"`
   Exit 0 = valid, 1 = invalid. It prints the expected signature prefix only, never the key.
2. **Make a signed test fixture** for unit/property tests: `python3 scripts/verify.py --sign samples/body.json`.
3. **Review the endpoint code** against [references/checklist.md](references/checklist.md) and report each item as pass/fail with file:line.
4. Never log the signing key, full tokens, or snapshot URLs (they are pre-signed).
