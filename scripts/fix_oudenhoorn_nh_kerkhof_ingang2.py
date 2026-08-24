#!/usr/bin/env python3
"""
One-time correction: NH Kerkhof, Oudenhoorn's entrance, take 2 (2026-08-24).

scripts/fix_oudenhoorn_nh_kerkhof_ingang.py moved the entrance onto NH
Kerkhof's own terrain, choosing the northeast BGT bridge (4.19145,
51.82833) of the 3 candidates found via the PDOK BGT OGC API. Wrong guess:
the opdrachtgever then shared a Google Maps pin
(https://maps.app.goo.gl/sjR4CcPvCResN9Ns5, resolves to
51.8280348,4.1908791999999995) for the real entrance -- 4.2m from the west
bridge candidate (4.19094, 51.82804), 51.3m from the northeast bridge
picked before. Uses the exact resolved Google Maps coordinate as the most
direct evidence available, rather than the BGT bridge centroid.

Run once. Re-run scripts/build_base_dataset.py afterwards to rebuild
data/generated/*.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_base_dataset as b  # noqa: E402

OLD_WKT = "POINT (4.19145 51.82833)"
NEW_WKT = "POINT (4.190879 51.828035)"


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
