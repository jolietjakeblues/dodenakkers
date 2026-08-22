#!/usr/bin/env python3
"""
One-time source correction: 2 more geruimd corrections reported by Leon
(opdrachtgever), 2026-08-22.

- "Oudenhoorn, fout in aanlevering: Kerkhof = geruimd, bevat geen ingang"
  -> the Oudenhoorn cemetery with no matched ingang (koppelwijze "missing"
  in the built dataset, zh-0354 "Gem. begraafplaats") is the one Leon means
  ("geen ingang" is the disambiguating detail -- Oudenhoorn also has a
  separate "NH Kerkhof" with a matched ingang, not this one).
- "Kerkhof Stad aan 't Haringvliet - Status: geruimd" -> matches the "NH
  kerkhof" entry by name (Stad aan 't Haringvliet also has a separate
  "Gem. Begraafplaats", not meant here).

Both terrein rows currently have geruimd blank; NH kerkhof/Stad aan 't
Haringvliet also has a matched ingang row that needs the same fix to avoid
creating a new statusconflict (same pattern as
scripts/fix_statusconflicten.py). Oudenhoorn's Gem. begraafplaats has no
ingang row at all, so only its terrein row needs the fix.

Run once. Re-run scripts/build_base_dataset.py afterwards to rebuild
data/generated/*.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_base_dataset as b  # noqa: E402

FIXES = [
    # (naam, plaats (opgeschoon), alleen terrein of ook ingang meenemen)
    ("Gem. begraafplaats", "Oudenhoorn", "terrein_only"),
    ("NH kerkhof", "Stad aan 't Haringvliet", "terrein_en_ingang"),
]


def main() -> None:
    df = b.load_source()
    fixed = []

    for naam, plaats, mode in FIXES:
        rows = df[(df["naam"] == naam) & (df["plaats (opgeschoon)"] == plaats)]
        if mode == "terrein_only":
            assert len(rows) == 1, f"{naam}/{plaats}: verwacht 1 rij (alleen terrein), gevonden {len(rows)}"
            targets = rows
        else:
            assert len(rows) == 2, f"{naam}/{plaats}: verwacht 2 rijen (terrein+ingang), gevonden {len(rows)}"
            terrein_rows = rows[rows["begraafplaats"] == "begraafplaats"]
            ingang_rows = rows[rows["ingang"] == "ingang"]
            assert len(terrein_rows) == 1 and len(ingang_rows) == 1, (
                f"{naam}/{plaats}: verwacht precies 1 terrein- en 1 ingangrij"
            )
            targets = rows

        for idx in targets.index:
            was = df.at[idx, "geruimd"]
            if was == "geruimd":
                continue
            df.at[idx, "geruimd"] = "geruimd"
            orig = df.at[idx, "plaats (origineel)"]
            if isinstance(orig, str) and "(geruimd)" not in orig:
                df.at[idx, "plaats (origineel)"] = f"{orig} (geruimd)"
            fixed.append((naam, plaats, idx, was))

    assert len(fixed) == 3, f"verwacht 3 aangepaste rijen (1 + 2), gevonden {len(fixed)} -- controleer handmatig"

    print("Aangepaste rijen:")
    for naam, plaats, idx, was in fixed:
        print(f"  - {naam} ({plaats}), csv-index {idx}: geruimd {was!r} -> 'geruimd'")

    out_path = b.SOURCE_CSV
    df.drop(columns=["orig_idx"]).to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nGeschreven naar {out_path}")


if __name__ == "__main__":
    main()
