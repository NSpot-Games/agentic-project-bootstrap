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
