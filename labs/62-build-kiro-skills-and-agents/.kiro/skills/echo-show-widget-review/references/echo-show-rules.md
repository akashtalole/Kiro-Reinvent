# Echo Show widget rules (Alexa+ add-on design guide)

Sources: Layout and Rendering, Visual Foundations, Components and Patterns, Functional Requirements, Local Inspector (developer.amazon.com/docs/alexaplus/add-ons/).

## Packaging and runtime
- One **single HTML file**, served from a **versioned** `ui://…/widget-<hash>.html` URI; gzip recommended.
- Tool metadata: `_meta.ui.resourceUri` points at it; `_meta.ui.csp` declares `connectDomains` (fetch/XHR/WebSocket) and `resourceDomains` (images/media). Alexa blocks anything not declared.
- Sandboxed, opaque-origin iframe: no `window.parent`, no cross-origin reads, no `localStorage` / cookies. The MCP Apps **postMessage bridge** is the only channel to the host.
- `hostContext` (deviceClass, maxWidth, maxHeight, isMobile, platform, displayMode, safeAreaInsets, deviceCapabilities, theme): resolve once at render; re-resolve on `host-context-changed`. `deviceClass` is authoritative.

## Layout and look
- Author at a **768×480 base canvas** and apply **one root scale** (Echo Show 8 and 15 render 1280×800: `zoom: 1.667`).
- Prefer the **Block** viewport (wider than tall) for native Alexa+ designs.
- Type tokens (px): 48, 40, 32, 28, 24, 20, 18, 16, 14, 12, 10, 8. Spacing: 2, 6, 8, 12, 16, 20, 24. Radii: 4, 8, 12, 16, 9999. Icons: 16, 20, 24.
- Light and dark mode both supported and tested; no saturated backgrounds; works with colour correction and inversion. Dark card `#14181E` (inner `#1B2028`); light card `#FFFFFF`.
- Readable at ~3 ft; essential information legible at ~10 ft.

## Patterns (don't invent others)
- **List** · **Carousel** (3–5 items inline, first item within 500 ms) · **Card** (one entity; tap = navigate; CTAs only for task-completing actions) · **Map** (compact by default: map + 3 ranked results; expanded 4–6).
- Account linking and checkout are Alexa's; don't build UI for them.

## Functional requirements on screen devices
- TTS and screen never contradict; visuals update with the voice turn (no stale previous-turn content); critical info is also available by voice.
- No blank screens, broken layouts or missing images; tapping equals the voice equivalent; nothing stays interactive after the session ends.
- Results within 3 seconds (send an interim "still working" message if slower).
- Works with VoiceView (screen reader).
