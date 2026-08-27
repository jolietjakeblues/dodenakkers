#!/usr/bin/env python3
"""
Fetch the 50 Zuid-Holland gemeentegrenzen from PDOK, for een echte
per-gemeente-koppeling op de statistiekenpagina (wens van Joop, 2026-08-27
-- de bron heeft alleen "plaats" (dorp/stad), geen gemeente; sommige
plaatsen horen sinds de 2019-herindeling bij een andere gemeente dan hun
eigen naam doet vermoeden).

Source: PDOK "bestuurlijkegebieden" WFS (Kadaster), layer Gemeentegebied --
zelfde endpoint als scripts/fetch_provinciegrens.py, andere laag. Elke
feature draagt een ligtInProvincieNaam-property, dus filteren op
Zuid-Holland kan client-side zonder aparte spatial join tegen de
provinciegrens.

Output: data/pdok/gemeenten-zuid-holland.geojson + metadata/gemeenten-zuid-holland.json
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "data" / "pdok"
METADATA_DIR = OUTPUT_DIR / "metadata"

ENDPOINT = "https://service.pdok.nl/kadaster/bestuurlijkegebieden/wfs/v1_0"
URL = (
    f"{ENDPOINT}?service=WFS&version=2.0.0&request=GetFeature"
    "&typeName=bestuurlijkegebieden:Gemeentegebied"
    "&outputFormat=application/json&srsName=EPSG:4326"
)
PROVINCIE_NAAM = "Zuid-Holland"


def main() -> None:
    with urllib.request.urlopen(URL) as resp:
        data = json.load(resp)

    matches = [f for f in data["features"] if f["properties"].get("ligtInProvincieNaam") == PROVINCIE_NAAM]
    assert len(matches) == 50, f"verwacht 50 gemeenten in {PROVINCIE_NAAM}, gevonden {len(matches)}"

    out = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"naam": f["properties"]["naam"], "code": f["properties"]["code"]},
                "geometry": f["geometry"],
            }
            for f in matches
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    geojson_path = OUTPUT_DIR / "gemeenten-zuid-holland.geojson"
    geojson_path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

    metadata = {
        "source": "PDOK bestuurlijkegebieden WFS (Kadaster)",
        "endpoint": ENDPOINT,
        "layer": "bestuurlijkegebieden:Gemeentegebied",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "filter": f"ligtInProvincieNaam == {PROVINCIE_NAAM!r} (client-side, zie docstring)",
        "aantal_gemeenten": len(matches),
    }
    (METADATA_DIR / "gemeenten-zuid-holland.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"{len(matches)} gemeenten in {PROVINCIE_NAAM} -> {geojson_path}")


if __name__ == "__main__":
    main()
