#!/usr/bin/env python3
"""
One-off: append Natuurbegraafplaats Staelduinen (Hoek van Holland) to the
normalized source CSV, in the same terrein+ingang row pair convention used
throughout the file (see docs/data/003-csv-bron-en-koppeling.md).

New KMZ from the domeinexpert (2026-10-10): a point (ingang) and a polygon
(terrein) for a cemetery that is not in the domeinexpert's own Excel/KML
sources either -- confirmed new, not a correction of an existing entry.
No jaartal/status in this KMZ (geometry only), so none is added here; the
cemetery simply has no datering entry yet, same as any other gap (see
docs/data/007-datering-bevindingen.md/008-datering-ontbrekend.md for the
"eerder niet gevonden dan een foute match" discipline this follows).

Reuses the same parsing/splitting logic as
scripts/add_tijdelijk_zuidholland_kmz2.py.

Run once. Not part of the regular build.
"""
from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KMZ_PATH = REPO_ROOT / "data" / "Staelduinen Zuid-Holland.kmz"
CSV_PATH = REPO_ROOT / "data" / "Begraafplaatsen Zuid-Holland- Zuid-Holland.csv"

NS = {"k": "http://www.opengis.net/kml/2.2"}


def coords_to_wkt_polygon(text: str) -> str:
    pairs = []
    for triplet in text.split():
        lon, lat, _alt = triplet.split(",")
        pairs.append(f"{lon} {lat}")
    return "POLYGON ((" + ", ".join(pairs) + "))"


def coords_to_wkt_point(text: str) -> str:
    lon, lat, _alt = text.strip().split(",")
    return f"POINT ({lon} {lat})"


def split_name(full_name: str) -> tuple[str, str, str, str]:
    """"Naam, Plaats[ (geruimd)]" -> (naam, plaats_origineel, plaats_opgeschoon, geruimd)."""
    naam, _, plaats_origineel = full_name.partition(",")
    naam = naam.strip()
    plaats_origineel = plaats_origineel.strip()
    if plaats_origineel.endswith("(geruimd)"):
        geruimd = "geruimd"
        plaats_opgeschoon = plaats_origineel[: -len("(geruimd)")].strip()
    else:
        geruimd = ""
        plaats_opgeschoon = plaats_origineel
    return naam, plaats_origineel, plaats_opgeschoon, geruimd


def parse_kmz(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as zf:
        kml_bytes = zf.read("doc.kml")
    root = ET.fromstring(kml_bytes)

    by_name: dict[str, dict] = {}
    order: list[str] = []
    for pm in root.iter("{http://www.opengis.net/kml/2.2}Placemark"):
        name_el = pm.find("k:name", NS)
        assert name_el is not None and name_el.text, "placemark zonder naam"
        name = name_el.text.strip()
        if name not in by_name:
            by_name[name] = {}
            order.append(name)

        point_coords = pm.find(".//k:Point/k:coordinates", NS)
        poly_coords = pm.find(".//k:Polygon//k:coordinates", NS)
        if point_coords is not None:
            assert "point" not in by_name[name], f"{name}: dubbel Point"
            by_name[name]["point"] = point_coords.text.strip()
        elif poly_coords is not None:
            assert "polygon" not in by_name[name], f"{name}: dubbele Polygon"
            by_name[name]["polygon"] = poly_coords.text.strip()
        else:
            raise AssertionError(f"{name}: placemark is geen Point en geen Polygon")

    cemeteries = []
    for name in order:
        entry = by_name[name]
        assert "point" in entry and "polygon" in entry, f"{name}: mist Point of Polygon"
        cemeteries.append({"name": name, "point": entry["point"], "polygon": entry["polygon"]})
    return cemeteries


def main() -> None:
    cemeteries = parse_kmz(KMZ_PATH)
    assert len(cemeteries) == 1, f"verwacht 1 begraafplaats in de kmz, gevonden {len(cemeteries)}"

    with CSV_PATH.open(encoding="utf-8-sig") as f:
        existing = list(csv.reader(f))[1:]
    existing_keys = {(row[1].strip().lower(), row[2].strip().lower()) for row in existing}

    new_rows = []
    for cem in cemeteries:
        naam, plaats_origineel, plaats_opgeschoon, geruimd = split_name(cem["name"])
        key = (naam.lower(), plaats_origineel.lower())
        assert key not in existing_keys, f"{cem['name']}: staat al in de bron"
        terrein_wkt = coords_to_wkt_polygon(cem["polygon"])
        ingang_wkt = coords_to_wkt_point(cem["point"])
        new_rows.append([terrein_wkt, naam, plaats_origineel, plaats_opgeschoon, geruimd, "", "begraafplaats"])
        new_rows.append([ingang_wkt, naam, plaats_origineel, plaats_opgeschoon, geruimd, "ingang", ""])

    with CSV_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in new_rows:
            writer.writerow(row)

    print(f"{len(cemeteries)} begraafplaats ({2 * len(cemeteries)} rijen) toegevoegd aan {CSV_PATH}")
    for cem in cemeteries:
        naam, plaats_origineel, plaats_opgeschoon, geruimd = split_name(cem["name"])
        print(f"  - {naam} | {plaats_origineel!r} -> plaats={plaats_opgeschoon!r} geruimd={geruimd!r}")


if __name__ == "__main__":
    main()
