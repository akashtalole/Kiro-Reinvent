---
inclusion: always
---
# Migration core workflow (shared brain)

- The **legacy application is the specification**. The port is done only when the parity harness agrees, or when each mismatch is logged as an approved change in `GAP_INVENTORY.md`.
- **Discovery before translation.** Never read, guess at or hand-translate a model/entity file before the discovery scanner has produced the manifest. Ambiguities go to the manifest's `flags[]` review queue for a human.
- **Build the judge before the code.** Phase 1 builds the parity harness. It must pass against the legacy app *and* fail when a breakage is injected deliberately. A harness that misses injected breakage is not trusted.
- **Fix the loop, not the code.** When the same mistake appears in more than one file, amend `RULEBOOK.md` and regenerate. Don't hand-patch.
- Each phase ends at an **approval gate**. Stop and ask for sign-off before starting the next phase.
- Per-project specs live in `.kiro/specs/<project>-migration/`. Methodology lives only in `.kiro/skills/migration-engine/`.
