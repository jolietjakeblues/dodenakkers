#!/usr/bin/env python3
"""
Compute a set of aggregate statistics/overviews from the begraafplaatsen
dataset + RCE-extracten, for a standalone statistiekenpagina (wens van
Joop, 2026-08-26: "zoveel mogelijk overzichten, tabellen enzo... meeste
kerkhoven liggen bij een molen, etc").

Input:
  data/generated/analyse.geojson
  data/rce/rijksmonumenten.geojson

Output:
  data/generated/statistieken.json

Alle metrische berekeningen (afstand) draaien in EPSG:28992 (RD New), net
als scripts/analyse_spatial.py -- nooit in WGS84-graden.

De bron zelf heeft geen "gemeente"-veld, alleen "plaats" (dorp/stad) -- dat
is niet hetzelfde na een herindeling (meerdere plaatsen kunnen bij één
gemeente horen, en een plaatsnaam kan bij een andere gemeente horen dan
zijn eigen naam doet vermoeden, bv. Oudenhoorn -> Voorne aan Zee). Sinds
2026-08-27 (wens van Joop) voegt scripts/analyse_spatial.py een echt
`gemeente`-veld toe via een spatial join tegen
data/pdok/gemeenten-zuid-holland.geojson (scripts/fetch_gemeentegrenzen.py),
dus dit script levert tabellen zowel per plaats als per gemeente.

Run bij elke build, na scripts/analyse_spatial.py. Alleen lezen + 1
outputbestand wegschrijven, idempotent.
"""
from __future__ import annotations

import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform
from shapely.strtree import STRtree

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = REPO_ROOT / "data" / "generated"
RCE_DIR = REPO_ROOT / "data" / "rce"
OUT_PATH = GENERATED_DIR / "statistieken.json"

to_rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True).transform

# Functiecategorieen (RCE oorspronkelijke_functie_kort) voor de aparte
# "nabijheid tot landmark X"-tabellen. Woningen van de beheerder/molenaar
# bewust uitgesloten -- dat is niet de molen/het kasteel zelf.
MOLEN_FUNCTIES = {
    "Molen", "Industrie- en poldermolen", "Korenmolen",
    "Ondermolen", "Bovenmolen", "Boezemmolen",
}
KASTEEL_FUNCTIES = {"Kasteel, buitenplaats"}
KERK_FUNCTIES = {"Kerk", "Kerk en kerkonderdeel"}
# Voor de "begraafplaats is zelf een rijksmonument"-tabel: functies die een
# begraafplaats of een integraal onderdeel ervan aanduiden.
BEGRAAFPLAATS_FUNCTIES = {
    "Begraafplaats", "Begraafplaats en -onderdelen", "Begraafplaatshek",
    "Begraafplaatsaula", "Dierenbegraafplaats",
}

# Denominatie (2026-08-27, wens van Joop: "per denominatie in de statistiek
# (indien bekend)") -- de bron heeft geen apart denominatie-veld, dus dit is
# een regex-classificatie op `naam` (geen ander betrouwbaar signaal
# beschikbaar). Prioriteit maakt niet uit: geverifieerd dat geen enkele naam
# in de dataset op 2+ patronen tegelijk matcht. Namen zonder duidelijke
# denominatie (bv. "Gem. begraafplaats", "Algemene begraafplaats") vallen in
# "Onbekend/algemeen" -- vaak zijn dat juist gemeentelijke/algemene
# begraafplaatsen voor alle gezindten, geen ontbrekend gegeven.
DENOMINATIE_PATTERNS = [
    ("Rooms-Katholiek", r"\bR\.?\s?K\.?\b|Rooms[- ]Katholiek|Katholiek"),
    ("Nederlands Hervormd", r"\bN\.?\s?H\.?\b|Hervormd"),
    ("Gereformeerd", r"Gereformeerd|\bGeref\."),
    ("Joods", r"Joods|Joodse|Isra[eë]litisch"),
    ("Doopsgezind", r"Doopsgezind"),
    ("Evangelisch-Luthers", r"Evangelisch[- ]?Lutherse?|\bLuthers"),
    ("Remonstrants", r"Remonstrant"),
]


def classify_denominatie(naam: str) -> str:
    for label, pattern in DENOMINATIE_PATTERNS:
        if re.search(pattern, naam, re.IGNORECASE):
            return label
    return "Onbekend/algemeen"


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)["features"]


def terrain_rd_geom(feature: dict):
    return transform(to_rd, shape(feature["geometry"]))


def monument_point_rd(feature: dict):
    geom = shape(feature["geometry"])
    if geom.geom_type != "Point":
        geom = geom.centroid
    return transform(to_rd, geom)


def nabijheid_tot_categorie(begraafplaatsen: list[dict], terrain_geoms: list, rijksmonumenten: list[dict], functies: set[str], thresholds=(25, 50, 100)) -> dict | None:
    """Voor elke begraafplaats de afstand tot het dichtstbijzijnde
    rijksmonument in `functies`, ongeacht de 250m-grens van de al
    opgeslagen rijksmonument_relations (die dekt dit niet voor bv. een
    molen op 600m die nog steeds relevant/zichtbaar is). Drempels op
    25/50/100m (2026-08-27, wens van Joop: "> 100 is niet interessant
    genoeg") -- de eerdere 250/500/1000m-drempels zaten te ruim voor een
    zinvolle "dichtbij"-vraag."""
    cat_feats = [f for f in rijksmonumenten if f["properties"].get("oorspronkelijke_functie_kort") in functies]
    if not cat_feats:
        return None
    cat_geoms = [monument_point_rd(f) for f in cat_feats]
    tree = STRtree(cat_geoms)
    rows = []
    for f, terrain_rd in zip(begraafplaatsen, terrain_geoms):
        i = tree.nearest(terrain_rd)
        rows.append({
            "naam": f["properties"]["naam"],
            "plaats": f["properties"]["plaats"],
            "monument_naam": cat_feats[i]["properties"].get("naam"),
            "distance_m": round(terrain_rd.distance(cat_geoms[i]), 1),
        })
    rows.sort(key=lambda r: r["distance_m"])
    return {
        "aantal_in_categorie": len(cat_feats),
        "binnen": {str(t): sum(1 for r in rows if r["distance_m"] <= t) for t in thresholds},
        "dichtstbij": rows[:10],
        "verste": rows[-1],
    }


def main() -> None:
    begraafplaatsen = load(GENERATED_DIR / "analyse.geojson")
    rijksmonumenten = load(RCE_DIR / "rijksmonumenten.geojson")
    terrain_geoms = [terrain_rd_geom(f) for f in begraafplaatsen]

    functie_by_nummer = {
        f["properties"]["rijksmonumentnummer"]: f["properties"].get("oorspronkelijke_functie_kort")
        for f in rijksmonumenten
    }

    # --- Basisstatistieken ---
    n = len(begraafplaatsen)
    areas = [f["properties"]["oppervlakte_m2"] for f in begraafplaatsen]
    geruimd = [f for f in begraafplaatsen if f["properties"]["geruimd"] is True]
    niet_geruimd = [f for f in begraafplaatsen if f["properties"]["geruimd"] is False]
    conflict = [f for f in begraafplaatsen if f["properties"].get("status_conflict")]
    largest = max(begraafplaatsen, key=lambda f: f["properties"]["oppervlakte_m2"])
    smallest = min(begraafplaatsen, key=lambda f: f["properties"]["oppervlakte_m2"])
    basis = {
        "totaal": n,
        "totaal_ha": round(sum(areas) / 10000, 1),
        "niet_geruimd": len(niet_geruimd),
        "geruimd": len(geruimd),
        "geruimd_pct": round(100 * len(geruimd) / n, 1),
        "statusconflict": len(conflict),
        "gemiddelde_m2": round(statistics.mean(areas), 1),
        "mediaan_m2": round(statistics.median(areas), 1),
        "grootste": {
            "naam": largest["properties"]["naam"], "plaats": largest["properties"]["plaats"],
            "m2": largest["properties"]["oppervlakte_m2"], "ha": largest["properties"]["oppervlakte_ha"],
        },
        "kleinste": {
            "naam": smallest["properties"]["naam"], "plaats": smallest["properties"]["plaats"],
            "m2": smallest["properties"]["oppervlakte_m2"],
        },
    }

    # --- Per plaats / per gemeente (zelfde rijvorm, dus 1 helper) ---
    def group_rows(group_key: str) -> dict:
        by_group = defaultdict(list)
        for f in begraafplaatsen:
            by_group[f["properties"][group_key]].append(f["properties"])
        rows = []
        for value, feats in by_group.items():
            g = sum(1 for p in feats if p["geruimd"] is True)
            rows.append({
                group_key: value,
                "aantal": len(feats),
                "geruimd": g,
                "totaal_m2": round(sum(p["oppervlakte_m2"] for p in feats), 0),
            })
        return {
            "meeste_begraafplaatsen": sorted(rows, key=lambda r: -r["aantal"])[:10],
            "meeste_geruimd": sorted(rows, key=lambda r: (-r["geruimd"], -r["aantal"]))[:10],
            "volledig_geruimd": sorted(
                [r for r in rows if r["aantal"] >= 2 and r["geruimd"] == r["aantal"]],
                key=lambda r: -r["aantal"],
            ),
            "grootste_totale_oppervlakte": sorted(rows, key=lambda r: -r["totaal_m2"])[:10],
        }

    per_plaats = group_rows("plaats")
    per_gemeente = group_rows("gemeente")

    # --- Beschermd gezicht ---
    in_gezicht = [f for f in begraafplaatsen if f["properties"]["in_beschermd_gezicht"] != "none"]
    top_plaats_gezicht = [
        {"plaats": p, "aantal": c} for p, c in Counter(f["properties"]["plaats"] for f in in_gezicht).most_common(10)
    ]
    top_gemeente_gezicht = [
        {"gemeente": g, "aantal": c} for g, c in Counter(f["properties"]["gemeente"] for f in in_gezicht).most_common(10)
    ]
    beschermd_gezicht = {
        "totaal": len(in_gezicht),
        "pct": round(100 * len(in_gezicht) / n, 1),
        "top_plaatsen": top_plaats_gezicht,
        "top_gemeenten": top_gemeente_gezicht,
    }

    # --- Rijksmonumenten nabijheid (bestaande relaties, tot 250m bewaard) ---
    def rm_count_100m(props):
        return len([r for r in props["rijksmonument_relations"] if r["distance_m"] <= 100])

    ranked_rm = sorted(begraafplaatsen, key=lambda f: -rm_count_100m(f["properties"]))[:10]
    functie_counter = Counter()
    for f in begraafplaatsen:
        for r in f["properties"]["rijksmonument_relations"]:
            if r["distance_m"] > 100:
                continue
            functie = functie_by_nummer.get(r["rijksmonumentnummer"])
            if functie:
                functie_counter[functie] += 1
    rijksmonumenten_stats = {
        "gemiddeld_binnen_100m": round(statistics.mean(rm_count_100m(f["properties"]) for f in begraafplaatsen), 2),
        "meeste_binnen_100m": [
            {"naam": f["properties"]["naam"], "plaats": f["properties"]["plaats"], "aantal_100m": rm_count_100m(f["properties"])}
            for f in ranked_rm
        ],
        "zonder_rijksmonument_binnen_250m": sum(1 for f in begraafplaatsen if not f["properties"]["rijksmonument_relations"]),
        "top_functies_nabij_100m": [{"functie": k, "aantal": v} for k, v in functie_counter.most_common(10)],
    }

    # --- Begraafplaats is zelf een rijksmonument ---
    zelf_rijksmonument = {}
    for f in begraafplaatsen:
        p = f["properties"]
        for r in p["rijksmonument_relations"]:
            if r["relation"] not in ("inside_on_site", "touches"):
                continue
            functie = functie_by_nummer.get(r["rijksmonumentnummer"])
            if functie in BEGRAAFPLAATS_FUNCTIES:
                key = (p["naam"], p["plaats"])
                zelf_rijksmonument[key] = functie
    begraafplaats_als_rijksmonument = {
        "aantal": len(zelf_rijksmonument),
        "lijst": [{"naam": k[0], "plaats": k[1], "functie": v} for k, v in sorted(zelf_rijksmonument.items())],
    }

    # --- Nabijheid tot molen / kasteel / kerk (eigen berekening, los van de
    # 100/250m-grenzen van rijksmonument_relations) ---
    molen = nabijheid_tot_categorie(begraafplaatsen, terrain_geoms, rijksmonumenten, MOLEN_FUNCTIES)
    kasteel = nabijheid_tot_categorie(begraafplaatsen, terrain_geoms, rijksmonumenten, KASTEEL_FUNCTIES)
    kerk = nabijheid_tot_categorie(begraafplaatsen, terrain_geoms, rijksmonumenten, KERK_FUNCTIES)

    # --- Denominatie (regex op naam, zie DENOMINATIE_PATTERNS hierboven) ---
    denominatie_counts = Counter(classify_denominatie(f["properties"]["naam"]) for f in begraafplaatsen)
    denominatie = {
        "verdeling": [{"denominatie": k, "aantal": v} for k, v in denominatie_counts.most_common()],
    }

    # --- Archeologie ---
    nearest_arch = sorted(
        (f for f in begraafplaatsen if f["properties"].get("archeologische_rm_nearest")),
        key=lambda f: f["properties"]["archeologische_rm_nearest"]["distance_m"],
    )[:5]
    archeologie = {
        "overlapt_aantal": sum(1 for f in begraafplaatsen if f["properties"]["archeologische_rm_count"] > 0),
        "dichtstbij": [
            {
                "naam": f["properties"]["naam"], "plaats": f["properties"]["plaats"],
                "distance_m": f["properties"]["archeologische_rm_nearest"]["distance_m"],
            }
            for f in nearest_arch
        ],
    }

    # --- Ingangen ---
    afstanden = [
        f["properties"]["ingang_afstand_tot_terrein_m"] for f in begraafplaatsen
        if f["properties"].get("ingang_afstand_tot_terrein_m") is not None
    ]
    verste_ingang = max(
        begraafplaatsen, key=lambda f: f["properties"].get("ingang_afstand_tot_terrein_m") or 0
    )
    ingangen = {
        "gedeeld_aantal": sum(1 for f in begraafplaatsen if f["properties"].get("ingang_gedeeld")),
        "gemiddelde_afstand_m": round(statistics.mean(afstanden), 1) if afstanden else None,
        "verste": {
            "naam": verste_ingang["properties"]["naam"],
            "plaats": verste_ingang["properties"]["plaats"],
            "afstand_m": verste_ingang["properties"].get("ingang_afstand_tot_terrein_m"),
        },
    }

    stats = {
        "basis": basis,
        "per_plaats": per_plaats,
        "per_gemeente": per_gemeente,
        "beschermd_gezicht": beschermd_gezicht,
        "rijksmonumenten": rijksmonumenten_stats,
        "begraafplaats_als_rijksmonument": begraafplaats_als_rijksmonument,
        "denominatie": denominatie,
        "molen": molen,
        "kasteel": kasteel,
        "kerk": kerk,
        "archeologie": archeologie,
        "ingangen": ingangen,
    }

    OUT_PATH.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"statistieken geschreven -> {OUT_PATH}")
    print(f"  {basis['totaal']} begraafplaatsen, {begraafplaats_als_rijksmonument['aantal']} zelf rijksmonument, "
          f"{molen['binnen']['100']} binnen 100m van een molen, {kerk['binnen']['100']} binnen 100m van een kerk")


if __name__ == "__main__":
    main()
