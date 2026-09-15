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
