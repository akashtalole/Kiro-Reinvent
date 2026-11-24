---
inclusion: always
---
# Structure

- `src/` application code — one file per route group.
- `test/` mirrors `src/`.
- `infra/` CDK app; stacks are named `<Service><Env>Stack`.
- `docs/` OpenAPI and ADRs (`docs/adr/NNNN-title.md`).
