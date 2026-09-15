# AGENTS.md

Instructions for any AI agent in this repository. `CLAUDE.md` imports this file. Keep under 120 lines.

## What this is
**{{Project}}** is {{one_sentence}}. The rule that shapes everything: **{{one_rule}}**.
**Profile:** {{profile}}  **Tier:** {{tier}}

## Read first
1. `DOCS.md`  2. `docs/CURRENT.md`  3. `docs/design/{{product}}-design.md`  4. `docs/GLOSSARY.md`  5. `docs/WORKFLOW.md`
Then the design doc for the area you're touching.

## Non-negotiable rules
- {{rule}}
- ...

## Repository layout
One line per top-level entry; cite `<file>.md §N`.

## How to work
1. Open `docs/CURRENT.md`. Resume a feature you claimed, or claim the next unclaimed one: set its plan to `in progress` and add a session stamp under `## Sessions`.
2. No plan? Ground → Brainstorm → Plan. No code before the plan.
3. Plan exists? Read it fully; resume at the first unticked task.
4. Work a task, run its verification, paste evidence, tick, commit as `M1-03: what changed`.
5. Before ending: plan matches reality; notes say where you stopped.
6. Before ending: run `python tools/check_docs.py --fix` and commit the generated files with your work.
Small fixes skip the plan (`WORKFLOW.md` §5).

## Commands
{{commands}}

## Conventions
- Words: `docs/GLOSSARY.md`. Say the precise term, not the loose one.
- Cross-references: `docs/design/<file>.md §N.M`, `ADR <NNNN>`, `M<n>-<nn>`.
- Tests: note what is test-first for this project.
- Docs and code agree, in the same commit.
- Hard-to-reverse choices get an ADR; agents propose, humans accept.

## Don't
- {{deferred}}
- Don't tick a box without running the verification.
- Don't renumber sections in design docs.
- Don't edit `docs/CURRENT.md` or any `README.md` index by hand; they are generated.
- Don't start a feature whose plan has a session stamp under 24 hours old.

## Tool-specific notes
- Claude Code: `CLAUDE.md` is `@AGENTS.md` plus nothing.
- Codex: reads this natively; nested `AGENTS.md` files scope to their subtree.
- Others: point them here first.
