---
name: migration-engine
description: Run a repeatable, parity-verified language or framework migration (e.g. PHP→Java, Python 2→3, .NET Framework→.NET, monolith→service) as a nine-phase workflow with discovery, a parity harness, a rulebook and approval gates. Use when asked to migrate, port, rewrite or translate an application or module to another language or framework.
license: MIT
metadata:
  inspired-by: "AWS ML Blog — Build a repeatable PHP-to-Java migration engine with Kiro (Oct 2026)"
  version: "1.0"
---
# Migration engine

Run the phases in order. **Stop at every gate** and summarise the deliverable for human sign-off.

| Phase | Name | Deliverable | Gate |
| --- | --- | --- | --- |
| 0 | Assess & discover | Discovery manifest (JSON) + inventory + cut-over choice | Human resolves every `flags[]` item |
| 1 | Build the judge | Parity harness that replays recorded request/response pairs against legacy *and* target | Harness passes on legacy, **fails on injected breakage** |
| 2 | Rulebook + gaps | `RULEBOOK.md` (mapping rules), `GAP_INVENTORY.md` (known, approved differences) | Rulebook approved |
| 3 | Stress-test rulebook | Rulebook hardened on 3–5 representative files | No new rule needed for 2 consecutive files |
| 4 | Scaffold | Target project that compiles/starts | Build green |
| 5 | Data model | Entities + schema baseline generated **from the manifest** | Schema diff reviewed |
| 6 | I/O layer | Routes→controllers, middleware→filters, validation→DTOs | Harness: I/O cases pass |
| 7 | Business logic | Converted in batches; tests green | Harness: ≥ 95 % pass, rest in gap inventory |
| 8 | Prove parity & cut over | Parity report + cut-over checklist | Human go/no-go |

## Rules

1. Run the discovery scanner first (`scripts/` in the project or the language-specific scanner named in [references/frameworks.md](references/frameworks.md)). Translate **from the manifest**, not from reading files.
2. Use the harness at `parity/parity_harness.py` (or the project's equivalent) as the referee. Run `--self-test` in Phase 1 to prove it catches breakage.
3. When a mismatch recurs, add or modify a rule in `RULEBOOK.md` using [references/rulebook-template.md](references/rulebook-template.md), then regenerate the affected files.
4. Record every intentional difference in `GAP_INVENTORY.md` with the reason and the approver.
5. Never mark a phase done while the harness has unexplained failures.
