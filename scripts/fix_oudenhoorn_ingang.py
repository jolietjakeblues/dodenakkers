#!/usr/bin/env python3
"""
One-time source correction: Oudenhoorn ingang situatie, gemeld door de
opdrachtgever (Joop) op 2026-08-23, naar aanleiding van Leons foutenlijst
("Oudenhoorn, fout in aanlevering: Kerkhof = geruimd, bevat geen ingang").

Twee stappen:

1. Naamverwisseling rechtzetten. De bron bevat een ingangpunt getagd als
   "NH Kerkhof, Oudenhoorn" (koppelt via exacte naam+plaats aan het
   NH Kerkhof-terrein), maar dat punt ligt ruimtelijk 132 m van het
   NH Kerkhof-terrein en 0 m van -- dus binnen -- het terrein van
   "Gem. begraafplaats, Oudenhoorn". Vrijwel zeker een naamfout in de
   oorspronkelijke aanlevering. Hernoemd naar "Gem. begraafplaats,
   Oudenhoorn" (met dezelfde geruimd-conventie als het terrein: "(geruimd)"
   in plaats (origineel), geruimd=geruimd). NH Kerkhof, Oudenhoorn heeft
   hierna zelf geen ingang meer -- dat is een aparte, niet hier opgeloste
   kwestie.

2. Tweede ingang toegevoegd op de zuidwesthoek van het terrein van
   Gem. begraafplaats (4.191578, 51.826529 -- het gemiddelde van de twee
   dicht bijeenliggende hoekpunten op de kleinste lengtegraad van de
   terreinpolygoon), op uitdrukkelijk verzoek van de opdrachtgever ("ter
   linkerzijde (west)"), bevestigd tegen zijn eigen database. Dit is geen
   verzonnen centroid: een expliciete, door de opdrachtgever aangewezen
   locatie voor een tweede, echte toegang.

Resultaat: Gem. begraafplaats, Oudenhoorn heeft twee ingangen. Dit is een
nieuw scenario in de bron (voorheen ondersteunde de matching maximaal één
ingang per terrein) -- scripts/build_base_dataset.py is aangepast om deze
ene, expliciet gedocumenteerde uitzondering toe te staan (zie
EXTRA_INGANG_EXCEPTIONS aldaar).

Run once. Re-run scripts/build_base_dataset.py afterwards to rebuild
data/generated/*.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_base_dataset as b  # noqa: E402

NAAM = "Gem. begraafplaats"
PLAATS = "Oudenhoorn"
NIEUW_PUNT_WKT = "POINT (4.191578 51.826529)"


def main() -> None:
    df = b.load_source()

    # Stap 1: hernoem het verkeerd-gelabelde ingangpunt.
    mislabeled = df[
        (df["naam"] == "NH Kerkhof") & (df["plaats (opgeschoon)"] == PLAATS) & (df["ingang"] == "ingang")
    ]
    assert len(mislabeled) == 1, f"verwacht 1 ingang 'NH Kerkhof, Oudenhoorn', gevonden {len(mislabeled)}"
    idx = mislabeled.index[0]
    df.at[idx, "naam"] = NAAM
    df.at[idx, "plaats (origineel)"] = f"{PLAATS} (geruimd)"
    df.at[idx, "geruimd"] = "geruimd"
    print(f"Hernoemd: csv-index {idx} 'NH Kerkhof, Oudenhoorn' -> '{NAAM}, {PLAATS}' (ingang), geruimd=geruimd")

    # Stap 2: nieuwe tweede ingang op de zuidwesthoek.
    nieuwe_rij = {
        "WKT": NIEUW_PUNT_WKT,
        "naam": NAAM,
        "plaats (origineel)": f"{PLAATS} (geruimd)",
        "plaats (opgeschoon)": PLAATS,
        "geruimd": "geruimd",
        "ingang": "ingang",
        "begraafplaats": "",
    }
    df = pd.concat([df, pd.DataFrame([nieuwe_rij])], ignore_index=True)
    print(f"Toegevoegd: nieuwe ingang '{NAAM}, {PLAATS}' op {NIEUW_PUNT_WKT}")

    out_path = b.SOURCE_CSV
    df.drop(columns=["orig_idx"]).to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nGeschreven naar {out_path}")


if __name__ == "__main__":
    main()
