# Bootstrap Kit v2 — Design

**Date:** 2026-09-15
**Status:** approved for planning
**Supersedes:** the single-file `PROJECT-BOOSTRAP.md`

## 1. Purpose

The kit helps a human and their AI agents start (or adopt) a software project so that both share one set of design docs, one workflow, and one source of truth for progress. Version 1 was a single 21KB file distilled from one data-driven game. It works well for that shape of project and poorly elsewhere. Version 2 keeps the machinery that is universal, moves the domain-specific parts behind profiles, adds a brownfield path, handles long roadmaps and parallel agents, and ships a working linter instead of a spec for one.

## 2. Goals and non-goals

Goals:

1. Fit every common software project type through a profile chosen at bootstrap.
2. Work for projects with many milestones without producing fantasy roadmaps or unbounded read cost.
3. Work with several agent sessions in parallel without merge conflicts on shared index files.
4. Cover adoption into an existing codebase, not only greenfield.
5. Ship a tested linter that also generates the indexes it checks.
6. Scale ceremony to project size through tiers.

Non-goals for v2:

- Ports of the linter to languages other than Python.
- Integration with issue trackers beyond a mirroring note.
- Any GUI or visual tooling.
- A hosted or packaged distribution. The kit is cloned or read from the repo.

## 3. Repository layout

```
agentic-project-bootstrap/
  README.md                 what this is, how to use it (3 paragraphs)
  BOOTSTRAP.md              the core: idea, machinery, procedure pointers (< 250 lines)
  AGENTS.md                 the kit dogfooding itself
  CLAUDE.md                 "@AGENTS.md"
  core/
    doc-kinds.md            five kinds of document, where each lives, how each changes
    layers.md               phases, milestones, features, plans; ID rules; status vocabularies
    lifecycle.md            Ground / Brainstorm / Plan / Execute / Close; spike and small-change hatches
    long-horizon.md         rolling wave, phase exits, re-planning cadence, moving and splitting rules
    parallel-agents.md      claiming, per-milestone plan directories, generated indexes
    adoption.md             greenfield procedure and brownfield procedure side by side
    tiers.md                lite / standard / full and promotion rules
    lessons.md              lessons from the reference project, extended with v2 lessons
  profiles/
    README.md               how to pick a profile; what every profile shares
    data-driven-product.md
    web-app-saas.md
    library-sdk-cli.md
    data-ml.md
    infra-platform.md
    research-prototype.md
  templates/
    README.md               placeholder glossary: every {{token}} used by templates
    AGENTS.md  CLAUDE.md  DOCS.md  PROJECT-README.md  WORKFLOW.md  GLOSSARY.md
    OPEN-QUESTIONS.md  CURRENT.md  roadmap.md  milestone.md  plan.md
    adr.md  decisions-AGENTS.md  design-header.md  evidence.md
  tools/
    check_docs.py           linter and generator, Python 3.10+, standard library only
    hooks/README.md         settings.json snippet running check_docs on session Stop
    tests/
      test_check_docs.py    pytest
      fixture/              a minimal valid project, plus variants that must fail
  skills/
    bootstrap/SKILL.md      the /bootstrap guided conversation
```

`BOOTSTRAP.md` is the entry point. It states the idea in one page, names the machinery, and points into `core/`, `profiles/`, and `templates/`. It contains no templates itself.

## 4. Document kinds

Five kinds, one job each. The v1 table had four and left the roadmap unclassified.

| Kind | Lives in | Answers | Changes |
|---|---|---|---|
| Design | `docs/design/` | What is this and why is it shaped this way | Rarely, deliberately, with a changelog entry |
| Decision | `docs/decisions/` | Why this over that | Never edited; superseded |
| Direction | `docs/roadmap.md` | In what order, and what each phase must prove | At phase boundaries and milestone reviews |
| Progress | `docs/milestones/`, `docs/plans/`, `docs/CURRENT.md` | What are we building now, what is done | Every session |
| Reference | `DOCS.md`, `WORKFLOW.md`, `GLOSSARY.md`, `AGENTS.md`, `OPEN-QUESTIONS.md` | How we work, what words mean, what is unresolved | When the process changes |

Design docs carry a header with status (`draft | stable | living`) and a `## Changelog` section at the end. A design change during a milestone appends a changelog line in the same commit. Section anchors remain contracts: never renumber, append `§6.1a`.

## 5. Layers and identifiers

Four layers, top to bottom:

1. **Phase** — a group of consecutive milestones with its own exit criteria. Lives only in `roadmap.md`. IDs `P1`, `P2`. A project under the lite tier has one implicit phase.
2. **Milestone** — a goal with a measurable exit. `docs/milestones/M<n>.md`. IDs `M<n>`, allocation order.
3. **Feature** — one line with a checkbox in its milestone. IDs `M<n>-<nn>`.
4. **Plan** — one file per feature. `docs/plans/M<n>/M<n>-<nn>-<slug>.md`.

ID rules:

- IDs are allocated in creation order and never reused or renumbered. Execution order is the roadmap's order, not the ID's.
- A dropped milestone keeps its file with status `dropped` and stays in the index.
- Splitting a milestone: the original keeps its ID and its narrowed scope; the split-off part becomes a new milestone with the next free ID, and the roadmap orders it. A note in both files records the split.
- Inserting a milestone between two others: new ID, placed in the roadmap where it belongs.
- Moving a feature to another milestone: allocate a new ID in the target, mark the old plan `moved to M7-02`, and leave the old feature line struck through with the same pointer. Cross-references to the old ID stay valid because the old plan file remains.

Status vocabularies:

| Object | Statuses |
|---|---|
| Phase | `sketch` · `active` · `done` |
| Milestone | `sketch` · `planned` · `in progress` · `done` · `dropped` |
| Feature | unticked · ticked · struck through with `moved to` |
| Plan | `grounding` · `planned` · `in progress` · `blocked` · `done` · `moved` · `superseded` |
| ADR | `proposed` · `accepted` · `superseded by NNNN` · `rejected` |
| Design doc | `draft` · `stable` · `living` |

Status lives in exactly one place per object. Everything else is generated.

## 6. Long-horizon rules

These rules exist so that a project with twenty milestones is planned as honestly as one with three.

**Rolling wave.** At any time, the current milestone and the next one are `planned` or later: measurable exit, features listed, milestone file present. Everything beyond is `sketch`: a goal in one or two sentences in the roadmap, no milestone file, no exit criteria required. The linter permits `TBD` inside `sketch` sections of the roadmap and nowhere else outside `OPEN-QUESTIONS.md`.

**Phase exits.** Each phase states what it must prove and how it is measured. The design doc's success criteria section is organised by phase, not by "first prototype". Phase 1's criteria are numeric at bootstrap; later phases' criteria are sharpened when the phase becomes `active`.

**Design docs by phase.** Bootstrap writes the vision, the core data model, the architecture skeleton, and one example instance covering phase 1. Each later phase, when it becomes `active`, gets the per-area design docs it needs under `docs/design/<area>/` and a new example instance exercising the new systems. Design docs written before their phase are sketches and say so in their header.

**Re-planning cadence.** The Close step of a milestone's last feature includes a roadmap review: check the milestone's exit with evidence, promote the next `sketch` milestone to `planned` with a real exit, re-order or split if what was learned demands it, and record any reordering with a reason as an ADR. `long-horizon.md` gives the checklist.

**Milestone size.** Three to ten features. The exit must be demonstrable in a single session by someone who did not build it. Larger is split; smaller is folded into a neighbour.

**Dependencies.** Milestone and feature lines may carry `depends on: M3, M4-02`. The linter fails if a `planned` or `in progress` item depends on a `sketch` or `dropped` one, and warns if a plan is `in progress` while a dependency is unticked. Dependencies allow parallel tracks in the roadmap; the roadmap shows tracks as sub-sections under the phase.

**Bounded read cost.** `docs/CURRENT.md` is generated: the active phase, the in-progress milestone(s), each claimed feature with its plan path and last progress note, open blockers, and the most recent evidence. It is under forty lines. Session start reads `AGENTS.md`, then `CURRENT.md`, then the plan. The milestone and roadmap are read only when planning. Done plans stay where they are but are listed in a collapsed section of the generated index.

## 7. Parallel agents

**Claiming.** A feature is claimed by setting its plan status to `in progress` and appending a session stamp line under `## Sessions`: date, agent or tool name, branch. An agent must not start a feature whose plan is `in progress` with a stamp under 24 hours old unless the human says so. The linter flags stamps older than a configurable threshold as stale.

**No hand-edited shared files.** `milestones/README.md`, `plans/README.md`, `decisions/README.md`, and `CURRENT.md` are generated by `check_docs.py --fix` from the individual files. The milestone file's feature checkboxes stay hand-edited because each feature line changes rarely and by one agent; merge conflicts there are one line and trivial.

**Per-milestone plan directories.** `docs/plans/M<n>/` keeps a milestone's plans together and keeps `git status` legible with two hundred plans.

**Decisions do not block by default.** A `proposed` ADR does not block Close unless tagged `blocking: yes`. Humans accept in batches at milestone close, which is listed in the Close checklist.

## 8. Lifecycle and escape hatches

Ground → Brainstorm → Plan → Execute → Close, as in v1, with these changes:

- Ground lists concrete actions and now begins with reading `CURRENT.md`.
- Brainstorm may end in a **spike**: time-boxed throwaway code to answer one question. The spike's question, box, and result are recorded in the plan's Current state (or an ADR if it decided something). Spike code is deleted or re-enters through Plan. Spikes are not committed to `main`.
- Close includes the roadmap review when the feature is the milestone's last, and includes running `check_docs.py --fix`.
- Small changes still skip the plan: reproducing-test bug fixes, typos, no-API dependency bumps. Growth past one commit promotes the change to a feature.
- Experiments (data-ml profile) close as `done` with a recorded negative result; a negative result is evidence, not failure.

## 9. Adoption

`core/adoption.md` gives two procedures.

**Greenfield** is v1's Part C, restructured: C0 decides name, naming convention, example location, tier, and profile. C1–C8 write the design docs the profile calls for, phase 1 only. C9 generates process files from templates. C10 runs the linter. C11 is the first session.

**Brownfield** replaces the writing steps with recovery steps:

1. Inventory: tree, build and test commands, existing docs, open issues, recent history.
2. Reverse-engineer the architecture doc from the code, marked `draft`, with a "confidence" column per module.
3. Recover the data model from schemas, migrations, or types; write one example instance from real data (anonymised).
4. Backfill ADRs from git history and existing docs: every hard-to-reverse choice already made becomes `accepted` with `Date: recovered`.
5. Write the design doc as a vision-and-current-state document; non-goals come from what the team has already declined.
6. Build the roadmap from the issue tracker: current work becomes M1 `in progress`, the backlog becomes `sketch` milestones grouped into phases. Issues stay in the tracker; milestone files cite them, and the note on mirroring says which side is authoritative (the milestone file).
7. Generate process files, run the linter, hold a first session whose feature is "close the gaps the inventory found".

## 10. Tiers

| Tier | Files | For |
|---|---|---|
| Lite | `AGENTS.md`, `docs/design.md`, `docs/roadmap.md` with checkboxes, `docs/decisions/` | Solo, one phase, under ten features. The roadmap is the milestone. |
| Standard | v1's set plus `CURRENT.md` and the linter | Most projects |
| Full | Standard plus phases, per-area design docs, evidence, profile optional docs | Multi-phase, multi-agent, or regulated |

Promotion rules: lite → standard when the roadmap passes ten features or a second person or agent joins. Standard → full when a second phase is planned or a profile's optional doc becomes load-bearing. Promotion is one feature: run the templates, move the checkboxes, run the linter.

The linter runs on all tiers. On lite it checks the roadmap's checkboxes against `docs/decisions/` and cited paths, and skips milestone and plan checks.

## 11. Profiles

Every profile shares the machinery and the reference files. A profile specifies: the design docs to write and their section outlines, vocabulary substitutions for the templates, the default tier, what "example instance" and "evidence" mean, what M0 nearly always is, and the profile-specific non-goals to suggest.

| Profile | Design docs | Example instance | Evidence | Notes |
|---|---|---|---|---|
| data-driven-product | design, data-model, runtime, architecture, tooling, example | one full authored instance | playtests, simulations | v1 unchanged |
| web-app-saas | design (jobs and journeys), data-model, architecture, security-and-privacy, deployment-and-observability | seed fixture for one tenant | usability sessions, load tests | "core loop" becomes "primary journeys" |
| library-sdk-cli | design (audience and API principles), api-surface, architecture, versioning-and-compat | golden usage examples that are also tests | benchmarks, adopter feedback | roadmap by version; milestones map to releases |
| data-ml | design (problem and metric), data-model (datasets and features), experiment-protocol, architecture, model-card | one labelled sample set | eval runs with numbers | features are experiments; negative results close as done |
| infra-platform | design (users and SLOs), architecture, environments, runbooks, security | one environment definition | SLO reports, incident reviews | runbooks are Reference kind |
| research-prototype | design (question and hypotheses), architecture-sketch | one worked example | experiment notes | lite tier; spike-first lifecycle |

## 12. The linter and generator

`tools/check_docs.py`, Python 3.10+, standard library only. Invoked as `check_docs.py [--fix] [--root PATH] [--stale-hours N]`.

Checks, each with a stable error code:

| Code | Check |
|---|---|
| E001 | A cited `path.md` does not exist |
| E002 | A cited `path.md §N.M` has no heading numbered `N.M` |
| E003 | A milestone file is missing from the index or its status differs |
| E004 | An ADR file is missing from its index |
| E005 | `{{`, `TBD`, or the codename placeholder appears outside `OPEN-QUESTIONS.md` or a `sketch` roadmap section |
| E006 | A plan is `done` but its feature is unticked, or ticked with a plan not `done` |
| E007 | A milestone is `done` with an unticked feature or without an evidence link |
| E008 | A `planned` or `in progress` item depends on a `sketch` or `dropped` item |
| E009 | A milestone has no measurable exit but is `planned` or later |
| E010 | A `moved` plan's pointer does not resolve |
| W001 | A claim stamp is older than the stale threshold |
| W002 | A plan is `in progress` with an unticked dependency |
| W003 | A generated file differs from what `--fix` would write |

`--fix` regenerates `milestones/README.md`, `plans/README.md`, `decisions/README.md`, and `CURRENT.md`. Generated files begin with a marker line stating they are generated and by what. `--fix` never touches any other file. Exit code is non-zero on any `E` code, zero otherwise; warnings print but pass.

Configuration: a `docs/.check_docs.toml` with `codename`, `stale_hours`, `allow_tbd_in`, `tier`. Defaults work without a config file; tier defaults to `standard` and is auto-detected as `lite` when `docs/milestones/` is absent. When neither `docs/milestones/` nor `docs/roadmap.md` exists (as in this kit's own repo), only the cross-reference and placeholder checks (E001, E002, E005) run.

Tests: `tools/tests/fixture/valid/` is a minimal standard-tier project that passes. Each error code has a sibling fixture variant that fails with exactly that code. Tests cover `--fix` output equality and idempotence.

Hook: `tools/hooks/README.md` gives a `settings.json` snippet for a Claude Code Stop hook and a pre-commit hook, both running `check_docs.py` and blocking on errors.

## 13. The bootstrap skill

`skills/bootstrap/SKILL.md` runs the greenfield or brownfield procedure as a guided conversation: asks the C0 questions one at a time, picks the profile and tier, then walks the design docs one per session with a human review gate after each, then generates from templates, runs the linter, and opens the first session. It refuses to write more than one design doc per session unless told to, because one-shot bootstraps produce shallow docs.

## 14. Migration of v1

`PROJECT-BOOSTRAP.md` is deleted after its content is redistributed: Part A into `BOOTSTRAP.md` and `core/doc-kinds.md`; Part B into `profiles/data-driven-product.md` and `templates/`; Part C into `core/adoption.md`; Part D into `core/lessons.md`; Part E into `templates/`. Lessons gain entries for the v2 changes, each stated as what went wrong in v1 and what changed.

## 15. Testing and acceptance

The work is done when:

1. `pytest tools/tests` passes and every error code has a failing fixture.
2. Running `check_docs.py` against the kit's own repo passes with zero errors.
3. Running `check_docs.py` against `tools/tests/fixture/valid` after `--fix` produces no diff.
4. Every `{{token}}` used in `templates/` is listed in `templates/README.md`.
5. Each profile lists its design docs and vocabulary substitutions.
6. `BOOTSTRAP.md` is under 250 lines and every path it cites exists.
7. `PROJECT-BOOSTRAP.md` is gone and nothing cites it.

## 16. Deferred

Two items are deferred to a later version. Generated indexes are committed in v2 so an agent without the tool still has them; gitignoring them is reconsidered later. A `check_docs.py --claim M3-04` helper is deferred because the plan-file edit is enough for now.
