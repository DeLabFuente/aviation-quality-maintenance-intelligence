"""
AQMI — Complete pipeline with a single command.

    1. Build the database and generate the synthetic data   (generate_data.py)
    2. Run the 82 validations — QUALITY GATE                 (run_validations.py)
    3. Calculate and check the 18 KPIs                       (run_kpis.py)
    4. Export the star schema for Power BI                   (export_powerbi.py)
    5. Check the Power BI project, if it exists              (validate_powerbi.py)

If the quality gate or the KPI checks fail, the pipeline stops and nothing is exported.

How to run it (from the main project folder, with the virtual environment active):
    python scripts/run_pipeline.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import export_powerbi, generate_data, run_kpis, run_validations, validate_powerbi  # noqa: E402
from config import settings  # noqa: E402
from scripts.common import setup_logging  # noqa: E402

logger = setup_logging("run_pipeline")


def main() -> int:
    logger.info("STEP 1/5 — Build database and generate synthetic data")
    if generate_data.main() != 0:
        logger.error("PIPELINE STOPPED at step 1")
        return 1
    logger.info("STEP 2/5 — Validations (quality gate)")
    if run_validations.main() != 0:
        logger.error("PIPELINE STOPPED at step 2: the quality gate did not pass")
        return 1
    logger.info("STEP 3/5 — Indicators (KPI checks)")
    if run_kpis.main() != 0:
        logger.error("PIPELINE STOPPED at step 3: the KPI checks did not pass")
        return 1
    logger.info("STEP 4/5 — Export the star schema for Power BI")
    if export_powerbi.main() != 0:
        logger.error("PIPELINE STOPPED at step 4: export to Power BI failed")
        return 1
    if any(settings.POWERBI_DIR.glob("*.pbip")):
        logger.info("STEP 5/5 — Check the Power BI project")
        if validate_powerbi.main() != 0:
            logger.error("PIPELINE STOPPED at step 5: the Power BI project has problems")
            return 1
    else:
        logger.info("STEP 5/5 — No Power BI project yet: run 'python scripts/build_powerbi_project.py'")
    logger.info("PIPELINE OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
