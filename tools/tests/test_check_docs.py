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
