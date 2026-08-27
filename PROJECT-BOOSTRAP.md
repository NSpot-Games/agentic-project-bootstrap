# PROJECT-BOOTSTRAP.md

A reusable kit for starting a project so that humans and AI agents (Claude Code, Codex, others) share one set of design docs, one workflow, and one source of truth for progress. Paste this file into a fresh agent session and say: *"Bootstrap a project from this file. Name: X. One-line idea: Y."* — or follow it by hand.

It was distilled from bootstrapping an AI-NPC detective game; everything project-specific has been removed. Part D records what was learned doing it.

---

## Part A — The idea in one page

**Docs are the contract with your agents.** An agent's session has no memory; what it knows about the project is what it can read. If the docs are complete, current, and consistent, every session starts grounded. If they aren't, every session starts by guessing.

**Four kinds of document, each with one job:**

| Kind | Lives in | Answers | Changes |
|---|---|---|---|
| **Design** | `docs/design/` | What is this and why is it shaped this way | Rarely, deliberately |
| **Decision** | `docs/decisions/` | Why this over that | Never edited; superseded |
| **Progress** | `docs/milestones/`, `docs/plans/` | What are we building now, what's done | Every session |
| **Reference** | `DOCS.md`, `WORKFLOW.md`, `GLOSSARY.md`, `AGENTS.md` | How we work, what words mean | When the process changes |

**Three layers of work:** roadmap (narrative order) → milestones (features with checkboxes, the source of truth for progress) → plans (one per feature: grounding, approach, tasks with checkboxes, progress notes — the handoff between sessions).

**Five-step feature lifecycle:** Ground → Brainstorm → Plan → Execute → Close. No code before a plan. No ticked box without verification evidence.

**One instruction file for all agents:** `AGENTS.md` at the root is canonical; `CLAUDE.md` is `@AGENTS.md`; nested `AGENTS.md` files scope rules to subtrees.

## Part B — Target structure

```
{{project}}/
  AGENTS.md              canonical agent instructions (< 120 lines)
  CLAUDE.md              "@AGENTS.md" and nothing else
  DOCS.md                map of docs/ and the rules for it
  README.md              one paragraph for humans + pointer to DOCS.md
  .gitignore
  docs/
    design/
      {{product}}-design.md      vision, pillars, core loop, systems, non-goals, open questions, success criteria
      {{core}}-data-model.md     the central schema, with validation rules
      {{runtime}}.md             how the data model becomes behaviour at runtime
      architecture.md            modules, boundaries, interfaces, hard-to-reverse decisions
      {{tooling}}.md             internal tools (authoring, simulation, admin) if any
      example-{{instance}}.md    a full real instance of the data model + the gaps it surfaced
    roadmap.md                   milestones in order, principles, deferred list. No checkboxes.
    WORKFLOW.md                  feature lifecycle, session handoff, templates
    GLOSSARY.md                  the project's words, grouped by area, with ID prefixes
    OPEN-QUESTIONS.md            every open question in one place, each with a deadline and owner
    decisions/
      AGENTS.md                  how to write ADRs; backfill list
      README.md                  ADR index
      NNNN-*.md                  one decision each
    milestones/
      README.md                  index with status
      M<n>.md                    goal, exit criteria, evidence, features as checkboxes
    plans/
      README.md
      M<n>-<nn>-*.md             one per feature
    evidence/                    playtest write-ups, benchmark numbers, reports (linked from milestones)
  tools/
    check_docs.{{ext}}           doc linter: cross-refs resolve, indexes current, no stale statuses
```

Not every project needs every design doc. Small projects merge `runtime` into `architecture` and skip `tooling`. Keep `design`, `data-model`, `architecture`, `example-instance`, `roadmap` — those five earn their place everywhere.

## Part C — Bootstrap procedure

Do these in order. Each step is a conversation with an agent (or yourself) that ends in a file. Do not skip ahead to code.

### C0. Decide three things before writing anything
1. **Project name and codename.** Changing it later touches every file.
2. **File naming convention.** Recommended: kebab-case, unnumbered, reading order stated in `DOCS.md`. Numbered prefixes look tidy and then break every cross-reference the first time you reorder. Whatever you pick, pick it now.
3. **Where the example instance lives** (e.g. `cases/<id>/`, `fixtures/`, `examples/`). The architecture doc will cite it.

### C1. Brainstorm the product (conversation, no file yet)
Cover: what it is, who it's for, what makes it compelling, what's hard, what the options are, what you won't build. Push on the hardest technical constraint early — it usually shapes the architecture. Write nothing down yet except a list of decisions made and questions left open.

### C2. `docs/design/{{product}}-design.md`
The "why". Sections that proved essential: one-liner; the user's core experience; 3–5 pillars (used as tiebreakers later); core loop at multiple timescales; what the user can do (a table); systems; the centrepiece moment and the rules that manufacture it; fairness/difficulty; retention; **non-goals for v1**; open questions; **success criteria for the first prototype** (measurable). Make concrete default decisions and list what you left open — vague docs produce vague code.

### C3. `docs/design/{{core}}-data-model.md`
The central schema. Principles first (what is authoritative, what is derived, what must be validatable), then the full structure with an annotated example of every collection, then a small expression language if behaviour is data-driven, then **validation rules as a numbered list** (these become the validator), then versioning and ID immutability. Use typed ID prefixes.

### C4. `docs/design/example-{{instance}}.md`
**Write a complete, real instance in the actual schema — before the runtime or architecture docs.** This is the highest-value step in the whole kit. It will expose every field the schema is missing, every ambiguity in the expression language, every place the design doc hand-waved. Record the gaps in a numbered "schema gaps" section and fold them back into the data model doc. Run a script that parses the instance and checks every cross-reference resolves.

### C5. `docs/design/{{runtime}}.md`
How data becomes behaviour. State the one rule that must never be broken at the top. A numbered pipeline diagram. Exact state shapes. Deterministic tables where behaviour is tunable. The contract with any external component (model, service) as a schema. Validation and fallback. Telemetry event names. Open questions.

### C6. `docs/design/architecture.md`
Repo layout (packages, apps, backend), one line per module, the key interfaces as code, data flow for the main operation with a latency budget, persistence, offline/failure behaviour, testing strategy, security, a **"decisions we're committing to"** list, open questions.

### C7. `docs/design/{{tooling}}.md` (if any)
Internal tools. Include a **build order** that says what not to build first.

### C8. `docs/roadmap.md`
Milestones in order, each with a goal and a measurable exit. Principles at the top. An **"explicitly deferred"** list. An open-decisions table with deadlines. No checkboxes.

### C9. Process and reference files
Generate from the templates in Part E: `WORKFLOW.md`, `DOCS.md`, `GLOSSARY.md` (built by scanning the design docs for every defined term), `OPEN-QUESTIONS.md` (collected from every doc's open-questions section), `decisions/AGENTS.md` with a **backfill list** of decisions already stated in the design docs, `decisions/README.md`, `milestones/M*.md` generated from the roadmap, `milestones/README.md`, `plans/README.md`, root `AGENTS.md`, `CLAUDE.md`, `README.md`.

### C10. Consistency pass
Run the doc linter (or a grep): every cited filename exists, every `§` section exists, no leftover codename placeholders, indexes match folders. Fix before the first agent session. Then create ADRs 0001–00NN from the backfill list.

### C11. First session
Open `milestones/M0.md`, take feature `M0-01`, and follow `WORKFLOW.md`. M0-01 is nearly always "fold the schema gaps from the example instance into the data model".

## Part D — Lessons and improvements

Things learned bootstrapping the reference project, and improvements over what it did.

1. **Write the example instance early.** It found ten schema gaps in one sitting. Nothing else came close.
2. **Decide naming before writing.** The reference project wrote seven docs with numbered names, then moved to `design/` unnumbered, breaking every cross-reference. Cost: a full consistency pass.
3. **Decide the codename before writing.** Same reason. `{{placeholder}}` churn touches every file.
4. **Add a doc linter on day one.** A script that checks cross-references, section anchors, index freshness, and placeholder leftovers, run in CI and by agents before ending a session. Drift is inevitable; detection shouldn't be manual. Spec: for every `path.md §N.M` in any doc, the file exists and has a heading numbered `N.M`; every milestone in `milestones/` is in its README with the same status; every ADR is in its index; no `{{` or `TBD` outside `OPEN-QUESTIONS.md`.
5. **One open-questions file.** The reference project scattered them across six docs' final sections; the ADR guide had to re-list them. Collect them in `OPEN-QUESTIONS.md` with owner and deadline; each doc's section becomes a one-line pointer.
6. **`docs/evidence/` from the start.** Exit criteria say "measured"; there needs to be a place for the measurement.
7. **Root `README.md` for humans.** Agents read `AGENTS.md`; a person landing on the repo needs three sentences and a link.
8. **Make "Ground" concrete.** "Understand the current state" produces plans against imagined code. List the actions: read these files, grep ADRs, run tests, inspect these packages, write findings before brainstorming.
9. **Verification evidence in the plan.** A ticked box with no pasted test output is a claim, not a fact. The template has a verification log for this reason.
10. **Escape hatch for small changes.** Without it the process is ignored the first time someone fixes a typo.
11. **Nested `AGENTS.md` for subtrees.** Codex applies them automatically; Claude Code can be pointed at them. Use them for `decisions/`, and later for packages with their own conventions.
12. **Backfill ADRs from the design docs.** The design docs already contain a dozen hard-to-reverse decisions. Listing them as ADR 0001–00NN on day one means the decisions folder is real from the first session, not aspirational.
13. **Success criteria for the prototype, in the design doc.** Measurable ones. It turns the first milestone's exit from opinion into numbers.
14. **Non-goals section.** Agents will otherwise helpfully build the thing you deferred.
15. **Say what not to build first.** The most visually impressive part of any tool is rarely the most important. Name it and order it late.
16. **Section anchors are contracts.** Once code or other docs cite `§6.1`, renumbering is a breaking change. Append `§6.1a` instead.
17. **Keep `AGENTS.md` short and pointing outward.** Rules that change behaviour, layout, commands, conventions, don'ts. Everything else is a link. Over 120 lines and agents stop reading it.
18. **Generate milestone files from the roadmap, then make them authoritative.** Never keep checkboxes in two places.
19. **Consider a bootstrap skill.** If your agent supports skills, turn Part C into one (`/bootstrap`) so the procedure runs as a guided conversation rather than a copy-paste.

## Part E — Templates

Generic skeletons. `{{...}}` marks a placeholder. Copy, fill, delete this note.

### E1. `AGENTS.md` (root)

```markdown
# AGENTS.md

Instructions for any AI agent in this repository. `CLAUDE.md` imports this file. Keep under 120 lines.

## What this is
**{{Project}}** is {{one sentence}}. The rule that shapes everything: **{{the one rule}}**.

## Read first
1. `DOCS.md` 2. `docs/design/{{product}}-design.md` 3. `docs/GLOSSARY.md` 4. `docs/WORKFLOW.md` 5. `docs/milestones/README.md`
Then the design doc for the area you're touching.

## Non-negotiable rules
- {{rule, one line, cite ADR}}
- ...

## Repository layout
{{tree, one line per top-level entry; cite architecture.md §N}}

## How to work
1. Open the in-progress milestone. Pick your feature.
2. No plan? Ground → Brainstorm → Plan. No code before the plan.
3. Plan exists? Read it fully; resume at the first unticked task.
4. Work a task, run its verification, paste evidence, tick, commit as `M1-03: what changed`.
5. Before ending: plan matches reality; notes say where you stopped.
Small fixes skip the plan (`WORKFLOW.md` §5).

## Commands
{{build / test / lint / run — update as the toolchain lands}}

## Conventions
- Words: `docs/GLOSSARY.md`. {{two or three "say X not Y"}}
- Cross-references: `docs/design/file.md §N.M`, `ADR 0007`, `M1-03`.
- Tests: {{what is test-first}}.
- Docs and code agree, in the same commit.
- Hard-to-reverse choices get an ADR; agents propose, humans accept.

## Don't
- {{deferred things}}
- Don't tick a box without running the verification.
- Don't renumber sections in design docs.

## Tool-specific notes
- Claude Code: `CLAUDE.md` is `@AGENTS.md` plus nothing.
- Codex: reads this natively; nested `AGENTS.md` files scope to their subtree.
- Others: point them here first.
```

### E2. `CLAUDE.md`

```markdown
@AGENTS.md

<!-- Deliberately empty. All instructions live in AGENTS.md so every agent reads the same thing. -->
```

### E3. `DOCS.md`

```markdown
# DOCS.md
How `docs/` is organised and kept honest.

## 1. Map
{{tree with one-line purpose per file}}

## 2. Four kinds of document
{{table: design / decision / progress / reference — where, answers, changes when}}

## 3. Reading order
New to the project: ... Starting a session: ... Making a design change: ...

## 4. Where things go
- A new rule → the design doc. If it contradicts the doc, that's a design change: update it, ADR if hard to reverse.
- A choice between alternatives → ADR + one-line pointer from the design doc.
- Something to build → milestone feature line. Never a design doc.
- How it's being built → the plan. Never a design doc or ADR.
- A new term → GLOSSARY, same change.
- An open question → OPEN-QUESTIONS.md. When answered → ADR, and remove it.
- Measurements → docs/evidence/, linked from the milestone.

## 5. Conventions
Headers on every doc (status, audience, related). Exact status vocabularies. Cite by path + §. Section anchors are contracts. One idea per document. Length limits.

## 6. Docs and code agree
A PR that changes described behaviour updates the doc. New schema field → data model + glossary. Resolved question → ADR. Finished task → tick with evidence.

## 7. What not to put here
Meeting notes, generated output, secrets, restatements of code.

## 8. Maintenance
Indexes regenerated on change. Drift review at each milestone close. Done plans are never deleted.
```

### E4. `WORKFLOW.md`

```markdown
# Workflow

## 1. Three layers
roadmap.md (narrative, no checkboxes) → milestones/M<n>.md (features, checkboxes; source of truth) → plans/M<n>-<nn>-*.md (grounding, approach, tasks, notes; session handoff).
Feature IDs: `M<n>-<nn>`. Status lives in exactly one place per layer.

## 2. Feature lifecycle
**Ground** — read CLAUDE/AGENTS, the milestone, the cited design docs; grep decisions/; run tests; inspect the packages touched; read the previous feature's plan. Write 3–10 concrete bullets into **Current state**. If the feature is done, mis-scoped, or blocked: stop and say so.
**Brainstorm** — approach, alternatives (one line each), risks and how they'll be checked, docs to update, ADR needed? (write it as `proposed` now). With the human if ambiguous; alone if the docs already say what to build.
**Plan** — tasks, each one commit, each naming its verification. Tests first where tests apply. Set plan status `planned`; link it from the milestone.
**Execute** — task by task: do, verify, paste evidence, tick, commit `M1-03: ...`, note anything learned. Plan wrong? Fix the plan first.
**Close** — all tasks ticked, suite green, docs updated, ADRs accepted by a human, feature ticked in the milestone, plan `done`. Last feature? Check exit criteria honestly; record evidence.

## 3. Sessions
Start: AGENTS.md → milestones/README → your plan → first unticked task. End: plan matches reality; notes say where you stopped; tree green or the plan says what's red. One feature per session by default.

## 4. Branches and commits
`feat/M1-03-title`. Commit messages start with the feature ID. PRs link the plan; don't duplicate it. `main` is always green.

## 5. Small changes
Skip the plan for: obvious bug fixes with a reproducing test; typos and formatting; no-API-change dependency bumps. If it grows past one commit, it's a feature.

## 6. When things don't fit
Too big → split. Blocked on a decision → ADR `proposed`, move on. Exit criteria unmeetable → say so with numbers. Doc is wrong → fix it in the same change.

## 7. Plan template
# M1-03 — Title
**Status:** grounding | planned | in progress | blocked | done
**Milestone:** M1  **Branch:** feat/M1-03-title  **Design docs:** ...  **ADRs:** ...  **Sessions:** n
## Objective
## Current state
## Approach  (+ Alternatives considered, Risks, Docs to update)
## Tasks
- [ ] T1 — ... **Verify:** `command`
## Progress notes
## Verification log

## 8. Milestone template
# M1 — Title
**Status:** not started | in progress | done
**Goal:**  **Exit criteria:**  **Evidence of exit:**
## Features
- [ ] M1-01 — Title — `docs/plans/M1-01-title.md`
## Notes

## 9. Every session, in order
1. Read AGENTS.md. 2. Open the in-progress milestone. 3. No plan → Ground → Brainstorm → Plan. 4. Plan → resume. 5. Verify before ticking. 6. Leave the plan true.
```

### E5. `docs/decisions/AGENTS.md`

```markdown
# docs/decisions/ — Architecture Decision Records

## Why
Design docs say what; ADRs say why. Check here before relitigating anything.

## When to write one
Hard to reverse; resolves an open question; changes a design doc; a real choice between alternatives; discussed at length. Not for: routine choices, naming, formatting, single-file changes. When unsure, write it.

## Naming
`NNNN-decision-as-a-sentence.md`. Next number; never reuse or renumber. One decision per file.

## Statuses
`proposed` (agents may create) · `accepted` (human sets) · `superseded by NNNN` · `rejected`. Never delete.

## Template
# NNNN. <Decision as a sentence>
**Status:** **Date:** **Deciders:** **Related:**
## Context
## Decision
## Alternatives considered
## Consequences

## Rules for agents
1. Read before writing (grep the topic). 2. Propose, don't accept — except backfills from accepted design docs. 3. Update the design doc in the same change. 4. Cite ADRs in code where it helps. 5. Keep README.md (the index) current. 6. Don't relitigate inside the ADR.

## Backfill list
| # | Decision | Source |
|---|---|---|
| 0001 | {{decision already stated in a design doc}} | {{doc §}} |
```

### E6. `docs/GLOSSARY.md`

```markdown
# Glossary
Use these exactly — in docs, code, prompts, telemetry, conversation. New concept → new entry, same change.

## {{Area}}
**Term** — Definition. Where it lives (`file.md §N`, schema field).

## ID prefixes
| Prefix | Collection |

## Words we avoid
- **"{{loose word}}"** — say *{{precise term}}*.
```

### E7. `docs/OPEN-QUESTIONS.md`

```markdown
# Open questions
Every unresolved question, in one place. When decided → ADR, delete the row.

| Question | Raised in | Blocks | Owner | Needed by |
|---|---|---|---|---|
```

### E8. `docs/roadmap.md`

```markdown
# Roadmap
**No checkboxes here.** Scope and progress live in `milestones/`. Edit only to reorder or re-purpose a milestone.

## Principles
- {{validate X before building Y}}
- Every milestone ends in something runnable or measurable.
- {{the stop-ship rule}}

## M0 — {{Foundations}}
Goal: ... Features: `milestones/M0.md` **Exit:** ...

## Explicitly deferred
- ...

## Open decisions with a deadline
See `OPEN-QUESTIONS.md`.
```

### E9. Design doc header

```markdown
# {{Title}}
**Project:** {{name}}  **Status:** Draft v0.1  **Audience:** {{who, and why they read this}}
Related: {{files}}
---
```

### E10. `README.md` (root)

```markdown
# {{Project}}
{{Three sentences: what, for whom, current state.}}
Docs: start at `DOCS.md`. Agents: start at `AGENTS.md`.
```

### E11. `tools/check_docs` (spec)

Exit non-zero if any of: a cited `path.md` doesn't exist; a cited `§N.M` isn't a heading in that file; a `milestones/M*.md` is missing from `milestones/README.md` or has a different status there; an ADR is missing from `decisions/README.md`; `{{`, `TBD`, or the codename placeholder appears outside `OPEN-QUESTIONS.md`; a plan is `done` but its feature isn't ticked, or vice versa. Run in CI and at the end of every agent session.