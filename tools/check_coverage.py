"""Enforce separate statement and branch floors from coverage.py JSON."""

import json
from pathlib import Path

totals = json.loads(Path("coverage.json").read_text())["totals"]
for label, covered, total, floor in (
    ("statement", totals["covered_lines"], totals["num_statements"], 83.75),
    ("branch", totals["covered_branches"], totals["num_branches"], 70.55),
):
    if not total or 100 * covered < floor * total:
        raise SystemExit(f"{label} coverage {covered}/{total} falls below {floor}%")
