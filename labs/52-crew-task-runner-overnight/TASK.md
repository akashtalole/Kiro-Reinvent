# Add `GET /orders/{id}/history` to the orders service

## Goal
Customers and support staff need to see every status change of an order, newest first.

## Context
- Service code: `src/orders/` (TypeScript, Express). Tests: `npm test` (Vitest).
- Status changes are already written to the `order_events` table by `src/orders/events.ts`.
- Follow the existing handler, validation and error patterns in `src/orders/routes.ts`.

## Requirements
1. `GET /orders/{id}/history` returns `[{status, at, actor}]` sorted by `at` descending.
2. Supports `?limit=` (default 20, max 100) and an opaque `?cursor=` for pagination.
3. Returns 404 when the order does not exist and 403 when the caller's tenant does not own it.
4. Adds the endpoint to `docs/api.md` with one request/response example.
5. No new runtime dependencies.

## Acceptance criteria
- Unit tests cover sorting, both limits, cursor round-trip, 404 and 403.
- `npm test` and `npm run lint` pass.
- The handler never reads the tenant from the request body; it uses the authenticated context.

## Out of scope
- UI changes. Deploying anything. (Any deploy or publish step must be marked force approval.)
