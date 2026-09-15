# AGENTS.md

This repository is the bootstrap kit itself — `core/`, `profiles/`, `templates/`, and
`tools/check_docs.py` — not a project built on the kit. Read `BOOTSTRAP.md` first: it states
the idea, names the machinery, and points into the rest of this repo.

## Rules

- Every path any doc here cites must exist, and every `§N` cited must be a real numbered
  heading. Run `python tools/check_docs.py --root .` before ending a session — zero errors,
  always.
- Templates (`templates/*.md`) keep the exact field formats `tools/check_docs.py` parses:
  status lines, ID forms, checkbox syntax. Changing a template's shape without updating the
  linter breaks every project that copies it.
- A change to what the linter checks adds a test to `tools/tests/test_check_docs.py` and, where
  the change needs one, an edit to a fixture under `tools/tests/fixture/`.
- No double-brace placeholders outside `templates/`. Elsewhere, a name that isn't fixed yet is
  written `<angle-bracketed>`.
- Section numbers (`## N. Title`) are contracts once another doc cites them — append a lettered
  section rather than renumbering.

## Commands

- `python -m pytest tools/tests -q` — the linter's own test suite.
- `python tools/check_docs.py --root .` — lint the kit's own docs; must report zero errors and
  zero warnings.
