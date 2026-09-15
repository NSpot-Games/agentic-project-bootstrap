import shutil
import subprocess
import sys as _sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

import check_docs as cd

FIXTURE = Path(__file__).parent / "fixture" / "valid"

CHECK = Path(__file__).resolve().parents[1] / "check_docs.py"


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
    # the fixture now carries committed, up-to-date generated files (needed by the
    # fixture-currency tests), so remove them here to exercise the missing-index case.
    for relp in GENERATED:
        (root / relp).unlink(missing_ok=True)
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


# --------------------------------------------------------------------------- final fix wave


def test_gen_current_m10_orders_numerically_not_lexically(tmp_path):
    root = make_project(tmp_path)
    (root / "docs/milestones/M2.md").write_text(
        "# M2 — Authoring tool\n"
        "**Status:** in progress\n"
        "**Goal:** an editor for instances.\n"
        "**Exit criteria:** an editor opens and edits one instance without corrupting it.\n"
        "**Evidence of exit:**\n"
        "**Depends on:**\n\n"
        "## Features\n"
        "- [ ] M2-01 — Basic editor\n\n"
        "## Notes\n",
        encoding="utf-8")
    (root / "docs/milestones/M10.md").write_text(
        "# M10 — Extra milestone\n"
        "**Status:** in progress\n"
        "**Goal:** something later.\n"
        "**Exit criteria:** something measurable.\n"
        "**Evidence of exit:**\n"
        "**Depends on:**\n\n"
        "## Features\n"
        "- [ ] M10-01 — Something\n\n"
        "## Notes\n",
        encoding="utf-8")
    roadmap = root / "docs/roadmap.md"
    text = roadmap.read_text(encoding="utf-8")
    text = text.replace(
        "## Explicitly deferred",
        "### M10 — Extra milestone\nGoal: something later.\n\n## Explicitly deferred")
    roadmap.write_text(text, encoding="utf-8")
    cur = cd.generate(cd.load_project(cd.load_config(root)))["docs/CURRENT.md"]
    prog_line = next(ln for ln in cur.splitlines() if ln.startswith("**Milestones in progress:**"))
    assert prog_line.index("M2 —") < prog_line.index("M10 —")
    assert cur.index("M2-01") < cur.index("M10-01")


def test_gen_current_stays_under_forty_lines_with_many_items(tmp_path):
    root = make_project(tmp_path)
    plans_dir = root / "docs" / "plans" / "M9"
    plans_dir.mkdir(parents=True, exist_ok=True)
    plan_body = (
        "**Milestone:** M9\n**Branch:** feat/{pid}\n**Design docs:**\n**ADRs:**\n**Depends on:**\n\n"
        "## Sessions\n{sessions}\n\n## Objective\nX\n\n## Current state\nX\n\n## Approach\nX\n\n"
        "## Tasks\n- [ ] T1 — X. **Verify:** `true`\n\n## Progress notes\n\n## Verification log\n"
    )
    for i in range(1, 8):
        pid = f"M9-{i:02d}"
        (plans_dir / f"{pid}-claimed.md").write_text(
            f"# {pid} — Claimed {i}\n**Status:** in progress\n" +
            plan_body.format(pid=pid, sessions=f"- 2026-09-15T09:00Z — claude-code — feat/{pid}"),
            encoding="utf-8")
    for i in range(1, 7):
        pid = f"M7-{i:02d}"
        (plans_dir / f"{pid}-blocked.md").write_text(
            f"# {pid} — Blocked {i}\n**Status:** blocked\n" +
            plan_body.format(pid=pid, sessions=""),
            encoding="utf-8")
    features = "\n".join(f"- [ ] M8-{i:02d} — Feature {i}" for i in range(1, 9))
    (root / "docs/milestones/M8.md").write_text(
        "# M8 — Extra\n**Status:** in progress\n**Goal:** test.\n"
        "**Exit criteria:** something measurable.\n**Evidence of exit:**\n**Depends on:**\n\n"
        f"## Features\n{features}\n\n## Notes\n",
        encoding="utf-8")
    for i in range(1, 4):
        (root / "docs" / "evidence" / f"extra-{i}.md").write_text(f"# Extra {i}\n", encoding="utf-8")
    cur = cd.generate(cd.load_project(cd.load_config(root)))["docs/CURRENT.md"]
    assert len(cur.strip().split("\n")) < 40
    assert "and " in cur and "more" in cur


def test_plan_rel_for_removed():
    assert not hasattr(cd, "_plan_rel_for")


def test_e011_non_utf8_file_reports_finding_not_traceback(tmp_path):
    root = make_project(tmp_path)
    (root / "docs" / "bad.md").write_bytes(b"\xff\xfe bad")
    found = cd.run(root)
    assert "E011" in codes(found)


def test_e012_malformed_config_toml_reports_finding_not_traceback(tmp_path):
    root = make_project(tmp_path, {
        "docs/.check_docs.toml": ("stale_hours = 876000", "stale_hours = ["),
    })
    found = cd.run(root)
    assert "E012" in codes(found)


def test_non_milestone_stem_in_milestones_dir_does_not_crash(tmp_path):
    root = make_project(tmp_path)
    (root / "docs/milestones/Mission.md").write_text("# Mission\nA note, not a milestone.\n", encoding="utf-8")
    found = cd.run(root)
    assert "E001" not in [f.code for f in found if f.path.endswith("Mission.md")]
    assert not any(f.path.endswith("Mission.md") for f in found)


def test_e006_ticked_feature_with_no_plan(tmp_path):
    root = make_project(tmp_path, {
        "docs/milestones/M1.md": ("- [ ] M1-02", "- [x] M1-02"),
    })
    assert "E006" in codes(cd.run(root))


def test_gen_current_stamp_rendered_in_utc(tmp_path):
    root = make_project(tmp_path, {
        "docs/plans/M1/M1-01-runtime-loop.md": (
            "2026-09-15T09:00Z — claude-code — feat/M1-01-runtime-loop",
            "2026-09-15T11:00:00+02:00 — claude-code — feat/M1-01-runtime-loop"),
    })
    cur = cd.generate(cd.load_project(cd.load_config(root)))["docs/CURRENT.md"]
    assert "2026-09-15T09:00Z" in cur
    assert "2026-09-15T11:00" not in cur


def test_evidence_ordered_numerically_not_lexically(tmp_path):
    root = make_project(tmp_path)
    (root / "docs/evidence/M2-exit.md").write_text("# M2 exit\n", encoding="utf-8")
    (root / "docs/evidence/M10-exit.md").write_text("# M10 exit\n", encoding="utf-8")
    cur = cd.generate(cd.load_project(cd.load_config(root)))["docs/CURRENT.md"]
    assert cur.index("M2-exit.md") < cur.index("M10-exit.md")


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
