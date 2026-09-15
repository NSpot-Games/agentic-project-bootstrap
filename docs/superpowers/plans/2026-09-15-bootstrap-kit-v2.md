# Bootstrap Kit v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the single-file bootstrap kit into a repo of core docs, profiles, templates, a tested doc linter/generator, and a `/bootstrap` skill, per the v2 spec.

**Architecture:** Two parts. Part 1 (Tasks 1–9) builds `tools/check_docs.py` test-first against a fixture project, because every later doc task is verified by running the linter. Part 2 (Tasks 10–18) writes the kit's documents: templates first (the doc tasks cite them), then core, profiles, skill, and finally the entry point, the kit's own config, and deletion of the v1 file.

**Tech Stack:** Python 3.11+ standard library (`re`, `pathlib`, `tomllib`, `dataclasses`, `datetime`, `argparse`), pytest for tests. Markdown for everything else.

**Spec:** `docs/superpowers/specs/2026-09-15-bootstrap-kit-v2-design.md` — read it before starting any task. Doc tasks below give the outline and the must-contain rules; the prose comes from the spec section cited. Do not invent rules the spec does not state.

## Global Constraints

- Python 3.11 or newer. Standard library only in `tools/check_docs.py`. pytest only in tests.
- All files UTF-8, LF line endings. The linter normalises CRLF on read and writes LF.
- Markdown separators inside IDs and headings use the em dash `—` (U+2014) with one space on each side: `M1-03 — Title`.
- One `**Field:** value` per line in milestone, plan, and ADR files. Never two fields on one line.
- Every `{{token}}` used in `templates/` must appear in `templates/README.md`.
- `BOOTSTRAP.md` under 250 lines. `templates/AGENTS.md` under 120 lines.
- Generic mentions of a path convention in prose use angle brackets for the variable part: `<file>.md §N.M`, `M<n>.md`, `<NNNN>-slug.md`, never `path.md §N.M` or `NNNN-slug.md`, so the linter does not try to resolve them.
- Commit after every task with the message given in the task. Commit messages end with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- Verification runs from the repo root: `python tools/check_docs.py --root .` and `python -m pytest tools/tests -q`.

---

## Part 1 — The linter and generator

### File map for Part 1

- `tools/check_docs.py` — single module. Sections in order: constants and dataclasses; config; markdown helpers; parsers (milestone, plan, ADR, roadmap); project loader; checks (one function per group); generators; `run`; `main`.
- `tools/tests/test_check_docs.py` — pytest. Imports `check_docs` by path. Helper `make_project` copies the valid fixture to `tmp_path` and applies string edits.
- `tools/tests/fixture/valid/` — a minimal standard-tier project that must pass with zero findings.
- `tools/hooks/README.md` — hook snippets.

Public interface of `check_docs.py` used by tests and later tasks:

```python
def load_config(root: Path) -> Config
def load_project(cfg: Config) -> Project
def check(project: Project) -> list[Finding]
def generate(project: Project) -> dict[str, str]        # rel path -> content
def run(root: Path, fix: bool = False, stale_hours: float | None = None) -> list[Finding]
def main(argv: list[str] | None = None) -> int
```

---

### Task 1: Fixture project, module skeleton, config loading

**Files:**
- Create: `tools/check_docs.py`
- Create: `tools/tests/test_check_docs.py`
- Create: `tools/tests/conftest.py`
- Create: `tools/tests/fixture/valid/**` (listed below)

**Interfaces:**
- Produces: `Finding`, `Config`, `load_config`, `run` (returns `[]` for now), `main`. Tests rely on `make_project(tmp_path, edits)` and `codes(findings)` helpers.

- [ ] **Step 1: Create the valid fixture project**

Create each file exactly. Paths are relative to `tools/tests/fixture/valid/`.

`AGENTS.md`
```markdown
# AGENTS.md

**Fixture** is a minimal project used to test the doc linter. The rule that shapes everything: **docs and code agree**.

## Read first
1. `DOCS.md` 2. the generated current-focus file under docs/ 3. `docs/design/product-design.md`

## How to work
Open the current-focus file, take a claimed feature or claim the next unclaimed one, follow `docs/WORKFLOW.md`.
```

(The fixture does not cite `docs/CURRENT.md` because that file is generated in Task 8; citing it earlier would fail E001.)

`CLAUDE.md`
```markdown
@AGENTS.md
```

`DOCS.md`
```markdown
# DOCS.md

## 1. Map
- `docs/design/product-design.md` — what and why
- `docs/roadmap.md` — direction
- `docs/milestones/` — progress, source of truth
- `docs/plans/` — one plan per feature
- `docs/decisions/` — ADRs
- `docs/evidence/` — measurements
- `docs/OPEN-QUESTIONS.md` — unresolved questions

## 2. Conventions
Cite by path and section: `docs/design/product-design.md §2.1`.
```

`README.md`
```markdown
# Fixture
A minimal project used to test `tools/check_docs.py`. Docs start at `DOCS.md`.
```

`docs/.check_docs.toml`
```toml
stale_hours = 876000
allow_tbd_in = ["docs/OPEN-QUESTIONS.md"]
```

`docs/WORKFLOW.md`
```markdown
# Workflow

## 1. Lifecycle
Ground, Brainstorm, Plan, Execute, Close. See `docs/design/product-design.md §3` for success criteria.
```

`docs/GLOSSARY.md`
```markdown
# Glossary

## Core
**Instance** — one authored unit of content. Lives in `docs/design/product-design.md §2.1`.
```

`docs/OPEN-QUESTIONS.md`
```markdown
# Open questions

| Question | Raised in | Blocks | Owner | Needed by |
|---|---|---|---|---|
| How many instances ship in v1? | `docs/design/product-design.md §3` | M2 | TBD | M1 close |
```

`docs/design/product-design.md`
```markdown
# Fixture product design
**Project:** Fixture
**Status:** stable
**Audience:** anyone testing the linter
Related: `docs/roadmap.md`

---

## 1. One-liner
A tiny product that exists so the linter has something to check.

## 2. Pillars
### 2.1 Instances are authored data
Everything the user sees comes from an instance.
### 2.1a Instances are validated
Every instance passes the validator before it ships.

## 3. Success criteria
- P1: one instance plays end to end with zero validator errors.

## Changelog
- 2026-09-15 — created.
```

`docs/roadmap.md`
```markdown
# Roadmap
**No checkboxes here.** Scope and progress live in `docs/milestones/`.

## Principles
- Every milestone ends in something runnable or measurable.

## P1 — Playable core
**Status:** active
**Exit:** one instance plays end to end; see `docs/design/product-design.md §3`.

### M0 — Foundations
Goal: schema and one example instance.

### M1 — First playable
Goal: the example instance runs in the runtime.

### M2 — Authoring tool
**Status:** sketch
Goal: an editor for instances. Exit: TBD.

## P2 — Content at scale
**Status:** sketch
**Exit:** TBD

### M3 — Ten instances
Goal: TBD.

## Explicitly deferred
- Multiplayer.
```

`docs/milestones/M0.md`
```markdown
# M0 — Foundations
**Status:** done
**Goal:** schema and one example instance.
**Exit criteria:** the example instance parses and every cross-reference resolves.
**Evidence of exit:** `docs/evidence/M0-exit.md`
**Depends on:**

## Features
- [x] M0-01 — Fold schema gaps — `docs/plans/M0/M0-01-fold-schema-gaps.md`
- ~~M0-02 — Old thing~~ moved to M1-02

## Notes
```

`docs/milestones/M1.md`
```markdown
# M1 — First playable
**Status:** in progress
**Goal:** the example instance runs in the runtime.
**Exit criteria:** one instance plays end to end with zero validator errors.
**Evidence of exit:**
**Depends on:** M0

## Features
- [ ] M1-01 — Runtime loop — `docs/plans/M1/M1-01-runtime-loop.md` (depends on: M0-01)
- [ ] M1-02 — Old thing, re-homed

## Notes
```

`docs/plans/M0/M0-01-fold-schema-gaps.md`
```markdown
# M0-01 — Fold schema gaps
**Status:** done
**Milestone:** M0
**Branch:** feat/M0-01-fold-schema-gaps
**Design docs:** `docs/design/product-design.md §2.1`
**ADRs:** 0001
**Depends on:**

## Sessions
- 2026-09-10T09:00Z — claude-code — feat/M0-01-fold-schema-gaps

## Objective
Fold the ten gaps found by the example instance into the data model.

## Current state
- Example instance exists; validator reports ten missing fields.

## Approach
Add the fields, re-run the validator.

## Tasks
- [x] T1 — Add fields. **Verify:** `python tools/validate.py`

## Progress notes
- 2026-09-10 — all fields added, validator green.

## Verification log
- T1: `python tools/validate.py` → `0 errors`
```

`docs/plans/M0/M0-02-old-thing.md`
```markdown
# M0-02 — Old thing
**Status:** moved to M1-02
**Milestone:** M0
**Branch:**
**Design docs:**
**ADRs:**
**Depends on:**

## Sessions

## Objective
Superseded. See M1-02.
```

`docs/plans/M1/M1-01-runtime-loop.md`
```markdown
# M1-01 — Runtime loop
**Status:** in progress
**Milestone:** M1
**Branch:** feat/M1-01-runtime-loop
**Design docs:** `docs/design/product-design.md §2.1a`
**ADRs:**
**Depends on:** M0-01

## Sessions
- 2026-09-15T09:00Z — claude-code — feat/M1-01-runtime-loop

## Objective
Run one instance end to end.

## Current state
- Validator green on the example instance.

## Approach
Load, step, render.

## Tasks
- [x] T1 — Loader. **Verify:** `pytest tests/test_loader.py`
- [ ] T2 — Step function. **Verify:** `pytest tests/test_step.py`

## Progress notes
- 2026-09-15 — loader done; step function next.

## Verification log
- T1: `pytest tests/test_loader.py` → `3 passed`
```

`docs/decisions/AGENTS.md`
```markdown
# docs/decisions/ — Architecture Decision Records
Design docs say what; ADRs say why. One decision per file, `<NNNN>-decision-as-a-sentence.md`.
```

`docs/decisions/0001-filenames-are-kebab-case-and-unnumbered.md`
```markdown
# 0001. Filenames are kebab-case and unnumbered
**Status:** accepted
**Date:** 2026-09-10
**Deciders:** the team
**Related:** `docs/design/product-design.md §1`

## Context
Numbered prefixes break cross-references on reorder.

## Decision
Kebab-case, unnumbered, reading order stated in `DOCS.md`.

## Alternatives considered
Numbered prefixes.

## Consequences
Reading order is documented, not encoded.
```

`docs/evidence/M0-exit.md`
```markdown
# M0 exit evidence
Validator run on 2026-09-10: `0 errors, 0 warnings`.
```

- [ ] **Step 2: Write the test helpers and first tests**

`tools/tests/conftest.py`
```python
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
```

`tools/tests/test_check_docs.py`
```python
import shutil
from pathlib import Path

import pytest

import check_docs as cd

FIXTURE = Path(__file__).parent / "fixture" / "valid"


def make_project(tmp_path: Path, edits: dict[str, tuple[str, str]] | None = None) -> Path:
    """Copy the valid fixture to tmp_path/proj and apply {relpath: (old, new)} replacements."""
    root = tmp_path / "proj"
    shutil.copytree(FIXTURE, root)
    for relpath, (old, new) in (edits or {}).items():
        p = root / relpath
        text = p.read_text(encoding="utf-8")
        assert old in text, f"{relpath} does not contain {old!r}"
        p.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
    return root


def codes(findings) -> list[str]:
    return sorted(f.code for f in findings)


def errors(findings) -> list[str]:
    return sorted(f.code for f in findings if f.is_error)


def test_valid_fixture_has_no_errors(tmp_path):
    root = make_project(tmp_path)
    assert errors(cd.run(root)) == []


def test_load_config_defaults(tmp_path):
    cfg = cd.load_config(tmp_path)
    assert cfg.stale_hours == 24
    assert cfg.allow_tbd_in == ["docs/OPEN-QUESTIONS.md"]
    assert cfg.codename_placeholder is None
    assert cfg.tier == "auto"


def test_load_config_reads_toml(tmp_path):
    root = make_project(tmp_path)
    cfg = cd.load_config(root)
    assert cfg.stale_hours == 876000


def test_finding_str():
    f = cd.Finding("E001", "docs/a.md", 3, "cited file missing: b.md")
    assert str(f) == "docs/a.md:3: E001 cited file missing: b.md"
    assert f.is_error
    assert not cd.Finding("W001", "x", 1, "m").is_error
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tools/tests -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'check_docs'`

- [ ] **Step 4: Write the module skeleton**

`tools/check_docs.py`
```python
#!/usr/bin/env python3
"""check_docs — doc linter and index generator for bootstrap-kit projects.

Usage: check_docs.py [--fix] [--root PATH] [--stale-hours N]
Exit status 1 if any E-code finding, else 0. Warnings (W-codes) print but pass.
"""
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

GENERATED_MARKER = "<!-- generated by tools/check_docs.py --fix; do not edit by hand -->"
DEFAULT_EXCLUDE = (".git", "node_modules", ".venv", "__pycache__")
PLACEHOLDER_SCOPE_ROOT_FILES = ("AGENTS.md", "CLAUDE.md", "DOCS.md", "README.md")
ACTIVE_MILESTONE_STATUSES = ("planned", "in progress", "done")


# --------------------------------------------------------------------------- data


@dataclass
class Finding:
    code: str
    path: str
    line: int
    message: str

    @property
    def is_error(self) -> bool:
        return self.code.startswith("E")

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.code} {self.message}"


@dataclass
class Config:
    root: Path
    codename_placeholder: str | None = None
    stale_hours: float = 24
    allow_tbd_in: list[str] = field(default_factory=lambda: ["docs/OPEN-QUESTIONS.md"])
    citation_exclude: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=lambda: list(DEFAULT_EXCLUDE))
    tier: str = "auto"

    @property
    def docs(self) -> Path:
        return self.root / "docs"


def load_config(root: Path) -> Config:
    cfg = Config(root=Path(root))
    path = cfg.docs / ".check_docs.toml"
    if path.exists():
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        for key in ("codename_placeholder", "stale_hours", "allow_tbd_in", "citation_exclude", "tier"):
            if key in data:
                setattr(cfg, key, data[key])
        if "exclude" in data:
            cfg.exclude = list(DEFAULT_EXCLUDE) + list(data["exclude"])
    return cfg


# --------------------------------------------------------------------------- run / main


def run(root: Path, fix: bool = False, stale_hours: float | None = None) -> list[Finding]:
    cfg = load_config(Path(root))
    if stale_hours is not None:
        cfg.stale_hours = stale_hours
    return []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Doc linter and index generator.")
    ap.add_argument("--root", default=".", help="project root (default: current directory)")
    ap.add_argument("--fix", action="store_true", help="regenerate index files and CURRENT.md")
    ap.add_argument("--stale-hours", type=float, default=None, help="claim staleness threshold")
    args = ap.parse_args(argv)
    findings = run(Path(args.root).resolve(), fix=args.fix, stale_hours=args.stale_hours)
    for f in sorted(findings, key=lambda f: (f.path, f.line, f.code)):
        print(f)
    n_err = sum(1 for f in findings if f.is_error)
    n_warn = len(findings) - n_err
    print(f"{n_err} error(s), {n_warn} warning(s)")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tools/tests -q`
Expected: `4 passed`

- [ ] **Step 6: Commit**

```bash
git add tools/
git commit -m "check_docs: skeleton, config loading, valid fixture project

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Citation checks E001 and E002

**Files:**
- Modify: `tools/check_docs.py` (add markdown helpers and `check_citations`; wire into `run`)
- Modify: `tools/tests/test_check_docs.py`

**Interfaces:**
- Produces: `read_text(path) -> str`, `rel(cfg, path) -> str`, `iter_md(cfg) -> list[Path]`, `numbered_headings(text) -> set[str]`, `line_of(text, pos) -> int`, `check_citations(cfg, md_files) -> list[Finding]`. `run` now calls `check_citations`.

- [ ] **Step 1: Write failing tests**

Append to `tools/tests/test_check_docs.py`:
```python
def test_e001_missing_cited_file(tmp_path):
    root = make_project(tmp_path, {
        "docs/WORKFLOW.md": ("`docs/design/product-design.md §3`", "`docs/design/missing.md §3`"),
    })
    assert "E001" in codes(cd.run(root))


def test_e002_missing_section(tmp_path):
    root = make_project(tmp_path, {
        "docs/WORKFLOW.md": ("`docs/design/product-design.md §3`", "`docs/design/product-design.md §9.9`"),
    })
    assert "E002" in codes(cd.run(root))


def test_citation_resolves_relative_to_citing_file(tmp_path):
    root = make_project(tmp_path, {
        "docs/WORKFLOW.md": ("`docs/design/product-design.md §3`", "`design/product-design.md §3`"),
    })
    assert errors(cd.run(root)) == []


def test_citation_with_lettered_anchor_resolves(tmp_path):
    root = make_project(tmp_path)
    # M1-01 plan cites §2.1a which exists
    assert errors(cd.run(root)) == []


def test_template_tokens_angle_brackets_and_urls_are_not_citations(tmp_path):
    root = make_project(tmp_path, {
        "docs/GLOSSARY.md": ("## Core", "## Core\nWrite `<product>-design.md`, `M<n>.md`, `<file>.md §N.M`, "
                                        "or see https://example.com/guide.md for more.\n"),
    })
    assert not any(c in ("E001", "E002") for c in codes(cd.run(root)))


def test_numbered_headings():
    text = "# T\n## 1. One\n### 1.2 Two\n### 1.2a Two-a\n## Changelog\n"
    assert cd.numbered_headings(text) == {"1", "1.2", "1.2a"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/tests -q`
Expected: `test_e001_missing_cited_file`, `test_e002_missing_section`, `test_numbered_headings` FAIL (no E-codes returned / `AttributeError: numbered_headings`).

- [ ] **Step 3: Implement helpers and the citation check**

Insert after the config section in `tools/check_docs.py`:
```python
# --------------------------------------------------------------------------- markdown helpers

HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*$", re.M)
NUMBERED_RE = re.compile(r"^(\d+(?:\.\d+)*[a-z]?)\.?(?=\s)")
# A citation is `path/to/file.md` optionally followed by `§N.M`. The lookbehind rejects
# tokens glued to template braces, angle brackets, a hyphen, a slash, a dot or a colon,
# so `{{x}}-design.md`, `M<n>.md`, `<file>.md` and `https://example.com/x.md` never match.
CITE_RE = re.compile(
    r"(?<![\w{}<>\-/.:])((?:[\w.-]+/)*[A-Za-z0-9_][\w.-]*\.md)(?:[ \t]*§[ \t]*(\d+(?:\.\d+)*[a-z]?))?"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def rel(cfg: Config, path: Path) -> str:
    return path.resolve().relative_to(cfg.root.resolve()).as_posix()


def _excluded(cfg: Config, relpath: str) -> bool:
    parts = relpath.split("/")
    for e in cfg.exclude:
        e = e.strip("/")
        if "/" in e:
            if relpath == e or relpath.startswith(e + "/"):
                return True
        elif e in parts:
            return True
    return False


def iter_md(cfg: Config) -> list[Path]:
    return [p for p in sorted(cfg.root.rglob("*.md")) if not _excluded(cfg, rel(cfg, p))]


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def numbered_headings(text: str) -> set[str]:
    out: set[str] = set()
    for m in HEADING_RE.finditer(text):
        n = NUMBERED_RE.match(m.group(2) + " ")
        if n:
            out.add(n.group(1))
    return out


def first_heading(text: str) -> str:
    m = HEADING_RE.search(text)
    return m.group(2).strip() if m else ""


def field_value(text: str, name: str) -> str | None:
    """Value of a `**Name:** value` line, or None if absent. Empty and dash values become ''."""
    m = re.search(rf"^\*\*{re.escape(name)}:\*\*[ \t]*(.*?)[ \t]*$", text, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    return "" if v in ("", "—", "-", "n/a") else v


def section_body(text: str, title: str) -> str:
    """Body of the `## title` section, up to the next `## ` heading."""
    m = re.search(rf"^## {re.escape(title)}[ \t]*$\n?(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


# --------------------------------------------------------------------------- checks: citations


def _resolve_citation(cfg: Config, citing: Path, target: str) -> Path | None:
    for base in (citing.parent, cfg.root, cfg.docs):
        cand = base / target
        if cand.is_file():
            return cand
    return None


def check_citations(cfg: Config, md_files: list[Path]) -> list[Finding]:
    out: list[Finding] = []
    heading_cache: dict[Path, set[str]] = {}
    for path in md_files:
        r = rel(cfg, path)
        if any(r == x.strip("/") or r.startswith(x.strip("/") + "/") for x in cfg.citation_exclude):
            continue
        text = read_text(path)
        for m in CITE_RE.finditer(text):
            target, anchor = m.group(1), m.group(2)
            resolved = _resolve_citation(cfg, path, target)
            if resolved is None:
                out.append(Finding("E001", r, line_of(text, m.start()), f"cited file missing: {target}"))
                continue
            if anchor:
                if resolved not in heading_cache:
                    heading_cache[resolved] = numbered_headings(read_text(resolved))
                if anchor not in heading_cache[resolved]:
                    out.append(Finding("E002", r, line_of(text, m.start()),
                                       f"no heading §{anchor} in {target}"))
    return out
```

Replace the body of `run` with:
```python
def run(root: Path, fix: bool = False, stale_hours: float | None = None) -> list[Finding]:
    cfg = load_config(Path(root))
    if stale_hours is not None:
        cfg.stale_hours = stale_hours
    md_files = iter_md(cfg)
    findings: list[Finding] = []
    findings += check_citations(cfg, md_files)
    return findings
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/tests -q`
Expected: `10 passed`

- [ ] **Step 5: Commit**

```bash
git add tools/
git commit -m "check_docs: E001/E002 citation and section-anchor checks

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Parsers and project loader

**Files:**
- Modify: `tools/check_docs.py` (add dataclasses `Feature`, `Milestone`, `Plan`, `Adr`, `Phase`, `Roadmap`, `Project`; parsers; `detect_tier`; `load_project`)
- Modify: `tools/tests/test_check_docs.py`

**Interfaces:**
- Produces:
  - `Feature(id, title, ticked, moved_to, plan_path, depends_on, line)`
  - `Milestone(id, path, title, status, exit_criteria, evidence, depends_on, features)` with method `feature(fid) -> Feature | None`
  - `Plan(id, path, title, status, moved_to, milestone, depends_on, stamps: list[tuple[datetime, str]], last_note, tasks_open: int)`
  - `Adr(number, path, title, status)`
  - `Phase(id, title, status, line, milestones: list[str])`
  - `Roadmap(path, phases, milestone_titles: dict[str, str], sketch_ranges: list[tuple[int, int]], order: list[str])`
  - `Project(cfg, tier, md_files, milestones: dict[str, Milestone], plans: dict[str, Plan], adrs: list[Adr], roadmap: Roadmap | None)` with `status_of(mid) -> str | None`, `feature_of(fid) -> tuple[Milestone, Feature] | None`, `milestone_order() -> list[str]`
  - `detect_tier(cfg) -> str` returning `"standard" | "lite" | "minimal"`
  - `load_project(cfg) -> Project`
  - `parse_stamp(s) -> datetime | None`

- [ ] **Step 1: Write failing tests**

Append:
```python
def test_parse_milestones(tmp_path):
    root = make_project(tmp_path)
    proj = cd.load_project(cd.load_config(root))
    assert proj.tier == "standard"
    m0, m1 = proj.milestones["M0"], proj.milestones["M1"]
    assert m0.status == "done" and m0.evidence == "`docs/evidence/M0-exit.md`"
    assert m1.status == "in progress" and m1.depends_on == ["M0"]
    f = m1.feature("M1-01")
    assert f.title == "Runtime loop" and not f.ticked
    assert f.plan_path == "docs/plans/M1/M1-01-runtime-loop.md" and f.depends_on == ["M0-01"]
    assert m0.feature("M0-01").ticked
    assert m0.feature("M0-02").moved_to == "M1-02"


def test_parse_plans(tmp_path):
    root = make_project(tmp_path)
    proj = cd.load_project(cd.load_config(root))
    p = proj.plans["M1-01"]
    assert p.status == "in progress" and p.milestone == "M1" and p.depends_on == ["M0-01"]
    assert len(p.stamps) == 1 and p.stamps[0][1] == "claude-code"
    assert p.stamps[0][0].isoformat() == "2026-09-15T09:00:00+00:00"
    assert p.last_note == "2026-09-15 — loader done; step function next."
    assert p.tasks_open == 1
    moved = proj.plans["M0-02"]
    assert moved.status == "moved" and moved.moved_to == "M1-02"


def test_parse_adrs_and_roadmap(tmp_path):
    root = make_project(tmp_path)
    proj = cd.load_project(cd.load_config(root))
    assert [a.number for a in proj.adrs] == ["0001"]
    assert proj.adrs[0].status == "accepted"
    rm = proj.roadmap
    assert [p.id for p in rm.phases] == ["P1", "P2"]
    assert rm.phases[0].status == "active" and rm.phases[0].milestones == ["M0", "M1", "M2"]
    assert rm.order == ["M0", "M1", "M2", "M3"]
    assert proj.status_of("M2") == "sketch" and proj.status_of("M3") == "sketch"
    assert proj.status_of("M1") == "in progress" and proj.status_of("M9") is None
    # sketch ranges cover the M2 section, the whole P2 section
    assert any(a <= 19 <= b for a, b in rm.sketch_ranges)   # "Exit: TBD." line of M2
    assert any(a <= 26 <= b for a, b in rm.sketch_ranges)   # "Goal: TBD." line of M3


def test_parse_stamp_variants():
    assert cd.parse_stamp("2026-09-15T09:00Z").isoformat() == "2026-09-15T09:00:00+00:00"
    assert cd.parse_stamp("2026-09-15").isoformat() == "2026-09-15T00:00:00+00:00"
    assert cd.parse_stamp("2026-09-15T09:00:00+02:00").utcoffset().total_seconds() == 7200
    assert cd.parse_stamp("yesterday") is None


def test_detect_tier(tmp_path):
    root = make_project(tmp_path)
    assert cd.detect_tier(cd.load_config(root)) == "standard"
    shutil.rmtree(root / "docs" / "milestones")
    assert cd.detect_tier(cd.load_config(root)) == "lite"
    (root / "docs" / "roadmap.md").unlink()
    assert cd.detect_tier(cd.load_config(root)) == "minimal"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/tests -q`
Expected: 5 new tests FAIL with `AttributeError` (no `load_project`, `parse_stamp`, `detect_tier`).

- [ ] **Step 3: Implement dataclasses, parsers, loader**

Insert after the markdown helpers and before the citation check:
```python
# --------------------------------------------------------------------------- model


@dataclass
class Feature:
    id: str
    title: str
    ticked: bool
    moved_to: str | None
    plan_path: str | None
    depends_on: list[str]
    line: int


@dataclass
class Milestone:
    id: str
    path: Path
    title: str
    status: str
    exit_criteria: str
    evidence: str
    depends_on: list[str]
    features: list[Feature]

    def feature(self, fid: str) -> Feature | None:
        return next((f for f in self.features if f.id == fid), None)


@dataclass
class Plan:
    id: str
    path: Path
    title: str
    status: str
    moved_to: str | None
    milestone: str
    depends_on: list[str]
    stamps: list[tuple[datetime, str]]
    last_note: str
    tasks_open: int


@dataclass
class Adr:
    number: str
    path: Path
    title: str
    status: str


@dataclass
class Phase:
    id: str
    title: str
    status: str
    line: int
    milestones: list[str] = field(default_factory=list)


@dataclass
class Roadmap:
    path: Path
    phases: list[Phase]
    milestone_titles: dict[str, str]
    sketch_ranges: list[tuple[int, int]]
    order: list[str]


@dataclass
class Project:
    cfg: Config
    tier: str
    md_files: list[Path]
    milestones: dict[str, Milestone]
    plans: dict[str, Plan]
    adrs: list[Adr]
    roadmap: Roadmap | None

    def status_of(self, mid: str) -> str | None:
        if mid in self.milestones:
            return self.milestones[mid].status
        if self.roadmap and mid in self.roadmap.milestone_titles:
            return "sketch"
        return None

    def feature_of(self, fid: str) -> tuple[Milestone, Feature] | None:
        for m in self.milestones.values():
            f = m.feature(fid)
            if f:
                return m, f
        return None

    def milestone_order(self) -> list[str]:
        ordered = list(self.roadmap.order) if self.roadmap else []
        for mid in sorted(self.milestones, key=lambda s: int(s[1:])):
            if mid not in ordered:
                ordered.append(mid)
        return ordered


# --------------------------------------------------------------------------- parsers

ID_LIST_RE = re.compile(r"\bM\d+(?:-\d+)?\b")
FEATURE_RE = re.compile(
    r"^- \[([ xX])\] (M\d+-\d+) — (.*?)(?: — `([^`]+)`)?(?: \(depends on: ([^)]*)\))?[ \t]*$", re.M
)
MOVED_FEATURE_RE = re.compile(r"^- ~~(M\d+-\d+) — (.*?)~~ moved to (M\d+-\d+)[ \t]*$", re.M)
SESSION_RE = re.compile(r"^- (\S+)(?: — ([^—\n]*?))?(?: — ([^\n]*))?[ \t]*$", re.M)
TASK_RE = re.compile(r"^- \[([ xX])\] T\d+", re.M)
ADR_FILE_RE = re.compile(r"^(\d{4})-.+\.md$")


def parse_ids(value: str | None) -> list[str]:
    return ID_LIST_RE.findall(value or "")


def _id_and_title(heading: str, pattern: str, fallback_id: str) -> tuple[str, str]:
    m = re.match(rf"({pattern})\s+—\s+(.*)$", heading)
    if m:
        return m.group(1), m.group(2).strip()
    return fallback_id, heading


def parse_milestone(path: Path) -> Milestone:
    text = read_text(path)
    mid, title = _id_and_title(first_heading(text), r"M\d+", path.stem)
    features: list[Feature] = []
    for m in FEATURE_RE.finditer(text):
        features.append(Feature(m.group(2), m.group(3).strip(), m.group(1) in "xX", None,
                                m.group(4), parse_ids(m.group(5)), line_of(text, m.start())))
    for m in MOVED_FEATURE_RE.finditer(text):
        features.append(Feature(m.group(1), m.group(2).strip(), False, m.group(3), None, [],
                                line_of(text, m.start())))
    features.sort(key=lambda f: f.line)
    return Milestone(
        id=mid, path=path, title=title,
        status=(field_value(text, "Status") or "").lower(),
        exit_criteria=field_value(text, "Exit criteria") or "",
        evidence=field_value(text, "Evidence of exit") or "",
        depends_on=parse_ids(field_value(text, "Depends on")),
        features=features,
    )


def parse_stamp(s: str) -> datetime | None:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def parse_plan(path: Path) -> Plan:
    text = read_text(path)
    fallback = re.match(r"(M\d+-\d+)", path.stem)
    pid, title = _id_and_title(first_heading(text), r"M\d+-\d+", fallback.group(1) if fallback else path.stem)
    status_raw = (field_value(text, "Status") or "").lower()
    moved_to = None
    status = status_raw
    if status_raw.startswith("moved"):
        status = "moved"
        ids = parse_ids(status_raw) or parse_ids(field_value(text, "Moved to"))
        moved_to = ids[0] if ids else None
    stamps: list[tuple[datetime, str]] = []
    for m in SESSION_RE.finditer(section_body(text, "Sessions")):
        dt = parse_stamp(m.group(1))
        if dt:
            stamps.append((dt, (m.group(2) or "").strip()))
    notes = [ln[2:].strip() for ln in section_body(text, "Progress notes").splitlines() if ln.startswith("- ")]
    tasks_open = sum(1 for m in TASK_RE.finditer(section_body(text, "Tasks")) if m.group(1) == " ")
    milestone = field_value(text, "Milestone") or pid.split("-")[0]
    return Plan(pid, path, title, status, moved_to, milestone, parse_ids(field_value(text, "Depends on")),
                stamps, notes[-1] if notes else "", tasks_open)


def parse_adr(path: Path) -> Adr:
    text = read_text(path)
    number = ADR_FILE_RE.match(path.name).group(1)
    title = re.sub(r"^\d{4}\.\s*", "", first_heading(text)) or path.stem
    return Adr(number, path, title, (field_value(text, "Status") or "").lower())


def parse_roadmap(path: Path) -> Roadmap:
    text = read_text(path)
    lines = text.split("\n")
    heads = [(line_of(text, m.start()), len(m.group(1)), m.group(2).strip()) for m in HEADING_RE.finditer(text)]

    def section_end(idx: int) -> int:
        """Last line of the section including nested sub-headings."""
        level = heads[idx][1]
        for j in range(idx + 1, len(heads)):
            if heads[j][1] <= level:
                return heads[j][0] - 1
        return len(lines)

    def own_end(idx: int) -> int:
        """Last line before the next heading of any level: the section's own body only."""
        return heads[idx + 1][0] - 1 if idx + 1 < len(heads) else len(lines)

    def status_in(start: int, end: int) -> str:
        return (field_value("\n".join(lines[start - 1:end]), "Status") or "").lower()

    phases: list[Phase] = []
    titles: dict[str, str] = {}
    sketch: list[tuple[int, int]] = []
    order: list[str] = []
    current: Phase | None = None
    for i, (ln, level, title) in enumerate(heads):
        pm = re.match(r"(P\d+)\s+—\s+(.*)$", title)
        mm = re.match(r"(M\d+)\s+—\s+(.*)$", title)
        end = section_end(i)
        if pm:
            current = Phase(pm.group(1), pm.group(2), status_in(ln, own_end(i)), ln)
            phases.append(current)
            if current.status == "sketch":
                sketch.append((ln, end))
        elif mm:
            titles[mm.group(1)] = mm.group(2)
            order.append(mm.group(1))
            if current is not None and level > 2:
                current.milestones.append(mm.group(1))
            if status_in(ln, own_end(i)) == "sketch":
                sketch.append((ln, end))
        else:
            current = None if level <= 2 else current
    return Roadmap(path, phases, titles, sketch, order)


# --------------------------------------------------------------------------- loader


def detect_tier(cfg: Config) -> str:
    if cfg.tier != "auto":
        return cfg.tier
    if (cfg.docs / "milestones").is_dir():
        return "standard"
    if (cfg.docs / "roadmap.md").is_file():
        return "lite"
    return "minimal"


def load_project(cfg: Config) -> Project:
    tier = detect_tier(cfg)
    milestones: dict[str, Milestone] = {}
    plans: dict[str, Plan] = {}
    adrs: list[Adr] = []
    roadmap: Roadmap | None = None
    if tier == "standard":
        for p in sorted((cfg.docs / "milestones").glob("M*.md")):
            m = parse_milestone(p)
            milestones[m.id] = m
        for p in sorted((cfg.docs / "plans").rglob("M*-*.md")):
            pl = parse_plan(p)
            plans[pl.id] = pl
    if tier in ("standard", "lite") and (cfg.docs / "roadmap.md").is_file():
        roadmap = parse_roadmap(cfg.docs / "roadmap.md")
    dec = cfg.docs / "decisions"
    if dec.is_dir():
        adrs = [parse_adr(p) for p in sorted(dec.glob("*.md")) if ADR_FILE_RE.match(p.name)]
    return Project(cfg, tier, iter_md(cfg), milestones, plans, adrs, roadmap)
```

Update `run` to build the project:
```python
def run(root: Path, fix: bool = False, stale_hours: float | None = None) -> list[Finding]:
    cfg = load_config(Path(root))
    if stale_hours is not None:
        cfg.stale_hours = stale_hours
    project = load_project(cfg)
    return check(project)


def check(project: Project) -> list[Finding]:
    cfg = project.cfg
    findings: list[Finding] = []
    findings += check_citations(cfg, project.md_files)
    return findings
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/tests -q`
Expected: `15 passed`. If `test_parse_adrs_and_roadmap` fails on the sketch-range line numbers, print `rm.sketch_ranges` and confirm they enclose the `TBD` lines of the fixture roadmap (M2's section and all of P2); adjust the asserted line numbers only if the fixture file differs from Task 1.

- [ ] **Step 5: Commit**

```bash
git add tools/
git commit -m "check_docs: parsers for milestones, plans, ADRs, roadmap; project loader; tier detection

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Status agreement checks E006, E007, E009, E010

**Files:**
- Modify: `tools/check_docs.py` (add `check_status_agreement`)
- Modify: `tools/tests/test_check_docs.py`

**Interfaces:**
- Produces: `check_status_agreement(project) -> list[Finding]` covering E006, E007, E009, E010. Wired into `check` for the standard tier only.

- [ ] **Step 1: Write failing tests**

Append:
```python
def test_e006_plan_done_but_feature_unticked(tmp_path):
    root = make_project(tmp_path, {
        "docs/plans/M1/M1-01-runtime-loop.md": ("**Status:** in progress", "**Status:** done"),
    })
    assert "E006" in codes(cd.run(root))


def test_e006_feature_ticked_but_plan_not_done(tmp_path):
    root = make_project(tmp_path, {
        "docs/milestones/M1.md": ("- [ ] M1-01", "- [x] M1-01"),
    })
    assert "E006" in codes(cd.run(root))


def test_e006_plan_without_feature_line(tmp_path):
    root = make_project(tmp_path)
    (root / "docs/plans/M1/M1-09-orphan.md").write_text(
        "# M1-09 — Orphan\n**Status:** planned\n**Milestone:** M1\n", encoding="utf-8")
    assert "E006" in codes(cd.run(root))


def test_e007_milestone_done_with_unticked_feature(tmp_path):
    root = make_project(tmp_path, {
        "docs/milestones/M1.md": ("**Status:** in progress", "**Status:** done"),
    })
    found = codes(cd.run(root))
    assert "E007" in found


def test_e007_milestone_done_without_evidence(tmp_path):
    root = make_project(tmp_path, {
        "docs/milestones/M0.md": ("**Evidence of exit:** `docs/evidence/M0-exit.md`", "**Evidence of exit:**"),
    })
    assert "E007" in codes(cd.run(root))


def test_e009_planned_milestone_without_exit(tmp_path):
    root = make_project(tmp_path, {
        "docs/milestones/M1.md": (
            "**Exit criteria:** one instance plays end to end with zero validator errors.",
            "**Exit criteria:**"),
    })
    assert "E009" in codes(cd.run(root))


def test_e010_moved_pointer_unresolved(tmp_path):
    root = make_project(tmp_path, {
        "docs/milestones/M0.md": ("moved to M1-02", "moved to M1-77"),
        "docs/plans/M0/M0-02-old-thing.md": ("moved to M1-02", "moved to M1-77"),
    })
    assert "E010" in codes(cd.run(root))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/tests -q`
Expected: the 7 new tests FAIL (codes list lacks E006/E007/E009/E010).

- [ ] **Step 3: Implement**

Insert after `check_citations`:
```python
# --------------------------------------------------------------------------- checks: status agreement


def check_status_agreement(project: Project) -> list[Finding]:
    cfg = project.cfg
    out: list[Finding] = []
    for pl in project.plans.values():
        r = rel(cfg, pl.path)
        hit = project.feature_of(pl.id)
        if pl.status == "moved":
            if not pl.moved_to or project.feature_of(pl.moved_to) is None:
                out.append(Finding("E010", r, 1, f"moved pointer does not resolve: {pl.moved_to or '(none)'}"))
            continue
        if hit is None:
            out.append(Finding("E006", r, 1, f"plan {pl.id} has no feature line in any milestone"))
            continue
        m, f = hit
        if f.moved_to:
            continue
        if pl.status == "done" and not f.ticked:
            out.append(Finding("E006", rel(cfg, m.path), f.line, f"{f.id} plan is done but feature is unticked"))
        if f.ticked and pl.status != "done":
            out.append(Finding("E006", rel(cfg, m.path), f.line, f"{f.id} feature is ticked but plan is '{pl.status}'"))
    for m in project.milestones.values():
        r = rel(cfg, m.path)
        for f in m.features:
            if f.moved_to and project.feature_of(f.moved_to) is None:
                out.append(Finding("E010", r, f.line, f"{f.id} moved pointer does not resolve: {f.moved_to}"))
        if m.status in ACTIVE_MILESTONE_STATUSES and not m.exit_criteria:
            out.append(Finding("E009", r, 1, f"{m.id} is '{m.status}' but has no exit criteria"))
        if m.status == "done":
            for f in m.features:
                if not f.moved_to and not f.ticked:
                    out.append(Finding("E007", r, f.line, f"{m.id} is done but {f.id} is unticked"))
            if not m.evidence:
                out.append(Finding("E007", r, 1, f"{m.id} is done but has no evidence link"))
    return out
```

In `check`, add after the citation line:
```python
    if project.tier == "standard":
        findings += check_status_agreement(project)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/tests -q`
Expected: `22 passed`

- [ ] **Step 5: Commit**

```bash
git add tools/
git commit -m "check_docs: E006/E007/E009/E010 status agreement checks

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: Dependency checks E008 and W002

**Files:**
- Modify: `tools/check_docs.py` (add `check_dependencies`)
- Modify: `tools/tests/test_check_docs.py`

**Interfaces:**
- Produces: `check_dependencies(project) -> list[Finding]`. Wired into `check` for standard tier.

- [ ] **Step 1: Write failing tests**

Append:
```python
def test_e008_milestone_depends_on_sketch(tmp_path):
    root = make_project(tmp_path, {
        "docs/milestones/M1.md": ("**Depends on:** M0", "**Depends on:** M0, M2"),
    })
    assert "E008" in codes(cd.run(root))


def test_e008_feature_depends_on_unknown(tmp_path):
    root = make_project(tmp_path, {
        "docs/milestones/M1.md": ("(depends on: M0-01)", "(depends on: M8-01)"),
    })
    assert "E008" in codes(cd.run(root))


def test_e008_not_raised_for_dropped_milestone_itself(tmp_path):
    root = make_project(tmp_path, {
        "docs/milestones/M1.md": ("**Status:** in progress", "**Status:** dropped"),
    })
    assert "E008" not in codes(cd.run(root))


def test_w002_in_progress_plan_with_unticked_dependency(tmp_path):
    root = make_project(tmp_path, {
        "docs/milestones/M0.md": ("- [x] M0-01", "- [ ] M0-01"),
        "docs/plans/M0/M0-01-fold-schema-gaps.md": ("**Status:** done", "**Status:** in progress"),
        # M0 stays 'done' in this edit, so E007 fires; we only assert on W002 here
    })
    assert "W002" in codes(cd.run(root))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/tests -q`
Expected: 3 of the 4 new tests FAIL (the `not in` test passes trivially).

- [ ] **Step 3: Implement**

Insert after `check_status_agreement`:
```python
# --------------------------------------------------------------------------- checks: dependencies


def _dep_status(project: Project, dep: str) -> str | None:
    """Status of the milestone that a dependency (M3 or M3-02) belongs to; None if unknown."""
    if "-" in dep:
        hit = project.feature_of(dep)
        return hit[0].status if hit else None
    return project.status_of(dep)


def check_dependencies(project: Project) -> list[Finding]:
    cfg = project.cfg
    out: list[Finding] = []
    for m in project.milestones.values():
        if m.status not in ("planned", "in progress"):
            continue
        r = rel(cfg, m.path)
        for dep in m.depends_on:
            st = _dep_status(project, dep)
            if st in (None, "sketch", "dropped"):
                out.append(Finding("E008", r, 1, f"{m.id} depends on {dep} which is {st or 'unknown'}"))
        for f in m.features:
            for dep in f.depends_on:
                st = _dep_status(project, dep)
                if st in (None, "sketch", "dropped"):
                    out.append(Finding("E008", r, f.line, f"{f.id} depends on {dep} which is {st or 'unknown'}"))
    for pl in project.plans.values():
        if pl.status != "in progress":
            continue
        hit = project.feature_of(pl.id)
        deps = list(pl.depends_on) + (hit[1].depends_on if hit else [])
        for dep in deps:
            if "-" not in dep:
                continue
            target = project.feature_of(dep)
            if target and not target[1].ticked:
                out.append(Finding("W002", rel(cfg, pl.path), 1, f"{pl.id} is in progress but dependency {dep} is unticked"))
    return out
```

In `check`, inside the standard-tier block, add `findings += check_dependencies(project)`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/tests -q`
Expected: `26 passed`

- [ ] **Step 5: Commit**

```bash
git add tools/
git commit -m "check_docs: E008/W002 dependency checks

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: Placeholder check E005

**Files:**
- Modify: `tools/check_docs.py` (add `check_placeholders`)
- Modify: `tools/tests/test_check_docs.py`

**Interfaces:**
- Produces: `check_placeholders(project) -> list[Finding]`. Runs on every tier. Scope: files under `docs/` plus root `AGENTS.md`, `CLAUDE.md`, `DOCS.md`, `README.md`. Exempt: `allow_tbd_in` prefixes, generated files, roadmap sketch ranges.

- [ ] **Step 1: Write failing tests**

Append:
```python
def test_e005_tbd_in_design_doc(tmp_path):
    root = make_project(tmp_path, {
        "docs/design/product-design.md": ("## Changelog", "## 4. Later\nTBD\n\n## Changelog"),
    })
    assert "E005" in codes(cd.run(root))


def test_e005_template_brace_in_root_agents(tmp_path):
    root = make_project(tmp_path, {"AGENTS.md": ("**Fixture**", "**{{Project}}**")})
    assert "E005" in codes(cd.run(root))


def test_e005_allowed_in_open_questions_and_sketch_sections(tmp_path):
    root = make_project(tmp_path)   # fixture has TBD in OPEN-QUESTIONS and in sketch roadmap sections
    assert "E005" not in codes(cd.run(root))


def test_e005_tbd_in_active_roadmap_section(tmp_path):
    root = make_project(tmp_path, {
        "docs/roadmap.md": ("Goal: the example instance runs in the runtime.", "Goal: TBD."),
    })
    assert "E005" in codes(cd.run(root))


def test_e005_codename_placeholder(tmp_path):
    root = make_project(tmp_path, {
        "docs/.check_docs.toml": ("stale_hours = 876000", 'stale_hours = 876000\ncodename_placeholder = "PROJECTNAME"'),
        "docs/GLOSSARY.md": ("**Instance**", "**PROJECTNAME instance**"),
    })
    assert "E005" in codes(cd.run(root))


def test_e005_not_applied_outside_docs_scope(tmp_path):
    root = make_project(tmp_path)
    (root / "CONTRIBUTING.md").write_text("TBD {{later}}\n", encoding="utf-8")
    assert "E005" not in codes(cd.run(root))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/tests -q`
Expected: 4 of the 6 new tests FAIL.

- [ ] **Step 3: Implement**

Insert after `check_dependencies`:
```python
# --------------------------------------------------------------------------- checks: placeholders

TBD_RE = re.compile(r"\bTBD\b")


def _in_placeholder_scope(cfg: Config, relpath: str) -> bool:
    return relpath.startswith("docs/") or relpath in PLACEHOLDER_SCOPE_ROOT_FILES


def check_placeholders(project: Project) -> list[Finding]:
    cfg = project.cfg
    out: list[Finding] = []
    allowed = [a.strip("/") for a in cfg.allow_tbd_in]
    sketch = project.roadmap.sketch_ranges if project.roadmap else []
    roadmap_rel = rel(cfg, project.roadmap.path) if project.roadmap else None
    for path in project.md_files:
        r = rel(cfg, path)
        if not _in_placeholder_scope(cfg, r):
            continue
        if any(r == a or r.startswith(a + "/") for a in allowed):
            continue
        text = read_text(path)
        if text.startswith(GENERATED_MARKER):
            continue
        for i, line in enumerate(text.split("\n"), start=1):
            if r == roadmap_rel and any(a <= i <= b for a, b in sketch):
                continue
            if "{{" in line:
                out.append(Finding("E005", r, i, "template placeholder '{{' left in doc"))
            if TBD_RE.search(line):
                out.append(Finding("E005", r, i, "TBD outside OPEN-QUESTIONS.md or a sketch section"))
            if cfg.codename_placeholder and cfg.codename_placeholder in line:
                out.append(Finding("E005", r, i, f"codename placeholder '{cfg.codename_placeholder}' left in doc"))
    return out
```

In `check`, add `findings += check_placeholders(project)` right after the citation check (outside the tier block).

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/tests -q`
Expected: `32 passed`

- [ ] **Step 5: Commit**

```bash
git add tools/
git commit -m "check_docs: E005 placeholder check with sketch-section and allow-list exemptions

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Claim staleness W001

**Files:**
- Modify: `tools/check_docs.py` (add `check_claims`; `now` injection for tests)
- Modify: `tools/tests/test_check_docs.py`

**Interfaces:**
- Produces: `check_claims(project, now: datetime | None = None) -> list[Finding]`. `check(project, now=None)` passes `now` through. `run(..., stale_hours=...)` overrides config.

- [ ] **Step 1: Write failing tests**

Append:
```python
from datetime import datetime, timezone


def test_w001_stale_claim(tmp_path):
    root = make_project(tmp_path)
    # fixture stamp is 2026-09-15T09:00Z; config allows 876000h, CLI override to 1h
    proj = cd.load_project(cd.load_config(root))
    proj.cfg.stale_hours = 1
    now = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)
    assert "W001" in codes(cd.check(proj, now=now))


def test_w001_fresh_claim_passes(tmp_path):
    root = make_project(tmp_path)
    proj = cd.load_project(cd.load_config(root))
    proj.cfg.stale_hours = 24
    now = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)
    assert "W001" not in codes(cd.check(proj, now=now))


def test_w001_claim_without_stamp(tmp_path):
    root = make_project(tmp_path, {
        "docs/plans/M1/M1-01-runtime-loop.md": (
            "- 2026-09-15T09:00Z — claude-code — feat/M1-01-runtime-loop", ""),
    })
    assert "W001" in codes(cd.run(root))


def test_run_stale_hours_override(tmp_path):
    root = make_project(tmp_path)
    assert "W001" in codes(cd.run(root, stale_hours=0.001))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/tests -q`
Expected: 3 FAIL with `TypeError: check() got an unexpected keyword argument 'now'` or missing W001.

- [ ] **Step 3: Implement**

Insert after `check_placeholders`:
```python
# --------------------------------------------------------------------------- checks: claims


def check_claims(project: Project, now: datetime | None = None) -> list[Finding]:
    cfg = project.cfg
    now = now or datetime.now(timezone.utc)
    out: list[Finding] = []
    for pl in project.plans.values():
        if pl.status != "in progress":
            continue
        r = rel(cfg, pl.path)
        if not pl.stamps:
            out.append(Finding("W001", r, 1, f"{pl.id} is in progress with no session stamp under ## Sessions"))
            continue
        latest = max(dt for dt, _ in pl.stamps)
        if now - latest > timedelta(hours=cfg.stale_hours):
            age_h = (now - latest).total_seconds() / 3600
            out.append(Finding("W001", r, 1, f"{pl.id} claim is stale: last stamp {latest.isoformat()} ({age_h:.0f}h ago)"))
    return out
```

Change `check` and `run` signatures and bodies:
```python
def check(project: Project, now: datetime | None = None) -> list[Finding]:
    cfg = project.cfg
    findings: list[Finding] = []
    findings += check_citations(cfg, project.md_files)
    findings += check_placeholders(project)
    if project.tier == "standard":
        findings += check_status_agreement(project)
        findings += check_dependencies(project)
        findings += check_claims(project, now)
    return findings
```

`run` is unchanged apart from calling `check(project)`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tools/tests -q`
Expected: `36 passed`

- [ ] **Step 5: Commit**

```bash
git add tools/
git commit -m "check_docs: W001 stale-claim warning

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 8: Generators, E003/E004/W003, `--fix`, idempotence

**Files:**
- Modify: `tools/check_docs.py` (add `generate`, `check_generated`, `--fix` handling)
- Modify: `tools/tests/test_check_docs.py`
- Create (by running `--fix`): `tools/tests/fixture/valid/docs/milestones/README.md`, `docs/plans/README.md`, `docs/decisions/README.md`, `docs/CURRENT.md`

**Interfaces:**
- Produces: `generate(project) -> dict[str, str]` keyed by `docs/milestones/README.md`, `docs/plans/README.md`, `docs/decisions/README.md`, `docs/CURRENT.md` (standard tier) or only `docs/decisions/README.md` (lite). `check_generated(project) -> list[Finding]` for E003, E004, W003. `run(fix=True)` writes generated files and drops E003/E004/W003 from the returned findings.

- [ ] **Step 1: Write failing tests**

Append:
```python
GENERATED = ["docs/milestones/README.md", "docs/plans/README.md", "docs/decisions/README.md", "docs/CURRENT.md"]


def test_generate_produces_four_files_with_marker(tmp_path):
    root = make_project(tmp_path)
    gen = cd.generate(cd.load_project(cd.load_config(root)))
    assert sorted(gen) == sorted(GENERATED)
    for content in gen.values():
        assert content.startswith(cd.GENERATED_MARKER)


def test_milestone_index_rows(tmp_path):
    root = make_project(tmp_path)
    gen = cd.generate(cd.load_project(cd.load_config(root)))
    idx = gen["docs/milestones/README.md"]
    assert "| M0 | Foundations | done | 1/1 |" in idx
    assert "| M1 | First playable | in progress | 0/2 |" in idx
    assert "| M2 | Authoring tool | sketch | — |" in idx
    assert "| M3 | Ten instances | sketch | — |" in idx


def test_current_md_content_and_length(tmp_path):
    root = make_project(tmp_path)
    cur = cd.generate(cd.load_project(cd.load_config(root)))["docs/CURRENT.md"]
    assert "P1 — Playable core" in cur
    assert "M1 — First playable" in cur
    assert "M1-01 — Runtime loop — `docs/plans/M1/M1-01-runtime-loop.md`" in cur
    assert "loader done; step function next." in cur
    assert "M1-02 — Old thing, re-homed" in cur          # next unclaimed
    assert "`docs/evidence/M0-exit.md`" in cur
    assert len(cur.strip().split("\n")) < 40


def test_plans_index_groups_and_collapses_done(tmp_path):
    root = make_project(tmp_path)
    idx = cd.generate(cd.load_project(cd.load_config(root)))["docs/plans/README.md"]
    assert "## M1" in idx and "## M0" in idx
    assert "<details>" in idx and "M0-01 — Fold schema gaps" in idx


def test_e003_and_e004_when_indexes_missing(tmp_path):
    root = make_project(tmp_path)
    found = codes(cd.run(root))
    assert "E003" in found and "E004" in found


def test_fix_writes_files_and_clears_generated_findings(tmp_path):
    root = make_project(tmp_path)
    found = cd.run(root, fix=True)
    assert not any(f.code in ("E003", "E004", "W003") for f in found)
    for relp in GENERATED:
        assert (root / relp).is_file()
    # second run without --fix is clean and idempotent
    again = cd.run(root)
    assert not any(f.code in ("E003", "E004", "W003") for f in again)
    before = {p: (root / p).read_text(encoding="utf-8") for p in GENERATED}
    cd.run(root, fix=True)
    after = {p: (root / p).read_text(encoding="utf-8") for p in GENERATED}
    assert before == after


def test_w003_on_stale_generated_file(tmp_path):
    root = make_project(tmp_path)
    cd.run(root, fix=True)
    p = root / "docs/CURRENT.md"
    p.write_text(p.read_text(encoding="utf-8") + "\nstale line\n", encoding="utf-8")
    assert "W003" in codes(cd.run(root))


def test_e003_on_wrong_status_in_index(tmp_path):
    root = make_project(tmp_path)
    cd.run(root, fix=True)
    p = root / "docs/milestones/README.md"
    p.write_text(p.read_text(encoding="utf-8").replace("| in progress |", "| done |"), encoding="utf-8")
    assert "E003" in codes(cd.run(root))


def test_valid_fixture_committed_generated_files_are_current():
    # the fixture directory itself (not a copy) must carry up-to-date generated files
    assert codes(cd.run(FIXTURE)) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tools/tests -q`
Expected: the new tests FAIL (`AttributeError: generate`, missing codes). `test_valid_fixture_committed_generated_files_are_current` fails until Step 5.

- [ ] **Step 3: Implement generators and generated-file checks**

Insert after `check_claims`:
```python
# --------------------------------------------------------------------------- generators


def _plan_rel_for(project: Project, f: Feature) -> str | None:
    if f.plan_path:
        return f.plan_path
    pl = project.plans.get(f.id)
    return rel(project.cfg, pl.path) if pl else None


def gen_milestones_index(project: Project) -> str:
    lines = [GENERATED_MARKER, "# Milestones", "",
             "| ID | Title | Status | Features done |", "|---|---|---|---|"]
    for mid in project.milestone_order():
        m = project.milestones.get(mid)
        if m:
            real = [f for f in m.features if not f.moved_to]
            done = sum(1 for f in real if f.ticked)
            lines.append(f"| {m.id} | {m.title} | {m.status} | {done}/{len(real)} |")
        else:
            title = project.roadmap.milestone_titles.get(mid, "") if project.roadmap else ""
            lines.append(f"| {mid} | {title} | sketch | — |")
    return "\n".join(lines) + "\n"


def gen_plans_index(project: Project) -> str:
    lines = [GENERATED_MARKER, "# Plans", ""]
    for mid in project.milestone_order():
        m = project.milestones.get(mid)
        if not m:
            continue
        plans = sorted((p for p in project.plans.values() if p.milestone == mid), key=lambda p: p.id)
        if not plans:
            continue
        lines += [f"## {mid} — {m.title}", ""]
        active = [p for p in plans if p.status not in ("done", "moved", "superseded")]
        closed = [p for p in plans if p.status in ("done", "moved", "superseded")]
        for p in active:
            lines.append(f"- {p.id} — {p.title} — `{rel(project.cfg, p.path)}` — {p.status}")
        if closed:
            lines += ["", "<details><summary>Closed</summary>", ""]
            for p in closed:
                extra = f" → {p.moved_to}" if p.moved_to else ""
                lines.append(f"- {p.id} — {p.title} — `{rel(project.cfg, p.path)}` — {p.status}{extra}")
            lines += ["", "</details>"]
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def gen_decisions_index(project: Project) -> str:
    lines = [GENERATED_MARKER, "# Architecture Decision Records", "",
             "| # | Decision | Status |", "|---|---|---|"]
    for a in project.adrs:
        lines.append(f"| {a.number} | [{a.title}]({a.path.name}) | {a.status} |")
    return "\n".join(lines) + "\n"


def gen_current(project: Project) -> str:
    cfg = project.cfg
    lines = [GENERATED_MARKER, "# Current focus", ""]
    active_phases = [p for p in (project.roadmap.phases if project.roadmap else []) if p.status == "active"]
    if active_phases:
        lines.append("**Phase:** " + "; ".join(f"{p.id} — {p.title}" for p in active_phases))
    in_prog = [m for m in project.milestones.values() if m.status == "in progress"]
    if in_prog:
        lines.append("**Milestones in progress:** " + "; ".join(f"{m.id} — {m.title}" for m in in_prog))
    lines.append("")
    claimed = sorted((p for p in project.plans.values() if p.status == "in progress"), key=lambda p: p.id)
    lines += ["## Claimed features", ""]
    for p in claimed[:8]:
        stamp = max(p.stamps)[0].strftime("%Y-%m-%dT%H:%MZ") + f" ({max(p.stamps)[1]})" if p.stamps else "no stamp"
        note = f" — last note: {p.last_note}" if p.last_note else ""
        lines.append(f"- {p.id} — {p.title} — `{rel(cfg, p.path)}` — {stamp}{note}")
    if not claimed:
        lines.append("- none")
    blocked = sorted((p for p in project.plans.values() if p.status == "blocked"), key=lambda p: p.id)
    if blocked:
        lines += ["", "## Blocked", ""]
        lines += [f"- {p.id} — {p.title} — `{rel(cfg, p.path)}`" for p in blocked[:8]]
    nxt = []
    for m in in_prog:
        for f in m.features:
            if f.ticked or f.moved_to:
                continue
            pl = project.plans.get(f.id)
            if pl is None or pl.status in ("grounding", "planned"):
                nxt.append(f"- {f.id} — {f.title}")
    lines += ["", "## Next unclaimed features", ""]
    lines += nxt[:8] or ["- none"]
    ev_dir = cfg.docs / "evidence"
    evidence = sorted(ev_dir.glob("*.md")) if ev_dir.is_dir() else []
    if evidence:
        lines += ["", "## Latest evidence", ""]
        lines += [f"- `{rel(cfg, p)}`" for p in evidence[-3:]]
    return "\n".join(lines) + "\n"


def generate(project: Project) -> dict[str, str]:
    out: dict[str, str] = {}
    if project.tier == "standard":
        out["docs/milestones/README.md"] = gen_milestones_index(project)
        out["docs/plans/README.md"] = gen_plans_index(project)
        out["docs/CURRENT.md"] = gen_current(project)
    if project.tier in ("standard", "lite") and (project.cfg.docs / "decisions").is_dir():
        out["docs/decisions/README.md"] = gen_decisions_index(project)
    return out


# --------------------------------------------------------------------------- checks: generated files


def check_generated(project: Project) -> list[Finding]:
    cfg = project.cfg
    out: list[Finding] = []
    for relp, expected in generate(project).items():
        path = cfg.root / relp
        actual = read_text(path) if path.is_file() else None
        if relp.endswith("milestones/README.md"):
            for row in expected.split("\n"):
                if row.startswith("| M") and (actual is None or row not in actual):
                    out.append(Finding("E003", relp, 1, f"milestone index missing or stale for row: {row}"))
        elif relp.endswith("decisions/README.md"):
            for a in project.adrs:
                if actual is None or f"| {a.number} |" not in actual:
                    out.append(Finding("E004", relp, 1, f"ADR {a.number} missing from index"))
        if actual != expected and not any(f.path == relp and f.is_error for f in out):
            out.append(Finding("W003", relp, 1, "generated file differs from --fix output; run check_docs.py --fix"))
    return out
```

Add to `check`:
```python
    findings += check_generated(project)
```
placed last, outside the tier block (generate() already handles tiers).

Replace `run`:
```python
def run(root: Path, fix: bool = False, stale_hours: float | None = None) -> list[Finding]:
    cfg = load_config(Path(root))
    if stale_hours is not None:
        cfg.stale_hours = stale_hours
    project = load_project(cfg)
    findings = check(project)
    if fix:
        for relp, content in generate(project).items():
            path = cfg.root / relp
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
        findings = [f for f in findings if f.code not in ("E003", "E004", "W003")]
    return findings
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tools/tests -q`
Expected: all pass except `test_valid_fixture_committed_generated_files_are_current` and `test_valid_fixture_has_no_errors` may now report E003/E004 on the un-fixed fixture. Fix that in Step 5.

- [ ] **Step 5: Generate the fixture's index files and re-run**

Run: `python tools/check_docs.py --root tools/tests/fixture/valid --fix`
Expected: prints `0 error(s), 0 warning(s)`. Four new files appear under the fixture.

Run: `python -m pytest tools/tests -q`
Expected: `45 passed`

- [ ] **Step 6: Commit**

```bash
git add tools/
git commit -m "check_docs: index and CURRENT.md generators, E003/E004/W003, --fix

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 9: CLI exit codes, lite/minimal tier behaviour, hooks README

**Files:**
- Modify: `tools/tests/test_check_docs.py`
- Create: `tools/hooks/README.md`

**Interfaces:**
- Consumes: `main`, `run`, `detect_tier` from earlier tasks.

- [ ] **Step 1: Write failing tests**

Append:
```python
import subprocess
import sys as _sys

CHECK = Path(__file__).resolve().parents[1] / "check_docs.py"


def test_cli_exit_zero_on_valid(tmp_path):
    root = make_project(tmp_path)
    r = subprocess.run([_sys.executable, str(CHECK), "--root", str(root)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 error(s)" in r.stdout


def test_cli_exit_one_on_error(tmp_path):
    root = make_project(tmp_path, {
        "docs/WORKFLOW.md": ("`docs/design/product-design.md §3`", "`docs/design/missing.md`"),
    })
    r = subprocess.run([_sys.executable, str(CHECK), "--root", str(root)], capture_output=True, text=True)
    assert r.returncode == 1
    assert "E001" in r.stdout


def test_cli_warnings_do_not_fail(tmp_path):
    root = make_project(tmp_path)
    r = subprocess.run([_sys.executable, str(CHECK), "--root", str(root), "--stale-hours", "0.001"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "W001" in r.stdout


def test_lite_tier_runs_only_lite_checks(tmp_path):
    root = make_project(tmp_path)
    shutil.rmtree(root / "docs" / "milestones")
    shutil.rmtree(root / "docs" / "plans")
    (root / "docs" / "CURRENT.md").unlink()
    (root / "docs" / "roadmap.md").write_text(
        "# Roadmap\n## P1 — Only phase\n**Status:** active\n- [x] Do the thing\n- [ ] Do the other thing\n",
        encoding="utf-8")
    found = cd.run(root)
    assert not any(f.code in ("E003", "E006", "E007", "E008", "E009", "E010", "W001", "W002") for f in found)
    assert set(cd.generate(cd.load_project(cd.load_config(root)))) == {"docs/decisions/README.md"}


def test_minimal_tier_only_citations_and_placeholders(tmp_path):
    root = tmp_path / "kit"
    (root / "docs").mkdir(parents=True)
    (root / "README.md").write_text("See `GUIDE.md §1`.\n", encoding="utf-8")
    (root / "GUIDE.md").write_text("# Guide\n## 1. Intro\nTBD is fine here: not in docs scope.\n", encoding="utf-8")
    (root / "docs" / "notes.md").write_text("TBD\n", encoding="utf-8")
    found = cd.run(root)
    assert codes(found) == ["E005"]
    assert cd.generate(cd.load_project(cd.load_config(root))) == {}
```

- [ ] **Step 2: Run tests to verify they fail or pass**

Run: `python -m pytest tools/tests -q`
Expected: all five new tests PASS already if Tasks 1–8 were implemented as written. If any fails, fix the implementation (not the test) until it passes. Do not proceed with a red suite.

- [ ] **Step 3: Write the hooks README**

`tools/hooks/README.md`
```markdown
# Running check_docs automatically

`tools/check_docs.py` is meant to run without anyone remembering to run it.

## Claude Code Stop hook

Add to `.claude/settings.json` in the project (or `settings.local.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python tools/check_docs.py --root . || (echo 'check_docs found errors; fix them before ending the session' && exit 2)"
          }
        ]
      }
    ]
  }
}
```

Exit code 2 from a Stop hook blocks the stop and shows the message to the agent. Warnings do not block.

## Pre-commit hook

`.git/hooks/pre-commit` (make it executable), or the equivalent entry in your pre-commit framework:

```sh
#!/bin/sh
python tools/check_docs.py --root . || exit 1
```

## CI

Run `python tools/check_docs.py --root .` as a step. It exits 1 on any E-code.

## Regenerating indexes

`python tools/check_docs.py --root . --fix` rewrites `docs/milestones/README.md`, `docs/plans/README.md`, `docs/decisions/README.md`, and `docs/CURRENT.md`. Run it at the end of every session and commit the result. Never edit those four files by hand.
```

- [ ] **Step 4: Run the full suite one more time**

Run: `python -m pytest tools/tests -q`
Expected: `50 passed`

- [ ] **Step 5: Commit**

```bash
git add tools/
git commit -m "check_docs: CLI and tier tests; hook snippets

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Part 2 — The kit's documents

Verification for every doc task is the same two commands unless a task adds more. The kit's own `docs/.check_docs.toml` is created in Task 10 so the linter can run on the kit from that point on.

```
python tools/check_docs.py --root .
python -m pytest tools/tests -q
```

The v1 file `PROJECT-BOOSTRAP.md` stays in place until Task 18 as the source for migrated text. When a task says "start from v1 Part E4", open that section of `PROJECT-BOOSTRAP.md` and apply the listed changes.

---

### Task 10: Kit config and templates

**Files:**
- Create: `docs/.check_docs.toml`
- Create: `templates/README.md`, `templates/AGENTS.md`, `templates/CLAUDE.md`, `templates/DOCS.md`, `templates/PROJECT-README.md`, `templates/WORKFLOW.md`, `templates/GLOSSARY.md`, `templates/OPEN-QUESTIONS.md`, `templates/CURRENT.md`, `templates/roadmap.md`, `templates/milestone.md`, `templates/plan.md`, `templates/adr.md`, `templates/decisions-AGENTS.md`, `templates/design-header.md`, `templates/evidence.md`

**Interfaces:**
- Produces: the file formats the linter parses. Every field name and separator below is what Tasks 3–8 parse. Do not change them.

- [ ] **Step 1: Create the kit's linter config**

`docs/.check_docs.toml`
```toml
# Config for running tools/check_docs.py on this kit's own repo.
allow_tbd_in = ["docs/superpowers/"]
citation_exclude = ["templates/", "tools/tests/fixture/", "docs/superpowers/"]
exclude = ["tools/tests/fixture"]
```

- [ ] **Step 2: Write `templates/README.md`**

Contents: a one-paragraph explanation that templates are copied into a new project and every `{{token}}` replaced, then a table of every token with its meaning. The table must contain at least these rows (add any token you introduce in later steps):

| Token | Meaning |
|---|---|
| `{{Project}}` | Project display name |
| `{{project}}` | Project slug (kebab-case) |
| `{{one_sentence}}` | What the project is, one sentence |
| `{{one_rule}}` | The rule that shapes everything |
| `{{product}}` | Slug of the product design doc |
| `{{profile}}` | Profile name from `profiles/` |
| `{{tier}}` | lite, standard, or full |
| `{{n}}`, `{{nn}}` | Milestone number, feature number |
| `{{Title}}` | Title of the object being created |
| `{{slug}}` | Kebab-case slug of the title |
| `{{date}}` | ISO date `YYYY-MM-DD` |
| `{{agent}}` | Agent or tool name for a session stamp |
| `{{commands}}` | Build, test, lint, run commands |
| `{{rule}}` | A single non-negotiable rule |
| `{{deferred}}` | A deferred item |
| `{{area}}` | Glossary area or design area |
| `{{Term}}` | Glossary term |
| `{{question}}` | An open question |
| `{{NNNN}}` | Four-digit ADR number |
| `{{decision_as_a_sentence}}` | ADR title |

End with the rule: "A template file has no `{{` left when copied into a project; the linter's E005 check enforces this."

- [ ] **Step 3: Write `templates/AGENTS.md`**

Start from v1 Part E1. Changes:
- "Read first" becomes: `1. DOCS.md  2. docs/CURRENT.md  3. docs/design/{{product}}-design.md  4. docs/GLOSSARY.md  5. docs/WORKFLOW.md`, then "the design doc for the area you're touching".
- "How to work" step 1 becomes: "Open `docs/CURRENT.md`. Resume a feature you claimed, or claim the next unclaimed one: set its plan to `in progress` and add a session stamp under `## Sessions`."
- Add step: "Before ending: run `python tools/check_docs.py --fix` and commit the generated files with your work."
- Add to Don't: "Don't edit `docs/CURRENT.md` or any `README.md` index by hand; they are generated." and "Don't start a feature whose plan has a session stamp under 24 hours old."
- Add a line under "What this is": `**Profile:** {{profile}}  **Tier:** {{tier}}`.
- Keep under 120 lines. Verify with `wc -l templates/AGENTS.md`.

- [ ] **Step 4: Write `templates/CLAUDE.md`, `templates/PROJECT-README.md`, `templates/design-header.md`, `templates/GLOSSARY.md`, `templates/OPEN-QUESTIONS.md`, `templates/evidence.md`**

`CLAUDE.md`: v1 E2 unchanged.
`PROJECT-README.md`: v1 E10 unchanged, plus one line: "Progress: `docs/CURRENT.md`."
`design-header.md`: v1 E9 with `**Status:** draft | stable | living` and a trailing note "End every design doc with `## Changelog`."
`GLOSSARY.md`: v1 E6 unchanged.
`OPEN-QUESTIONS.md`: v1 E7 unchanged.
`evidence.md`:
```markdown
# {{Title}}
**Milestone:** M{{n}}  **Date:** {{date}}  **Collected by:** {{agent}}

## What was measured
## How
## Result
## Raw output
```

- [ ] **Step 5: Write `templates/DOCS.md`**

Start from v1 E3. Changes:
- Section 2 table has five kinds (Design, Decision, Direction, Progress, Reference) copied from spec §4.
- Section 4 "Where things go" gains: "A phase or reordering → `roadmap.md`, with an ADR if the order changed for a reason." and "Current focus → nothing; `CURRENT.md` is generated."
- Section 8 Maintenance: "Indexes and `CURRENT.md` are generated by `tools/check_docs.py --fix` at the end of every session. Drift review and roadmap review at each milestone close. Done plans are never deleted."
- Section 5 Conventions adds: "One `**Field:** value` per line in milestone, plan, and ADR headers. Separator between ID and title is ` — `."

- [ ] **Step 6: Write `templates/WORKFLOW.md`**

Start from v1 E4. Changes, section by section:
- §1 Three layers → "Four layers": phase (roadmap only) → milestone → feature → plan at `docs/plans/M<n>/M<n>-<nn>-<slug>.md`. Add: "IDs are allocated in order and never reused. A moved feature gets a new ID; the old plan stays with status `moved to M<n>-<nn>`."
- §2 Ground begins with "read `docs/CURRENT.md`". Brainstorm adds the spike paragraph from spec §8 verbatim in substance: time-boxed, throwaway, recorded in Current state or an ADR, never committed to `main`. Close adds: "run `check_docs.py --fix`; proposed ADRs do not block unless `blocking: yes`; if this is the milestone's last feature, run the roadmap review in `docs/roadmap.md`'s checklist section."
- §3 Sessions: "Claim before you start: plan status `in progress` plus a stamp line `- {{date}}T{{hh}}:{{mm}}Z — {{agent}} — {{branch}}` under `## Sessions`. Never take a feature stamped under 24 hours ago by someone else." Add `{{hh}}`, `{{mm}}`, `{{branch}}` to `templates/README.md`.
- §5 Small changes unchanged. Add §5a Spikes: the rule from spec §8.
- §7 Plan template: replace with one field per line:
```markdown
# M{{n}}-{{nn}} — {{Title}}
**Status:** grounding
**Milestone:** M{{n}}
**Branch:** feat/M{{n}}-{{nn}}-{{slug}}
**Design docs:**
**ADRs:**
**Depends on:**

## Sessions

## Objective
## Current state
## Approach
### Alternatives considered
### Risks
### Docs to update
## Tasks
- [ ] T1 — ... **Verify:** `command`
## Progress notes
## Verification log
```
- §8 Milestone template:
```markdown
# M{{n}} — {{Title}}
**Status:** planned
**Goal:**
**Exit criteria:**
**Evidence of exit:**
**Depends on:**

## Features
- [ ] M{{n}}-01 — {{Title}} — `docs/plans/M{{n}}/M{{n}}-01-{{slug}}.md`

## Notes
```
- §9 Every session: 1. `AGENTS.md` 2. `docs/CURRENT.md` 3. claim or resume 4. verify before ticking 5. `check_docs.py --fix` 6. leave the plan true.
- Add §10 Roadmap review checklist (from spec §6 "Re-planning cadence"): check exit with evidence; promote next `sketch` to `planned` with a real exit; reorder or split if needed; ADR for a reasoned reorder; batch-accept proposed ADRs.

- [ ] **Step 7: Write `templates/roadmap.md`, `templates/milestone.md`, `templates/plan.md`, `templates/CURRENT.md`, `templates/adr.md`, `templates/decisions-AGENTS.md`**

`roadmap.md`:
```markdown
# Roadmap
**No checkboxes here.** Scope and progress live in `docs/milestones/`. Edit at phase boundaries and milestone reviews.

## Principles
- Every milestone ends in something runnable or measurable.
- The current and next milestone are `planned`; everything beyond is `sketch`.
- {{rule}}

## P1 — {{Title}}
**Status:** active
**Exit:** {{measurable statement}}

### M0 — {{Title}}
Goal: {{one or two sentences}}. Features: `docs/milestones/M0.md`

### M1 — {{Title}}
Goal: {{one or two sentences}}. Features: `docs/milestones/M1.md`

### M2 — {{Title}}
**Status:** sketch
Goal: {{one or two sentences}}. Exit: TBD.

## P2 — {{Title}}
**Status:** sketch
**Exit:** TBD

### M3 — {{Title}}
Goal: TBD.

## Explicitly deferred
- {{deferred}}

## Open decisions with a deadline
See `OPEN-QUESTIONS.md`.
```
Add `{{measurable statement}}` and `{{one or two sentences}}` to `templates/README.md`.

`milestone.md` and `plan.md`: the same bodies as WORKFLOW §8 and §7 above, as standalone files.

`CURRENT.md`:
```markdown
<!-- generated by tools/check_docs.py --fix; do not edit by hand -->
# Current focus
This file is regenerated by `python tools/check_docs.py --fix`. Run it once after bootstrap to fill it in.
```

`adr.md`: v1 E5 template block with one field per line and an added optional field `**Blocking:** no`.

`decisions-AGENTS.md`: v1 E5 minus the template block (which now lives in `adr.md`), plus in "Rules for agents": "A `proposed` ADR does not block a feature's Close unless `**Blocking:** yes`. Humans accept proposed ADRs in a batch at milestone close." The index is generated: replace rule 5 with "Never edit `README.md`; it is generated."

- [ ] **Step 8: Verify**

Run:
```
python tools/check_docs.py --root .
wc -l templates/AGENTS.md
grep -oh "{{[a-zA-Z_ ]*}}" templates/*.md | sort -u
```
Expected: linter prints `0 error(s)`. AGENTS.md under 120 lines. Every token printed by the grep appears in `templates/README.md`. If one is missing, add it to the table.

- [ ] **Step 9: Commit**

```bash
git add docs/.check_docs.toml templates/
git commit -m "templates: v2 project templates with one-field-per-line headers, claims, generated indexes

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 11: `core/doc-kinds.md` and `core/layers.md`

**Files:**
- Create: `core/doc-kinds.md`, `core/layers.md`

**Interfaces:**
- Consumes: spec §4 and §5. Produces: the two docs later tasks cite as `core/doc-kinds.md` and `core/layers.md §N`.

- [ ] **Step 1: Write `core/doc-kinds.md`**

Numbered sections:
1. Why docs are the contract (v1 Part A first paragraph, reworded: an agent's session has no memory; docs complete, current, consistent).
2. The five kinds: the table from spec §4, then one paragraph per kind saying what goes there and what does not.
3. Design doc rules: header from `templates/design-header.md`, status vocabulary `draft | stable | living`, the `## Changelog` rule, section anchors as contracts with the `§6.1a` rule, and the convention that generic mentions are written `<file>.md §N.M`.
4. Where things go: the list from `templates/DOCS.md` §4.

- [ ] **Step 2: Write `core/layers.md`**

Numbered sections:
1. The four layers with the table: layer, lives in, ID form, status lives in.
2. ID rules: the five bullets from spec §5 verbatim in substance, each followed by a two-line worked example (for example, "M3 is split: M3 keeps the runtime work; M8 is created for the authoring tool; roadmap lists M8 right after M3").
3. Status vocabularies: the table from spec §5.
4. Where status lives: "exactly one place per object" and the list of generated files.
5. Milestone size: three to ten features; exit demonstrable in one session by someone who did not build it; larger is split, smaller is folded.

- [ ] **Step 3: Verify and commit**

Run: `python tools/check_docs.py --root .`
Expected: `0 error(s)`.

```bash
git add core/doc-kinds.md core/layers.md
git commit -m "core: document kinds and layers

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 12: `core/lifecycle.md` and `core/long-horizon.md`

**Files:**
- Create: `core/lifecycle.md`, `core/long-horizon.md`

- [ ] **Step 1: Write `core/lifecycle.md`**

Numbered sections:
1. The five steps, one paragraph each, taken from `templates/WORKFLOW.md` §2 and expanded with the concrete Ground actions from v1 Part D lesson 8 (read these files, grep ADRs, run tests, inspect packages, write findings before brainstorming).
2. Spikes: definition, time box, where the result is recorded, what happens to the code (spec §8).
3. Small changes: the three cases, and the promotion rule.
4. Experiments: for the data-ml profile, a feature that closes with a negative result is `done`; the evidence file records the result.
5. Close in detail: the checklist including `check_docs.py --fix`, ADR non-blocking rule, roadmap review trigger.

- [ ] **Step 2: Write `core/long-horizon.md`**

Numbered sections mapping one to one onto the bold paragraphs of spec §6:
1. Rolling wave. 2. Phase exits. 3. Design docs by phase (with the `docs/design/<area>/` layout and the per-phase example instance). 4. Re-planning cadence, with the roadmap review checklist as a numbered list. 5. Milestone size. 6. Dependencies, with the `depends on:` syntax on milestone header and feature lines and what the linter does (E008, W002). 7. Bounded read cost: what `CURRENT.md` contains and the session read order.
Add section 8, "Worked example": a twenty-milestone project sketched as three phases, showing which milestones are `planned` versus `sketch` at bootstrap, at M2 close, and at P1 close.

- [ ] **Step 3: Verify and commit**

Run: `python tools/check_docs.py --root .`
Expected: `0 error(s)`.

```bash
git add core/lifecycle.md core/long-horizon.md
git commit -m "core: lifecycle with spikes; long-horizon planning rules

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 13: `core/parallel-agents.md` and `core/tiers.md`

**Files:**
- Create: `core/parallel-agents.md`, `core/tiers.md`

- [ ] **Step 1: Write `core/parallel-agents.md`**

Numbered sections from spec §7:
1. Claiming: the exact stamp line format, the 24-hour rule, what W001 flags.
2. Generated files: the four files, the marker line, the `--fix` command, why hand-editing them is forbidden.
3. Per-milestone plan directories.
4. Decisions do not block by default: `**Blocking:** yes`, batch acceptance at milestone close.
5. Branches and commits: from v1 E4 §4 (`feat/M1-03-title`, messages start with the feature ID, `main` always green).
6. Conflict recovery: if two sessions did claim the same feature, the later stamp yields; its work is rebased onto the earlier session's branch or moved to a new feature ID.

- [ ] **Step 2: Write `core/tiers.md`**

Numbered sections from spec §10:
1. The tier table.
2. Lite in detail: the three files, the roadmap carrying checkboxes, what the linter checks on lite.
3. Standard in detail: the v1 set plus `CURRENT.md`.
4. Full in detail: what phases, per-area design docs, evidence, and profile optional docs add.
5. Promotion rules and the "promotion is one feature" procedure.

- [ ] **Step 3: Verify and commit**

Run: `python tools/check_docs.py --root .`
Expected: `0 error(s)`.

```bash
git add core/parallel-agents.md core/tiers.md
git commit -m "core: parallel agents and tiers

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 14: `core/adoption.md`

**Files:**
- Create: `core/adoption.md`

- [ ] **Step 1: Write the greenfield procedure**

Section 1 "Greenfield": v1 Part C restructured per spec §9. C0 now decides five things: name and codename, naming convention, example location, tier, profile. C1–C8 write the design docs the chosen profile lists (say "see `profiles/<name>.md` for the list"), phase 1 only, with rolling wave applied to the roadmap in C8. C9 generates process files from `templates/` and lists the token substitutions. C10 runs `python tools/check_docs.py --root . --fix`. C11 is the first session. Keep v1's emphasis that each step is a conversation ending in a file and that C4 (example instance) is the highest-value step.

- [ ] **Step 2: Write the brownfield procedure**

Section 2 "Brownfield": the seven numbered steps from spec §9 with, for each, the concrete actions an agent takes (commands to run, files to read, what to write). Step 6 includes the mirroring note: issues stay in the tracker; the milestone file cites them as `(tracker: #123)`; the milestone file is authoritative for status.

- [ ] **Step 3: Write section 3 "Which procedure"**

A short decision list: empty repo → greenfield; any code → brownfield; code but no docs → brownfield with steps 2–4 given most of the time.

- [ ] **Step 4: Verify and commit**

Run: `python tools/check_docs.py --root .`
Expected: `0 error(s)`.

```bash
git add core/adoption.md
git commit -m "core: greenfield and brownfield adoption procedures

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 15: `core/lessons.md`

**Files:**
- Create: `core/lessons.md`

- [ ] **Step 1: Migrate v1 Part D**

Copy the nineteen v1 lessons as section 1 "From the reference project", renumbered 1–19, text unchanged except: lesson 5 gains "and the linter allows TBD only there and in sketch sections"; lesson 18 gains "and generate the indexes from them"; lesson 19 becomes "Turn Part C into a skill" and points to `skills/bootstrap/SKILL.md`.

- [ ] **Step 2: Add section 2 "From v2"**

One entry per v2 change, each as "What went wrong in v1 / What changed", for: game-specific design docs (profiles); roadmap written once (rolling wave and phases); feature IDs coupled to milestones (moved-to rule); hand-maintained indexes (generation); no claim mechanism (stamps); ADR acceptance blocking Close (non-blocking by default); no brownfield path; no spike hatch; no tiers; linter as a spec (real linter with codes and tests); unbounded read cost (`CURRENT.md`); roadmap unclassified (Direction kind); status vocabularies missing `moved`, `sketch`, `dropped`; filename typo in the kit itself (the linter would have caught a citation to it).

- [ ] **Step 3: Verify and commit**

Run: `python tools/check_docs.py --root .`
Expected: `0 error(s)`.

```bash
git add core/lessons.md
git commit -m "core: lessons from v1 and v2

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 16: Profiles

**Files:**
- Create: `profiles/README.md`, `profiles/data-driven-product.md`, `profiles/web-app-saas.md`, `profiles/library-sdk-cli.md`, `profiles/data-ml.md`, `profiles/infra-platform.md`, `profiles/research-prototype.md`

**Interfaces:**
- Every profile file has the same numbered sections so `core/adoption.md` and the skill can point at them by number:
  1. Fits when. 2. Design docs (table: file, sections, written at bootstrap or at phase start). 3. Vocabulary (table: template word → profile word). 4. Example instance and evidence. 5. Default tier and M0. 6. Suggested non-goals. 7. Profile-specific lessons.

- [ ] **Step 1: Write `profiles/README.md`**

How to pick: a short decision list keyed on "what is the central artefact" (authored data → data-driven; tenants and journeys → web-app-saas; a public API → library; datasets and metrics → data-ml; environments and SLOs → infra; a question → research). Then "What every profile shares" (the machinery from `core/`) and the seven-section contract above.

- [ ] **Step 2: Write `profiles/data-driven-product.md`**

Section 2 lists v1 Part B's design docs with their section outlines from v1 C2–C7 verbatim in substance. Section 3 vocabulary table is identity (no substitutions). Section 4: one full authored instance; playtests and simulations. Section 5: standard tier; M0 is "fold the schema gaps from the example instance into the data model". Section 6: v1's non-goals guidance.

- [ ] **Step 3: Write the other five profiles**

Fill each from the row of spec §11's table. Section 2 must give a section outline for every design doc it names (at least five section titles each). Section 3 must include at minimum:
- web-app-saas: core loop → primary journeys; player → user; playtest → usability session; centrepiece moment → key moment of value.
- library-sdk-cli: data model → API surface; example instance → golden example; runtime → execution model; milestone → release.
- data-ml: feature → experiment; exit criteria → target metric with threshold; evidence → eval run.
- infra-platform: design → service design; data model → environment and config schema; example instance → one environment definition.
- research-prototype: milestone → question; feature → probe; plan → protocol.
Section 7 for research-prototype states that spikes are the default and the lifecycle's Plan step is a protocol, not a task list.

- [ ] **Step 4: Verify and commit**

Run:
```
python tools/check_docs.py --root .
grep -c "^## " profiles/*.md
```
Expected: `0 error(s)`; every profile file (not README) has exactly 7 `## ` headings.

```bash
git add profiles/
git commit -m "profiles: six project profiles and selection guide

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 17: The `/bootstrap` skill

**Files:**
- Create: `skills/bootstrap/SKILL.md`

- [ ] **Step 1: Write the skill**

Frontmatter:
```markdown
---
name: bootstrap
description: Bootstrap a new project or adopt an existing one into the docs-as-contract workflow. Use when the user says "bootstrap a project", "set up docs for this repo", "adopt the bootstrap kit", or pastes BOOTSTRAP.md.
---
```
Body, numbered sections:
1. Announce and classify: greenfield or brownfield, using `core/adoption.md §3`.
2. C0 questions, one per message, in order: name and codename; naming convention (recommend kebab-case unnumbered); example location; tier (recommend from `core/tiers.md`); profile (recommend from `profiles/README.md`). Record answers in a scratch list, write nothing yet.
3. One design doc per session: the skill states the rule and the reason (one-shot bootstraps produce shallow docs). After each doc: a human review gate, phrased as "Review `<path>`. Say 'next' to continue or tell me what to change."
4. Generation: copy `templates/`, substitute tokens per `templates/README.md`, create phase 1 milestone files, run `python tools/check_docs.py --root . --fix`.
5. First session: open `docs/CURRENT.md`, claim M0-01.
6. Brownfield variant: the seven steps of `core/adoption.md §2`, with the same one-doc-per-session gate.
7. What the skill never does: write more than one design doc per session unless told to; tick a box; accept an ADR; edit a generated file.

- [ ] **Step 2: Verify and commit**

Run: `python tools/check_docs.py --root .`
Expected: `0 error(s)`.

```bash
git add skills/
git commit -m "skills: /bootstrap guided procedure

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 18: Entry point, kit self-documentation, v1 removal, acceptance

**Files:**
- Create: `BOOTSTRAP.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`
- Delete: `PROJECT-BOOSTRAP.md`

- [ ] **Step 1: Write `BOOTSTRAP.md`**

Under 250 lines. Sections:
1. The idea in one page (from v1 Part A, updated: five kinds, four layers, five-step lifecycle with spike and small-change hatches, one instruction file).
2. The machinery: one paragraph each pointing to `core/doc-kinds.md`, `core/layers.md`, `core/lifecycle.md`, `core/long-horizon.md`, `core/parallel-agents.md`, `core/tiers.md`.
3. Start here: "New project → `core/adoption.md §1`. Existing code → `core/adoption.md §2`. Pick a profile in `profiles/README.md`. Templates in `templates/`. Linter in `tools/check_docs.py`; hooks in `tools/hooks/README.md`. Agents with skills: `skills/bootstrap/SKILL.md`."
4. Target structure: the v1 Part B tree updated with `CURRENT.md`, `plans/M<n>/`, and the note that the design doc list comes from the profile.
5. Lessons: pointer to `core/lessons.md`.

- [ ] **Step 2: Write `README.md`, `AGENTS.md`, `CLAUDE.md`**

`README.md`: three paragraphs. What the kit is and who it is for. How to use it (clone or read `BOOTSTRAP.md`; or invoke the skill). How to run the linter and tests.

`AGENTS.md` (the kit's own, under 60 lines): what this repo is; read `BOOTSTRAP.md` first; rules: every path cited must exist (run the linter before ending a session); templates keep the field formats the linter parses; a change to a check adds a test and a fixture edit; no `{{` outside `templates/`; commands: the two verification commands.

`CLAUDE.md`: `@AGENTS.md`.

- [ ] **Step 3: Remove v1 and check nothing cites it**

Run:
```
git rm PROJECT-BOOSTRAP.md
grep -rn "PROJECT-BOOSTRAP\|PROJECT-BOOTSTRAP" --include="*.md" . | grep -v "docs/superpowers/"
```
Expected: the grep prints nothing.

- [ ] **Step 4: Run the acceptance checks from spec §15**

```
python -m pytest tools/tests -q
python tools/check_docs.py --root .
python tools/check_docs.py --root tools/tests/fixture/valid --fix && git status --short tools/tests/fixture
wc -l BOOTSTRAP.md templates/AGENTS.md
grep -oh "{{[a-zA-Z_ ]*}}" templates/*.md | sort -u > /tmp/tokens.txt; for t in $(cat /tmp/tokens.txt); do grep -q -F "$t" templates/README.md || echo "MISSING $t"; done
grep -c "^## " profiles/*.md
```
Expected: tests pass; linter `0 error(s)`; fixture `--fix` produces no changes in `git status`; BOOTSTRAP.md under 250 and templates/AGENTS.md under 120; no `MISSING` lines; each profile has 7 sections.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "kit v2: BOOTSTRAP.md entry point, kit AGENTS.md, remove v1 single file

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Self-review against the spec

| Spec section | Task |
|---|---|
| §3 layout | 1, 9, 10–18 |
| §4 doc kinds | 10 (DOCS.md), 11 |
| §5 layers, IDs, statuses | 3 (parsing), 10 (templates), 11 |
| §6 long-horizon | 3 (roadmap sketch), 4 (E009), 5 (E008/W002), 6 (E005 sketch), 8 (CURRENT.md), 10 (roadmap template), 12 |
| §7 parallel agents | 7 (W001), 8 (generation), 10 (WORKFLOW claims), 13 |
| §8 lifecycle | 10 (WORKFLOW), 12 |
| §9 adoption | 14 |
| §10 tiers | 3 (detect_tier), 8–9 (lite/minimal generation), 13 |
| §11 profiles | 16 |
| §12 linter | 1–9 |
| §13 skill | 17 |
| §14 migration | 15, 18 |
| §15 acceptance | 18 |
| §16 deferred | none (deferred) |

Placeholder scan: doc tasks give outlines and must-contain rules with the spec section as source; no "TBD" or "similar to" remains. Type consistency: `Finding`, `Config`, `Project`, `Milestone`, `Feature`, `Plan`, `Adr`, `Phase`, `Roadmap`, `generate`, `check`, `run`, `main`, `detect_tier`, `parse_stamp`, `GENERATED_MARKER` are named identically across Tasks 1–9.
