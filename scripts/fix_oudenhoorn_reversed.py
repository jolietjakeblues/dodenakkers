#!/usr/bin/env python3
"""
One-time correction: Leon (opdrachtgever's principal) reversed the Oudenhoorn
call from scripts/fix_oudenhoorn_ingang.py after seeing the live map,
2026-08-23 (forwarded by Joop via WhatsApp, satellite screenshot with both
terreinen marked):

  "De groene moet geruimd en de bruine niet. Ingang aan westzijde van de
  bruine moet naar de groene, nagenoeg zelfde locatie."

Green = NH Kerkhof, Oudenhoorn (niet-geruimd until now). Brown = Gem.
begraafplaats, Oudenhoorn (geruimd until now, via
scripts/fix_geruimd_oudenhoorn_haringvliet.py 2026-08-22 -- that call was
backwards). This script:

1. Flips geruimd: NH Kerkhof -> geruimd, Gem. begraafplaats -> niet-geruimd.
2. Reassigns the west-corner ingang (added 2026-08-23 by
   fix_oudenhoorn_ingang.py at POINT(4.191578 51.826529)) from Gem.
   begraafplaats to NH Kerkhof, geruimd status following its new terrain.
3. Reverts the *other* ingang (POINT(4.192397 51.826557), the originally
   mislabeled point reassigned by fix_oudenhoorn_ingang.py) to niet-geruimd,
   staying with Gem. begraafplaats -- Leon only called out "de ingang aan
   westzijde", so this one keeps its current terrain attribution.

Net result: each terrain has exactly 1 ingang again, same as every other
record in the dataset. The EXTRA_INGANG_EXCEPTIONS two-ingangen-per-terrein
mechanism added for the previous (wrong) call is no longer needed and is
reverted separately in scripts/build_base_dataset.py and src/app.js.

Run once. Re-run scripts/build_base_dataset.py afterwards to rebuild
data/generated/*.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_base_dataset as b  # noqa: E402

PLAATS = "Oudenhoorn"


def set_geruimd(df, mask, geruimd: bool) -> int:
    idxs = df[mask].index
    for idx in idxs:
        df.at[idx, "geruimd"] = "geruimd" if geruimd else ""
        orig = df.at[idx, "plaats (origineel)"]
        has_suffix = isinstance(orig, str) and "(geruimd)" in orig
        if geruimd and not has_suffix:
            df.at[idx, "plaats (origineel)"] = f"{orig} (geruimd)"
        elif not geruimd and has_suffix:
            df.at[idx, "plaats (origineel)"] = orig.replace(" (geruimd)", "")
    return len(idxs)


def main() -> None:
    df = b.load_source()

    # 1. Terrein-status omdraaien.
    nh_terrein = (df["naam"] == "NH Kerkhof") & (df["plaats (opgeschoon)"] == PLAATS) & (df["begraafplaats"] == "begraafplaats")
    gem_terrein = (df["naam"] == "Gem. begraafplaats") & (df["plaats (opgeschoon)"] == PLAATS) & (df["begraafplaats"] == "begraafplaats")
    assert nh_terrein.sum() == 1 and gem_terrein.sum() == 1, "verwacht precies 1 terrein per naam"
    n1 = set_geruimd(df, nh_terrein, True)
    n2 = set_geruimd(df, gem_terrein, False)
    print(f"Terrein NH Kerkhof, Oudenhoorn: geruimd -> True ({n1} rij)")
    print(f"Terrein Gem. begraafplaats, Oudenhoorn: geruimd -> False ({n2} rij)")

    # 2. West-hoek-ingang (nieuw toegevoegd 2026-08-23) naar NH Kerkhof.
    west_ingang = (df["ingang"] == "ingang") & (df["WKT"] == "POINT (4.191578 51.826529)")
    assert west_ingang.sum() == 1, f"verwacht 1 west-ingang, gevonden {west_ingang.sum()}"
    idx = df[west_ingang].index[0]
    df.at[idx, "naam"] = "NH Kerkhof"
    set_geruimd(df, df.index == idx, True)
    print(f"Ingang op westhoek (csv-index {idx}): naam -> 'NH Kerkhof', geruimd -> True")

    # 3. Overige ingang (oorspronkelijk verkeerd gelabeld, blijft bij Gem.
    #    begraafplaats) terug naar niet-geruimd.
    other_ingang = (df["ingang"] == "ingang") & (df["WKT"] == "POINT (4.192397 51.826557)")
    assert other_ingang.sum() == 1, f"verwacht 1 overige ingang, gevonden {other_ingang.sum()}"
    idx2 = df[other_ingang].index[0]
    set_geruimd(df, df.index == idx2, False)
    print(f"Ingang bij Gem. begraafplaats (csv-index {idx2}): geruimd -> False (naam ongewijzigd)")

    out_path = b.SOURCE_CSV
    df.drop(columns=["orig_idx"]).to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nGeschreven naar {out_path}")


if __name__ == "__main__":
    main()
