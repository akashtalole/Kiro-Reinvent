---
name: echo-show-widget-review
description: Review and lint an Alexa+ MCP add-on widget (MCP Apps ui:// HTML) for Echo Show — sandbox rules, hostContext handling, the 768x480 base canvas with one root scale, typography tokens, light and dark mode, declared CSP domains, versioned ui:// URI — and check voice-visual parity. Use when building or reviewing an Echo Show visual for an Alexa+ add-on or before running the Local Inspector.
license: MIT
---
# Echo Show widget review

Alexa+ renders your tool's UI payload on screen devices when the tool declares a `ui://` resource in `_meta.ui.resourceUri`; tools without one are data-only and Alexa renders them natively or by voice.

1. Lint the widget and its tool metadata:
   `python3 scripts/check_widget.py path/to/widget.html --meta path/to/tool-meta.json`
   Fix every `FAIL`; read every `WARN`.
2. Check the design against [references/echo-show-rules.md](references/echo-show-rules.md): one of the four patterns (List, Carousel, Card, Map), glanceable metadata, readable at ~3 ft (essential info at ~10 ft).
3. Check **voice-visual parity** by reading the tool's spoken text next to the widget: no contradictions, nothing critical that is screen-only, and touch does exactly what the voice equivalent does.
4. Run the Alexa+ Local Inspector (`addon-local-inspector <mcp-url>`) for Echo Show 8/15, mobile and voice-only, then verify on a real Echo Show. The inspector needs `resources/read` on the `ui://` URI before the first `tools/call`.
