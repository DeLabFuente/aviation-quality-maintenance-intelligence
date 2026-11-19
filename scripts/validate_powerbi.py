"""
AQMI — Phase 7: validate the Power BI project (.pbip) before opening it.

Power BI Desktop rejects a project with a syntax error, and a visual that points
to a field that does not exist shows an error instead of a chart. This script
catches those problems first, without Power BI:

  STRUCTURE   the .pbip, report and model files exist and point to each other
  JSON        every JSON file is valid and, when the official Microsoft schemas
              are available (tests/schemas), matches its schema
  TMDL        the model files are well formed: tables, columns, data types,
              sort columns, partitions, unique names, tab indentation
  DATA        the columns of every table match the header of its CSV file
  RELATIONS   relationships point to existing columns, at most one active
              relationship between two tables, and no ambiguous paths (cycles)
  DAX         every Table[Column] and [Measure] used by a measure exists;
              brackets and quotes are balanced
  REPORT      pages, page order and navigation buttons are consistent; every
              field used by a visual exists in the model with the right kind
              (column or measure); visuals stay inside the page

How to run it (from the main project folder, with the virtual environment active):
    python scripts/validate_powerbi.py
Result: a list of problems (if any) and "POWER BI PROJECT OK", or exit code 1.
"""

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings  # noqa: E402
from scripts.common import setup_logging  # noqa: E402

logger = setup_logging("validate_powerbi")

SCHEMA_DIR = PROJECT_ROOT / "tests" / "schemas"
SCHEMA_URL = "https://developer.microsoft.com/json-schemas/"
NAME_RE = r"(?:'(?:[^']|'')+'|[A-Za-z_][A-Za-z0-9_]*)"


def unquote(name: str) -> str:
    name = name.strip()
    return name[1:-1].replace("''", "'") if name.startswith("'") and name.endswith("'") else name


# ----------------------------------------------------------------- TMDL parsing
def parse_table(path: Path, problems: list) -> dict:
    """Light TMDL parser: enough to check names, columns, measures and partitions."""
    lines = path.read_text(encoding="utf-8").splitlines()
    table = {"name": None, "columns": {}, "measures": {}, "partition_m": "", "file": path.name}
    current = None            # ("column"|"measure"|"partition", name)
    for number, raw in enumerate(lines, start=1):
        if raw.strip() == "":
            continue
        indent = len(raw) - len(raw.lstrip("\t"))
        if raw[indent:indent + 1] == " " and indent < 4 and not raw.lstrip().startswith("///"):
            if not (current and current[0] in ("measure", "partition") and indent >= 2):
                problems.append(f"TMDL {path.name}:{number}: indentation with spaces instead of tabs")
        line = raw.strip()
        if indent == 0:
            m = re.match(rf"^table ({NAME_RE})$", line)
            if m:
                table["name"] = unquote(m.group(1))
            elif not line.startswith("///"):
                problems.append(f"TMDL {path.name}:{number}: unexpected line at top level: {line[:60]}")
            continue
        if indent == 1:
            current = None
            m = re.match(rf"^column ({NAME_RE})$", line)
            if m:
                current = ("column", unquote(m.group(1)))
                table["columns"][current[1]] = {"line": number}
                continue
            m = re.match(rf"^measure ({NAME_RE}) =(.*)$", line)
            if m:
                current = ("measure", unquote(m.group(1)))
                if current[1] in table["measures"]:
                    problems.append(f"TMDL {path.name}: measure '{current[1]}' defined twice")
                table["measures"][current[1]] = {"expression": m.group(2).strip(), "line": number}
                continue
            m = re.match(rf"^partition ({NAME_RE}) = m$", line)
            if m:
                current = ("partition", unquote(m.group(1)))
                continue
            if line.startswith(("///", "annotation ", "changedProperty ")):
                continue
            # Table properties, e.g. "lineageTag: …" (added by Power BI Desktop
            # when it saves the project) or flags such as "isHidden".
            if re.match(r"^[a-z][A-Za-z]*(?::\s.*)?$", line):
                continue
            problems.append(f"TMDL {path.name}:{number}: unexpected line in table: {line[:60]}")
            continue
        if current is None:
            continue
        kind, name = current
        if kind == "column" and indent == 2:
            key, _, value = line.partition(":")
            table["columns"][name][key.strip()] = value.strip() if value else True
        elif kind == "measure":
            if indent >= 3:
                table["measures"][name]["expression"] += "\n" + line
            elif indent == 2:
                key, _, value = line.partition(":")
                table["measures"][name][key.strip()] = value.strip()
        elif kind == "partition" and indent >= 4:
            table["partition_m"] += line + "\n"
    if table["name"] is None:
        problems.append(f"TMDL {path.name}: no 'table' declaration")
    return table


def check_model(model_dir: Path, data_dir: Path | None, problems: list) -> dict:
    definition = model_dir / "definition"
    for required in ("database.tmdl", "model.tmdl", "relationships.tmdl", "expressions.tmdl"):
        if not (definition / required).exists():
            problems.append(f"STRUCTURE: {required} is missing in {model_dir.name}")
    tables = {}
    for path in sorted((definition / "tables").glob("*.tmdl")):
        t = parse_table(path, problems)
        if t["name"]:
            if t["name"] != path.stem:
                problems.append(f"TMDL {path.name}: table name '{t['name']}' differs from the file name")
            tables[t["name"]] = t

    # model.tmdl must reference every table
    model_text = (definition / "model.tmdl").read_text(encoding="utf-8")
    refs = {unquote(m) for m in re.findall(rf"^ref table ({NAME_RE})$", model_text, re.M)}
    if refs != set(tables):
        problems.append(f"TMDL model.tmdl: 'ref table' list differs from the table files: {sorted(refs ^ set(tables))}")
    groups = {unquote(m) for m in re.findall(rf"^queryGroup ({NAME_RE})$", model_text, re.M)}

    expressions = (definition / "expressions.tmdl").read_text(encoding="utf-8")
    parameters = {m for m in re.findall(r"^expression (\w+) =", expressions, re.M)}

    all_columns = {}
    for t in tables.values():
        for col, props in t["columns"].items():
            all_columns.setdefault(col, []).append(t["name"])
            for required in ("dataType", "sourceColumn"):
                if required not in props:
                    problems.append(f"TMDL {t['file']}: column '{col}' has no {required}")
            sort = props.get("sortByColumn")
            if sort and unquote(sort) not in t["columns"]:
                problems.append(f"TMDL {t['file']}: column '{col}' sorted by missing column {sort}")
        if t["columns"] and not t["partition_m"]:
            problems.append(f"TMDL {t['file']}: table has no M partition")
        for group in re.findall(r"queryGroup: (\S+)", (definition / "tables" / t["file"]).read_text(encoding="utf-8")):
            if unquote(group) not in groups:
                problems.append(f"TMDL {t['file']}: query group {group} not declared in model.tmdl")
        for used in re.findall(r"\b([A-Z][A-Za-z]+) &", t["partition_m"]):
            if used not in parameters:
                problems.append(f"TMDL {t['file']}: M code uses unknown parameter {used}")
        # CSV header and M column list must match the columns of the table
        source_columns = [p.get("sourceColumn") for p in t["columns"].values()]
        typed = re.findall(r'\{"([^"]+)", (?:Int64\.Type|type \w+)\}', t["partition_m"])
        csv_match = re.search(r'DataFolder & "([^"]+\.csv)"', t["partition_m"])
        if csv_match:
            if sorted(typed) != sorted(source_columns):
                problems.append(f"TMDL {t['file']}: M type list differs from the columns of the table")
            if data_dir is not None:
                csv_path = data_dir / csv_match.group(1)
                if not csv_path.exists():
                    problems.append(f"DATA: {csv_path.name} not found for table {t['name']}")
                else:
                    with open(csv_path, encoding="utf-8") as handle:
                        header = next(csv.reader(handle))
                    if header != source_columns:
                        problems.append(f"DATA: header of {csv_path.name} differs from the columns of {t['name']}")

    measures = {}
    for t in tables.values():
        for name, props in t["measures"].items():
            if name in measures:
                problems.append(f"TMDL: measure '{name}' defined in two tables")
            measures[name] = props
            if name in all_columns:
                problems.append(f"TMDL: measure '{name}' has the same name as a column in {all_columns[name]}")

    # ---- relationships
    rel_text = (definition / "relationships.tmdl").read_text(encoding="utf-8")
    active_pairs = defaultdict(int)
    filters = defaultdict(set)          # filter direction: "one" side -> "many" side
    for block in re.split(r"\n(?=relationship )", rel_text.strip()):
        frm = re.search(rf"fromColumn: ({NAME_RE})\.({NAME_RE})", block)
        to = re.search(rf"toColumn: ({NAME_RE})\.({NAME_RE})", block)
        if not frm or not to:
            problems.append(f"RELATIONS: malformed relationship block: {block[:60]}")
            continue
        (ft, fc), (tt, tc) = [(unquote(a), unquote(b)) for a, b in (frm.groups(), to.groups())]
        for table_name, column in ((ft, fc), (tt, tc)):
            if table_name not in tables or column not in tables[table_name]["columns"]:
                problems.append(f"RELATIONS: {table_name}[{column}] does not exist")
        if "crossFilteringBehavior: bothDirections" in block:
            problems.append(f"RELATIONS: {ft} - {tt} filters in both directions (not used in this model)")
        if "isActive: false" not in block:
            active_pairs[(ft, tt)] += 1
            filters[tt].add(ft)
    for (ft, tt), count in active_pairs.items():
        if count > 1:
            problems.append(f"RELATIONS: {count} active relationships between {ft} and {tt} (only one allowed)")

    # Ambiguity = a filter can reach the same table along two different paths.
    def paths_from(node: str, path: tuple) -> list:
        found = []
        for nxt in filters[node]:
            if nxt in path:
                problems.append(f"RELATIONS: circular filter path {' -> '.join(path + (nxt,))}")
                continue
            found.append(nxt)
            found += paths_from(nxt, path + (nxt,))
        return found
    for start in list(filters):
        reached = paths_from(start, (start,))
        for target in {r for r in reached if reached.count(r) > 1}:
            problems.append(f"RELATIONS: ambiguous filter paths from {start} to {target}")

    # ---- DAX references
    for name, props in measures.items():
        expr = props["expression"]
        code = re.sub(r'"(?:[^"]|"")*"', '""', expr)                 # ignore text inside strings
        if expr.count('"') % 2:
            problems.append(f"DAX [{name}]: unbalanced double quotes")
        for open_, close in (("(", ")"), ("{", "}"), ("[", "]")):
            if code.count(open_) != code.count(close):
                problems.append(f"DAX [{name}]: unbalanced '{open_}{close}'")
        for table_ref, column in re.findall(r"('(?:[^']|'')+'|\b[A-Za-z_][A-Za-z0-9_]*)\[([^\]]+)\]", code):
            table_name = unquote(table_ref)
            if table_name not in tables:
                problems.append(f"DAX [{name}]: unknown table {table_name}")
            elif column not in tables[table_name]["columns"]:
                problems.append(f"DAX [{name}]: unknown column {table_name}[{column}]")
        for measure_ref in re.findall(r"(?<![A-Za-z0-9_'\]])\[([^\]]+)\]", code):
            if measure_ref not in measures:
                problems.append(f"DAX [{name}]: unknown measure [{measure_ref}]")
    return {"tables": tables, "measures": measures}


# ----------------------------------------------------------------- JSON schemas
def schema_validator():
    """Return a function that validates a JSON document against its $schema, or None."""
    try:
        from jsonschema import Draft7Validator
        from referencing import Registry, Resource
    except ImportError:
        return None
    if not SCHEMA_DIR.exists():
        return None

    def retrieve(uri: str):
        path = SCHEMA_DIR / uri.replace(SCHEMA_URL, "").split("#")[0]
        if not path.exists():
            raise FileNotFoundError(uri)
        return Resource.from_contents(json.loads(path.read_text(encoding="utf-8")))

    registry = Registry(retrieve=retrieve)

    def validate(document: dict) -> list[str] | None:
        url = document.get("$schema", "")
        local = SCHEMA_DIR / url.replace(SCHEMA_URL, "")
        if not url.startswith(SCHEMA_URL) or not local.exists():
            return None                                       # schema not available offline
        schema = json.loads(local.read_text(encoding="utf-8"))
        validator = Draft7Validator(schema, registry=registry)
        return [f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message[:160]}"
                for e in validator.iter_errors(document)]
    return validate


# ----------------------------------------------------------------- report
def walk_fields(node, found: list):
    """Collect every Column/Measure reference in a visual definition."""
    if isinstance(node, dict):
        for kind in ("Column", "Measure"):
            if kind in node and isinstance(node[kind], dict) and "Property" in node[kind]:
                entity = node[kind].get("Expression", {}).get("SourceRef", {}).get("Entity")
                found.append((kind, entity, node[kind]["Property"]))
        for value in node.values():
            walk_fields(value, found)
    elif isinstance(node, list):
        for value in node:
            walk_fields(value, found)


def check_report(report_dir: Path, model: dict, problems: list, validate) -> dict:
    definition = report_dir / "definition"
    stats = {"pages": 0, "visuals": 0, "schema_checked": 0}
    pages_meta = json.loads((definition / "pages" / "pages.json").read_text(encoding="utf-8"))
    folders = sorted(p.name for p in (definition / "pages").iterdir() if p.is_dir())
    if sorted(pages_meta["pageOrder"]) != folders:
        problems.append(f"REPORT: pages.json page order {pages_meta['pageOrder']} differs from page folders {folders}")
    if pages_meta.get("activePageName") not in pages_meta["pageOrder"]:
        problems.append("REPORT: activePageName is not a page")
    report = json.loads((definition / "report.json").read_text(encoding="utf-8"))
    for package in report.get("resourcePackages", []):
        if package["type"] == "RegisteredResources":
            for item in package["items"]:
                if not (report_dir / "StaticResources" / "RegisteredResources" / item["path"]).exists():
                    problems.append(f"REPORT: registered resource {item['path']} is missing")
    tables, measures = model["tables"], model["measures"]
    for page in pages_meta["pageOrder"]:
        page_dir = definition / "pages" / page
        page_json = json.loads((page_dir / "page.json").read_text(encoding="utf-8"))
        stats["pages"] += 1
        if page_json["name"] != page:
            problems.append(f"REPORT: page folder {page} contains page named {page_json['name']}")
        names = set()
        for visual_file in sorted(page_dir.glob("visuals/*/visual.json")):
            v = json.loads(visual_file.read_text(encoding="utf-8"))
            stats["visuals"] += 1
            where = f"{page}/{visual_file.parent.name}"
            if v["name"] != visual_file.parent.name:
                problems.append(f"REPORT {where}: visual name differs from its folder")
            if v["name"] in names:
                problems.append(f"REPORT {where}: duplicated visual name")
            names.add(v["name"])
            pos = v["position"]
            if pos["x"] < 0 or pos["y"] < 0 or pos["x"] + pos["width"] > page_json["width"] + 0.5 \
                    or pos["y"] + pos["height"] > page_json["height"] + 0.5:
                problems.append(f"REPORT {where}: visual outside the page")
            found = []
            walk_fields(v["visual"], found)
            for kind, entity, prop in found:
                if entity not in tables:
                    problems.append(f"REPORT {where}: unknown table {entity}")
                elif kind == "Column" and prop not in tables[entity]["columns"]:
                    problems.append(f"REPORT {where}: unknown column {entity}[{prop}]")
                elif kind == "Measure" and prop not in tables[entity]["measures"]:
                    problems.append(f"REPORT {where}: unknown measure {entity}[{prop}]")
            for selector_target in re.findall(r'"metadata": "([^"]+)"', json.dumps(v)):
                entity, _, prop = selector_target.partition(".")
                if entity not in tables or (prop not in tables[entity]["measures"] and prop not in tables[entity]["columns"]):
                    problems.append(f"REPORT {where}: formatting selector points to unknown field {selector_target}")
            for link in v["visual"].get("visualContainerObjects", {}).get("visualLink", []):
                target = link["properties"].get("navigationSection", {}).get("expr", {}).get("Literal", {}).get("Value", "")
                if target and target.strip("'") not in pages_meta["pageOrder"]:
                    problems.append(f"REPORT {where}: navigation to unknown page {target}")
    if validate:
        for path in sorted(report_dir.rglob("*.json")) + [report_dir / "definition.pbir"]:
            if "StaticResources" in path.parts:
                continue
            errors = validate(json.loads(path.read_text(encoding="utf-8")))
            if errors is None:
                continue
            stats["schema_checked"] += 1
            for error in errors[:3]:
                problems.append(f"SCHEMA {path.relative_to(report_dir)}: {error}")
    return stats


def validate_project(project_dir: Path = settings.POWERBI_DIR, data_dir: Path | None = settings.POWERBI_DATA_DIR,
                     use_schemas: bool = True) -> dict:
    problems = []
    pbips = list(project_dir.glob("*.pbip"))
    if len(pbips) != 1:
        return {"problems": [f"STRUCTURE: expected one .pbip file in {project_dir}, found {len(pbips)}"], "stats": {}}
    validate = schema_validator() if use_schemas else None
    pbip = json.loads(pbips[0].read_text(encoding="utf-8"))
    report_dir = project_dir / pbip["artifacts"][0]["report"]["path"]
    pbir = json.loads((report_dir / "definition.pbir").read_text(encoding="utf-8"))
    model_dir = (report_dir / pbir["datasetReference"]["byPath"]["path"]).resolve()
    for path, label in ((report_dir, "report"), (model_dir, "semantic model")):
        if not path.exists():
            problems.append(f"STRUCTURE: {label} folder {path.name} not found")
    for path in list(project_dir.rglob("*.json")) + list(project_dir.rglob("*.pbir")) + \
            list(project_dir.rglob("*.pbism")) + list(project_dir.rglob(".platform")) + pbips:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            problems.append(f"JSON {path.relative_to(project_dir)}: {error}")
            continue
        if validate and path.suffix in (".pbip", ".pbism"):
            for error in (validate(document) or [])[:3]:
                problems.append(f"SCHEMA {path.relative_to(project_dir)}: {error}")
    if problems:
        return {"problems": problems, "stats": {}}
    model = check_model(model_dir, data_dir, problems)
    stats = check_report(report_dir, model, problems, validate)
    stats.update(tables=len(model["tables"]), measures=len(model["measures"]),
                 columns=sum(len(t["columns"]) for t in model["tables"].values()),
                 schemas="official schemas" if validate else "not available (schema check skipped)")
    return {"problems": problems, "stats": stats}


def main() -> int:
    if not settings.POWERBI_DIR.exists():
        logger.error("Power BI project not found. Run 'python scripts/build_powerbi_project.py' first.")
        return 1
    result = validate_project()
    for problem in result["problems"]:
        logger.error("%s", problem)
    s = result["stats"]
    if s:
        logger.info("Model: %d tables, %d columns, %d measures", s["tables"], s["columns"], s["measures"])
        logger.info("Report: %d pages, %d visuals; JSON files checked against %s: %d",
                    s["pages"], s["visuals"], s["schemas"], s["schema_checked"])
    if result["problems"]:
        logger.error("POWER BI PROJECT HAS %d PROBLEM(S)", len(result["problems"]))
        return 1
    logger.info("POWER BI PROJECT OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
