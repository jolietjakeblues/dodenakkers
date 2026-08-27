#!/usr/bin/env python3
"""
One-off: fix 2 plaats-veld gebreken in de bron, gevonden als bijvangst bij
het bouwen van de statistiekenpagina (2026-08-26) -- "Dan Haag" verstoorde
de "meeste totale oppervlakte per plaats"-tabel (Den Haag werd in twee
groepen gesplitst) en de lege plaats bij "RK begraafplaats Schiedam" gaf een
begraafplaats zonder plaats in elke per-plaats-tabel.

1. "Gem. begraafplaats Westduin" (csv-rijen 450 terrein + 485 ingang) had
   plaats (origineel) = plaats (opgeschoon) = "Dan Haag" -- een tikfout,
   geen andere "Gem. begraafplaats Westduin, Den Haag" bestaat om mee te
   botsen. Naar "Den Haag".
2. "RK begraafplaats Schiedam" (csv-rij 167, terrein) had een lege
   plaats (origineel)/plaats (opgeschoon) -- de plaatsnaam stond alleen in
   naam gebakken, niet apart. De gekoppelde ingang (csv-rij 184, naam "RK
   begraafplaats", plaats "Schiedam") heeft het wel correct, en de koppeling
   liep toch al via spatial_name_variant (de naam-strings verschillen sowieso
   al: "RK begraafplaats Schiedam" vs "RK begraafplaats"), dus dit vult
   alleen de ontbrekende waarde aan -- verandert geen koppelcategorie.

Run once. Re-run scripts/build_base_dataset.py + scripts/analyse_spatial.py
+ scripts/compute_statistics.py afterwards.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_base_dataset as b  # noqa: E402


def main() -> None:
    df = b.load_source()

    mask_westduin = (df["naam"] == "Gem. begraafplaats Westduin") & (df["plaats (opgeschoon)"] == "Dan Haag")
    assert mask_westduin.sum() == 2, f"verwacht 2 rijen Gem. begraafplaats Westduin/Dan Haag, gevonden {mask_westduin.sum()}"
    df.loc[mask_westduin, "plaats (origineel)"] = "Den Haag"
    df.loc[mask_westduin, "plaats (opgeschoon)"] = "Den Haag"
    print(f"Gem. begraafplaats Westduin ({mask_westduin.sum()} rijen): 'Dan Haag' -> 'Den Haag'")

    mask_schiedam = (df["naam"] == "RK begraafplaats Schiedam") & df["plaats (opgeschoon)"].isna()
    assert mask_schiedam.sum() == 1, f"verwacht 1 rij RK begraafplaats Schiedam zonder plaats, gevonden {mask_schiedam.sum()}"
    df.loc[mask_schiedam, "plaats (origineel)"] = "Schiedam"
    df.loc[mask_schiedam, "plaats (opgeschoon)"] = "Schiedam"
    print(f"RK begraafplaats Schiedam ({mask_schiedam.sum()} rij): lege plaats -> 'Schiedam'")

    out_path = b.SOURCE_CSV
    df.drop(columns=["orig_idx"]).to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nGeschreven naar {out_path}")


if __name__ == "__main__":
    main()
