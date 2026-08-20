#!/usr/bin/env python3
"""
Fetch the Zuid-Holland province boundary from PDOK, for a reference outline
on the viewer's map (user's wens, 2026-08-20 -- "kun je de grens van
Zuid-Holland aangeven op de kaarten?").

Source: PDOK "bestuurlijkegebieden" WFS (Kadaster), layer Provinciegebied.
CQL_FILTER on naam=Zuid-Holland isn't applied server-side reliably via a
plain query string (returns all 12 provinces instead), so this fetches the
full Provinciegebied collection and filters client-side, then writes out
only the Zuid-Holland feature with its identifying properties.

Output: data/pdok/provincie-zuid-holland.geojson + metadata/provincie-zuid-holland.json
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
    "&typeName=bestuurlijkegebieden:Provinciegebied"
    "&outputFormat=application/json&srsName=EPSG:4326"
)
PROVINCIE_NAAM = "Zuid-Holland"


def main() -> None:
    with urllib.request.urlopen(URL) as resp:
        data = json.load(resp)

    matches = [f for f in data["features"] if f["properties"].get("naam") == PROVINCIE_NAAM]
    assert len(matches) == 1, f"verwacht 1 feature voor {PROVINCIE_NAAM!r}, gevonden {len(matches)}"
    feature = matches[0]
    props = feature["properties"]

    out = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"naam": props["naam"], "code": props["code"]},
                "geometry": feature["geometry"],
            }
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    geojson_path = OUTPUT_DIR / "provincie-zuid-holland.geojson"
    geojson_path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

    metadata = {
        "source": "PDOK bestuurlijkegebieden WFS (Kadaster)",
        "endpoint": ENDPOINT,
        "layer": "bestuurlijkegebieden:Provinciegebied",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "filter": f"naam == {PROVINCIE_NAAM!r} (client-side, zie docstring)",
        "geometry_type": feature["geometry"]["type"],
    }
    (METADATA_DIR / "provincie-zuid-holland.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"{PROVINCIE_NAAM} ({props['code']}) -> {geojson_path}")


if __name__ == "__main__":
    main()
