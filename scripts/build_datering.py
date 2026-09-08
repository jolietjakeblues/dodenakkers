#!/usr/bin/env python3
"""
Geocodeert de datering-data van de domeinexpert (data/Begraafplaatsen
Zuid-Holland - datering.csv, 448 rijen) tot losse punten met jaartal/
periode. Dit script koppelt zelf niets aan de hoofddataset -- dat gebeurt
in een aparte stap, `nearest_datering()` in scripts/analyse_spatial.py,
die elke begraafplaats aan het dichtstbijzijnde punt hier koppelt binnen
een afstandsdrempel van 300m (zie docs/data/007-datering-bevindingen.md
voor de onderbouwing van die drempel en docs/data/008-datering-ontbrekend.md
voor de gevallen die erbuiten vallen).

Waarom niet direct op naam+plaats gekoppeld: eerst geprobeerd, matchte maar
37% zeker en fuzzy naam-matching leverde aantoonbaar verkeerde koppelingen
op bij generieke namen ("Gem. begraafplaats", "RK Begraafplaats" komen
tientallen keren voor). Waarom niet blind 1-op-1 op volgorde: de 448
brondata-rijen komen niet 1-op-1 overeen met onze 448 terreinen -- een deel
is een sub-onderdeel van een terrein dat wij als één geheel tellen (bv. een
Joodse afdeling binnen een algemene begraafplaats, letterlijk dezelfde
coördinaat), een ander deel is een begraafplaats die niet in onze 448 zit.
Een geforceerde 1-op-1 koppeling zou dus op meerdere plekken een verkeerde
of misleidende suggestie van precisie geven -- zelfde valkuil als de
in_hoofddataset-heuristiek die eerder al bij de verdwenen-begraafplaatsen-
laag is verwijderd (2026-08-31, zie docs/geschiedenis.md). Vandaar de
ruimtelijke koppeling met expliciete drempel in plaats daarvan.

Geocoding via de gratis PDOK Locatieserver (Bezoekadres + Huisnummer + PC +
Plaats -> centroide_ll van het beste treffer, meestal postcode-niveau,
ruim voldoende nauwkeurig om het juiste terrein te tonen).

De bron was oorspronkelijk een xlsx met ook Contactpersoon/Telefoon/E-mail
per begraafplaats (persoonsgegevens van derden) -- de domeinexpert heeft die
zelf opgeschoond tot deze CSV (2026-09-07), zonder die kolommen. Wel nog
Eigenaar/Postadres (van de beherende organisatie, geen privépersoon) en
Ontwerp van (historische toeschrijving aan een landschapsarchitect, zelfde
soort attributie als bij rijksmonumenten) -- dit script gebruikt sowieso
alleen naam/adres/jaartal/circa/periode/gemeente, dus die kolommen komen
nergens in de output terecht.

Output:
  data/generated/datering.geojson
"""
from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "Begraafplaatsen Zuid-Holland - datering.csv"
GENERATED_DIR = REPO_ROOT / "data" / "generated"
OUT_PATH = GENERATED_DIR / "datering.geojson"

GEOCODE_URL = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"
POINT_PATTERN = re.compile(r"POINT\(([-\d.]+) ([-\d.]+)\)")

# Kolomindexen (0-based) in de bron-CSV -- "Plaats" komt twee keer voor
# (bezoekadres en postadres van de eigenaar), dus positioneel gebruiken
# i.p.v. op kolomnaam opzoeken.
COL_NAAM = 1
COL_BEZOEKADRES = 4
COL_HUISNUMMER = 5
COL_PC = 7
COL_PLAATS = 8
COL_GEMEENTE = 9
COL_JAARTAL = 23
COL_CIRCA = 24
COL_PERIODE = 25


def geocode(adres: str | None, huisnummer, postcode: str | None, plaats: str | None) -> tuple[float, float] | None:
    q_parts = [adres or "", str(huisnummer or ""), postcode or "", plaats or ""]
    q = " ".join(p for p in q_parts if p).strip()
    if not q:
        return None
    url = f"{GEOCODE_URL}?{urllib.parse.urlencode({'q': q, 'rows': 1})}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read())
    docs = data.get("response", {}).get("docs", [])
    if not docs:
        return None
    m = POINT_PATTERN.match(docs[0].get("centroide_ll", ""))
    if not m:
        return None
    return float(m.group(1)), float(m.group(2))


def main() -> None:
    with CSV_PATH.open(encoding="utf-8-sig") as f:
        rows = list(csv.reader(f, delimiter="|"))
    data_rows = rows[1:]

    punten = []
    geocode_mislukt = []
    for row in data_rows:
        naam = row[COL_NAAM].strip()
        if not naam:
            continue
        adres = row[COL_BEZOEKADRES].strip() or None
        huisnummer = row[COL_HUISNUMMER].strip() or None
        pc = row[COL_PC].strip() or None
        plaats = row[COL_PLAATS].strip() or None
        gemeente = row[COL_GEMEENTE].strip() or None
        jaartal_raw = row[COL_JAARTAL].strip()
        jaartal = int(jaartal_raw) if jaartal_raw else None
        circa = row[COL_CIRCA].strip() == "Ja"
        periode = row[COL_PERIODE].strip() or None

        coords = geocode(adres, huisnummer, pc, plaats)
        time.sleep(0.03)  # de PDOK Locatieserver is een gratis, gedeelde dienst
        if coords is None:
            geocode_mislukt.append(f"{naam} ({plaats})")
            continue
        lon, lat = coords

        punten.append({
            "naam": naam,
            "plaats": plaats,
            "gemeente": gemeente,
            "jaartal": jaartal,
            "jaartal_circa": circa,
            "periode": periode,
            "lon": round(lon, 6),
            "lat": round(lat, 6),
        })

    punten.sort(key=lambda k: (k["plaats"] or "", k["naam"]))

    n_jaartal = sum(1 for p in punten if p["jaartal"])
    n_periode = sum(1 for p in punten if p["periode"] and not p["jaartal"])

    out = {
        "type": "FeatureCollection",
        "waarschuwing": (
            "Bron: de domeinexpert (data/Begraafplaatsen Zuid-Holland - "
            "datering.csv). Zelfstandige laag, geen 1-op-1 koppeling aan "
            "de 448 begraafplaatsen van de hoofddataset -- zie de "
            "toelichting in scripts/build_datering.py en methode.html. "
            "Locatie is gegeocodeerd op het bezoekadres (PDOK Locatieserver), "
            "meestal postcode-nauwkeurig."
        ),
        "aantal": len(punten),
        "aantal_met_jaartal": n_jaartal,
        "aantal_met_alleen_periode": n_periode,
        "features": [
            {
                "type": "Feature",
                "properties": {k: v for k, v in punt.items() if k not in ("lon", "lat")},
                "geometry": {"type": "Point", "coordinates": [punt["lon"], punt["lat"]]},
            }
            for punt in punten
        ],
    }
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"datering geschreven -> {OUT_PATH}")
    print(f"  {len(punten)} punten, {n_jaartal} met jaartal, {n_periode} met alleen periode")
    if geocode_mislukt:
        print(f"  {len(geocode_mislukt)} niet gegeocodeerd: {geocode_mislukt}")


if __name__ == "__main__":
    main()
