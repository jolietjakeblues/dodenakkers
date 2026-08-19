#!/usr/bin/env python3
"""
Spatial join between the base cemetery dataset and the RCE extracts.

Input:
  data/generated/begraafplaatsen.geojson  (terrain, WGS84)
  data/rce/beschermde-gezichten.geojson
  data/rce/rijksmonumenten.geojson
  data/rce/archeologische-rijksmonumenten.geojson

Output:
  data/generated/analyse.geojson          (begraafplaatsen + erfgoedrelaties)
  docs/data/005-erfgoedrelaties-resultaten.md

All metric operations (contains/intersects/distance/area) run in EPSG:28992
(RD New), never in WGS84 degrees (section 8/16 of the briefing). Output
geometry stays in the original WGS84 terrain geometry.

Categories for "aangrenzend rijksmonument" (inside_on_site / touches /
intersects / 0-25m / 25-100m) are provisional working hypotheses (section
18): the raw distance_m is always kept so they can be recomputed later.
Monuments beyond 100m are not included in rijksmonument_relations.
"""
from __future__ import annotations

import json
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform
from shapely.strtree import STRtree

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = REPO_ROOT / "data" / "generated"
RCE_DIR = REPO_ROOT / "data" / "rce"

# 100m was de eerste werkhypothese (sectie 18 van de briefing); de viewer
# heeft nu een schuifregelaar (stappen van 50m) zodat Leon zelf kan
# verkennen welke afstand de juiste is, dus de dataset bewaart alvast tot
# 250m aan ruwe afstanden -- de viewer filtert daarna client-side.
RM_NEARBY_BUFFER_M = 250

to_rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True).transform


def load_features(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)["features"]


def to_rd_geom(feature: dict):
    return transform(to_rd, shape(feature["geometry"]))


def classify_gezicht(terrain_rd, gezichten_index: STRtree, gezichten: list[dict], gezichten_geoms: list):
    candidate_idx = gezichten_index.query(terrain_rd)
    matches = []
    best = "none"
    for i in candidate_idx:
        geom = gezichten_geoms[i]
        if terrain_rd.within(geom):
            relation = "within"
        elif terrain_rd.intersects(geom):
            relation = "intersects"
        else:
            continue
        props = gezichten[i]["properties"]
        matches.append(
            {
                "gezichtsnummer": props.get("gezichtsnummer"),
                "naam": props.get("naam"),
                "gezicht_uri": props.get("gezicht_uri"),
                "relation": relation,
            }
        )
        if relation == "within":
            best = "within"
        elif relation == "intersects" and best != "within":
            best = "intersects"
    return best, matches


def nearest_archeologie(terrain_rd, arch_index: STRtree, arch: list[dict], arch_geoms: list):
    """Informational nearest archeologisch rijksmonument, regardless of overlap.

    Not a "relation" in the sense of section 20 (no overlap implied) -- kept
    so near-misses (e.g. a monument a few metres from a terrain boundary)
    stay visible instead of silently reading as "none". See section 18: the
    raw distance is what matters, categories are working hypotheses.
    """
    if len(arch_geoms) == 0:
        return None
    i = arch_index.nearest(terrain_rd)
    geom = arch_geoms[i]
    props = arch[i]["properties"]
    return {
        "rijksmonumentnummer": props.get("rijksmonumentnummer"),
        "naam": props.get("naam"),
        "cho_uri": props.get("cho_uri"),
        "distance_m": round(terrain_rd.distance(geom), 1),
    }


def classify_archeologie(terrain_rd, arch_index: STRtree, arch: list[dict], arch_geoms: list):
    candidate_idx = arch_index.query(terrain_rd)
    relations = []
    terrain_area = terrain_rd.area
    for i in candidate_idx:
        geom = arch_geoms[i]
        props = arch[i]["properties"]
        entry = {
            "rijksmonumentnummer": props.get("rijksmonumentnummer"),
            "naam": props.get("naam"),
            "cho_uri": props.get("cho_uri"),
        }
        if geom.geom_type == "Point":
            if not terrain_rd.contains(geom):
                continue
            entry["relation"] = "point_inside"
            entry["point_inside"] = True
        else:
            if terrain_rd.contains(geom):
                entry["relation"] = "contains"
            elif geom.contains(terrain_rd):
                entry["relation"] = "within"
            elif terrain_rd.intersects(geom):
                entry["relation"] = "intersects"
            else:
                continue
            overlap_area = terrain_rd.intersection(geom).area
            entry["overlap_area_m2"] = round(overlap_area, 2)
            entry["overlap_pct_cemetery"] = round(100 * overlap_area / terrain_area, 2) if terrain_area else None
        relations.append(entry)
    return relations


def classify_rijksmonumenten(terrain_rd, rm_index: STRtree, rm: list[dict], rm_geoms: list):
    search_area = terrain_rd.buffer(RM_NEARBY_BUFFER_M)
    candidate_idx = rm_index.query(search_area)
    relations = []
    for i in candidate_idx:
        geom = rm_geoms[i]
        distance_m = terrain_rd.distance(geom)
        if distance_m > RM_NEARBY_BUFFER_M:
            continue
        if distance_m == 0:
            if terrain_rd.contains(geom):
                relation = "inside_on_site"
            elif terrain_rd.touches(geom):
                relation = "touches"
            else:
                relation = "intersects"
        elif distance_m <= 25:
            relation = "0-25m"
        elif distance_m <= 100:
            relation = "25-100m"
        else:
            relation = "100-250m"
        props = rm[i]["properties"]
        relations.append(
            {
                "rijksmonumentnummer": props.get("rijksmonumentnummer"),
                "naam": props.get("naam"),
                "cho_uri": props.get("cho_uri"),
                "relation": relation,
                "distance_m": round(distance_m, 1),
            }
        )
    relations.sort(key=lambda r: r["distance_m"])
    return relations


def main() -> None:
    begraafplaatsen = load_features(GENERATED_DIR / "begraafplaatsen.geojson")
    gezichten = load_features(RCE_DIR / "beschermde-gezichten.geojson")
    rijksmonumenten_all = load_features(RCE_DIR / "rijksmonumenten.geojson")
    archeologisch = load_features(RCE_DIR / "archeologische-rijksmonumenten.geojson")

    # "gebouwde rijksmonumenten" excludes the archeologisch subset -- those
    # are handled separately via the dedicated archeologische-rijksmonumenten
    # extract (section 21 vs section 20 of the briefing).
    rijksmonumenten_gebouwd = [
        f for f in rijksmonumenten_all if f["properties"].get("monument_aard") != "archeologisch"
    ]
    skipped_null_aard = sum(1 for f in rijksmonumenten_all if f["properties"].get("monument_aard") is None)

    gezichten_geoms = [to_rd_geom(f) for f in gezichten]
    arch_geoms = [to_rd_geom(f) for f in archeologisch]
    rm_geoms = [to_rd_geom(f) for f in rijksmonumenten_gebouwd]

    gezichten_index = STRtree(gezichten_geoms)
    arch_index = STRtree(arch_geoms)
    rm_index = STRtree(rm_geoms)

    out_features = []
    stats = {
        "within_gezicht": 0,
        "intersects_gezicht": 0,
        "met_archeologie": 0,
        "met_rijksmonument_100m": 0,
        "met_rijksmonument_250m": 0,
    }

    for feature in begraafplaatsen:
        terrain_rd = to_rd_geom(feature)

        in_gezicht, gezicht_matches = classify_gezicht(terrain_rd, gezichten_index, gezichten, gezichten_geoms)
        arch_relations = classify_archeologie(terrain_rd, arch_index, archeologisch, arch_geoms)
        arch_nearest = nearest_archeologie(terrain_rd, arch_index, archeologisch, arch_geoms)
        rm_relations = classify_rijksmonumenten(terrain_rd, rm_index, rijksmonumenten_gebouwd, rm_geoms)

        if in_gezicht == "within":
            stats["within_gezicht"] += 1
        elif in_gezicht == "intersects":
            stats["intersects_gezicht"] += 1
        if arch_relations:
            stats["met_archeologie"] += 1
        if rm_relations:
            stats["met_rijksmonument_250m"] += 1
        if any(r["distance_m"] <= 100 for r in rm_relations):
            stats["met_rijksmonument_100m"] += 1

        props = dict(feature["properties"])
        props["in_beschermd_gezicht"] = in_gezicht
        props["beschermd_gezicht_relaties"] = gezicht_matches
        props["archeologische_rm_count"] = len(arch_relations)
        props["archeologische_rm_relations"] = arch_relations
        props["archeologische_rm_nearest"] = arch_nearest
        props["rijksmonument_count"] = len(rm_relations)
        props["rijksmonument_relations"] = rm_relations

        out_features.append({"type": "Feature", "properties": props, "geometry": feature["geometry"]})

    out_fc = {
        "type": "FeatureCollection",
        "name": "begraafplaatsen_zuid_holland_analyse",
        "features": out_features,
    }
    out_path = GENERATED_DIR / "analyse.geojson"
    out_path.write_text(json.dumps(out_fc, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{len(out_features)} begraafplaatsen geanalyseerd -> {out_path}")
    print(f"  binnen beschermd gezicht: {stats['within_gezicht']}")
    print(f"  overlapt beschermd gezicht (intersects): {stats['intersects_gezicht']}")
    print(f"  overlapt archeologisch rijksmonument: {stats['met_archeologie']}")
    print(f"  rijksmonument binnen 100m: {stats['met_rijksmonument_100m']}")
    print(f"  rijksmonument binnen {RM_NEARBY_BUFFER_M}m (opgeslagen bereik voor de schuifregelaar): {stats['met_rijksmonument_250m']}")
    print(f"  rijksmonumenten zonder monument_aard (uitgesloten van gebouwd-set): {skipped_null_aard}")

    write_audit(out_features, stats, skipped_null_aard)


def write_audit(features: list[dict], stats: dict, skipped_null_aard: int) -> None:
    lines = [
        "# Data 005: erfgoedrelaties resultaten",
        "",
        "## Samenvatting",
        "",
        f"- {len(features)} begraafplaatsen geanalyseerd tegen de RCE-extracten uit `data/rce/`;",
        f"- **{stats['within_gezicht']}** volledig binnen een rijksbeschermd gezicht (`in_beschermd_gezicht = within`);",
        f"- **{stats['intersects_gezicht']}** deels overlappend met een rijksbeschermd gezicht (`intersects`);",
        f"- **{stats['met_archeologie']}** met minstens één overlappend archeologisch rijksmonument;",
        f"- **{stats['met_rijksmonument_100m']}** met minstens één gebouwd rijksmonument binnen 100 m "
        f"(**{stats['met_rijksmonument_250m']}** binnen {RM_NEARBY_BUFFER_M} m -- de dataset bewaart relaties tot "
        f"{RM_NEARBY_BUFFER_M} m zodat de schuifregelaar in de viewer verder dan 100 m kan verkennen). "
        "Categorieën `inside_on_site`/`touches`/`intersects`/`0-25m`/`25-100m`/`100-250m`, zie sectie 18 van de "
        "briefing — voorlopige werkhypothesen, ruwe afstand blijft altijd bewaard.",
        "",
        f"{skipped_null_aard} rijksmonumenten zonder `monument_aard` zijn uitgesloten van de "
        "'gebouwd'-set in `data/rce/rijksmonumenten.geojson` (noch als gebouwd, noch als archeologisch geteld).",
        "",
        "## Voorbeelden binnen een beschermd gezicht",
        "",
    ]
    examples = [f for f in features if f["properties"]["in_beschermd_gezicht"] == "within"][:10]
    for f in examples:
        p = f["properties"]
        gezicht_namen = ", ".join(g["naam"] or "?" for g in p["beschermd_gezicht_relaties"])
        lines.append(f"- `{p['id']}` {p['naam']} ({p['plaats']}) — gezicht: {gezicht_namen}")

    lines += ["", "## Voorbeelden met archeologische overlap", ""]
    examples = [f for f in features if f["properties"]["archeologische_rm_count"] > 0][:10]
    if not examples:
        lines.append(
            "Geen enkel terrein overlapt een archeologisch rijksmonument (zie 'Bijna-overlap' hieronder voor "
            "de dichtstbijzijnde niet-overlappende gevallen)."
        )
    for f in examples:
        p = f["properties"]
        rels = ", ".join(
            f"{r['naam'] or r['rijksmonumentnummer']} ({r['relation']})" for r in p["archeologische_rm_relations"]
        )
        lines.append(f"- `{p['id']}` {p['naam']} ({p['plaats']}) — {rels}")

    lines += [
        "",
        "## Bijna-overlap met archeologische rijksmonumenten",
        "",
        "Geen overlap (dus niet in `archeologische_rm_relations`), maar wel de dichtstbijzijnde "
        "archeologische rijksmonumenten per terrein — puur informatief (`archeologische_rm_nearest`), "
        "om te laten zien wanneer 'geen overlap' een randgeval is in plaats van 'ver weg'.",
        "",
    ]
    with_nearest = [f for f in features if f["properties"].get("archeologische_rm_nearest")]
    with_nearest.sort(key=lambda f: f["properties"]["archeologische_rm_nearest"]["distance_m"])
    for f in with_nearest[:10]:
        p = f["properties"]
        n = p["archeologische_rm_nearest"]
        lines.append(
            f"- `{p['id']}` {p['naam']} ({p['plaats']}) — {n['distance_m']} m tot "
            f"{n['naam'] or n['rijksmonumentnummer']}"
        )

    lines += [
        "",
        "## Gegenereerde bestanden",
        "",
        "- `data/generated/analyse.geojson` — `begraafplaatsen.geojson` verrijkt met "
        "`in_beschermd_gezicht`, `beschermd_gezicht_relaties`, `archeologische_rm_*` en `rijksmonument_*`.",
        "",
        "## Open punten",
        "",
        "1. De 100 m-grens voor 'nabij gebouwd rijksmonument' is een werkhypothese (sectie 18), nog niet door "
        "Leon bevestigd. Wel al bevestigd (2026-08-19): 'annex aan een rijksmonument' betekent grenscontact "
        "-- de relatie `touches` -- niet zomaar 'binnen X meter'; de viewer toont dit nu als 'annex (grenst aan)'.",
        "2. `rijksmonument_relations` gebruikt alleen de punt/polygoon-geometrie uit `data/rce/rijksmonumenten.geojson`; "
        "monumenten zonder geometrie in die extractie ontbreken hier per definitie.",
        "3. Kadastrale percelen (fase 2, sectie 22) zijn nog niet meegenomen. Zonder percelen kunnen we ook niet "
        "zien of meerdere rijksmonumenten (zoals de cluster bij NH Kerkhof Wassenaar) op hetzelfde perceel liggen "
        "en dus als 1 site geclusterd zouden moeten worden i.p.v. als losse punten -- dat is precies waar sectie "
        "42-vraag 4 van de briefing over gaat.",
    ]

    out_path = REPO_ROOT / "docs" / "data" / "005-erfgoedrelaties-resultaten.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"audit geschreven -> {out_path}")


if __name__ == "__main__":
    main()
