---
name: alexa-addon-preflight
description: Pre-flight checks for an Alexa+ MCP add-on before alexa-ai deploy — validate addon.json limits (name, descriptions, example phrases, icon sizes, image formats) and probe the MCP endpoint's unauthenticated behaviour (401 with no WWW-Authenticate header, RFC 9728 metadata). Use when you are about to run alexa-ai deploy or when an add-on is rejected.
license: MIT
---
# Alexa+ add-on pre-flight

Alexa+ refreshes tool information **only on deploy**, so catch problems first.

1. Validate the manifest: `python3 scripts/check_addon.py addon-package/addon.json`. Fix every `FAIL`.
2. Probe the endpoint (no credentials): `python3 scripts/check_addon.py --probe https://<your-mcp-host>/mcp`. Expect `401` **without** a `WWW-Authenticate` header and a reachable `/.well-known/oauth-protected-resource`.
3. Confirm the server speaks MCP **2025-11-25** over **Streamable HTTP** (not legacy SSE) and that p95 tool latency is under 500 ms in your metrics.
4. Only then run `alexa-ai deploy`. Never put tokens in addon.json or in chat.

Limits checked (from the Alexa+ MCP QuickStart): name ≤ 30 chars, short description ≤ 123, full description ≤ 4000, 3–4 example phrases of ≤ 200 chars, light icons in all six sizes (72, 64, 88, 126, 180, 241), at least one 600×900 carousel image, HTTPS image URIs in PNG/JPG/JPEG/WEBP.
