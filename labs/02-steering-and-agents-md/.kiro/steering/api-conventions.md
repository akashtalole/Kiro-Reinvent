---
inclusion: fileMatch
fileMatchPattern: ["src/**/*.js", "docs/openapi.yaml"]
---
# API conventions

- Errors: `{ "error": { "code": "SNAKE_CASE", "message": "..." } }` with the right HTTP status.
- Pagination: `?limit=` (max 100) and opaque `?cursor=`; respond with `nextCursor`.
- Timestamps are ISO-8601 UTC strings.
- Reference implementation: #[[file:src/app.js]]
