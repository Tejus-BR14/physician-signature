"""
check_before_push.py

Run this from the top folder of the repository before every commit:

    python scripts/check_before_push.py          # check only, changes nothing
    python scripts/check_before_push.py --strip  # also clear outputs and hide the project ID

What it checks, in plain words:

  FAIL  (must be fixed before you push)
    1. A data file is in the repository (csv, parquet, pickle, and so on).
    2. A notebook still has outputs. Outputs can contain row-level MIMIC-III values.
    3. A notebook contains a Google Cloud project ID.
    4. A notebook uses the superseded Study 1 cohort (AND ISERROR IS NULL)
       or a superseded guard value or bootstrap size.
    5. A Markdown or Python file contains an em dash or en dash (house style).

  WARN  (read the line it points to and decide)
    6. Code that could print or save note text.
    7. A cell that ends by displaying a table, which shows database rows when run.

Items 2 and 3 are fixed automatically by --strip. Nothing else is ever changed:
the code in each cell stays exactly as it was run.

The script uses only the Python standard library.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_DIR = ROOT / "notebooks"
PLACEHOLDER = "YOUR-GCP-PROJECT-ID"

DATA_EXTENSIONS = {".csv", ".tsv", ".parquet", ".feather", ".pkl", ".pickle",
                   ".xlsx", ".xls", ".db", ".sqlite", ".gz", ".zip"}

# A Google Cloud project ID written into the code, for example project-12345678-ab12-...
PROJECT_ID_PATTERN = re.compile(r"project-\d{6,}-[0-9a-z\-]+")

# Patterns that only appear in superseded versions of the notebooks. Each one
# matches real code (a SQL line or an assignment), not a warning message that
# merely mentions the old value, so the current notebooks pass.
SUPERSEDED = [
    (re.compile(r"^\s*(AND|WHERE)\s+ISERROR\s+IS\s+NULL", re.I),
     "Study 1 query drops ISERROR-flagged notes. The analysis retains them (62,682 notes)."),
    (re.compile(r"=\s*62569\b|62569\s*,\s*0\.6945"),
     "Guard value from the superseded 62,569-note cohort."),
    (re.compile(r"=\s*0\.6945\b"),
     "Correlation from the superseded 62,569-note cohort (correct value 0.6953)."),
    (re.compile(r"\bB\s*,\s*SEED\s*=\s*200\b"),
     "200-replicate bootstrap. The reported interval uses 1,000 replicates."),
]

# Code patterns that could print or save note text.
RISKY_PATTERNS = [
    (re.compile(r"print\(.*(\[\s*['\"]TEXT['\"]\s*\]|\.TEXT\b|\{\s*(text|txt|line|ln)\b)"),
     "may print note text"),
    (re.compile(r"\[\s*['\"]TEXT['\"]\s*\]\s*\.\s*(head|tail|iloc|loc|sample|values|to_list|tolist)"),
     "shows values from the TEXT column"),
    (re.compile(r"\.to_(csv|parquet|excel|pickle|feather|json)\("), "writes data to a file"),
]

# A last line that is just a variable name (or name.head()) displays a table when run.
DISPLAY_LAST_LINE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.(head|tail|sample)\(\s*\d*\s*\))?$")

DASHES = {chr(0x2014): "em dash", chr(0x2013): "en dash"}

fails, warns = [], []


def cell_source(cell):
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def check_data_files():
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if path.suffix.lower() in DATA_EXTENSIONS:
            fails.append(f"Data file in repository: {path.relative_to(ROOT)}")


def check_notebook(path, strip):
    nb = json.loads(path.read_text(encoding="utf-8"))
    name = path.name
    changed = False

    for i, cell in enumerate(nb.get("cells", [])):
        src = cell_source(cell)

        if cell.get("cell_type") == "code":
            # 2. Outputs
            if cell.get("outputs"):
                if strip:
                    cell["outputs"] = []
                    changed = True
                else:
                    fails.append(f"{name}, cell {i}: has outputs (run with --strip to clear)")
            if cell.get("execution_count") is not None and strip:
                cell["execution_count"] = None
                changed = True

        # 3. Project ID
        if PROJECT_ID_PATTERN.search(src):
            if strip:
                src = PROJECT_ID_PATTERN.sub(PLACEHOLDER, src)
                cell["source"] = src.splitlines(keepends=True)
                changed = True
            else:
                fails.append(f"{name}, cell {i}: contains a Google Cloud project ID (run with --strip)")

        # 4. Superseded versions (code lines only, comments skipped)
        for lineno, line in enumerate(src.splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            for pattern, why in SUPERSEDED:
                if pattern.search(line):
                    fails.append(f"{name}, cell {i}, line {lineno}: {why} "
                                 "Use the current Colab version of this notebook.")

        if cell.get("cell_type") != "code":
            continue

        # 6. Risky code
        for lineno, line in enumerate(src.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pattern, what in RISKY_PATTERNS:
                if pattern.search(line):
                    warns.append(f"{name}, cell {i}, line {lineno}: {what}: {stripped[:80]}")

        # 7. Table display at the end of a cell
        lines = [l.strip() for l in src.splitlines() if l.strip() and not l.strip().startswith("#")]
        if lines and DISPLAY_LAST_LINE.match(lines[-1]) and lines[-1] not in {"pass", "None"}:
            warns.append(f"{name}, cell {i}: last line '{lines[-1]}' displays a table when run. "
                         "Fine while outputs are cleared; never commit its output.")

    # Notebook-level metadata that can hold rendered widgets
    if strip and "widgets" in nb.get("metadata", {}):
        del nb["metadata"]["widgets"]
        changed = True

    if changed:
        path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  cleaned: {name}")


def check_dashes():
    for path in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.py")) + list(ROOT.rglob("*.cff")):
        if ".git" in path.parts:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for ch, label in DASHES.items():
                if ch in line:
                    fails.append(f"{path.relative_to(ROOT)}, line {lineno}: contains an {label}")


def main():
    strip = "--strip" in sys.argv
    print("Checking repository:", ROOT)

    check_data_files()

    notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    if not notebooks:
        fails.append("No notebooks found in notebooks/")
    for nb_path in notebooks:
        check_notebook(nb_path, strip)

    check_dashes()

    print()
    for w in warns:
        print("WARN ", w)
    for f in fails:
        print("FAIL ", f)
    print()
    if fails:
        print(f"{len(fails)} problem(s) must be fixed before pushing. {len(warns)} warning(s).")
        sys.exit(1)
    print(f"All checks passed. {len(warns)} warning(s) to read above. Safe to push.")


if __name__ == "__main__":
    main()
