#!/usr/bin/env python3
"""
One-time source correction: resolve the 4 known geruimd status conflicts.

Leon confirmed 2026-08-20 that all four are geruimd:
  - RK begraafplaats, Oude Wetering
  - Oud NH kerkhof, Schoonhoven
  - NH Kerkhof, Zwammerdam
  - Vm. NH kerkhof, Maasland

For each, the terrein and ingang source rows disagreed on `geruimd` (see
data/generated/statusconflicten.csv, produced by
scripts/export_statusconflicten.py). This sets both rows' `geruimd` column
to "geruimd" and appends the "(geruimd)" suffix to `plaats (origineel)` on
whichever row was missing it, matching this CSV's existing convention.

Run once. Re-run scripts/build_base_dataset.py afterwards to rebuild
data/generated/* -- the 4 status_conflict records should become 0.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_base_dataset as b  # noqa: E402

# (naam, plaats (origineel) zonder suffix, begraafplaats-kolom, ingang-kolom)
# identificeert de terrein- resp. ingangrij ondubbelzinnig per begraafplaats.
CONFLICTS = [
    ("RK begraafplaats", "Oude Wetering"),
    ("Oud NH kerkhof", "Schoonhoven"),
    ("NH Kerkhof", "Zwammerdam"),
    ("Vm. NH kerkhof", "Maasland"),
]


def plaats_zonder_suffix(value) -> str:
    if not isinstance(value, str):
        return value
    return value.replace(" (geruimd)", "")


def main() -> None:
    df = b.load_source()

    fixed = []
    for naam, plaats in CONFLICTS:
        rows = df[(df["naam"] == naam) & (df["plaats (opgeschoon)"] == plaats)]
        assert len(rows) == 2, f"{naam}/{plaats}: verwacht 2 rijen (terrein+ingang), gevonden {len(rows)}"
        terrein_rows = rows[rows["begraafplaats"] == "begraafplaats"]
        ingang_rows = rows[rows["ingang"] == "ingang"]
        assert len(terrein_rows) == 1 and len(ingang_rows) == 1, (
            f"{naam}/{plaats}: verwacht precies 1 terrein- en 1 ingangrij"
        )
        for idx in list(terrein_rows.index) + list(ingang_rows.index):
            was = df.at[idx, "geruimd"]
            if was == "geruimd":
                continue
            df.at[idx, "geruimd"] = "geruimd"
            orig = df.at[idx, "plaats (origineel)"]
            if isinstance(orig, str) and "(geruimd)" not in orig:
                df.at[idx, "plaats (origineel)"] = f"{orig} (geruimd)"
            fixed.append((naam, plaats, idx, was))

    assert len(fixed) == 4, f"verwacht 4 aangepaste rijen (1 per conflict), gevonden {len(fixed)} -- controleer handmatig"

    print("Aangepaste rijen:")
    for naam, plaats, idx, was in fixed:
        print(f"  - {naam} ({plaats}), csv-index {idx}: geruimd {was!r} -> 'geruimd'")

    out_path = b.SOURCE_CSV
    df.drop(columns=["orig_idx"]).to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nGeschreven naar {out_path}")


if __name__ == "__main__":
    main()
