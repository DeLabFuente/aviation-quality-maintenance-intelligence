"""
AQMI — Point the Power BI project to the CSV files on this computer.

Power BI reads the CSV files of `data/processed/` through one Power Query
parameter, `DataFolder`, which must hold the FULL path of that folder (Power BI
does not accept relative paths). This script writes the right path for the
computer it runs on, so that the project works after cloning or moving it.

Close Power BI Desktop before running it: if the project is open, Power BI
overwrites the change the next time it saves.

How to run it (from the main project folder, with the virtual environment active):
    python scripts/set_powerbi_data_folder.py            # use this computer's path
    python scripts/set_powerbi_data_folder.py --check    # only show the current value
    python scripts/set_powerbi_data_folder.py --path "D:\\AQMI\\data\\processed"

Expected result:
    INFO    | DataFolder was: C:\\old\\place\\data\\processed\\
    INFO    | DataFolder now: C:\\Users\\<you>\\aqmi\\data\\processed\\
"""

import argparse
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings  # noqa: E402
from scripts.common import setup_logging  # noqa: E402

logger = setup_logging("set_powerbi_data_folder")

EXPRESSIONS = Path("AQMI.SemanticModel") / "definition" / "expressions.tmdl"
PARAMETER_RE = re.compile(r'^(expression DataFolder = )"((?:[^"]|"")*)"', re.M)


def default_folder() -> str:
    """Full path of data/processed on this computer, ending with a separator."""
    return str(settings.POWERBI_DATA_DIR.resolve()) + os.sep


def read_data_folder(project_dir: Path) -> str:
    """Return the current value of the DataFolder parameter."""
    text = (project_dir / EXPRESSIONS).read_text(encoding="utf-8")
    match = PARAMETER_RE.search(text)
    if not match:
        raise ValueError(f"DataFolder parameter not found in {EXPRESSIONS}")
    return match.group(2).replace('""', '"')


def set_data_folder(project_dir: Path, folder: str) -> tuple[str, str]:
    """Write `folder` into the DataFolder parameter. Returns (old value, new value)."""
    if not folder.endswith(("\\", "/")):
        folder += "\\" if "\\" in folder else "/"
    path = project_dir / EXPRESSIONS
    # newline="" keeps the line endings exactly as Power BI wrote them
    with open(path, encoding="utf-8", newline="") as handle:
        text = handle.read()
    old = read_data_folder(project_dir)
    literal = folder.replace('"', '""')                    # quotes are doubled in M text
    new_text = PARAMETER_RE.sub(lambda m: f'{m.group(1)}"{literal}"', text, count=1)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(new_text)
    return old, folder


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Set the DataFolder parameter of the Power BI project.")
    parser.add_argument("--path", help="folder to use (default: data/processed of this project)")
    parser.add_argument("--check", action="store_true", help="only show the current value")
    args = parser.parse_args(argv)

    project_dir = settings.POWERBI_DIR
    if not (project_dir / EXPRESSIONS).exists():
        logger.error(f"Power BI project not found: {project_dir / EXPRESSIONS}")
        return 1
    current = read_data_folder(project_dir)
    if args.check:
        logger.info(f"DataFolder: {current}")
        exists = Path(current).is_dir()
        if exists:
            logger.info("The folder exists on this computer.")
        else:
            logger.warning("That folder does not exist on this computer. Run this script without --check.")
        return 0 if exists else 1

    folder = args.path or default_folder()
    if not Path(folder).is_dir():
        logger.error(f"Folder not found: {folder}. Run scripts/run_pipeline.py first.")
        return 1
    old, new = set_data_folder(project_dir, folder)
    logger.info(f"DataFolder was: {old}")
    logger.info(f"DataFolder now: {new}")
    logger.info("Open powerbi/AQMI.pbip and press Refresh.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
