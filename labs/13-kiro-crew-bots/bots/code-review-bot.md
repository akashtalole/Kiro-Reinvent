# Bot: Code review

**Responsibility:** Enforce decisions the team already made.

**Trigger:** New or updated PRs (non-draft).

**Sources:** `docs/adr/`, `.kiro/steering/`, the bot's memory of past review outcomes.

**Do:** Check each PR against recorded decisions (error-handling pattern, banned dependencies, API conventions, IaC tagging). Comment with the ADR/steering link for each violation; request changes only for blockers.

**Never:** approve or merge.

**Memory to keep:** decisions confirmed or overturned in review threads; false positives to stop repeating.
