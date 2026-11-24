# Bot: Build health

**Responsibility:** Separate real CI failures from noise.

**Trigger:** Every 30 minutes, `main` and release branches.

**Do:**
1. Fetch failed workflow runs since the last check.
2. Compare failing tests against the known-flaky list kept in memory.
3. New failures → open/append a thread with the failing job, first failing commit, suspected cause.
4. Repeat flakes (≥3 in 7 days) → propose adding them to the quarantine issue; do not quarantine yourself.

**Never:** re-run jobs more than once, edit workflows, push commits.

**Hand-off:** Silent when green. One message per new failure.
