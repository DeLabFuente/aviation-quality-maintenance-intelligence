"""
AQMI — Pre-publication check (Phase 8).

Before the repository is published on GitHub, this script checks that it is
complete, that its documentation is consistent and that nothing personal or
restricted is about to be made public. It applies to the repository the same
idea as the data quality gate: a checklist of rules, each with a severity.

    ERROR    blocks the publication (exit code 1)
    WARNING  must be reviewed, but does not block
    INFO     for information

Rules
    R01  Required files exist (README, LICENSE, requirements, .gitignore, .pbip …)
    R02  The README has every section required by the project specification
    R03  Every relative link and image in the Markdown files points to an existing file
    R04  No placeholder is left (YOUR NAME, YOUR-GITHUB-USER …)
    R05  No personal absolute path (C:\\Users\\<name>, /home/<name>) in text files
    R06  .gitignore excludes the local and generated files
    R07  No file is too large for GitHub (100 MB limit; warning from 50 MB)
    R08  No security classification marking in any text file
    R09  The README states that the data is synthetic and the company fictitious
    R10  The dashboard screenshots exist

How to run it (from the main project folder, with the virtual environment active):
    python scripts/check_release.py

Expected result: "RELEASE CHECK PASSED" and a report in reports/release_check.md.
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings  # noqa: E402
from scripts.common import setup_logging  # noqa: E402

logger = setup_logging("check_release")

# Folders that are never published (local, generated or vendored third-party files).
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".pbi", "logs", "schemas"}
TEXT_SUFFIXES = {".md", ".py", ".sql", ".json", ".tmdl", ".txt", ".yml", ".yaml", ".ini", ".pbip",
                 ".pbir", ".pbism", ".platform", ".cff", ""}

REQUIRED_FILES = [
    "README.md", "LICENSE", "requirements.txt", ".gitignore", "pytest.ini",
    "config/settings.py", "scripts/run_pipeline.py", "powerbi/AQMI.pbip",
    "documentation/README.md", ".github/workflows/tests.yml",
]

# Section of the README  ->  words that its heading must contain (any of them)
README_SECTIONS = {
    "Project description": ("overview", "about"),
    "Objectives": ("objective",),
    "Architecture": ("architecture",),
    "Technologies": ("tech stack", "technolog"),
    "Features": ("feature",),
    "Data model": ("data model",),
    "Indicators": ("kpi", "indicator"),
    "Screenshots": ("screenshot", "dashboard"),
    "Installation": ("install", "getting started", "quick start"),
    "Methodology": ("methodolog",),
    "Limitations": ("limitation",),
    "Synthetic data notice": ("synthetic", "disclaimer"),
}

GITIGNORE_RULES = ["database/*.db", ".venv/", "__pycache__/", "**/.pbi/localSettings.json", "**/.pbi/cache.abf"]
PLACEHOLDERS = re.compile(r"YOUR[ _-]NAME|YOUR[ _-]GITHUB[ _-]USER|<your[ _-][a-z-]+>", re.I)
PERSONAL_PATH = re.compile(r"\b[A-Za-z]:\\Users\\(?!<)[^\\\s`'\"<>*|]+|(?<![\w.~])/(?:home|Users)/(?!<)[A-Za-z0-9._-]+")
MARKINGS = re.compile(r"\b(CONFIDENCIAL|RESTRINGIDO|DIFUSIÓN LIMITADA|SECRETO|NATO RESTRICTED|"
                      r"NATO CONFIDENTIAL|RESTRICTED|CONFIDENTIAL)\b")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_SRC = re.compile(r"""<(?:img|a)\s[^>]*(?:src|href)=["']([^"']+)["']""", re.I)
MB = 1024 * 1024


@dataclass
class Finding:
    rule: str
    severity: str
    message: str


def published_files(root: Path):
    """Every file that would be published (local and vendored folders skipped)."""
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]) or not path.is_file():
            continue
        if path.suffix == ".db" or path.name.endswith((".db-journal", ".db-wal", ".db-shm")):
            continue
        yield path


SELF_REPORT = ("reports", "release_check.md")   # this script's own output is not scanned


def is_text(path: Path) -> bool:
    return (path.suffix.lower() in TEXT_SUFFIXES and path.name != ".gitkeep"
            and path.parts[-2:] != SELF_REPORT)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


# ------------------------------------------------------------------------ rules
def r01_required_files(root: Path) -> list[Finding]:
    return [Finding("R01", "ERROR", f"required file missing: {name}")
            for name in REQUIRED_FILES if not (root / name).exists()]


def r02_readme_sections(root: Path) -> list[Finding]:
    readme = root / "README.md"
    if not readme.exists():
        return []
    headings = [line.lstrip("#").strip().lower() for line in read(readme).splitlines()
                if line.startswith("#")]
    findings = []
    for section, words in README_SECTIONS.items():
        if not any(word in heading for heading in headings for word in words):
            findings.append(Finding("R02", "ERROR", f"README: no section for '{section}'"))
    return findings


def r03_links(root: Path) -> list[Finding]:
    findings = []
    for path in published_files(root):
        if path.suffix.lower() != ".md":
            continue
        text = read(path)
        text = re.sub(r"```.*?```", "", text, flags=re.S)       # ignore code blocks
        targets = LINK.findall(text) + HTML_SRC.findall(text)
        for target in targets:
            if re.match(r"^(https?:|mailto:|#)", target):
                continue
            clean = target.split("#")[0].split("?")[0]
            if not clean:
                continue
            resolved = (path.parent / clean).resolve()
            if not resolved.exists():
                rel = path.relative_to(root).as_posix()
                findings.append(Finding("R03", "ERROR", f"{rel}: broken link -> {target}"))
    return findings


def r04_placeholders(root: Path) -> list[Finding]:
    findings = []
    candidates = [root / "README.md", root / "LICENSE", root / "CITATION.cff"]
    candidates += list((root / ".github").rglob("*")) if (root / ".github").exists() else []
    for path in candidates:
        if path.is_file():
            for number, line in enumerate(read(path).splitlines(), start=1):
                for match in PLACEHOLDERS.findall(line):
                    rel = path.relative_to(root).as_posix()
                    findings.append(Finding("R04", "ERROR", f"{rel}:{number}: placeholder left: {match}"))
    return findings


def r05_personal_paths(root: Path) -> list[Finding]:
    findings = []
    for path in published_files(root):
        if not is_text(path):
            continue
        rel = path.relative_to(root).as_posix()
        for number, line in enumerate(read(path).splitlines(), start=1):
            for match in PERSONAL_PATH.findall(line):
                if rel.endswith("expressions.tmdl") and line.startswith("expression DataFolder"):
                    findings.append(Finding("R05", "INFO", f"{rel}: the DataFolder parameter holds the path of "
                                            "the computer that last saved the project (each user sets their "
                                            "own with scripts/set_powerbi_data_folder.py)"))
                else:
                    findings.append(Finding("R05", "ERROR", f"{rel}:{number}: personal path: {match}"))
    return findings


def r06_gitignore(root: Path) -> list[Finding]:
    path = root / ".gitignore"
    if not path.exists():
        return []
    lines = {line.strip() for line in read(path).splitlines()}
    return [Finding("R06", "ERROR", f".gitignore does not exclude {rule}") for rule in GITIGNORE_RULES
            if rule not in lines]


def r07_sizes(root: Path) -> list[Finding]:
    findings = []
    for path in published_files(root):
        size = path.stat().st_size
        rel = path.relative_to(root).as_posix()
        if size > 100 * MB:
            findings.append(Finding("R07", "ERROR", f"{rel}: {size / MB:.0f} MB (GitHub rejects files over 100 MB)"))
        elif size > 50 * MB:
            findings.append(Finding("R07", "WARNING", f"{rel}: {size / MB:.0f} MB (GitHub warns over 50 MB)"))
    return findings


def r08_markings(root: Path) -> list[Finding]:
    findings = []
    for path in published_files(root):
        if not is_text(path) or path.name in ("check_release.py", "test_release.py"):
            continue
        for number, line in enumerate(read(path).splitlines(), start=1):
            for match in MARKINGS.findall(line):
                rel = path.relative_to(root).as_posix()
                findings.append(Finding("R08", "ERROR", f"{rel}:{number}: classification marking '{match}'"))
    return findings


def r09_disclaimer(root: Path) -> list[Finding]:
    readme = root / "README.md"
    if not readme.exists():
        return []
    text = read(readme).lower()
    needed = {"synthetic": "synthetic", "fictitious": "fictitious", "not certified": "not certified"}
    return [Finding("R09", "ERROR", f"README does not say the system is '{word}'")
            for word in needed.values() if word not in text]


def r10_screenshots(root: Path) -> list[Finding]:
    folder = root / "assets" / "screenshots"
    images = sorted(folder.glob("*.png")) if folder.exists() else []
    if len(images) < 8:
        return [Finding("R10", "WARNING", f"assets/screenshots has {len(images)} of 8 dashboard screenshots")]
    return [Finding("R10", "INFO", f"{len(images)} screenshots in assets/screenshots")]


RULES = [r01_required_files, r02_readme_sections, r03_links, r04_placeholders, r05_personal_paths,
         r06_gitignore, r07_sizes, r08_markings, r09_disclaimer, r10_screenshots]


def check_release(root: Path) -> list[Finding]:
    findings = []
    for rule in RULES:
        findings.extend(rule(root))
    return findings


def write_report(findings: list[Finding], path: Path) -> None:
    errors = sum(f.severity == "ERROR" for f in findings)
    warnings = sum(f.severity == "WARNING" for f in findings)
    lines = ["# AQMI — Pre-publication check", "",
             f"Result: **{'PASSED' if errors == 0 else 'FAILED'}** — {errors} error(s), {warnings} warning(s).", "",
             "| Rule | Severity | Finding |", "|---|---|---|"]
    lines += [f"| {f.rule} | {f.severity} | {f.message.replace('|', '/')} |" for f in findings]
    if not findings:
        lines.append("| — | — | No findings |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    findings = check_release(settings.PROJECT_ROOT)
    for f in findings:
        log = logger.error if f.severity == "ERROR" else logger.warning if f.severity == "WARNING" else logger.info
        log(f"{f.rule} {f.message}")
    report = settings.REPORTS_DIR / "release_check.md"
    write_report(findings, report)
    errors = sum(f.severity == "ERROR" for f in findings)
    logger.info(f"Report: {report.relative_to(settings.PROJECT_ROOT).as_posix()}")
    if errors:
        logger.error(f"RELEASE CHECK FAILED: {errors} error(s)")
        return 1
    logger.info("RELEASE CHECK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
