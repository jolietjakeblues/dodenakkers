#!/usr/bin/env python3
"""
Build the base cemetery dataset from the normalized CSV.

Main geometry: cemetery terrain.
Entrance: preserved as a Point in properties, never as a derived centroid.
Measurements: calculated in EPSG:28992 (RD New).

Matching strategy (docs/data/003-csv-bron-en-koppeling.md):
  1. exact match on normalized (naam, plaats) -- case/whitespace-insensitive;
  2. for the rest: nearest not-yet-claimed ingang within a distance threshold;
  3. an ingang claimed by more than one terrain is a genuine shared entrance
     (documented exception, e.g. Duinrust in Katwijk aan Zee) -- the closest
     terrain gets "spatial_name_variant", the others "shared_entrance_spatial",
     and ingang_gedeeld=True on all of them;
  4. a terrain with no ingang within the threshold keeps ingang=null
     (documented exception, e.g. Oudenhoorn) -- never invent one.

This script intentionally does not silently resolve geruimd status
conflicts between terrain and ingang: it reports geruimd=null,
status_conflict=True and keeps both source values.

Asserts against the known invariants in docs/data/kml-audit-resultaten.md
so a change in the source data fails loudly instead of silently drifting.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd
from pyproj import Transformer
from shapely import wkt as shapely_wkt
from shapely.geometry import mapping
from shapely.ops import transform

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_CSV = REPO_ROOT / "data" / "Begraafplaatsen Zuid-Holland- Zuid-Holland.csv"
SOURCE_FILE_NAME = SOURCE_CSV.name
OUTPUT_DIR = REPO_ROOT / "data" / "generated"
AUDIT_PATH = REPO_ROOT / "docs" / "data" / "kml-audit-resultaten.md"

# Comfortably above the largest observed legitimate spatial match (~217m,
# "Gem. begraafplaats De Essenhof" <-> "Gemeentelijke begraafplaats De
# Essenhof", Dordrecht) and comfortably below the one real gap (~19km,
# Oudenhoorn's nearest leftover ingang belongs to an unrelated village).
SPATIAL_MATCH_THRESHOLD_M = 500

# Zuid-Holland plausibility bbox (WGS84), generous buffer around the
# province -- an audit signal, not a hard province-boundary check.
PLAUSIBLE_BBOX = {"min_lon": 3.5, "max_lon": 5.5, "min_lat": 51.4, "max_lat": 52.6}

to_rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True).transform


def clean(value):
    """pandas NaN -> None. json.dumps would otherwise emit the invalid
    JSON token NaN for a missing plaats value (e.g. zh-0088, "RK
    begraafplaats Schiedam" has no plaats (opgeschoon) in the source)."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return value


def normalize(value) -> str:
    """Case/whitespace-insensitive key for name matching. Never used for
    display -- the raw value is always kept separately for provenance."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return " ".join(str(value).strip().lower().split())


def load_source() -> pd.DataFrame:
    df = pd.read_csv(SOURCE_CSV, encoding="utf-8-sig")
    # 924 -> 884 op 2026-08-19: 20 begraafplaatsen in Vijfheerenlanden-dorpen
    # (Tienhoven, Ameide, Lexmond, Hei en Boeicop, Schoonrewoerd, Leerbroek,
    # Kedichem, Leerdam, Oosterwijk, Nieuwland, Meerkerk) verwijderd -- die
    # gemeente ging in 2019 van Zuid-Holland naar Utrecht. Leon had dit al
    # in een oude Excel gecorrigeerd, maar niet in de KML/CSV die deze build
    # leest. Zie scripts/fix_vijfheerenlanden.py (eenmalig gedraaid) en
    # docs/data/003-csv-bron-en-koppeling.md.
    # 884 -> 890 op 2026-08-23: 3 begraafplaatsen (Nieuwe Joodse begraafplaats
    # Schiedam, Grafmonument juffrouw Begeer Voorschoten, NH Kerkhof
    # Oud-Alblas) toegevoegd uit Leons "Tijdelijk Zuid-Holland.kmz". Zie
    # scripts/add_tijdelijk_zuidholland_kmz.py (eenmalig gedraaid) en
    # docs/data/003-csv-bron-en-koppeling.md.
    # 890 -> 891 op 2026-08-23: 1 nieuwe ingang toegevoegd voor Oudenhoorn
    # (eerst voor Gem. begraafplaats, later diezelfde dag door Leon
    # omgedraaid naar NH Kerkhof -- zie scripts/fix_oudenhoorn_ingang.py en
    # scripts/fix_oudenhoorn_reversed.py, beide eenmalig gedraaid, en
    # docs/data/003-csv-bron-en-koppeling.md. Rijenaantal blijft 891: de
    # omdraaiing hernoemt/herlabelt bestaande rijen, voegt er geen toe.
    assert len(df) == 891, f"bronrecords: verwacht 891, gevonden {len(df)}"
    return df.reset_index().rename(columns={"index": "orig_idx"})


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["geom"] = df["WKT"].apply(shapely_wkt.loads)
    df["geom_rd"] = df["geom"].apply(lambda g: transform(to_rd, g))
    df["geruimd_bron"] = df["geruimd"] == "geruimd"
    df["nkey"] = df["naam"].apply(normalize)
    df["pkey"] = df["plaats (opgeschoon)"].apply(normalize)
    return df


def match_terrein_ingang(terrein: pd.DataFrame, ingang: pd.DataFrame) -> list[dict]:
    assert terrein.groupby(["nkey", "pkey"]).size().max() == 1, "dubbele terrein naam+plaats-sleutel"
    assert ingang.groupby(["nkey", "pkey"]).size().max() == 1, "dubbele ingang naam+plaats-sleutel"

    ingang_by_key = {(r.nkey, r.pkey): i for i, r in ingang.iterrows()}

    matches: list[dict] = []
    matched_ingang_idx: set[int] = set()

    # Tier 1: exact genormaliseerde naam + opgeschoonde plaats.
    for ti, trow in terrein.iterrows():
        ii = ingang_by_key.get((trow.nkey, trow.pkey))
        if ii is not None:
            matches.append({"terrein_idx": ti, "ingang_idx": ii, "koppelwijze": "exact_name_place"})
            matched_ingang_idx.add(ii)

    matched_terrein_idx = {m["terrein_idx"] for m in matches}
    remaining_terrein = [ti for ti in terrein.index if ti not in matched_terrein_idx]
    pool_idx = [ii for ii in ingang.index if ii not in matched_ingang_idx]

    # Tier 2: dichtstbijzijnde nog-niet-geclaimde ingang, binnen de drempel.
    # Elk terrein zoekt onafhankelijk in dezelfde pool (geen greedy-verwijdering
    # vooraf) zodat een genuine gedeelde ingang correct als zodanig naar voren
    # komt in plaats van afhankelijk te zijn van verwerkingsvolgorde.
    tier2: dict[int, tuple[int, float]] = {}
    for ti in remaining_terrein:
        centroid = terrein.loc[ti, "geom_rd"].centroid
        best_ii, best_dist = None, None
        for ii in pool_idx:
            d = centroid.distance(ingang.loc[ii, "geom_rd"])
            if best_dist is None or d < best_dist:
                best_ii, best_dist = ii, d
        if best_dist is not None and best_dist <= SPATIAL_MATCH_THRESHOLD_M:
            tier2[ti] = (best_ii, best_dist)

    by_ingang: dict[int, list[int]] = {}
    for ti, (ii, _dist) in tier2.items():
        by_ingang.setdefault(ii, []).append(ti)
    shared_ingang_idx = {ii for ii, claimants in by_ingang.items() if len(claimants) > 1}

    for ti, (ii, _dist) in tier2.items():
        if ii in shared_ingang_idx:
            closest = min(by_ingang[ii], key=lambda t: tier2[t][1])
            koppelwijze = "spatial_name_variant" if ti == closest else "shared_entrance_spatial"
        else:
            koppelwijze = "spatial_name_variant"
        matches.append({"terrein_idx": ti, "ingang_idx": ii, "koppelwijze": koppelwijze})

    matched_terrein_idx = {m["terrein_idx"] for m in matches}
    for ti in terrein.index:
        if ti not in matched_terrein_idx:
            matches.append({"terrein_idx": ti, "ingang_idx": None, "koppelwijze": "missing"})

    assert len(matches) == len(terrein), f"matches: verwacht {len(terrein)}, gevonden {len(matches)}"
    counts = Counter(m["koppelwijze"] for m in matches)
    # 433 -> 434 op 2026-08-23: na Leons omdraaiing (scripts/fix_oudenhoorn_
    # reversed.py) heeft zowel NH Kerkhof als Gem. begraafplaats, Oudenhoorn
    # weer precies 1 eigen ingang (voorheen had één van de twee er geen).
    # Zie docs/data/003-csv-bron-en-koppeling.md.
    assert counts["exact_name_place"] == 434, counts
    assert counts["spatial_name_variant"] == 11, counts
    assert counts["shared_entrance_spatial"] == 1, counts
    assert counts["missing"] == 0, counts

    matches.sort(key=lambda m: m["terrein_idx"])
    return matches, shared_ingang_idx


def build_record(seq: int, match: dict, terrein: pd.DataFrame, ingang: pd.DataFrame, shared_ingang_idx: set[int]) -> dict:
    fid = f"zh-{seq:04d}"
    trow = terrein.loc[match["terrein_idx"]]
    geom_wgs84 = trow["geom"]
    geom_rd = trow["geom_rd"]

    assert not geom_wgs84.is_empty, f"{fid}: lege terreingeometrie"
    b = geom_wgs84.bounds
    assert (
        PLAUSIBLE_BBOX["min_lon"] <= b[0] <= PLAUSIBLE_BBOX["max_lon"]
        and PLAUSIBLE_BBOX["min_lat"] <= b[1] <= PLAUSIBLE_BBOX["max_lat"]
    ), f"{fid}: geometrie buiten plausibele Zuid-Holland-bbox: {b}"

    area_m2 = round(geom_rd.area, 2)
    area_ha = round(area_m2 / 10000, 4)
    perimeter_m = round(geom_rd.length, 2)
    assert area_m2 > 0, f"{fid}: oppervlakte <= 0"
    assert perimeter_m > 0, f"{fid}: omtrek <= 0"

    ii = match["ingang_idx"]
    geruimd_bron_terrein = bool(trow["geruimd_bron"])

    if ii is None:
        ingang_point = None
        ingang_lon = ingang_lat = None
        ingang_afstand = None
        geruimd_bron_ingang = None
        naam_bron_ingang = None
        bron_rij_ingang = None
        ingang_gedeeld = False
        geruimd = geruimd_bron_terrein
        status_conflict = False
    else:
        irow = ingang.loc[ii]
        assert irow["geom"].geom_type == "Point", f"{fid}: ingang is geen Point"
        ingang_point = irow["geom"]
        ingang_lon, ingang_lat = ingang_point.x, ingang_point.y
        ingang_afstand = round(geom_rd.distance(irow["geom_rd"]), 2)
        geruimd_bron_ingang = bool(irow["geruimd_bron"])
        naam_bron_ingang = irow["naam"]
        bron_rij_ingang = int(irow["orig_idx"]) + 2  # +1 kopregel, +1 1-indexering
        ingang_gedeeld = ii in shared_ingang_idx
        if geruimd_bron_terrein == geruimd_bron_ingang:
            geruimd = geruimd_bron_terrein
            status_conflict = False
        else:
            geruimd = None
            status_conflict = True

    props = {
        "id": fid,
        "naam": trow["naam"],
        "plaats_origineel": clean(trow["plaats (origineel)"]),
        "plaats": clean(trow["plaats (opgeschoon)"]),
        "geruimd": geruimd,
        "geruimd_bron_terrein": geruimd_bron_terrein,
        "geruimd_bron_ingang": geruimd_bron_ingang,
        "status_conflict": status_conflict,
        "oppervlakte_m2": area_m2,
        "oppervlakte_ha": area_ha,
        "omtrek_m": perimeter_m,
        "ingang": mapping(ingang_point) if ingang_point is not None else None,
        "ingang_lon": ingang_lon,
        "ingang_lat": ingang_lat,
        "ingang_koppelwijze": match["koppelwijze"],
        "ingang_afstand_tot_terrein_m": ingang_afstand,
        "ingang_gedeeld": ingang_gedeeld,
        "naam_bron_terrein": trow["naam"],
        "naam_bron_ingang": naam_bron_ingang,
        "bron_rij_terrein": int(trow["orig_idx"]) + 2,
        "bron_rij_ingang": bron_rij_ingang,
        "bron": "Begraafplaatsen Zuid-Holland",
        "source_file": SOURCE_FILE_NAME,
    }
    return {
        "type": "Feature",
        "properties": props,
        "geometry": mapping(geom_wgs84),
        "_wkt_terrein": trow["WKT"],
        "_wkt_ingang": ingang.loc[ii, "WKT"] if ii is not None else None,
    }


def write_geojson(features: list[dict]) -> None:
    fc = {
        "type": "FeatureCollection",
        "name": "begraafplaatsen_zuid_holland",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": [
            {"type": "Feature", "properties": f["properties"], "geometry": f["geometry"]} for f in features
        ],
    }
    path = OUTPUT_DIR / "begraafplaatsen.geojson"
    path.write_text(json.dumps(fc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(features)} begraafplaatsen -> {path}")


def write_csv(features: list[dict]) -> None:
    import csv

    fieldnames = [
        "id", "naam", "plaats_origineel", "plaats", "geruimd", "geruimd_bron_terrein",
        "geruimd_bron_ingang", "status_conflict", "oppervlakte_m2", "oppervlakte_ha", "omtrek_m",
        "ingang_lon", "ingang_lat", "ingang_koppelwijze", "ingang_afstand_tot_terrein_m",
        "ingang_gedeeld", "naam_bron_terrein", "naam_bron_ingang", "bron_rij_terrein",
        "bron_rij_ingang", "bron", "source_file", "terrein_wkt", "ingang_wkt",
    ]
    path = OUTPUT_DIR / "begraafplaatsen.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for feat in features:
            row = dict(feat["properties"])
            row.pop("ingang", None)
            row["terrein_wkt"] = feat["_wkt_terrein"]
            row["ingang_wkt"] = feat["_wkt_ingang"]
            writer.writerow(row)
    print(f"{len(features)} begraafplaatsen -> {path}")


def write_audit(features: list[dict], terrein: pd.DataFrame, ingang: pd.DataFrame) -> None:
    method_counts = Counter(f["properties"]["ingang_koppelwijze"] for f in features)
    conflicts = [f for f in features if f["properties"]["status_conflict"]]
    missing = [f for f in features if f["properties"]["ingang_koppelwijze"] == "missing"]
    shared = [f for f in features if f["properties"]["ingang_gedeeld"]]
    geruimd_bron_count = int((terrein["geruimd_bron"]).sum() + (ingang["geruimd_bron"]).sum())
    n_geometrycollection = sum(1 for f in features if f["geometry"]["type"] == "GeometryCollection")
    n_polygon = len(features) - n_geometrycollection

    areas = [f["properties"]["oppervlakte_m2"] for f in features]
    perimeters = [f["properties"]["omtrek_m"] for f in features]

    lines = [
        "# Data: auditresultaten basisdataset",
        "",
        "*Gegenereerd door `scripts/build_base_dataset.py` -- niet handmatig bewerken.*",
        "",
        "## Samenvatting",
        "",
        f"De genormaliseerde CSV bevat **{len(terrein) + len(ingang)} bronrecords**:",
        "",
        f"- **{len(terrein)}** begraafplaatsterreinen;",
        f"- **{len(ingang)}** ingangen;",
        f"- **{n_polygon}** terreinpolygonen;",
        f"- **{n_geometrycollection}** terreinrecord met een `GeometryCollection`;",
        f"- **{geruimd_bron_count}** bronrecords met status `geruimd`.",
        "",
        f"De basisdataset bevat **{len(features)} begraafplaatsrecords**, één record per terrein.",
        "",
        "## Koppeling terrein en ingang",
        "",
        "Koppeling is uitgevoerd met behoud van de bronwaarden.",
        "",
        "| Koppelwijze | Terreinen |",
        "|---|---:|",
        f"| Exacte genormaliseerde naam + opgeschoonde plaats | {method_counts['exact_name_place']} |",
        f"| Ruimtelijke koppeling bij naamvariant | {method_counts['spatial_name_variant']} |",
        f"| Gedeelde ingang, ruimtelijk gekoppeld | {method_counts['shared_entrance_spatial']} |",
        f"| Geen ingang gevonden | {method_counts['missing']} |",
        "",
        "### Gedeelde ingang",
        "",
    ]
    for f in shared:
        p = f["properties"]
        lines.append(f"- `{p['id']}` {p['naam']} ({p['plaats']}), koppelwijze `{p['ingang_koppelwijze']}`")
    lines += ["", "### Ontbrekende ingang", ""]
    for f in missing:
        p = f["properties"]
        lines.append(f"- `{p['id']}`: {p['naam']}, {p['plaats']}")
    lines += [
        "",
        "## Statusconflicten",
        "",
        f"Er zijn **{len(conflicts)}** gevallen waarin terrein en ingang een verschillende bronwaarde",
        "voor `geruimd` hebben.",
        "",
        "In deze gevallen krijgt het afgeleide veld `geruimd` voorlopig `null` en `status_conflict = true`.",
        "",
    ]
    for f in conflicts:
        p = f["properties"]
        lines.append(
            f"- {p['naam']}, {p['plaats']}: terrein = `{p['geruimd_bron_terrein']}`, "
            f"ingang = `{p['geruimd_bron_ingang']}`"
        )
    lines += [
        "",
        "## Oppervlakte en omtrek",
        "",
        "Oppervlakte en omtrek zijn berekend na transformatie van WGS84 naar RD New (`EPSG:28992`).",
        "",
        f"- kleinste oppervlakte: **{min(areas):.2f} m²**;",
        f"- mediaan oppervlakte: **{sorted(areas)[len(areas) // 2]:,.2f} m²**;",
        f"- grootste oppervlakte: **{max(areas):,.2f} m²**;",
        f"- kleinste omtrek: **{min(perimeters):.2f} m**;",
        f"- mediaan omtrek: **{sorted(perimeters)[len(perimeters) // 2]:,.2f} m**;",
        f"- grootste omtrek: **{max(perimeters):,.2f} m**.",
        "",
        "Deze extremen zijn signalen voor controle en niet automatisch fouten.",
        "",
        "## Gegenereerde bestanden",
        "",
        "- `data/generated/begraafplaatsen.geojson`",
        "- `data/generated/begraafplaatsen.csv`",
        "",
        "De GeoJSON gebruikt het **terrein als feature geometry**. De ingang wordt daarnaast als "
        "Point-object in `properties.ingang` bewaard. Hierdoor blijft de terreinpolygoon direct "
        "bruikbaar voor kaartweergave en ruimtelijke analyse, zonder de betekenis van de ingang te verliezen.",
    ]
    AUDIT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"audit herschreven -> {AUDIT_PATH}")


def main() -> None:
    df = load_source()
    terrein = prepare(df[df["begraafplaats"] == "begraafplaats"])
    ingang = prepare(df[df["ingang"] == "ingang"])
    assert len(terrein) == 446, f"terreinen: verwacht 446, gevonden {len(terrein)}"
    assert len(ingang) == 445, f"ingangen: verwacht 445, gevonden {len(ingang)}"

    matches, shared_ingang_idx = match_terrein_ingang(terrein, ingang)

    features = [
        build_record(seq, m, terrein, ingang, shared_ingang_idx) for seq, m in enumerate(matches, start=1)
    ]

    conflicts = sum(1 for f in features if f["properties"]["status_conflict"])
    # De 4 conflicten (Oude Wetering RK, Schoonhoven, Zwammerdam, Maasland)
    # zijn op 2026-08-20 door Leon bevestigd als geruimd en opgelost in de
    # bron via scripts/fix_statusconflicten.py -- zie
    # docs/data/003-csv-bron-en-koppeling.md.
    assert conflicts == 0, f"statusconflicten: verwacht 0, gevonden {conflicts}"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_geojson(features)
    write_csv(features)
    write_audit(features, terrein, ingang)


if __name__ == "__main__":
    main()
