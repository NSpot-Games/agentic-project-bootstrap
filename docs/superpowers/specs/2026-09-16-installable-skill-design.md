# Installable Skill — Design

**Status:** approved for planning
**Date:** 2026-09-16
**Supersedes nothing.** Builds on `2026-09-15-bootstrap-kit-v2-design.md`.

## 1. Purpose

Make the kit's skill installable into any agent harness the way the large public skill
repositories are: `npx skills add NSpotGames/agentic-project-bootstrap` for the forty-plus
agents the `skills` CLI supports, and `claude plugin install` for Claude Code. Today the skill
at `skills/bootstrap/SKILL.md` cites `core/`, `profiles/`, `templates/` and
`tools/check_docs.py` relative to the repo root; every installer copies only the skill
directory, so an installed copy cannot run. The fix is to make the skill directory the unit of
distribution, following the Agent Skills specification's layout, and to add the two manifests
the chosen surfaces need.

## 2. Goals and non-goals

Goals:

- One copy of every kit document, inside the skill directory. Nothing at the repo root
  duplicates it.
- The skill works when installed alone: every path it and its references cite resolves from
  the skill root.
- Target projects are unaffected: they still copy templates and `tools/check_docs.py` into
  their tree and run `python tools/check_docs.py --fix` as today.
- Two install surfaces this cycle: the `skills` CLI (needs only the layout) and a Claude Code
  plugin (needs `.claude-plugin/` manifests). Plus a documented "clone and copy" fallback.
- The kit's own linter keeps reporting zero errors and zero warnings on the kit repo.

Non-goals (deferred, see §12): Gemini, OpenCode and Pi manifests; submission to the official
Claude plugin marketplace; a CI workflow; `skills-ref validate` in the test run.

## 3. Decisions taken in brainstorming

| Question | Decision |
|---|---|
| Skill name | `project-bootstrap` |
| Repo root | Thin: README, BOOTSTRAP.md, AGENTS.md, CLAUDE.md, LICENSE, manifests, tests, `docs/`. Single copy of kit docs inside the skill. |
| Surfaces | `skills` CLI and Claude Code plugin now; others later |
| License | MIT, copyright 2026 NSpotGames |
| First packaged version | 2.1.0 |

## 4. Repository layout after the change

```
.
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── hooks/
│   ├── hooks.json
│   └── stop.sh
├── skills/project-bootstrap/
│   ├── SKILL.md
│   ├── references/
│   │   ├── core/        doc-kinds.md layers.md lifecycle.md long-horizon.md
│   │   │                parallel-agents.md tiers.md adoption.md lessons.md
│   │   └── profiles/    README.md data-driven-product.md web-app-saas.md
│   │                    library-sdk-cli.md data-ml.md infra-platform.md
│   │                    research-prototype.md
│   ├── assets/templates/   the 16 files now in templates/
│   └── scripts/
│       ├── check_docs.py
│       └── hooks/       README.md stop.sh
├── tests/               conftest.py test_check_docs.py test_skill_package.py fixture/
├── docs/                .check_docs.toml superpowers/
├── AGENTS.md  BOOTSTRAP.md  CLAUDE.md  LICENSE  README.md  .gitignore
```

Moves are `git mv` so history follows the files:

| From | To |
|---|---|
| `skills/bootstrap/` | `skills/project-bootstrap/` |
| `core/` | `skills/project-bootstrap/references/core/` |
| `profiles/` | `skills/project-bootstrap/references/profiles/` |
| `templates/` | `skills/project-bootstrap/assets/templates/` |
| `tools/check_docs.py` | `skills/project-bootstrap/scripts/check_docs.py` |
| `tools/hooks/` | `skills/project-bootstrap/scripts/hooks/` |
| `tools/tests/` | `tests/` |

`tools/` and `core/`, `profiles/`, `templates/` cease to exist at the root.

## 5. Citation rules

Three kinds of path appear in kit docs. Each has one form.

1. **Kit-internal paths cited from inside the skill directory** are skill-relative:
   `references/core/layers.md §1`, `assets/templates/plan.md`, `scripts/check_docs.py`.
   This is the form the Agent Skills spec prescribes and the form that resolves after
   installation. It applies to `SKILL.md`, every file under `references/`, and
   `scripts/hooks/README.md`.
2. **Kit-internal paths cited from the repo root** (README.md, BOOTSTRAP.md, AGENTS.md) are
   full: `skills/project-bootstrap/references/core/layers.md §1`.
3. **Target-project paths** keep the existing `<project>/` prefix and are not citations:
   `<project>/tools/check_docs.py`, `<project>/docs/roadmap.md`. Unchanged from v2.

Generic filenames in angle brackets (`<file>.md §N.M`, `M<n>.md`) are unchanged.

The linter's citation check resolves kind 1 through a new config key (§6). Kinds 2 and 3
need no linter change.

## 6. Linter change: `citation_roots`

`docs/.check_docs.toml` gains an optional key:

```toml
citation_roots = ["skills/project-bootstrap"]
```

- Type: list of strings, each a directory relative to the project root. Default `[]`.
- Resolution: for each cited path, try `<root>/<path>` first, then `<citation_root>/<path>`
  for each entry in order. The first existing file wins. E001 fires only if none exists. E002
  (missing `§` anchor) is checked against the file that resolved.
- An entry naming a directory that does not exist is E012 (invalid config) with a message
  naming the entry.
- Invalid type (not a list of strings) is E012 as for other keys.
- No change to target projects: the key is absent from every template, so the default applies.

The `Config` dataclass gains `citation_roots: list[str]`; `load_config` reads it;
`check_citations` uses it. The kit's own config sets it as above.

## 7. Skill contract

Frontmatter of `skills/project-bootstrap/SKILL.md`:

```yaml
---
name: project-bootstrap
description: Bootstrap a new project or adopt an existing one into the docs-as-contract workflow. Use when the user says "bootstrap a project", "set up docs for this repo", "adopt the bootstrap kit", or pastes BOOTSTRAP.md.
license: MIT
compatibility: Requires Python 3.11+ for scripts/check_docs.py
metadata:
  author: NSpotGames
  version: "2.1.0"
---
```

Body changes, and only these:

- Every kit-internal citation takes the skill-relative form (§5, kind 1).
- The Generate step copies, in this order: the templates for the chosen tier from
  `assets/templates/` into the project; `scripts/check_docs.py` to
  `<project>/tools/check_docs.py`; `scripts/hooks/stop.sh` to `<project>/tools/hooks/stop.sh`
  when the user wants the hook. Then substitutes tokens and runs
  `python tools/check_docs.py --root . --fix` from the project root.
- A one-line note near the top: the skill's files are addressed relative to its own directory
  and it works when installed alone.

Constraints the spec places on the file: the body stays under 500 lines (spec recommendation;
today 101); the seven-section structure is kept; section numbers are unchanged.

`scripts/hooks/README.md` is rewritten for the same reason: its snippets are for the target
project, so it shows the copy step (`scripts/hooks/stop.sh` → `<project>/tools/hooks/stop.sh`)
and the `.claude/settings.json` entry that runs `sh tools/hooks/stop.sh`. The plugin-level
hook (§8) is mentioned as the alternative for Claude Code users who installed the plugin.

## 8. Install surfaces

### 8a. `skills` CLI

No repo-side configuration. The CLI discovers `skills/*/SKILL.md`, requires `name` and
`description`, and installs by symlink or copy into each agent's directory or the universal
`.agents/skills/`. README documents:

```
npx skills add NSpotGames/agentic-project-bootstrap
```

### 8b. Claude Code plugin

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

Skills load from the default `skills/` directory and hooks from the default `hooks/hooks.json`,
so neither path is declared.

`.claude-plugin/marketplace.json`:

```json
{
  "name": "agentic-project-bootstrap",
  "description": "Docs-as-contract bootstrap kit for agent-driven projects.",
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

README documents:

```
claude plugin marketplace add NSpotGames/agentic-project-bootstrap
claude plugin install project-bootstrap@agentic-project-bootstrap
```

with the slash-command equivalents `/plugin marketplace add …` and `/plugin install …`.

### 8c. Plugin Stop hook

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

`hooks/stop.sh`:

```sh
#!/bin/sh
# Plugin-level Stop hook. Runs the project's own copy of the linter, and only in projects
# that have one, so repos not built on the kit are never linted.
input=$(cat)
root="${CLAUDE_PROJECT_DIR:-.}"
[ -f "$root/tools/check_docs.py" ] || exit 0
py=python3
"$py" -c "pass" >/dev/null 2>&1 || py=python
"$py" -c "pass" >/dev/null 2>&1 || { echo 'check_docs: no python interpreter found; skipping'; exit 0; }
if printf '%s' "$input" | "$py" -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get("stop_hook_active") else 1)' 2>/dev/null; then exit 0; fi
"$py" "$root/tools/check_docs.py" --root "$root" \
  || { echo 'check_docs found errors; fix them before ending the session'; exit 2; }
```

The guard parses stdin as JSON because Claude Code writes compact JSON; when no Python
interpreter is on PATH the hook exits 0 rather than block.

Three properties the plan must preserve: exit 0 when `stop_hook_active` is true; exit 0 when
the project has no `tools/check_docs.py`; exit 0 when no Python interpreter is on PATH.

### 8d. Manual

README documents: clone the repo and copy `skills/project-bootstrap/` into the harness's
skills directory (`.claude/skills/`, `.agents/skills/`, `~/.codex/skills/`, or wherever the
harness reads them), or just read `BOOTSTRAP.md` and hand it to the agent.

## 9. Root documents

- **README.md**: what the kit is (two paragraphs), an **Install** section with 8a–8d in that
  order, a **Use** section (invoke the skill; or read BOOTSTRAP.md; run the linter), a
  **Repository layout** list, and **Develop** (test and lint commands). All kit-internal
  citations in the full form.
- **BOOTSTRAP.md**: unchanged content; every citation rewritten to the full form; §3 "Start
  here" points at `skills/project-bootstrap/SKILL.md` and the new paths for templates, linter
  and hooks.
- **AGENTS.md**: first paragraph names the new directories; commands become
  `python -m pytest tests -q` and
  `python skills/project-bootstrap/scripts/check_docs.py --root .`; rules unchanged except
  the templates rule names `skills/project-bootstrap/assets/templates/` and the test rule
  names `tests/`.
- **CLAUDE.md**: unchanged (`@AGENTS.md`).
- **LICENSE**: MIT, `Copyright (c) 2026 NSpotGames`.
- **docs/.check_docs.toml**:

```toml
# Config for running the kit's own linter on this repo.
citation_roots = ["skills/project-bootstrap"]
allow_tbd_in = ["docs/superpowers/"]
citation_exclude = ["skills/project-bootstrap/assets/templates/", "tests/fixture/", "docs/superpowers/"]
exclude = ["tests/fixture", ".superpowers"]
```

## 10. Tests

`tests/conftest.py` puts `skills/project-bootstrap/scripts` on `sys.path`;
`tests/test_check_docs.py` derives `CHECK` from the same directory. The fixture is unchanged in
content and moves with the directory.

New in `tests/test_check_docs.py`:

- `citation_roots` resolves a citation that is missing from the root but present under a
  listed root, and E002 is checked against the resolved file.
- A cited path missing from both root and every listed root is E001.
- A `citation_roots` entry naming a nonexistent directory is E012.

New file `tests/test_skill_package.py`, stdlib only:

- Frontmatter `name` equals the directory name and matches `^[a-z0-9]+(-[a-z0-9]+)*$`,
  length 1–64.
- `description` is non-empty and at most 1024 characters.
- `SKILL.md` has fewer than 500 lines.
- Every relative path cited in `SKILL.md` (same regex the linter uses, plus bare directory
  mentions ending in `/`) exists under the skill directory.
- The version string is identical in `SKILL.md` metadata, `.claude-plugin/plugin.json`, and
  `.claude-plugin/marketplace.json`.
- `hooks/hooks.json` parses and its Stop command references `hooks/stop.sh`.
- `hooks/stop.sh` exits 0 on `{"stop_hook_active": true}` input and exits 0 in a temp
  directory with no `tools/check_docs.py` (skipped when no `sh` is on PATH).

## 11. Versioning

- Version `2.1.0` in the three places §10 checks. Bumped together, by hand.
- After merge to `main`: annotated tag `v2.1.0`, and a GitHub release whose notes are the
  install commands and the layout change. No changelog file.

## 12. Deferred

- `gemini-extension.json` and `GEMINI.md` for Gemini CLI; `package.json` for OpenCode and Pi.
- Submission to Anthropic's official plugin marketplace.
- A GitHub Actions workflow running the tests and the kit lint.
- Running `skills-ref validate` in the test suite (it is an external dependency; the
  frontmatter checks in §10 cover the same rules).
- The three v2 leftovers recorded in memory: evidence-cap boundary test, sourced lessons for
  five profiles, lite-tier checkbox roadmap template.

## 13. Acceptance

1. `python -m pytest tests -q` passes, including the new tests in §10.
2. `python skills/project-bootstrap/scripts/check_docs.py --root .` reports 0 errors, 0
   warnings.
3. `python skills/project-bootstrap/scripts/check_docs.py --root tests/fixture/valid --fix`
   produces no diff.
4. No file under `skills/project-bootstrap/` cites a path outside the skill directory except
   through the `<project>/` convention, except the trigger phrase `BOOTSTRAP.md` in the
   skill's frontmatter description.
5. `core/`, `profiles/`, `templates/`, `tools/`, `skills/bootstrap/` no longer exist.
6. `git log --follow` on a moved file shows its pre-move history.
7. Copying `skills/project-bootstrap/` alone into an empty directory and running
   `python scripts/check_docs.py --help` from inside it works, and every path cited in
   `SKILL.md` exists in that copy.
8. `plugin.json`, `marketplace.json`, `hooks.json` are valid JSON; `hooks/stop.sh` satisfies
   the three exit-0 properties in §8c.
9. Version `2.1.0` agrees in all three places.
