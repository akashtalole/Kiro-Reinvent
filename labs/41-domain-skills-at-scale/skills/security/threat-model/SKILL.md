---
name: threat-model
description: Produce a STRIDE threat model for a feature, API or architecture diagram, with ranked mitigations. Use when asked about threats, attack surface, abuse cases, security design review or "is this design secure".
---
# Threat model (STRIDE)

1. List assets, actors and trust boundaries. Draw the data flow as mermaid if none exists.
2. For **each element crossing a trust boundary**, walk S-T-R-I-D-E:
   Spoofing · Tampering · Repudiation · Information disclosure · Denial of service · Elevation of privilege.
3. Score each threat: likelihood (1–3) × impact (1–3). Drop anything that scores below 3 unless it's regulatory.
4. Mitigations must be concrete AWS controls (e.g. "Cognito JWT authorizer with `aud` check", not "add auth").
5. Output: table `id | element | STRIDE | threat | L×I | mitigation | owner`, then the top 3 actions.

Common misses this skill exists to prevent: missing authZ on internal APIs, logs leaking PII, no rate limits on agent-facing tools, prompt injection through user-controlled content reaching tool arguments.
