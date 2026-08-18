from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "release_meta", _ROOT / "scripts" / "release_meta.py"
)
assert _SPEC and _SPEC.loader
release_meta = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(release_meta)


def test_parse_tag_stable():
    assert release_meta.parse_tag("v0.5.0") == ("0.5.0", "0.5.0", "0.5.0", False)


def test_parse_tag_beta():
    display, pep440, docker_tag, is_pre = release_meta.parse_tag("v0.5.0-beta.1")
    assert display == "0.5.0-beta.1"
    assert pep440 == "0.5.0b1"
    assert docker_tag == "0.5.0-beta.1"
    assert is_pre is True


def test_parse_tag_rc_and_refs_prefix():
    display, pep440, docker_tag, is_pre = release_meta.parse_tag("refs/tags/v0.5.0-rc.2")
    assert display == "0.5.0-rc.2"
    assert pep440 == "0.5.0rc2"
    assert docker_tag == "0.5.0-rc.2"
    assert is_pre is True


def test_parse_tag_rejects_incomplete():
    with pytest.raises(SystemExit, match="Unsupported tag"):
        release_meta.parse_tag("v1.2")


def test_normalize_tag_from_github_ref():
    assert release_meta.normalize_tag("refs/tags/v0.4.9") == "v0.4.9"
    assert release_meta.resolve_tag_arg("v0.4.9") == "v0.4.9"


def test_pyproject_version_pep621(tmp_path: Path):
    path = tmp_path / "pyproject.toml"
    path.write_text('[project]\nname = "x"\nversion = "0.5.0b1"\n', encoding="utf-8")
    assert release_meta.pyproject_version(path) == "0.5.0b1"


def test_pyproject_version_poetry(tmp_path: Path):
    path = tmp_path / "pyproject.toml"
    path.write_text('[tool.poetry]\nname = "x"\nversion = "1.2.3"\n', encoding="utf-8")
    assert release_meta.pyproject_version(path) == "1.2.3"


def test_pyproject_version_missing(tmp_path: Path):
    path = tmp_path / "pyproject.toml"
    path.write_text('[project]\nname = "x"\n', encoding="utf-8")
    with pytest.raises(SystemExit, match="No version found"):
        release_meta.pyproject_version(path)


def test_changelog_section_extracts_body(tmp_path: Path):
    path = tmp_path / "CHANGELOG.md"
    path.write_text(
        "## [Unreleased]\n\nstaging\n\n"
        "## [0.5.0-beta.1] — 2026-08-18\n\n### Added\n\n- freeze\n\n"
        "## [0.4.9] — 2026-08-18\n\nold\n",
        encoding="utf-8",
    )
    notes = release_meta.changelog_section("0.5.0-beta.1", "0.5.0b1", path)
    assert "## [0.5.0-beta.1] — 2026-08-18" in notes
    assert "freeze" in notes
    assert "staging" not in notes
    assert "old" not in notes


def test_changelog_missing_heading_shows_snippet(tmp_path: Path):
    path = tmp_path / "CHANGELOG.md"
    path.write_text("## [Unreleased]\n\nstill here\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="Found top of file") as exc:
        release_meta.changelog_section("0.5.0-beta.1", "0.5.0b1", path)
    assert "still here" in str(exc.value)
    assert "[Unreleased]" in str(exc.value)
