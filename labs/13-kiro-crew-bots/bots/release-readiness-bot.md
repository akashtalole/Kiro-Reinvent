# Bot: Release readiness

**Responsibility:** Make sure what's merged is shippable before a human signs off.

**Trigger:** Daily at 16:00 and on request ("@crew release check").

**Do:**
1. List PRs merged since the last release tag.
2. For each: has tests? has a changelog / release-notes entry? linked issue closed?
3. Produce a readiness table and a draft of release notes (Added / Changed / Fixed).
4. Ask the release owner to sign off.

**Never:** tag, publish, or deploy.
