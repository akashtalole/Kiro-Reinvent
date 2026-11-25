---
inclusion: fileMatch
fileMatchPattern: "labs/**/*"
---
# Writing or editing a lab

Follow #[[file:docs/authoring.md]] exactly. The front-matter fields are `id`, `title`, `category`, `level`, `duration`, `summary`, `services`, `tags`, optional `popular` and `products`.

- `category` must be one of the categories in `scripts/build_site.py`; `level` is Beginner | Intermediate | Advanced.
- `services` drives the Product filter. Name products the way the site does (`Kiro CLI`, `Kiro Crew`, `AgentCore Runtime`, `Amazon Bedrock`). Quote list items that contain commas.
- Sections in order: Outcome → Scenario + mermaid → How it works → Steps → Verify (checkboxes) → Clean up (if anything bills) → Learn more (official docs first, then the next lab).
- Mermaid: keep edge labels free of `.` in dotted-edge shorthand; use `-.->|label|` instead.
- Commands, flags, config keys and file formats must come from official docs or the product's source. Never invent them. If you couldn't verify one, say so in the lab.
- Verify assets you add: `python -m py_compile`, `bash -n`, `python -m json.tool`, `cdk synth`, and record what you verified.
- Link other labs as `../NN-slug/README.md` and docs as `../../docs/name.md`.
