---
inclusion: fileMatch
fileMatchPattern: "site/**/*"
---
# Editing the static site

- Plain HTML + one `site.css` + small IIFE scripts using `window.KRL` helpers (`getJSON`, `esc`, `labCard`, `labHref`). No frameworks, no build step.
- Escape every data value with `K.esc()` before inserting HTML. Never nest `<a>` inside a card that is itself an `<a>`.
- Filters keep state in the URL (`?product=…&level=…`) with `history.replaceState`, and render chip rows with `aria-pressed`.
- Must work at 390 px wide with no horizontal scroll, in light and dark themes.
- After changes, run the build and a Playwright check against the GitHub Pages path prefix `/Kiro-Reinvent/`.
