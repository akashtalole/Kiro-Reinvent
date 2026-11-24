---
name: sql-review
description: Review SQL queries and schema changes for correctness, performance and safety (indexes, joins, N+1, locking, migrations). Use when writing, reviewing or optimizing SQL, migrations, or when a query is slow.
---
# SQL review

Check in this order and report only failures:

1. **Correctness:** join cardinality (does a 1:N join inflate SUM/COUNT?), NULL semantics in `NOT IN`/comparisons, time zones, off-by-one date ranges (`< next_day` not `<= 23:59:59`).
2. **Performance:** predicates are sargable; supporting index exists (show `CREATE INDEX`); no `SELECT *` in hot paths; pagination by keyset, not `OFFSET` on large tables.
3. **Safety:** parameterized queries only; migrations are backwards compatible (expand → migrate → contract); long-running `ALTER` uses online DDL; no table rewrite under lock in peak hours.
4. Ask for `EXPLAIN (ANALYZE, BUFFERS)` output before claiming a performance fix.
