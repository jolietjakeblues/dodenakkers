#!/usr/bin/env python3
"""
One-time correction: NH Kerkhof, Oudenhoorn's own entrance, 2026-08-24.

The entrance point attached to NH Kerkhof (POINT(4.191578 51.826529), the
"west corner" point moved there in scripts/fix_oudenhoorn_reversed.py) sits
~130m from NH Kerkhof's own terrain -- it's actually the southwest corner
of the *other* terrain, Gem. begraafplaats. That placement matched the
opdrachtgever's verbal instruction at the time ("nagenoeg zelfde locatie"),
but NH Kerkhof itself is a moated churchyard with real footbridges crossing
its own moat -- verified via the PDOK BGT OGC API
(https://api.pdok.nl/lv/bgt/ogc/v1/collections/overbruggingsdeel/items),
which returns exactly 3 active bridges (hoort_bij_typeoverbrugging=brug)
crossing the moat around NH Kerkhof's terrain, each with a connecting
voetpad: south (4.19132, 51.82773), northeast (4.19145, 51.82833), west
(4.19094, 51.82804).

Chosen: the northeast bridge, matching the access path visible in both the
opdrachtgever's satellite screenshot and a BGT-layer screenshot (path
running from the north side of the ring straight to the church building).
Moves NH Kerkhof's entrance onto its own terrain for the first time --
previously it was always attributed to a point geographically inside the
other cemetery.

Run once. Re-run scripts/build_base_dataset.py afterwards to rebuild
data/generated/*.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_base_dataset as b  # noqa: E402

OLD_WKT = "POINT (4.191578 51.826529)"
NEW_WKT = "POINT (4.19145 51.82833)"


def main() -> None:
    df = b.load_source()
    mask = (df["naam"] == "NH Kerkhof") & (df["plaats (opgeschoon)"] == "Oudenhoorn") & (df["ingang"] == "ingang")
    assert mask.sum() == 1, f"verwacht 1 ingang NH Kerkhof, Oudenhoorn, gevonden {mask.sum()}"
    idx = df[mask].index[0]
    assert df.at[idx, "WKT"] == OLD_WKT, f"onverwachte WKT: {df.at[idx, 'WKT']!r}"
    df.at[idx, "WKT"] = NEW_WKT
    print(f"Ingang NH Kerkhof, Oudenhoorn (csv-index {idx}): {OLD_WKT} -> {NEW_WKT}")

    out_path = b.SOURCE_CSV
    df.drop(columns=["orig_idx"]).to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nGeschreven naar {out_path}")


if __name__ == "__main__":
    main()
