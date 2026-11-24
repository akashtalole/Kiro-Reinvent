---
name: ticket-to-repro
description: Convert a customer support ticket into a reproducible bug report with tenant context, redacted PII, logs and traces, known-issue matches and severity. Use when support escalates a ticket to engineering or asks "is this a bug".
metadata: { persona: support }
---
# Ticket → reproduction

1. Redact PII from the ticket (emails, names, phone numbers, payment data) before doing anything else.
2. Identify the tenant, tier, region, time window and feature. Pull the logs and traces for **that tenant only** in that window.
3. Search open and closed issues for matches. If one matches, link it and stop.
4. Write the bug: steps to reproduce (using a test tenant, never the customer's), expected vs actual, evidence (trace ids), severity (tenants affected × business impact), and a suggested owner.
5. Draft a customer reply that is empathetic and specific, with no internal details. A human sends it.
