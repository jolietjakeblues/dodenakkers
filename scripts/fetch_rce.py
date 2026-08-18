#!/usr/bin/env python3
"""
Fetch RCE CHO Linked Data extracts for the Zuid-Holland dodenakkers project.

Runs the saved SPARQL queries in queries/rce/ against the public RCE CHO
endpoint, converts WKT geometries to GeoJSON, and writes one GeoJSON +
one metadata.json per extract into data/rce/.

Q2 and Q3 each consist of two SPARQL SELECTs (points, polygons) because
the bounding-box filter parses the WKT string directly (see the .sparql
files for why: geof:sfWithin/sfIntersects time out on this endpoint).
Per CHO, this script prefers the polygon geometry over the point when
both are present (see section 21 of the briefing).

Does not resolve status conflicts, does not silently drop rows, does not
invent geometry: it only reshapes what the endpoint returns.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from shapely import wkt as shapely_wkt
from shapely.geometry import mapping

ENDPOINT = "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/sparql"
REPO_ROOT = Path(__file__).resolve().parent.parent
QUERIES_DIR = REPO_ROOT / "queries" / "rce"
OUTPUT_DIR = REPO_ROOT / "data" / "rce"
METADATA_DIR = OUTPUT_DIR / "metadata"

# Bounding box used to filter Q1 client-side (Q2/Q3 filter server-side,
# see the .sparql files), derived from the extent of
# data/generated/begraafplaatsen.geojson with a buffer.
ZH_BBOX = {"min_lon": 3.90, "max_lon": 5.14, "min_lat": 51.66, "max_lat": 52.32}

QUERY_BLOCK_RE = re.compile(r"# --- QUERY: (?P<name>[a-z]+) ---\n(?P<body>.*?)(?=\n# --- QUERY:|\Z)", re.DOTALL)


def split_queries(sparql_text: str) -> dict[str, str]:
    """Split a .sparql file into named blocks, or {"default": text} if unmarked."""
    blocks = {m.group("name"): m.group("body").strip() for m in QUERY_BLOCK_RE.finditer(sparql_text)}
    if blocks:
        return blocks
    return {"default": sparql_text.strip()}


def run_query(sparql_query: str) -> list[dict]:
    resp = requests.post(
        ENDPOINT,
        data={"query": sparql_query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    rows = []
    for binding in data["results"]["bindings"]:
        row = {var: val["value"] for var, val in binding.items()}
        rows.append(row)
    return rows


FUNCTIE_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")


def strip_functie_suffix(label: str | None) -> str | None:
    """Drop a trailing RCE subtype code, e.g. "Woonhuis(K)" -> "Woonhuis",
    "Boerderij (M1)" -> "Boerderij". Used to bucket near-duplicate labels
    for filtering; the raw label is kept separately for display."""
    if not label:
        return label
    return FUNCTIE_SUFFIX_RE.sub("", label).strip() or label


def wkt_to_geojson_geometry(wkt_str: str) -> dict:
    geom = shapely_wkt.loads(wkt_str)
    return mapping(geom)


def bbox_ok(lon: float, lat: float) -> bool:
    return (
        ZH_BBOX["min_lon"] <= lon <= ZH_BBOX["max_lon"]
        and ZH_BBOX["min_lat"] <= lat <= ZH_BBOX["max_lat"]
    )


def build_gezichten() -> tuple[dict, dict]:
    query_file = QUERIES_DIR / "beschermde-gezichten.sparql"
    rows = run_query(split_queries(query_file.read_text(encoding="utf-8"))["default"])

    features = []
    skipped_out_of_bbox = 0
    for row in rows:
        geom = shapely_wkt.loads(row["wkt"])
        centroid = geom.centroid
        if not bbox_ok(centroid.x, centroid.y):
            skipped_out_of_bbox += 1
            continue
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "gezicht_uri": row["gezicht"],
                    "gezichtsnummer": row.get("gezichtsnummer"),
                    "naam": row.get("naam"),
                    "status": "rijksbeschermd stads- of dorpsgezicht",
                },
                "geometry": mapping(geom),
            }
        )

    fc = {"type": "FeatureCollection", "name": "beschermde_gezichten_zuid_holland", "features": features}
    stats = {
        "rows_from_endpoint": len(rows),
        "features_in_bbox": len(features),
        "skipped_out_of_bbox": skipped_out_of_bbox,
    }
    return fc, stats


def build_rijksmonumenten(query_file: Path, feature_name: str, include_aard: bool) -> tuple[dict, dict]:
    blocks = split_queries(query_file.read_text(encoding="utf-8"))
    point_rows = run_query(blocks["points"])
    polygon_rows = run_query(blocks["polygons"])

    by_cho: dict[str, dict] = {}
    for row in point_rows:
        cho = row["cho"]
        entry = by_cho.setdefault(cho, {"row": row, "geometry_type": "Point", "wkt": row["wkt"]})
        # keep first point seen; near-duplicate points for the same CHO are expected
    for row in polygon_rows:
        cho = row["cho"]
        # polygon always wins over point (section 21 of the briefing)
        by_cho[cho] = {"row": row, "geometry_type": "Polygon", "wkt": row["wkt"]}

    features = []
    for cho, entry in by_cho.items():
        row = entry["row"]
        props = {
            "cho_uri": cho,
            "rijksmonumentnummer": row.get("rijksmonumentnummer"),
            "naam": row.get("naam"),
            "geometry_bron": entry["geometry_type"],
            "monumentenregister_url": (
                f"https://monumentenregister.cultureelerfgoed.nl/monumenten/{row['rijksmonumentnummer']}"
                if row.get("rijksmonumentnummer")
                else None
            ),
            "oorspronkelijke_functie": row.get("oorspronkelijkeFunctie"),
            "oorspronkelijke_functie_kort": strip_functie_suffix(row.get("oorspronkelijkeFunctie")),
            "huidige_functie": row.get("huidigeFunctie"),
            "type": row.get("type"),
        }
        if include_aard:
            aard_uri = row.get("aard")
            props["monument_aard"] = (
                "archeologisch"
                if aard_uri == "https://data.cultureelerfgoed.nl/term/id/rn/2/b673c8c1-5d93-496d-8f9e-89133d579d77"
                else "onroerend gebouwd"
                if aard_uri
                else None
            )
        features.append(
            {"type": "Feature", "properties": props, "geometry": wkt_to_geojson_geometry(entry["wkt"])}
        )

    fc = {"type": "FeatureCollection", "name": feature_name, "features": features}
    stats = {
        "point_rows_from_endpoint": len(point_rows),
        "polygon_rows_from_endpoint": len(polygon_rows),
        "distinct_cho": len(by_cho),
        "cho_with_polygon": sum(1 for e in by_cho.values() if e["geometry_type"] == "Polygon"),
    }
    return fc, stats


def write_extract(name: str, feature_collection: dict, query_file: Path, stats: dict, notes: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    geojson_path = OUTPUT_DIR / f"{name}.geojson"
    geojson_path.write_text(json.dumps(feature_collection, ensure_ascii=False, indent=2), encoding="utf-8")

    metadata = {
        "source": "RCE Linked Data Voorziening (CHO)",
        "endpoint": ENDPOINT,
        "query_file": str(query_file.relative_to(REPO_ROOT)).replace("\\", "/"),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "feature_count": len(feature_collection["features"]),
        "stats": stats,
        "bbox_wgs84": ZH_BBOX,
        "notes": notes,
    }
    metadata_path = METADATA_DIR / f"{name}.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{name}: {len(feature_collection['features'])} features -> {geojson_path}")
    print(f"  stats: {stats}")


def main() -> None:
    gezichten_fc, gezichten_stats = build_gezichten()
    write_extract(
        "beschermde-gezichten",
        gezichten_fc,
        QUERIES_DIR / "beschermde-gezichten.sparql",
        gezichten_stats,
        notes=(
            "Nationale fetch (472 rijksbeschermde gezichten op 2026-08-18), "
            "lokaal gefilterd op de Zuid-Holland bbox via de centroid van elke polygon."
        ),
    )

    rm_fc, rm_stats = build_rijksmonumenten(
        QUERIES_DIR / "rijksmonumenten.sparql", "rijksmonumenten_zuid_holland", include_aard=True
    )
    write_extract(
        "rijksmonumenten",
        rm_fc,
        QUERIES_DIR / "rijksmonumenten.sparql",
        rm_stats,
        notes=(
            "heeftJuridischeStatus = rijksmonument, serverside bbox-filter op WKT-string. "
            "oorspronkelijke_functie/huidige_functie/type via heeftOorspronkelijkeFunctie/"
            "heeftHuidigeFunctie/heeftType (geen curatie, echte labels), zie "
            "queries/rce/rijksmonumenten.sparql. oorspronkelijke_functie_kort heeft de "
            "RCE-subtypecode ('(K)', '(M1)', ...) afgeknipt, voor filtering. "
            "Aanwijzingsinformatie (aanwijzingenmonumenten-graph) is nog niet meegenomen; "
            "zie docs/data/004-rce-mcp-querystrategie.md."
        ),
    )

    arch_fc, arch_stats = build_rijksmonumenten(
        QUERIES_DIR / "archeologische-rijksmonumenten.sparql",
        "archeologische_rijksmonumenten_zuid_holland",
        include_aard=False,
    )
    write_extract(
        "archeologische-rijksmonumenten",
        arch_fc,
        QUERIES_DIR / "archeologische-rijksmonumenten.sparql",
        arch_stats,
        notes=(
            "Subset van Rijksmonument met heeftMonumentAard = archeologisch "
            "(concept-URI, geen keyword-classificatie), serverside bbox-filter op WKT-string."
        ),
    )


if __name__ == "__main__":
    sys.exit(main())
