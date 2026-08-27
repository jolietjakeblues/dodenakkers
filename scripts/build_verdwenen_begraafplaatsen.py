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
ZH). Voegt een RUWE, naam+plaats-gebaseerde match tegen de hoofddataset toe
(in_hoofddataset) zodat duidelijk is welke van de 92 al bekend zijn (vaak als
"geruimd") en welke echt ontbreken in Begraafplaatsen Zuid-Holland -- dit is
een heuristiek (substring-vergelijking op genormaliseerde naam, zelfde plaats),
geen exacte koppeling; bij twijfel telt een record als "niet gematcht".

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
STOPWOORDEN = {"begraafplaats", "kerkhof", "oude", "oud", "nieuwe", "nh", "rk", "gem", "algemene", "de", "het", "van", "op"}

# Leons KMZ gebruikt af en toe een historische/alternatieve plaatsnaam die
# niet letterlijk in de hoofddataset voorkomt (die noemt de plaats zelf
# "Den Haag", nooit "'s-Gravenhage") -- zonder deze alias mist de
# plaats-matching in match_hoofddataset() alle vier Haagse verdwenen
# begraafplaatsen, puur door een schrijfwijzeverschil, niet omdat ze echt
# onbekend zijn.
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


def normalize(tekst: str) -> set[str]:
    woorden = re.findall(r"[a-zà-ÿ]+", tekst.lower())
    return {w for w in woorden if w not in STOPWOORDEN}


def match_hoofddataset(naam: str, plaats: str, begraafplaatsen: list[dict]) -> bool:
    """Ruwe heuristiek: zelfde plaats + betekenisvolle woordoverlap in de
    naam (na strippen van generieke woorden als "begraafplaats"/"kerkhof"/
    "oude"). Geen exacte koppeling, zie module-docstring."""
    naam_woorden = normalize(naam)
    for f in begraafplaatsen:
        p = f["properties"]
        if p["plaats"].strip().lower() != plaats.strip().lower():
            continue
        bp_woorden = normalize(p["naam"])
        if naam_woorden and bp_woorden and (naam_woorden & bp_woorden):
            return True
        # Val terug op substring-vergelijking voor het geval geen van beide
        # genoeg betekenisvolle woorden overhoudt na het strippen.
        n1, n2 = naam.strip().lower(), p["naam"].strip().lower()
        if n1 and n2 and (n1 in n2 or n2 in n1):
            return True
    return False


def main() -> None:
    alle_items = parse_kmz(KMZ_PATH)

    provincie = json.load(open(PDOK_DIR / "provincie-zuid-holland.geojson", encoding="utf-8"))
    provincie_geom = shape(provincie["features"][0]["geometry"])

    begraafplaatsen = json.load(open(GENERATED_DIR / "analyse.geojson", encoding="utf-8"))["features"]

    kandidaten = []
    for item in alle_items:
        punt = Point(item["lon"], item["lat"])
        if not provincie_geom.contains(punt):
            continue
        naam, plaats, status = split_naam_plaats(item["omschrijving"])
        kandidaten.append({
            "naam": naam,
            "plaats": plaats,
            "status_vermeld": status,
            "in_hoofddataset": match_hoofddataset(naam, plaats, begraafplaatsen),
            "lon": round(item["lon"], 6),
            "lat": round(item["lat"], 6),
        })

    kandidaten.sort(key=lambda k: (k["plaats"], k["naam"]))

    out = {
        "type": "FeatureCollection",
        "waarschuwing": (
            "Bron: Leon (data/Verdwenen.kmz), niet de automatische "
            "kandidaat-signalen op kandidaten.html. 'in_hoofddataset' is een "
            "ruwe naam+plaats-heuristiek, geen exacte koppeling -- bij "
            "twijfel staat 'false'. Punten, geen terreinpolygoon: de "
            "begraafplaats bestaat niet meer, alleen de historische locatie "
            "is bekend."
        ),
        "aantal_landelijk": len(alle_items),
        "features": [
            {
                "type": "Feature",
                "properties": {k: v for k, v in kand.items() if k not in ("lon", "lat")},
                "geometry": {"type": "Point", "coordinates": [kand["lon"], kand["lat"]]},
            }
            for kand in kandidaten
        ],
    }
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    in_hoofddataset = sum(1 for k in kandidaten if k["in_hoofddataset"])
    print(f"verdwenen begraafplaatsen geschreven -> {OUT_PATH}")
    print(f"  {len(alle_items)} landelijk, {len(kandidaten)} in Zuid-Holland")
    print(f"  {in_hoofddataset} lijken al bekend in de hoofddataset (naam+plaats-heuristiek), {len(kandidaten) - in_hoofddataset} niet")


if __name__ == "__main__":
    main()
