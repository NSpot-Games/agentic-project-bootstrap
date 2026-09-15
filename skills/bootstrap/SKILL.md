---
name: bootstrap
description: Bootstrap a new project or adopt an existing one into the docs-as-contract workflow. Use when the user says "bootstrap a project", "set up docs for this repo", "adopt the bootstrap kit", or pastes BOOTSTRAP.md.
---

# Bootstrap

Runs the greenfield or brownfield adoption procedure as a guided conversation: classify the
project, ask the setup questions, write the design docs one per session with a human review
gate after each, generate the process files, run the linter, and open the first session. Follow
the sections below in order; do not skip ahead to generation before the docs it depends on exist.

## 1. Announce and classify

Look at the target repository and say which of these it is, per `core/adoption.md §3`:

- **Greenfield** — an empty repository, no code, nothing to recover.
- **Brownfield** — any repository with real code in it, even rough or partial, or with code but
  no docs.

Greenfield follows §2 through §5 below. Brownfield follows §6.

## 2. C0: five questions, one at a time

Ask these one per message, in this order, and wait for the answer before asking the next.
Record each answer in a scratch list; write nothing to disk yet.

1. **Name and codename.** What is the project called?
2. **Naming convention.** Recommend kebab-case, unnumbered — numbered prefixes look tidy and
   then break every cross-reference the first time something is reordered.
3. **Example location.** Where will the example instance live — `<project>/cases/<id>/`,
   `<project>/fixtures/`, or similar? The architecture doc will cite it.
4. **Tier.** Recommend one from `core/tiers.md`, based on scope: solo, one phase, under ten
   features suggests lite; most projects land on standard; multi-phase, multi-agent, or
   regulated suggests full.
5. **Profile.** Recommend one from `profiles/README.md`, based on the project's central
   artefact.

Do not write any file until all five are answered.

## 3. Brainstorm, design docs, roadmap — one document per session

This section runs C1 through C8 of `core/adoption.md §1`, one session per step below, in
order.

**(a) Brainstorm (C1).** Hold this as its own session, with no file written: what the project
is, who it's for, what's hard, what the real alternatives are, what will not be built. Push on
the hardest technical constraint early. End the session with a list of decisions made and
questions left open, held in the scratch list alongside C0's answers.

**(b) Design docs (C2 through C7), one per session.** State the rule and the reason to the
user: this skill writes at most one design doc per session, because a one-shot bootstrap that
writes several docs back to back produces shallow docs — each later one gets less scrutiny
than the last. Write the docs the chosen profile calls for (`profiles/<name>.md`), phase 1
only, in the order the profile lists.

After finishing each doc, stop and post exactly:

> Review `<path>`. Say 'next' to continue or tell me what to change.

Do not start the next doc, or move on to the roadmap, until the user replies.

**(c) Roadmap (C8), its own session.** Decide phase 1's exit, then the current and next
milestones' goals and measurable exits; everything beyond those two is `sketch` — a goal
sentence and nothing more. Write `<project>/docs/roadmap.md` from `templates/roadmap.md`, then
apply the same review gate as (b): stop and post the message above. Do not move on to
generation (§4) until the user replies.

## 4. Generation

Once the brainstorm, phase 1's design docs, and the roadmap are all written and reviewed:

1. Copy the files `templates/` provides for the chosen tier into the project.
2. Substitute every `{{token}}` using the table in `templates/README.md`; values come from C0's
   answers, the brainstorm's decisions, the design docs, and the roadmap just written.
3. Create the milestone files for the current and next milestone; everything beyond stays
   `sketch` in the roadmap only.
4. Run `python tools/check_docs.py --root . --fix` and fix whatever it reports.

## 5. First session

Open `<project>/docs/CURRENT.md` and claim `M0-01`. Follow `<project>/docs/WORKFLOW.md` from there.

## 6. Brownfield variant

Follow the seven steps of `core/adoption.md §2`, in order: inventory; reverse-engineer the
architecture doc from the code; recover the data model and an anonymised example instance;
backfill ADRs from git history; write the design doc as a vision-and-current-state document;
build the roadmap from the issue tracker; generate, lint, and open on a feature named "close
the gaps the inventory found". The same one-doc-per-session gate from §3 applies to every doc
this variant writes — stop after each one and post the review-gate message before continuing.

## 7. What this skill never does

- Write more than one design doc in a single session, unless the user explicitly says to.
- This skill never ticks a box; ticking happens in feature work, with verification evidence.
- Accept an ADR — an ADR moves from `proposed` to `accepted` by human decision, never by this
  skill.
- Edit a generated file by hand (`<project>/docs/CURRENT.md`,
  `<project>/docs/milestones/README.md`, `<project>/docs/plans/README.md`,
  `<project>/docs/decisions/README.md`); only `tools/check_docs.py --fix` writes those.
