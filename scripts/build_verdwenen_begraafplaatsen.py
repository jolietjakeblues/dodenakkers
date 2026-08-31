#!/usr/bin/env python3
"""
Verwerkt "Verdwenen begraafplaatsen" van Leon (data/Verdwenen.kmz, 907
punten landelijk) tot een aparte referentielaag voor de viewer -- niet de
tekstzoekactie/rijksmonument-heuristieken van
scripts/compute_kandidaat_begraafplaatsen.py, maar Leons eigen, geverifieerde
kennis over begraafplaatsen die niet meer bestaan.

Andere aard dan zowel de hoofddataset (Begraafplaatsen Zuid-Holland: actueel
bestaande terreinen met polygoon+ingang) als de EXPERIMENTELE kandidatenpagina
(onzekere, automatisch gevonden aanwijzingen): dit zijn punten, geen
polygonen (er is geen terrein meer om te tonen), en ze zijn niet
"experimenteel" -- het is Leons eigen historische kennis, alleen niet
(per se) verwerkt in de hoofdbron.

Elk placemark heeft alleen een naam ("Verdwenen NNNN", betekenisloos) en een
description-veld met de eigenlijke naam + plaats, bv. "Oude joodse
begraafplaats, Leiden" of "NH kerkhof, Giessenburg (verdwenen)". Plaats =
tekst na de laatste komma; eventuele "(geruimd)"/"(verdwenen)"-annotatie
wordt er als apart veld uitgehaald.

Filtert tot Zuid-Holland via de provinciepolygoon (907 landelijk -> 92 in
ZH).

Had tot 2026-08-28 ook een ruwe naam+plaats-heuristiek (in_hoofddataset) die
liet zien welke punten "al bekend" leken in Begraafplaatsen Zuid-Holland --
verwijderd op verzoek van de opdrachtgever: dit zijn stuk voor stuk
geverifieerde locaties, geen kandidaat-indicatie zoals de kandidatenpagina.
Ook wanneer zo'n punt vlak bij een bestaand restant ligt, staat het op
zichzelf. Alle 92 punten tonen dus nu gelijk, zonder onderscheid.

Output:
  data/generated/verdwenen-begraafplaatsen.geojson
"""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from shapely.geometry import Point, shape

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = REPO_ROOT / "data" / "generated"
PDOK_DIR = REPO_ROOT / "data" / "pdok"
KMZ_PATH = REPO_ROOT / "data" / "Verdwenen.kmz"
OUT_PATH = GENERATED_DIR / "verdwenen-begraafplaatsen.geojson"

KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}

STATUS_PATTERN = re.compile(r"\((geruimd|verdwenen)\)", re.IGNORECASE)

# Leons KMZ gebruikt af en toe een historische/alternatieve plaatsnaam die
# niet overeenkomt met de schrijfwijze die de hoofddataset zelf aanhoudt
# (die noemt de plaats zelf "Den Haag", nooit "'s-Gravenhage") -- puur een
# schrijfwijze-normalisatie voor de weergave, geen matching-logica.
PLAATS_ALIASEN = {"'s-gravenhage": "Den Haag"}


def parse_kmz(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as z:
        kml_name = next(n for n in z.namelist() if n.endswith(".kml"))
        with z.open(kml_name) as f:
            root = ET.parse(f).getroot()

    items = []
    for pm in root.findall(".//kml:Placemark", KML_NS):
        desc_el = pm.find("kml:description", KML_NS)
        desc = (desc_el.text or "").strip() if desc_el is not None else ""
        coords_el = pm.find("kml:Point/kml:coordinates", KML_NS)
        if coords_el is None or not desc:
            continue
        lon_str, lat_str, *_ = coords_el.text.strip().split(",")
        items.append({"omschrijving": desc, "lon": float(lon_str), "lat": float(lat_str)})
    return items


def split_naam_plaats(omschrijving: str) -> tuple[str, str, str | None]:
    status_match = STATUS_PATTERN.search(omschrijving)
    status = status_match.group(1).lower() if status_match else None
    tekst = STATUS_PATTERN.sub("", omschrijving).strip()
    if "," in tekst:
        naam, plaats = tekst.rsplit(",", 1)
        plaats = plaats.strip()
        plaats = PLAATS_ALIASEN.get(plaats.lower(), plaats)
        return naam.strip(), plaats, status
    return tekst, "", status


def main() -> None:
    alle_items = parse_kmz(KMZ_PATH)

    provincie = json.load(open(PDOK_DIR / "provincie-zuid-holland.geojson", encoding="utf-8"))
    provincie_geom = shape(provincie["features"][0]["geometry"])

    punten = []
    for item in alle_items:
        punt = Point(item["lon"], item["lat"])
        if not provincie_geom.contains(punt):
            continue
        naam, plaats, status = split_naam_plaats(item["omschrijving"])
        punten.append({
            "naam": naam,
            "plaats": plaats,
            "status_vermeld": status,
            "lon": round(item["lon"], 6),
            "lat": round(item["lat"], 6),
        })

    punten.sort(key=lambda k: (k["plaats"], k["naam"]))

    out = {
        "type": "FeatureCollection",
        "waarschuwing": (
            "Bron: Leon (data/Verdwenen.kmz), niet de automatische "
            "kandidaat-signalen op kandidaten.html. Dit zijn geverifieerde "
            "locaties, geen kandidaat-indicatie -- ook een punt vlak bij een "
            "bestaand restant staat op zichzelf. Punten, geen "
            "terreinpolygoon: de begraafplaats bestaat niet meer, alleen de "
            "historische locatie is bekend."
        ),
        "aantal_landelijk": len(alle_items),
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

    print(f"verdwenen begraafplaatsen geschreven -> {OUT_PATH}")
    print(f"  {len(alle_items)} landelijk, {len(punten)} in Zuid-Holland")


if __name__ == "__main__":
    main()
