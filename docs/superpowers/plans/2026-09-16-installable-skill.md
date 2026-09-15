# Installable Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `skills/project-bootstrap/` a self-contained, spec-conformant Agent Skill that `npx skills add` and `claude plugin install` can install, with one copy of every kit document.

**Architecture:** Move `core/`, `profiles/`, `templates/`, `tools/check_docs.py` and `tools/hooks/` under the skill directory in the Agent Skills layout (`references/`, `assets/`, `scripts/`); rewrite kit-internal citations to the skill-relative form; add a `citation_roots` config key so the linter resolves those; add Claude plugin manifests and a guarded plugin Stop hook; move tests to `tests/` and add a package test.

**Tech Stack:** Python 3.11+ standard library (linter and tests, pytest for the runner), Markdown, JSON, POSIX sh.

**Spec:** `docs/superpowers/specs/2026-09-16-installable-skill-design.md`

## Global Constraints

- The linter stays Python 3.11+ standard library only.
- Every kit-internal path a doc cites must exist; every `§N` cited must be a real numbered heading. `python skills/project-bootstrap/scripts/check_docs.py --root .` reports 0 errors, 0 warnings at the end of every task from Task 2 on.
- Three path forms (spec §5): inside the skill directory, skill-relative (`references/core/layers.md §1`); at the repo root, full (`skills/project-bootstrap/references/core/layers.md §1`); target-project paths keep `<project>/` and commands keep bare `tools/check_docs.py`.
- Templates (`skills/project-bootstrap/assets/templates/*.md`) do not change in this plan.
- No `{{` outside `assets/templates/`; unfixed names use `<angle brackets>`.
- Section numbers `## N. Title` in existing docs are not renumbered.
- Skill name is `project-bootstrap`; version is `2.1.0` in SKILL.md metadata, plugin.json and marketplace.json.
- Moves use `git mv`. Commits stage files by name or by directory, never `git add -A` (avoids `__pycache__`).
- Every commit message ends with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- Work happens on branch `feat/installable-skill` off `main`.
- On Windows Git Bash, multi-line file content is written with the Write tool, not heredocs.

---

### Task 1: `citation_roots` in the linter

**Files:**
- Modify: `tools/check_docs.py` (docstring lines 7–8, `Config` at ~line 54, `load_config` at ~line 69, `_resolve_citation` at ~line 461, `check()` E012 message at ~line 830)
- Test: `tools/tests/test_check_docs.py` (append)

**Interfaces:**
- Produces: `Config.citation_roots: list[str]` (default `[]`); config key `citation_roots`; E012 message form `invalid config: <detail>`.

- [ ] **Step 1: Write the failing tests**

Append to `tools/tests/test_check_docs.py`:

```python
def _kit_layout(root: Path) -> None:
    """A skill-like subtree whose files cite each other relative to that subtree."""
    ref = root / "kit" / "ref"
    ref.mkdir(parents=True)
    (ref / "a.md").write_text("# A\n\n## 1. One\n\nSee `ref/b.md §2`.\n", encoding="utf-8", newline="\n")
    (ref / "b.md").write_text("# B\n\n## 1. One\n\n## 2. Two\n", encoding="utf-8", newline="\n")


def _add_config(root: Path, line: str) -> None:
    cfg = root / "docs" / ".check_docs.toml"
    cfg.write_text(cfg.read_text(encoding="utf-8") + "\n" + line + "\n", encoding="utf-8", newline="\n")


def test_citation_roots_resolves_paths_under_listed_root(tmp_path):
    root = make_project(tmp_path)
    _kit_layout(root)
    (root / "docs" / "note.md").write_text("See `ref/a.md §1` and `ref/b.md §2`.\n", encoding="utf-8", newline="\n")
    _add_config(root, 'citation_roots = ["kit"]')
    found = cd.run(root)
    assert "E001" not in codes(found)
    assert "E002" not in codes(found)
    assert "E012" not in codes(found)


def test_citation_roots_checks_anchor_against_resolved_file(tmp_path):
    root = make_project(tmp_path)
    _kit_layout(root)
    (root / "docs" / "note.md").write_text("See `ref/b.md §9`.\n", encoding="utf-8", newline="\n")
    _add_config(root, 'citation_roots = ["kit"]')
    found = cd.run(root)
    assert "E002" in codes(found)
    assert "E001" not in codes(found)


def test_citation_missing_from_root_and_all_citation_roots_is_e001(tmp_path):
    root = make_project(tmp_path)
    _kit_layout(root)
    (root / "docs" / "note.md").write_text("See `ref/zzz.md`.\n", encoding="utf-8", newline="\n")
    _add_config(root, 'citation_roots = ["kit"]')
    found = cd.run(root)
    assert "E001" in codes(found)


def test_citation_roots_nonexistent_directory_is_e012(tmp_path):
    root = make_project(tmp_path)
    _add_config(root, 'citation_roots = ["no-such-dir"]')
    found = cd.run(root)
    e012 = [f for f in found if f.code == "E012"]
    assert e012 and "no-such-dir" in e012[0].message


def test_citation_roots_wrong_type_is_e012(tmp_path):
    root = make_project(tmp_path)
    _add_config(root, 'citation_roots = "kit"')
    found = cd.run(root)
    assert "E012" in codes(found)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tools/tests/test_check_docs.py -q -k citation_roots`
Expected: 5 failed (E001 present where none expected; E012 absent where expected).

- [ ] **Step 3: Implement**

In `tools/check_docs.py`:

Docstring line 8 becomes:
```python
E012: `docs/.check_docs.toml` is not valid TOML, or `citation_roots` is not a list of existing directories; defaults were used for the bad key.
```

`Config` gains, after `citation_exclude`:
```python
    citation_roots: list[str] = field(default_factory=list)
```

`load_config` becomes:
```python
def load_config(root: Path) -> Config:
    cfg = Config(root=Path(root))
    path = cfg.docs / ".check_docs.toml"
    if path.exists():
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as e:
            cfg.config_error = f"not valid TOML: {e}"
            return cfg
        for key in ("codename_placeholder", "stale_hours", "allow_tbd_in", "citation_exclude",
                    "citation_roots", "tier"):
            if key in data:
                setattr(cfg, key, data[key])
        if "exclude" in data:
            cfg.exclude = list(DEFAULT_EXCLUDE) + list(data["exclude"])
        roots = cfg.citation_roots
        if not isinstance(roots, list) or not all(isinstance(r, str) for r in roots):
            cfg.config_error = "citation_roots must be a list of strings"
            cfg.citation_roots = []
        else:
            missing = [r for r in roots if not (cfg.root / r).is_dir()]
            if missing:
                cfg.config_error = f"citation_roots entry is not a directory: {missing[0]}"
                cfg.citation_roots = [r for r in roots if r not in missing]
    return cfg
```

`_resolve_citation` becomes:
```python
def _resolve_citation(cfg: Config, citing: Path, target: str) -> Path | None:
    bases = [citing.parent, cfg.root, cfg.docs] + [cfg.root / r for r in cfg.citation_roots]
    for base in bases:
        cand = base / target
        if cand.is_file():
            return cand
    return None
```

In `check()`, the E012 finding message becomes `f"invalid config: {cfg.config_error}"`.

- [ ] **Step 4: Run the full suite**

Run: `python -m pytest tools/tests -q`
Expected: 64 passed (59 + 5).

- [ ] **Step 5: Lint the kit and commit**

Run: `python tools/check_docs.py --root .` → `0 error(s), 0 warning(s)`.

```bash
git checkout -b feat/installable-skill
git add tools/check_docs.py tools/tests/test_check_docs.py
git commit -m "linter: citation_roots resolves skill-relative citations

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Move the kit into the skill directory and rewrite internal citations

**Files:**
- Move (git mv): `skills/bootstrap` → `skills/project-bootstrap`; `core` → `skills/project-bootstrap/references/core`; `profiles` → `skills/project-bootstrap/references/profiles`; `templates` → `skills/project-bootstrap/assets/templates`; `tools/check_docs.py` → `skills/project-bootstrap/scripts/check_docs.py`; `tools/hooks` → `skills/project-bootstrap/scripts/hooks`; `tools/tests` → `tests`
- Modify: `tests/conftest.py`, `tests/test_check_docs.py:13`, `docs/.check_docs.toml`, every `.md` under `skills/project-bootstrap/references/` (citation prefixes), `skills/project-bootstrap/SKILL.md` (citation prefixes only; body rewrite is Task 3)

**Interfaces:**
- Produces: the final directory layout (spec §4). Later tasks assume it.

- [ ] **Step 1: Move**

```bash
git mv skills/bootstrap skills/project-bootstrap
mkdir -p skills/project-bootstrap/references skills/project-bootstrap/assets skills/project-bootstrap/scripts
git mv core skills/project-bootstrap/references/core
git mv profiles skills/project-bootstrap/references/profiles
git mv templates skills/project-bootstrap/assets/templates
git mv tools/check_docs.py skills/project-bootstrap/scripts/check_docs.py
git mv tools/hooks skills/project-bootstrap/scripts/hooks
git mv tools/tests tests
rm -rf tools
```

Verify: `ls` shows no `core profiles templates tools`; `git status --short | grep -c '^R'` is large; `ls skills/project-bootstrap` shows `SKILL.md assets references scripts`.

- [ ] **Step 2: Repoint the tests**

`tests/conftest.py` becomes:
```python
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "skills" / "project-bootstrap" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
```

`tests/test_check_docs.py` line 13 becomes:
```python
CHECK = Path(__file__).resolve().parents[1] / "skills" / "project-bootstrap" / "scripts" / "check_docs.py"
```

Run: `python -m pytest tests -q` → 64 passed.

- [ ] **Step 3: Kit config**

`docs/.check_docs.toml` becomes:
```toml
# Config for running the kit's own linter on this repo.
citation_roots = ["skills/project-bootstrap"]
allow_tbd_in = ["docs/superpowers/"]
citation_exclude = ["skills/project-bootstrap/assets/templates/", "tests/fixture/", "docs/superpowers/"]
exclude = ["tests/fixture", ".superpowers"]
```

- [ ] **Step 4: Rewrite kit-internal citations inside the skill directory**

Every kit-internal `.md` citation in `references/**` and `SKILL.md` is backtick-prefixed. Rewrite with sed (Git Bash; `-i` works on these files):

```bash
cd skills/project-bootstrap
FILES=$(find references SKILL.md -name '*.md')
sed -i -E \
  -e 's#`core/#`references/core/#g' \
  -e 's#`profiles/#`references/profiles/#g' \
  -e 's#`templates/#`assets/templates/#g' \
  -e 's#`tools/hooks/README\.md#`scripts/hooks/README.md#g' \
  -e 's#`skills/bootstrap/SKILL\.md`#`SKILL.md`#g' \
  $FILES
```

Then verify nothing bare is left (the only allowed remaining forms are the rewritten ones, `<project>/…`, and bare `tools/check_docs.py` / `tools/hooks/stop.sh` commands, which are target-project paths and not `.md` citations):

```bash
grep -rnE '`(core|profiles|templates)/' references SKILL.md          # expect no output
grep -rn 'skills/bootstrap' references SKILL.md                       # expect no output
grep -rn 'tools/hooks/README' references SKILL.md                     # expect no output
```

Also fix prose that named the old directories without a backtick citation. Check and edit by hand:
```bash
grep -rnE '(^|[^`/<])(core|profiles|templates)/' references SKILL.md
```
Any hit that means the kit directory becomes the skill-relative form; any hit that means a target-project directory gets `<project>/`.

- [ ] **Step 5: Lint**

Run: `python skills/project-bootstrap/scripts/check_docs.py --root .`
Expected: E001 findings only in `README.md`, `BOOTSTRAP.md`, `AGENTS.md` (root docs, fixed in Task 4) and possibly `skills/project-bootstrap/scripts/hooks/README.md` (fixed in Task 3). Zero findings under `skills/project-bootstrap/references/`. If a `references/` file still reports E001/E002, fix that citation now.

Record the count of remaining root-doc E001s in the report; Task 4 must bring it to zero.

- [ ] **Step 6: Commit**

```bash
git add -u
git add skills/project-bootstrap tests docs/.check_docs.toml
git status --short | grep -v '^R\|^M\|^A\|^D' && echo "UNEXPECTED" || true
git commit -m "Move the kit into skills/project-bootstrap in the Agent Skills layout

core/ → references/core/, profiles/ → references/profiles/, templates/ → assets/templates/,
tools/check_docs.py and tools/hooks/ → scripts/, tools/tests/ → tests/. Skill-internal
citations become skill-relative and resolve through citation_roots.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

`git add -u` stages the renames and modifications of tracked files; confirm no `__pycache__` entry appears in `git status --short` before committing.

---

### Task 3: Rewrite SKILL.md and the hooks README for standalone use

**Files:**
- Rewrite: `skills/project-bootstrap/SKILL.md`
- Rewrite: `skills/project-bootstrap/scripts/hooks/README.md`

**Interfaces:**
- Consumes: layout from Task 2.
- Produces: frontmatter fields Task 5's tests read (`name`, `description`, `metadata.version` = `2.1.0`).

- [ ] **Step 1: Write SKILL.md**

Replace the whole file with (Write tool):

````markdown
---
name: project-bootstrap
description: Bootstrap a new project or adopt an existing one into the docs-as-contract workflow. Use when the user says "bootstrap a project", "set up docs for this repo", "adopt the bootstrap kit", or pastes BOOTSTRAP.md.
license: MIT
compatibility: Requires Python 3.11+ for scripts/check_docs.py
metadata:
  author: NSpotGames
  version: "2.1.0"
---

# Project Bootstrap

Runs the greenfield or brownfield adoption procedure as a guided conversation: classify the
project, ask the setup questions, write the design docs one per session with a human review
gate after each, generate the process files, run the linter, and open the first session. Follow
the sections below in order; do not skip ahead to generation before the docs it depends on exist.

Every file this skill names lives inside its own directory: rules in `references/core/`,
profiles in `references/profiles/`, templates in `assets/templates/`, the linter in
`scripts/check_docs.py`. Paths are relative to the skill root, so the skill works when installed
on its own. Paths written `<project>/...` are in the project being bootstrapped.

## 1. Announce and classify

Look at the target repository and say which of these it is, per `references/core/adoption.md §3`:

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
4. **Tier.** Recommend one from `references/core/tiers.md`, based on scope: solo, one phase,
   under ten features suggests lite; most projects land on standard; multi-phase, multi-agent,
   or regulated suggests full.
5. **Profile.** Recommend one from `references/profiles/README.md`, based on the project's
   central artefact.

Do not write any file until all five are answered.

## 3. Brainstorm, design docs, roadmap — one document per session

This section runs C1 through C8 of `references/core/adoption.md §1`, one session per step
below, in order.

**(a) Brainstorm (C1).** Hold this as its own session, with no file written: what the project
is, who it's for, what's hard, what the real alternatives are, what will not be built. Push on
the hardest technical constraint early. End the session with a list of decisions made and
questions left open, held in the scratch list alongside C0's answers.

**(b) Design docs (C2 through C7), one per session.** State the rule and the reason to the
user: this skill writes at most one design doc per session, because a one-shot bootstrap that
writes several docs back to back produces shallow docs — each later one gets less scrutiny
than the last. Write the docs the chosen profile calls for (`references/profiles/<name>.md`),
phase 1 only, in the order the profile lists.

After finishing each doc, stop and post exactly:

> Review `<path>`. Say 'next' to continue or tell me what to change.

Do not start the next doc, or move on to the roadmap, until the user replies.

**(c) Roadmap (C8), its own session.** Decide phase 1's exit, then the current and next
milestones' goals and measurable exits; everything beyond those two is `sketch` — a goal
sentence and nothing more. Write `<project>/docs/roadmap.md` from
`assets/templates/roadmap.md`, then apply the same review gate as (b): stop and post the message
above. Do not move on to generation (§4) until the user replies.

## 4. Generation

Once the brainstorm, phase 1's design docs, and the roadmap are all written and reviewed:

1. Copy the files `assets/templates/` provides for the chosen tier into the project;
   `references/core/tiers.md` lists which files each tier gets.
2. Copy `scripts/check_docs.py` to `<project>/tools/check_docs.py`. If the user wants the
   linter to run without being remembered, also copy `scripts/hooks/stop.sh` to
   `<project>/tools/hooks/stop.sh` and wire it as `scripts/hooks/README.md` shows.
3. Substitute every `{{token}}` using the table in `assets/templates/README.md`; values come
   from C0's answers, the brainstorm's decisions, the design docs, and the roadmap just written.
4. Create the milestone files for the current and next milestone; everything beyond stays
   `sketch` in the roadmap only.
5. From the project root, run `python tools/check_docs.py --root . --fix` and fix whatever it
   reports.

## 5. First session

Open `<project>/docs/CURRENT.md` and claim `M0-01`. Follow `<project>/docs/WORKFLOW.md` from there.

## 6. Brownfield variant

Follow the seven steps of `references/core/adoption.md §2`, in order: inventory;
reverse-engineer the architecture doc from the code; recover the data model and an anonymised
example instance; backfill ADRs from git history; write the design doc as a
vision-and-current-state document; build the roadmap from the issue tracker; generate, lint,
and open on a feature named "close the gaps the inventory found". Generation follows §4 steps
1 through 5. The same one-doc-per-session gate from §3 applies to every doc this variant
writes — stop after each one and post the review-gate message before continuing.

## 7. What this skill never does

- Write more than one design doc in a single session, unless the user explicitly says to.
- This skill never ticks a box; ticking happens in feature work, with verification evidence.
- Accept an ADR — an ADR moves from `proposed` to `accepted` by human decision, never by this
  skill.
- Edit a generated file by hand (`<project>/docs/CURRENT.md`,
  `<project>/docs/milestones/README.md`, `<project>/docs/plans/README.md`,
  `<project>/docs/decisions/README.md`); only the project's `tools/check_docs.py --fix` writes
  those.
````

- [ ] **Step 2: Write scripts/hooks/README.md**

Replace the whole file with:

````markdown
# Running check_docs automatically

The linter is meant to run without anyone remembering to run it. The project keeps its own
copy at `<project>/tools/check_docs.py` (the bootstrap skill copies `scripts/check_docs.py`
there in its generation step), and the snippets below run that copy.

The snippets call `python3`, the name on macOS and Debian-family Linux; Windows users
substitute `python`.

## Claude Code Stop hook (per project)

Copy `scripts/hooks/stop.sh` to `<project>/tools/hooks/stop.sh`. It receives Claude Code's
JSON on stdin and exits 0 when `stop_hook_active` is true, so a session that cannot fix the
errors is not blocked forever:

```sh
#!/bin/sh
input=$(cat)
case "$input" in *'"stop_hook_active": true'*) exit 0;; esac
python3 tools/check_docs.py --root . || { echo 'check_docs found errors; fix them before ending the session'; exit 2; }
```

Add to `<project>/.claude/settings.json` (or `settings.local.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "sh tools/hooks/stop.sh"
          }
        ]
      }
    ]
  }
}
```

Exit code 2 from a Stop hook blocks the stop and shows the message to the agent. Warnings do
not block.

## Claude Code Stop hook (from the plugin)

If the kit was installed as a Claude Code plugin, the plugin already registers a Stop hook. It
runs the project's `tools/check_docs.py` when that file exists and does nothing otherwise, so
no per-project setting is needed. Installing both is harmless; the linter runs twice.

## Pre-commit hook

`<project>/.git/hooks/pre-commit` (make it executable), or the equivalent entry in your
pre-commit framework:

```sh
#!/bin/sh
python3 tools/check_docs.py --root . || exit 1
```

## CI

Run `python3 tools/check_docs.py --root .` as a step. It exits 1 on any E-code.

## Regenerating indexes

`python3 tools/check_docs.py --root . --fix` rewrites `<project>/docs/milestones/README.md`,
`<project>/docs/plans/README.md`, `<project>/docs/decisions/README.md`, and
`<project>/docs/CURRENT.md`. Run it at the end of every session and commit the result. Never
edit those four files by hand.
````

- [ ] **Step 3: Verify**

```bash
wc -l skills/project-bootstrap/SKILL.md                                  # < 500
python skills/project-bootstrap/scripts/check_docs.py --root . | grep 'skills/project-bootstrap'   # expect no output
```

- [ ] **Step 4: Commit**

```bash
git add skills/project-bootstrap/SKILL.md skills/project-bootstrap/scripts/hooks/README.md
git commit -m "skill: project-bootstrap frontmatter and standalone paths; hooks README for target projects

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Root documents, license, and BOOTSTRAP.md citations

**Files:**
- Rewrite: `README.md`, `AGENTS.md`
- Create: `LICENSE`
- Modify: `BOOTSTRAP.md` (intro paragraph, §3, citation prefixes)

**Interfaces:**
- Consumes: layout from Task 2, skill name and install commands from spec §8.

- [ ] **Step 1: README.md**

Replace the whole file with:

````markdown
# agentic-project-bootstrap

A bootstrap kit: docs, templates, and a linter that a software project copies in, or is pointed
at, so a human and their AI agents — Claude Code, Codex, others — share one set of design docs,
one workflow, and one source of truth for progress. It fits new projects and existing
codebases, solo weekend builds and multi-agent, multi-phase efforts, by picking a profile and a
tier instead of assuming one fixed shape of project.

The kit ships as one Agent Skill, `skills/project-bootstrap/`, that follows the
[Agent Skills](https://agentskills.io) layout: the procedure in `SKILL.md`, the rules in
`references/`, the templates in `assets/`, the linter in `scripts/`. Install it into your agent
or just read it.

## Install

**Any agent, via the `skills` CLI** (Claude Code, Codex, Cursor, Gemini CLI, Copilot, Cline
and others):

```
npx skills add NSpotGames/agentic-project-bootstrap
```

**Claude Code, as a plugin** (adds a Stop hook that runs the linter in projects built on the
kit):

```
claude plugin marketplace add NSpotGames/agentic-project-bootstrap
claude plugin install project-bootstrap@agentic-project-bootstrap
```

or `/plugin marketplace add NSpotGames/agentic-project-bootstrap` and
`/plugin install project-bootstrap@agentic-project-bootstrap` inside a session.

**By hand:** clone this repo and copy `skills/project-bootstrap/` into your agent's skills
directory (`.claude/skills/`, `.agents/skills/`, `~/.codex/skills/`, or wherever it reads
them). Or skip installing and hand your agent `BOOTSTRAP.md`.

## Use

Tell your agent to bootstrap the project. The skill classifies the repo as greenfield or
brownfield, asks five setup questions, writes the design docs one per session with a review
gate after each, generates the process files for the chosen tier, copies the linter into the
project, and opens the first session. Without a skill-aware agent, read `BOOTSTRAP.md` for the
idea in one page and follow `skills/project-bootstrap/references/core/adoption.md` by hand.

Projects built on the kit run the linter and generator as
`python tools/check_docs.py --root . --fix` at the end of every session. It is Python 3.11+,
standard library only. `skills/project-bootstrap/scripts/hooks/README.md` shows how to run it
from a Stop hook, a pre-commit hook, or CI.

## Repository layout

- `BOOTSTRAP.md` — the idea and the machinery, one page each, with pointers into the skill.
- `skills/project-bootstrap/SKILL.md` — the guided procedure.
- `skills/project-bootstrap/references/core/` — document kinds, layers, lifecycle,
  long-horizon rules, parallel agents, tiers, adoption, lessons.
- `skills/project-bootstrap/references/profiles/` — six project profiles and how to pick one.
- `skills/project-bootstrap/assets/templates/` — the files a project copies in.
- `skills/project-bootstrap/scripts/` — `check_docs.py` and hook snippets.
- `tests/` — the linter's test suite and fixture project.
- `.claude-plugin/`, `hooks/` — Claude Code plugin manifests and the plugin Stop hook.

## Develop

- `python -m pytest tests -q` — test suite.
- `python skills/project-bootstrap/scripts/check_docs.py --root .` — lint this repo's own
  docs; must report zero errors and zero warnings.
````

- [ ] **Step 2: AGENTS.md**

Replace the whole file with:

````markdown
# AGENTS.md

This repository is the bootstrap kit itself — one Agent Skill at `skills/project-bootstrap/`
holding `references/core/`, `references/profiles/`, `assets/templates/` and
`scripts/check_docs.py` — not a project built on the kit. Read `BOOTSTRAP.md` first: it states
the idea, names the machinery, and points into the skill.

## Rules

- Every path any doc here cites must exist, and every `§N` cited must be a real numbered
  heading. Run `python skills/project-bootstrap/scripts/check_docs.py --root .` before ending
  a session — zero errors, always.
- Paths have three forms. Inside `skills/project-bootstrap/`, kit paths are relative to the
  skill root (`references/core/layers.md §1`) so the skill works when installed alone. At the
  repo root they are full (`skills/project-bootstrap/references/core/layers.md §1`). Paths in
  the project being bootstrapped are written `<project>/...`.
- Templates (`skills/project-bootstrap/assets/templates/*.md`) keep the exact field formats
  `scripts/check_docs.py` parses: status lines, ID forms, checkbox syntax. Changing a
  template's shape without updating the linter breaks every project that copies it.
- A change to what the linter checks adds a test to `tests/test_check_docs.py` and, where the
  change needs one, an edit to a fixture under `tests/fixture/`.
- No double-brace placeholders outside `skills/project-bootstrap/assets/templates/`.
  Elsewhere, a name that isn't fixed yet is written `<angle-bracketed>`.
- Section numbers (`## N. Title`) are contracts once another doc cites them — append a lettered
  section rather than renumbering.
- The version is `2.1.0` in `skills/project-bootstrap/SKILL.md` metadata,
  `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`; bump all three together.

## Commands

- `python -m pytest tests -q` — the linter's own test suite and the skill package tests.
- `python skills/project-bootstrap/scripts/check_docs.py --root .` — lint the kit's own docs;
  must report zero errors and zero warnings.
````

- [ ] **Step 3: LICENSE**

Create `LICENSE`:

```
MIT License

Copyright (c) 2026 NSpotGames

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 4: BOOTSTRAP.md**

First the mechanical prefix:

```bash
sed -i -E \
  -e 's#`core/#`skills/project-bootstrap/references/core/#g' \
  -e 's#`profiles/#`skills/project-bootstrap/references/profiles/#g' \
  BOOTSTRAP.md
```

Then two hand edits. The intro paragraph (lines 3–5) becomes:

```markdown
The entry point to this kit. Read this file first; it states the idea in one page, names the
machinery, and points into the skill at `skills/project-bootstrap/`, where the rules
(`references/core/`), profiles (`references/profiles/`), templates (`assets/templates/`) and
linter (`scripts/check_docs.py`) live. It contains no templates of its own.
```

Section 3 becomes:

```markdown
## 3. Start here

- New project → `skills/project-bootstrap/references/core/adoption.md §1`.
- Existing code → `skills/project-bootstrap/references/core/adoption.md §2`.
- Pick a profile in `skills/project-bootstrap/references/profiles/README.md`.
- Templates in `skills/project-bootstrap/assets/templates/`.
- Linter in `skills/project-bootstrap/scripts/check_docs.py`; hooks in
  `skills/project-bootstrap/scripts/hooks/README.md`.
- Agents with skills: `skills/project-bootstrap/SKILL.md`, or install it — see `README.md`.
```

Verify no old form remains: `grep -nE '`(core|profiles|templates|tools)/|skills/bootstrap' BOOTSTRAP.md` → no output.

- [ ] **Step 5: Lint and test**

```bash
python skills/project-bootstrap/scripts/check_docs.py --root .    # 0 error(s), 0 warning(s)
python -m pytest tests -q                                         # 64 passed
```

If the linter still reports anything, fix the cited path; do not add exclusions.

- [ ] **Step 6: Commit**

```bash
git add README.md AGENTS.md LICENSE BOOTSTRAP.md
git commit -m "docs: root README, AGENTS and BOOTSTRAP point into the skill; add MIT LICENSE

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: Plugin manifests, plugin Stop hook, and the skill package tests

**Files:**
- Create: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `hooks/hooks.json`, `hooks/stop.sh`
- Test: `tests/test_skill_package.py` (new)

**Interfaces:**
- Consumes: SKILL.md frontmatter from Task 3.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_skill_package.py`:

```python
"""Checks that skills/project-bootstrap/ is a valid, self-contained Agent Skill and that the
Claude plugin manifests agree with it."""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "project-bootstrap"
SKILL_MD = SKILL_DIR / "SKILL.md"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
HOOKS = ROOT / "hooks" / "hooks.json"
STOP_SH = ROOT / "hooks" / "stop.sh"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Backticked skill-relative paths: `references/...`, `assets/...`, `scripts/...`, with an
# optional ` §N.M` anchor before the closing backtick.
SKILL_PATH_RE = re.compile(r"`((?:references|assets|scripts)/[A-Za-z0-9_./<>-]*)(?:\s*§[\d.a-z]+)?`")


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


def frontmatter() -> dict[str, str]:
    text = _text(SKILL_MD)
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    block = text.split("---\n", 2)[1]
    out: dict[str, str] = {}
    parent = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith("  ") and parent:
            k, v = line.strip().split(":", 1)
            out[f"{parent}.{k.strip()}"] = v.strip().strip('"')
        else:
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if v:
                out[k] = v.strip('"')
                parent = None
            else:
                parent = k
    return out


def test_name_matches_directory_and_spec_rules():
    fm = frontmatter()
    assert fm["name"] == SKILL_DIR.name
    assert 1 <= len(fm["name"]) <= 64
    assert NAME_RE.match(fm["name"])


def test_description_is_present_and_bounded():
    fm = frontmatter()
    assert 1 <= len(fm["description"]) <= 1024


def test_skill_md_is_under_500_lines():
    assert len(_text(SKILL_MD).splitlines()) < 500


def test_every_skill_relative_path_in_skill_md_exists():
    missing = []
    for m in SKILL_PATH_RE.finditer(_text(SKILL_MD)):
        p = m.group(1)
        if "<" in p:
            continue  # generic name such as references/profiles/<name>.md
        if not (SKILL_DIR / p.rstrip("/")).exists():
            missing.append(p)
    assert missing == []


def test_version_agrees_across_skill_and_manifests():
    fm = frontmatter()
    plugin = json.loads(_text(PLUGIN))
    market = json.loads(_text(MARKETPLACE))
    assert fm["metadata.version"] == plugin["version"] == market["plugins"][0]["version"]


def test_plugin_and_marketplace_name_the_skill():
    plugin = json.loads(_text(PLUGIN))
    market = json.loads(_text(MARKETPLACE))
    assert plugin["name"] == "project-bootstrap"
    assert market["plugins"][0]["name"] == "project-bootstrap"
    assert market["plugins"][0]["source"] == "./"


def test_hooks_json_registers_the_stop_script():
    hooks = json.loads(_text(HOOKS))
    stop = hooks["hooks"]["Stop"]
    cmd = stop[0]["hooks"][0]["command"]
    assert "hooks/stop.sh" in cmd
    assert "${CLAUDE_PLUGIN_ROOT}" in cmd


def _run_stop(cwd: Path, stdin: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(cwd)}
    return subprocess.run(["sh", str(STOP_SH)], input=stdin, capture_output=True, text=True, cwd=cwd, env=env)


needs_sh = pytest.mark.skipif(shutil.which("sh") is None, reason="no sh on PATH")


@needs_sh
def test_stop_hook_exits_zero_when_stop_hook_active(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    r = _run_stop(tmp_path, '{"stop_hook_active": true}')
    assert r.returncode == 0, r.stderr


@needs_sh
def test_stop_hook_exits_zero_when_project_has_no_linter(tmp_path):
    r = _run_stop(tmp_path, "{}")
    assert r.returncode == 0, r.stderr


@needs_sh
def test_stop_hook_blocks_when_project_linter_fails(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "check_docs.py").write_text("import sys; sys.exit(1)\n", encoding="utf-8")
    r = _run_stop(tmp_path, "{}")
    assert r.returncode == 2
    assert "check_docs found errors" in r.stdout + r.stderr


def test_skill_directory_works_when_copied_alone(tmp_path):
    copy = tmp_path / "project-bootstrap"
    shutil.copytree(SKILL_DIR, copy, ignore=shutil.ignore_patterns("__pycache__"))
    for m in SKILL_PATH_RE.finditer(_text(copy / "SKILL.md")):
        p = m.group(1)
        if "<" not in p:
            assert (copy / p.rstrip("/")).exists(), p
    r = subprocess.run([sys.executable, "scripts/check_docs.py", "--help"], cwd=copy, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_skill_package.py -q`
Expected: the manifest and hook tests fail with `FileNotFoundError`; the frontmatter and copied-alone tests pass (Task 3 wrote the frontmatter).

- [ ] **Step 3: Create the manifests and hook**

`.claude-plugin/plugin.json`:
```json
{
  "name": "project-bootstrap",
  "displayName": "Project Bootstrap",
  "version": "2.1.0",
  "description": "Docs-as-contract bootstrap for agent-driven projects: design docs, milestones, plans, ADRs, and a linter that keeps them true.",
  "author": { "name": "NSpotGames", "url": "https://github.com/NSpotGames" },
  "homepage": "https://github.com/NSpotGames/agentic-project-bootstrap",
  "repository": "https://github.com/NSpotGames/agentic-project-bootstrap",
  "license": "MIT",
  "keywords": ["skills", "bootstrap", "documentation", "planning", "adr", "milestones", "workflow"]
}
```

`.claude-plugin/marketplace.json`:
```json
{
  "name": "agentic-project-bootstrap",
  "owner": { "name": "NSpotGames", "url": "https://github.com/NSpotGames" },
  "plugins": [
    {
      "name": "project-bootstrap",
      "source": "./",
      "description": "Docs-as-contract bootstrap for agent-driven projects.",
      "version": "2.1.0"
    }
  ]
}
```

`hooks/hooks.json`:
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/stop.sh\""
          }
        ]
      }
    ]
  }
}
```

`hooks/stop.sh` (LF line endings; `git update-index --chmod=+x hooks/stop.sh` after adding):
```sh
#!/bin/sh
# Plugin-level Stop hook. Runs the project's own copy of the linter, and only in projects
# that have one, so repos not built on the kit are never linted.
input=$(cat)
case "$input" in *'"stop_hook_active": true'*) exit 0;; esac
root="${CLAUDE_PROJECT_DIR:-.}"
[ -f "$root/tools/check_docs.py" ] || exit 0
py=python3
command -v python3 >/dev/null 2>&1 || py=python
"$py" "$root/tools/check_docs.py" --root "$root" \
  || { echo 'check_docs found errors; fix them before ending the session'; exit 2; }
```

- [ ] **Step 4: Run the tests**

Run: `python -m pytest tests -q`
Expected: 75 passed (64 + 11), or 72 passed and 3 skipped if no `sh` is on PATH.

Run: `python skills/project-bootstrap/scripts/check_docs.py --root .` → `0 error(s), 0 warning(s)`.

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json hooks/hooks.json hooks/stop.sh tests/test_skill_package.py
git update-index --chmod=+x hooks/stop.sh
git commit -m "plugin: Claude Code manifests and guarded Stop hook; skill package tests

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: Acceptance pass

**Files:**
- Modify only if a check fails.

- [ ] **Step 1: Run every acceptance item from the spec (§13)**

```bash
python -m pytest tests -q
python skills/project-bootstrap/scripts/check_docs.py --root .
python skills/project-bootstrap/scripts/check_docs.py --root tests/fixture/valid --fix && git status --short tests/fixture   # no output
grep -rnE '`(core|profiles|templates|tools)/[^`]*\.md' skills/project-bootstrap/references skills/project-bootstrap/SKILL.md   # no output
ls core profiles templates tools skills/bootstrap 2>&1 | grep -c 'No such file'   # 5
git log --oneline --follow -- skills/project-bootstrap/references/core/layers.md | wc -l   # > 1
grep -h '"version"' .claude-plugin/plugin.json .claude-plugin/marketplace.json; grep 'version:' skills/project-bootstrap/SKILL.md   # all 2.1.0
python -c "import json;[json.load(open(p)) for p in ['.claude-plugin/plugin.json','.claude-plugin/marketplace.json','hooks/hooks.json']];print('json ok')"
```

Item 7 (copied alone) and item 8 (hook exit codes) are covered by `tests/test_skill_package.py`.

- [ ] **Step 2: Skill-directory hygiene**

```bash
find skills/project-bootstrap -name '__pycache__' -o -name '*.pyc'   # no output; if any, delete (they are git-ignored)
git status --short   # clean
```

- [ ] **Step 3: Report**

Write the results of every command above into the task report. No commit unless a fix was needed; if one was, commit it with a message naming the acceptance item.

---

## Self-review notes

- Spec §5 kinds 1–3 → Tasks 2, 3, 4. §6 → Task 1. §7 → Task 3. §8a–d → Tasks 4 (README) and 5 (manifests, hook). §9 → Task 4 and Task 2 (config). §10 → Tasks 1, 2, 5. §11 (tag) happens after merge, outside this plan. §13 → Task 6.
- `_resolve_citation` already tries `citing.parent`, so `SKILL.md` citing `references/core/x.md` would resolve without Task 1; `citation_roots` is still needed for `references/core/a.md` citing `references/core/b.md`, which is most of the 130 citations.
- Only `.md` paths are citations (CITE_RE ends in `\.md`), so bare `tools/check_docs.py` and `tools/hooks/stop.sh` command mentions never produce E001 and are left as target-project commands.
- `check_placeholders` scopes to root files and `docs/`, so `{{token}}` mentions in SKILL.md and the moved templates stay out of E005's scope, as they are today.
