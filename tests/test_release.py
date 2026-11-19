"""
AQMI — Tests of the pre-publication check (Phase 8) and of the DataFolder tool.

Each test builds a small, complete repository in a temporary folder, checks
that it passes, and then introduces one defect to check that the rule that
should catch it does catch it.

Run them with:   pytest -v tests/test_release.py
"""

import pytest

from scripts import check_release as rc
from scripts.set_powerbi_data_folder import read_data_folder, set_data_folder

README = """# Demo
## Overview
## Objectives
## Architecture
## Tech stack
## Features
## Data model
## KPIs
## Screenshots
![Executive](assets/screenshots/01.png)
## Installation
## Methodology
## Limitations
## Synthetic data and disclaimer
All data is synthetic, the company is fictitious and the system is not certified.
See [the docs](documentation/README.md).
"""

EXPRESSIONS = ('expression DataFolder = "C:\\\\data\\\\processed\\\\" meta [IsParameterQuery=true, Type="Text"]\r\n'
               '\tqueryGroup: Parameters\r\n')


@pytest.fixture
def repo(tmp_path):
    files = {
        "README.md": README,
        "LICENSE": "MIT License\n\nCopyright (c) 2026 Jane Doe\n",
        "requirements.txt": "pytest\n",
        ".gitignore": "\n".join(rc.GITIGNORE_RULES) + "\n",
        "pytest.ini": "[pytest]\n",
        "config/settings.py": "",
        "scripts/run_pipeline.py": "",
        "powerbi/AQMI.pbip": "{}",
        "powerbi/AQMI.SemanticModel/definition/expressions.tmdl": EXPRESSIONS,
        "documentation/README.md": "# Docs\n",
        ".github/workflows/tests.yml": "name: tests\n",
    }
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="")
    shots = tmp_path / "assets" / "screenshots"
    shots.mkdir(parents=True)
    for i in range(1, 9):
        (shots / f"{i:02d}.png").write_bytes(b"\x89PNG")
    return tmp_path


def errors(root):
    return [f for f in rc.check_release(root) if f.severity == "ERROR"]


def test_complete_repository_passes(repo):
    assert errors(repo) == []


def test_missing_required_file_is_an_error(repo):
    (repo / "LICENSE").unlink()
    assert any(f.rule == "R01" for f in errors(repo))


def test_missing_readme_section_is_an_error(repo):
    text = (repo / "README.md").read_text(encoding="utf-8").replace("## Methodology\n", "")
    (repo / "README.md").write_text(text, encoding="utf-8")
    assert [f.message for f in errors(repo) if f.rule == "R02"] == ["README: no section for 'Methodology'"]


def test_broken_link_is_an_error(repo):
    (repo / "documentation" / "README.md").write_text("[phase 9](09_missing.md)\n", encoding="utf-8")
    assert any(f.rule == "R03" and "09_missing.md" in f.message for f in errors(repo))


def test_links_inside_code_blocks_are_ignored(repo):
    (repo / "documentation" / "README.md").write_text("```\n[x](not_a_file.md)\n```\n", encoding="utf-8")
    assert errors(repo) == []


def test_placeholder_left_in_license_is_an_error(repo):
    (repo / "LICENSE").write_text("Copyright (c) 2026 YOUR NAME\n", encoding="utf-8")
    assert any(f.rule == "R04" for f in errors(repo))


def test_personal_path_is_an_error_but_the_datafolder_parameter_is_only_info(repo):
    (repo / "documentation" / "README.md").write_text("Open C:\\Users\\jdoe\\Desktop\\AQMI\n", encoding="utf-8")
    expressions = repo / "powerbi/AQMI.SemanticModel/definition/expressions.tmdl"
    expressions.write_text('expression DataFolder = "C:\\Users\\jdoe\\aqmi\\data\\processed\\"\n', encoding="utf-8")
    findings = [f for f in rc.check_release(repo) if f.rule == "R05"]
    assert [f.severity for f in findings] == ["ERROR", "INFO"]


def test_generic_paths_are_allowed(repo):
    (repo / "documentation" / "README.md").write_text("Go to C:\\Users\\<usuario>\\Proyectos\n", encoding="utf-8")
    assert errors(repo) == []


def test_gitignore_must_exclude_the_power_bi_cache(repo):
    (repo / ".gitignore").write_text("database/*.db\n", encoding="utf-8")
    messages = [f.message for f in errors(repo) if f.rule == "R06"]
    assert ".gitignore does not exclude **/.pbi/cache.abf" in messages


def test_file_over_100_mb_is_an_error(repo):
    big = repo / "data" / "huge.csv"
    big.parent.mkdir(parents=True)
    with open(big, "wb") as handle:              # sparse file: no real disk space used
        handle.truncate(101 * rc.MB)
    assert any(f.rule == "R07" for f in errors(repo))


def test_classification_marking_is_an_error(repo):
    (repo / "documentation" / "notes.md").write_text("DIFUSIÓN LIMITADA\n", encoding="utf-8")
    assert any(f.rule == "R08" for f in errors(repo))


def test_readme_must_say_the_data_is_synthetic(repo):
    text = (repo / "README.md").read_text(encoding="utf-8").replace("not certified", "reliable")
    (repo / "README.md").write_text(text, encoding="utf-8")
    assert any(f.rule == "R09" for f in errors(repo))


def test_missing_screenshots_are_only_a_warning(repo):
    for image in (repo / "assets" / "screenshots").glob("*.png"):
        image.unlink()
    (repo / "README.md").write_text(README.replace("![Executive](assets/screenshots/01.png)\n", ""),
                                    encoding="utf-8")
    findings = [f for f in rc.check_release(repo) if f.rule == "R10"]
    assert findings[0].severity == "WARNING" and errors(repo) == []


def test_local_folders_are_not_checked(repo):
    cache = repo / "powerbi" / "AQMI.SemanticModel" / ".pbi"
    cache.mkdir()
    (cache / "localSettings.json").write_text('{"path": "C:\\\\Users\\\\jdoe\\\\x"}', encoding="utf-8")
    assert errors(repo) == []


# ------------------------------------------------------------- DataFolder tool
def test_set_data_folder_changes_only_the_parameter(repo):
    project = repo / "powerbi"
    old, new = set_data_folder(project, "D:\\AQMI\\data\\processed")
    assert old == "C:\\\\data\\\\processed\\\\" and new == "D:\\AQMI\\data\\processed\\"
    assert read_data_folder(project) == new
    content = (project / "AQMI.SemanticModel/definition/expressions.tmdl").read_bytes()
    assert content.count(b"\r\n") == 2                 # Power BI's line endings are kept
    assert b"queryGroup: Parameters" in content


# ------------------------------------------------------------------ case study
def test_case_study_in_the_repository_matches_the_data(tmp_path):
    """The case study is generated from the data: the committed file must be
    exactly what the generator writes from a freshly simulated database."""
    from config import settings
    from scripts.build_case_study import OUTPUT, build
    from scripts.generate_data import generate

    db_path = tmp_path / "aqmi.db"
    generate(db_path, export_dir=None)
    fresh = tmp_path / "case_study.md"
    assert build(db_path, fresh) == "NC-2025-0021"
    committed = settings.PROJECT_ROOT / "documentation" / OUTPUT.name
    assert committed.read_text(encoding="utf-8") == fresh.read_text(encoding="utf-8")
