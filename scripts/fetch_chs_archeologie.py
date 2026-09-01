#!/usr/bin/env python3
"""
Fetch de laag "Archeologische terreinen van provinciaal belang" uit de
Cultuurhistorische Hoofdstructuur (CHS) van Provincie Zuid-Holland, als
toggelbare referentielaag op de hoofdkaart (wens van de opdrachtgever, 2026-08-27,
gevonden via https://data.overheid.nl/dataset/32677).

Andere bron dan de RCE-rijksmonumenten/-onderzoeksgebieden: dit is een
eigen provinciale WFS-dienst (geen landelijke bbox-fetch, dus geen
bbox-rand-effect -- de dienst dekt per definitie alleen Zuid-Holland).
Open data, publiek domein (CC0-achtig), geen API-key nodig.

Output: data/zuid-holland/chs-archeologie-provinciaal-belang.geojson
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "data" / "zuid-holland"
METADATA_DIR = OUTPUT_DIR / "metadata"

ENDPOINT = "https://geodata.zuid-holland.nl/geoserver/cultuur/wfs"
LAYER = "cultuur:CHS_2016_ARCHEOLOGIE_PROVINCIAAL_BELANG"
URL = (
    f"{ENDPOINT}?service=WFS&version=2.0.0&request=GetFeature"
    f"&typeNames={LAYER}&outputFormat=application/json&srsName=EPSG:4326"
)

# GDB_GEOMATTR_DATA is bij alle 662 features leeg; GRENS_SRC/VERWERKT zijn
# interne bronregistratie-/verwerkingsvelden zonder betekenis voor de domeinexpert --
# zelfde principe als eerder toegepaste opschoning van technische velden
# (zie docs/geschiedenis.md, "paneel-/popup-opschoning").
KEEP_PROPERTIES = [
    "MONUMENTNR", "Gemeente", "Plaats", "Toponiem", "Datering", "WAARDE", "Zichtbaarh", "Beschrijving",
]


def main() -> None:
    with urllib.request.urlopen(URL) as resp:
        data = json.load(resp)

    features = data["features"]
    out = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {k: f["properties"].get(k) for k in KEEP_PROPERTIES},
                "geometry": f["geometry"],
            }
            for f in features
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    geojson_path = OUTPUT_DIR / "chs-archeologie-provinciaal-belang.geojson"
    geojson_path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

    metadata = {
        "source": "Provincie Zuid-Holland, Cultuurhistorische Hoofdstructuur (CHS)",
        "dataset": "https://data.overheid.nl/dataset/32677-cultuurhistorische-hoofdstructuur--archeologische-terreinen-van-provinciaal-belang",
        "endpoint": ENDPOINT,
        "layer": LAYER,
        "licentie": "Publiek domein (CC0-achtig)",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "aantal_features": len(features),
    }
    (METADATA_DIR / "chs-archeologie-provinciaal-belang.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"{len(features)} archeologische terreinen van provinciaal belang -> {geojson_path}")


if __name__ == "__main__":
    main()
