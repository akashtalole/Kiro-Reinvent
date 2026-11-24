---
name: tenant-isolation-tests
description: Generate and run negative tests proving one tenant cannot read, modify, enumerate or infer another tenant's data across APIs, queues, search, caches, exports and AI features (RAG, memory, agent tools). Use when adding endpoints, data stores, AI features, or before releases of a multi-tenant system.
metadata: { persona: qa }
---
# Tenant isolation tests

For every route and AI capability in scope, build the matrix **actor tenant × target tenant × operation** and assert:

| Operation | Expectation for a cross-tenant attempt |
| --- | --- |
| read / list / search | 403 or 404, with zero items from the other tenant (check counts, not just status) |
| create / update / delete | 403; target unchanged (re-read as the owner) |
| ID guessing | Sequential and UUID ids from tenant B return 404, never 403, so their existence isn't leaked |
| caches | Keys include the tenant id; warm the cache as A, then read as B |
| exports / reports | Files contain only the caller's tenant data |
| **RAG** | A question about B's documents gets "I don't know"; retrieved chunks all have `tenantId = A` |
| **agent memory** | Memory recall as A never returns B's facts |
| **agent tools** | Tool calls with B's ids are denied by policy (log the policy decision) |

Write the tests next to the existing suite, tagged `@isolation`, and run them against dev with two seeded tenants. A failing isolation test blocks the release.
