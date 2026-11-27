---
name: bee-to-spec
description: Turn a Bee conversation (a feature described out loud while wearing Bee) into a Kiro spec requirements.md in EARS form where every requirement cites the transcript moment it came from, then write a follow-up todo back to Bee. Use when the user says "spec this" about a Bee conversation or asks to turn a recording into requirements.
license: MIT
---
# Bee to spec

Requires the Bee MCP server (`bee mcp serve`, after `bee login`) or the Bee API. Only process conversations the user explicitly points at; drop other people's speech.

1. Find the conversation: Bee MCP search, or ask the user which one. Fetch its transcript with the `bee_get_conversation_transcript` tool.
2. Extract the feature, users, rules and edge cases **the speaker actually said**. Don't invent requirements; list open questions instead.
3. Write `.kiro/specs/<feature>/requirements.md` from [assets/requirements-template.md](assets/requirements-template.md). Each acceptance criterion is EARS (`WHEN … THE SYSTEM SHALL …`, `IF … THEN …`, `WHILE …`) and ends with a citation `[bee:<conversation-id>@<mm:ss>]`.
4. Check it: `python3 scripts/check_citations.py .kiro/specs/<feature>/requirements.md`. Fix every reported line.
5. Offer to create a Bee todo such as "Review spec: <feature>" (Bee todos are writable via the API/MCP). Ask before writing.
