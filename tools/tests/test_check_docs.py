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
