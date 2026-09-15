# Tiers

Not every project needs every file the kit offers. Tiers scale the ceremony to the size of the project instead of making a solo weekend build carry the same machinery as a twenty-milestone team effort — or letting the twenty-milestone effort get away with the solo build's structure.

## 1. The tier table

| Tier | Files | For |
|---|---|---|
| Lite | `<project>/AGENTS.md`, `<project>/docs/design.md`, `<project>/docs/roadmap.md` with checkboxes, `<project>/docs/decisions/` | Solo, one phase, under ten features. The roadmap is the milestone. |
| Standard | v1's set plus `<project>/docs/CURRENT.md` and the linter | Most projects |
| Full | Standard plus phases, per-area design docs, evidence, profile optional docs | Multi-phase, multi-agent, or regulated |

The linter runs at every tier (`tools/check_docs.py`); what it checks scales with the tier, detailed per tier below.

## 2. Lite in detail

Lite carries three files: `<project>/AGENTS.md`, a single `<project>/docs/design.md`, and `<project>/docs/decisions/` for ADRs. Layered on top is `<project>/docs/roadmap.md`, which — uniquely at this tier — carries checkboxes directly on its milestone entries: there is no separate `<project>/docs/milestones/` directory, because the roadmap *is* the milestone. This fits a solo project with one phase and under ten features, where a full `<project>/docs/plans/` tree and generated indexes would be more process than the work needs.

The linter checks the roadmap's checkboxes against `<project>/docs/decisions/` and the paths the roadmap cites, and skips milestone and plan checks entirely — there is nothing at those layers to check. A project is auto-detected as `lite` when `<project>/docs/milestones/` is absent (`tools/check_docs.py`, the `tier` key in `<project>/docs/.check_docs.toml`).

## 3. Standard in detail

Standard is v1's whole set, plus `<project>/docs/CURRENT.md` and the linter, both new in v2: `<project>/AGENTS.md`, `<project>/CLAUDE.md`, `<project>/DOCS.md`, `<project>/README.md`, `<project>/WORKFLOW.md`, `<project>/GLOSSARY.md`, `<project>/OPEN-QUESTIONS.md`, `<project>/docs/design/` (the design docs the profile lists, `profiles/<name>.md`), `<project>/docs/roadmap.md`, `<project>/docs/decisions/`, `<project>/docs/milestones/`, `<project>/docs/plans/`, and `<project>/docs/evidence/`. This is the tier most projects land on: enough structure to survive several months and more than one contributor, with `<project>/docs/CURRENT.md` bounding read cost (`core/long-horizon.md §7`) and `tools/check_docs.py` catching drift that used to be caught by nobody.

## 4. Full in detail

Full adds what a project needs once it outgrows a single sequence of work: phases, each with its own exit criteria stated in the roadmap (`core/layers.md §1`, `core/long-horizon.md §2`); per-area design docs under `<project>/docs/design/<area>/`, written when each phase becomes `active` rather than all at bootstrap (`core/long-horizon.md §3`); evidence linked from every milestone's exit rather than kept informally; and whichever of the chosen profile's optional docs (`profiles/<name>.md`) the project has actually put to use. This is the tier for multi-phase work, more than a couple of agents in parallel, or anything regulated enough that "we measured it" needs a citable record.

## 5. Promotion rules

Lite promotes to standard when the roadmap passes ten features, or when a second person or agent joins the project — either one means the informal roadmap-as-milestone stops being enough to coordinate on. Standard promotes to full when a second phase is planned, or when one of the profile's optional docs becomes load-bearing rather than aspirational.

Promotion is one feature, not a rewrite: run the relevant templates to generate the files the new tier adds, move the existing checkboxes into their proper home (lite's roadmap checkboxes into real milestone files, for example), and run `python tools/check_docs.py --fix` to regenerate the indexes and confirm nothing the new tier expects is missing.
