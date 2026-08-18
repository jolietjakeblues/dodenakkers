#!/usr/bin/env python3
"""
Export the known geruimd-statusconflicten to a CSV Leon can put next to the
source CSV, to manually resolve (e.g. by adding a "hoort bij"-achtige kolom).

Input:  data/generated/analyse.geojson
Output: data/generated/statusconflicten.csv

csv_regel_terrein/csv_regel_ingang zijn 1-geindexeerde regelnummers in
data/Begraafplaatsen Zuid-Holland- Zuid-Holland.csv INCLUSIEF de kopregel
(dus direct te gebruiken als "ga naar regel X" in Excel/een editor).
"""
import csv
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ANALYSE_PATH = REPO_ROOT / "data" / "generated" / "analyse.geojson"
OUTPUT_PATH = REPO_ROOT / "data" / "generated" / "statusconflicten.csv"

FIELDS = [
    "id",
    "naam",
    "plaats",
    "csv_regel_terrein",
    "csv_regel_ingang",
    "geruimd_bron_terrein",
    "geruimd_bron_ingang",
    "ingang_gedeeld",
    "opmerking",
]


def main() -> None:
    with ANALYSE_PATH.open(encoding="utf-8") as f:
        features = json.load(f)["features"]

    conflicts = [f for f in features if f["properties"]["status_conflict"]]

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for feat in conflicts:
            p = feat["properties"]
            writer.writerow(
                {
                    "id": p["id"],
                    "naam": p["naam"],
                    "plaats": p["plaats"],
                    "csv_regel_terrein": p["bron_rij_terrein"],
                    "csv_regel_ingang": p["bron_rij_ingang"],
                    "geruimd_bron_terrein": p["geruimd_bron_terrein"],
                    "geruimd_bron_ingang": p["geruimd_bron_ingang"],
                    "ingang_gedeeld": p["ingang_gedeeld"],
                    "opmerking": "",
                }
            )

    print(f"{len(conflicts)} statusconflicten -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
