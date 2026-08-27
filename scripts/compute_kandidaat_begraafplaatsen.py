#!/usr/bin/env python3
"""
EXPERIMENTEEL. Zoekt in de omschrijvingen van archeologische
onderzoeksgebieden (data/rce/archeologische-onderzoeksgebieden.geojson,
22.254 rapporten) naar tekstuele aanwijzingen voor begravingen, en meet de
afstand tot de dichtstbijzijnde al bekende begraafplaats -- als hulpmiddel
om kandidaat-locaties te vinden die mogelijk nog ontbreken in de
hoofddataset (wens van Joop, 2026-08-27: "waar zou je een begraafplaats
verwachten").

Dit is GEEN verificatie en GEEN claim dat er een begraafplaats is. Het is
een woordenboek-achtige tekstzoekactie op archeologische bureau-/
veldonderzoeksrapporten, die vaak schrijven over wat er "verwacht" of
"mogelijk" aanwezig is, niet alleen over bevestigde vondsten. Elke
kandidaat moet door een mens (Leon) beoordeeld worden tegen de brontekst
zelf (via monumentenregister_url/cho_uri) voordat er iets aan de
hoofddataset wordt toegevoegd.

Zoektermen bewust beperkt tot ondubbelzinnige zelfstandige naamwoorden.
"graven"/"begraven"/"begraving" zijn expres UITGESLOTEN: "graven" betekent
in archeologische rapporten meestal "opgraven/boren" (bv. "proefsleuven
graven"), en "begraven bodem/A-horizont" is een geologische standaardterm
(begraven bodemlaag), geen menselijke begraving. Beide bleken bij
handmatige steekproef overwegend fout-positief.

"beenderen" is om dezelfde reden UITGESLOTEN: in de dataset (22.254
rapporten) komt de term maar 2x voor, waarvan 1x "de beenderen van een
onvolgroeid rund" (dierlijk, geen mens) en 1x "menselijke botten" die
via "begraafplaats" al apart wordt gevonden. Netto voegde "beenderen"
dus alleen een fout-positief toe en geen enkele nieuwe echte treffer.

Naast de tekstzoekactie op archeologische rapporten bevat de output ook
twee kleinere signalen op basis van rijksmonumenten (data/rce/rijksmonumenten.geojson,
oorspronkelijke_functie_kort): kloosters en synagoges. Zelfde bbox-fetch
kanttekening als bij de eerdere kerk-analyse (scripts/analyse_spatial.py) --
ook hier eerst filteren op de echte ZH-gemeentegrenzen. Complexen met
meerdere apart geregistreerde rijksmonumentnummers (bv. losse vleugels)
worden geclusterd binnen CLUSTER_AFSTAND_M om dubbele kandidaten voor
hetzelfde fysieke gebouw te voorkomen. Zie de losse waarschuwingsteksten
per categorie verderop in dit bestand voor waarom "afstand tot een
bekende begraafplaats" bij synagoges NIET hetzelfde betekent als bij
kloosters/kerken.

Output:
  data/generated/kandidaat_begraafplaatsen.json

Run los, niet als onderdeel van de reguliere build (experimenteel, geen
onderdeel van de "vertrouwde" statistieken).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import MultiPoint, shape
from shapely.ops import transform
from shapely.strtree import STRtree

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = REPO_ROOT / "data" / "generated"
RCE_DIR = REPO_ROOT / "data" / "rce"
PDOK_DIR = REPO_ROOT / "data" / "pdok"
OUT_PATH = GENERATED_DIR / "kandidaat_begraafplaatsen.json"

to_rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True).transform

# Ondubbelzinnige zelfstandige naamwoorden voor een begraving/grafveld. Zie
# de module-docstring voor waarom "graven"/"begraven" NIET meedoen.
GRAFTERM_PATTERN = re.compile(
    r"begraafplaats|kerkhof|grafveld|grafkuil|grafheuvel|skeletresten|"
    r"crematieresten|crematiegraf|inhumatiegraf|necropool|"
    r"grafmonument|dodenakker|urnenveld",
    re.IGNORECASE,
)

# Zeer ruwe zekerheidsindicator: staat er hedge-taal ("mogelijk", "zou",
# "verwacht", "(?)") in het fragment, dan is het waarschijnlijk een
# hypothese uit het bureauonderzoek, geen bevestigde vondst. Geen hedge-taal
# wil niet zeggen dat het zeker is -- alleen dat de tekst het niet als
# hypothese formuleert. Handmatige beoordeling blijft nodig; zie ook de
# bekende valkuil dat "Kerkhof" een achternaam van een onderzoeker kan zijn.
HEDGE_PATTERN = re.compile(r"\bzou\w*\b|\bkunnen\b|\bkan\b|mogelijk\w*|verwacht\w*|\(\?\)", re.IGNORECASE)

# Rijksmonumenten-signalen (aanvullend op de tekstzoekactie). Gezocht op
# oorspronkelijke_functie_kort, niet op naam -- die ontbreekt voor de
# meeste records (zie main()).
KLOOSTER_PATTERN = re.compile(r"klooster", re.IGNORECASE)
SYNAGOGE_PATTERN = re.compile(r"synagoge", re.IGNORECASE)

# Onderdelen van hetzelfde fysieke complex (bv. losse vleugels) staan vaak
# als aparte rijksmonumentnummers geregistreerd, vlak bij elkaar --
# samengevoegd tot 1 kandidaat om geen dubbele rijen voor hetzelfde gebouw
# te tonen.
CLUSTER_AFSTAND_M = 250

KLOOSTER_WAARSCHUWING = (
    "EXPERIMENTEEL. Kloosters (oorspronkelijke_functie_kort bevat 'klooster') "
    "uit de rijksmonumenten, gefilterd op echte Zuid-Holland-gemeentegrenzen "
    "(zelfde bbox-rand-effect als bij de kerk-analyse). Een grote afstand tot "
    "een bekende begraafplaats is GEEN bevestiging: veel kloosters zijn al "
    "tijdens/na de Reformatie (16e eeuw) opgeheven en gesloopt of herbestemd, "
    "een kloosterbegraafplaats kan eeuwen geleden spoorloos verdwenen zijn, "
    "of lag binnen het kloostercomplex zelf en is nooit apart geregistreerd. "
    "Puur een aanwijzing waar het de moeite waard is om te kijken."
)

SYNAGOGE_WAARSCHUWING = (
    "EXPERIMENTEEL. Synagoges (oorspronkelijke_functie_kort bevat 'synagoge') "
    "uit de rijksmonumenten, gefilterd op echte Zuid-Holland-gemeentegrenzen. "
    "LET OP, anders dan bij kerken/kloosters: een joodse begraafplaats hoort "
    "van oudsher juist NIET dicht bij de synagoge te liggen -- vaak bewust "
    "buiten de bebouwde kom, op een afgelegen plek (denk aan toponiemen als "
    "'Jodenberg(je)'). De afstand hieronder is dus geen signaal op zichzelf, "
    "alleen een startpunt: waar stond de synagoge, en is er apart archief- of "
    "toponiemenonderzoek nodig naar de bijbehorende begraafplaats elders? Met "
    "maar een handvol synagoges in Zuid-Holland is dit bovendien een heel "
    "kleine set, niet generaliseerbaar."
)


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)["features"]


def rijksmonument_kandidaten(
    rijksmonumenten: list[dict],
    pattern: re.Pattern,
    gem_tree: STRtree,
    gemeenten: list[dict],
    gem_geoms: list,
    bp_tree: STRtree,
    bp_geoms: list,
    begraafplaatsen: list[dict],
) -> tuple[list[dict], int]:
    items = []
    buiten_zh = 0
    for f in rijksmonumenten:
        functie = f["properties"].get("oorspronkelijke_functie_kort") or ""
        if not pattern.search(functie):
            continue
        geom = shape(f["geometry"])
        point = geom.centroid if geom.geom_type != "Point" else geom
        point_rd = transform(to_rd, point)
        gemeente = gemeente_for_point(point_rd, gem_tree, gemeenten, gem_geoms)
        if gemeente is None:
            buiten_zh += 1
            continue
        items.append({
            "point_rd": point_rd,
            "gemeente": gemeente,
            "naam": f["properties"].get("naam"),
            "rijksmonumentnummer": f["properties"].get("rijksmonumentnummer"),
            "monumentenregister_url": f["properties"].get("monumentenregister_url"),
            "lon": round(point.x, 6),
            "lat": round(point.y, 6),
        })

    # Greedy clustering: alles binnen CLUSTER_AFSTAND_M van het eerste
    # ongebruikte punt hoort bij hetzelfde complex.
    clusters: list[list[dict]] = []
    used = [False] * len(items)
    for i in range(len(items)):
        if used[i]:
            continue
        cluster = [items[i]]
        used[i] = True
        for j in range(i + 1, len(items)):
            if used[j]:
                continue
            if items[i]["point_rd"].distance(items[j]["point_rd"]) < CLUSTER_AFSTAND_M:
                cluster.append(items[j])
                used[j] = True
        clusters.append(cluster)

    results = []
    for cluster in clusters:
        named = [c["naam"] for c in cluster if c["naam"]]
        centroid_rd = MultiPoint([c["point_rd"] for c in cluster]).centroid
        i = bp_tree.nearest(centroid_rd)
        afstand = round(centroid_rd.distance(bp_geoms[i]), 1)
        url = next((c["monumentenregister_url"] for c in cluster if c["monumentenregister_url"]), None)
        results.append({
            "naam": named[0] if named else None,
            "gemeente": cluster[0]["gemeente"],
            "aantal_rijksmonumenten_in_cluster": len(cluster),
            "rijksmonumentnummers": [c["rijksmonumentnummer"] for c in cluster],
            "monumentenregister_url": url,
            "afstand_tot_bekende_bp_m": afstand,
            "dichtstbijzijnde_bp": f"{begraafplaatsen[i]['properties']['naam']}, {begraafplaatsen[i]['properties']['plaats']}",
            "lon": round(sum(c["lon"] for c in cluster) / len(cluster), 6),
            "lat": round(sum(c["lat"] for c in cluster) / len(cluster), 6),
        })

    results.sort(key=lambda r: -r["afstand_tot_bekende_bp_m"])
    return results, buiten_zh


def snippet(text: str, match: re.Match, context: int = 70) -> str:
    start = max(0, match.start() - context)
    end = min(len(text), match.end() + context)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"


def gemeente_for_point(pt, gem_tree: STRtree, gemeenten: list[dict], gem_geoms: list) -> str | None:
    for i in gem_tree.query(pt):
        if gem_geoms[i].contains(pt):
            return gemeenten[i]["properties"]["naam"]
    return None  # buiten Zuid-Holland (bbox-rand-effect, zie docs/README.md)


def main() -> None:
    onderzoeksgebieden = load(RCE_DIR / "archeologische-onderzoeksgebieden.geojson")
    rijksmonumenten = load(RCE_DIR / "rijksmonumenten.geojson")
    begraafplaatsen = load(GENERATED_DIR / "analyse.geojson")
    gemeenten = load(PDOK_DIR / "gemeenten-zuid-holland.geojson")

    bp_geoms = [transform(to_rd, shape(f["geometry"])) for f in begraafplaatsen]
    bp_tree = STRtree(bp_geoms)
    gem_geoms = [transform(to_rd, shape(f["geometry"])) for f in gemeenten]
    gem_tree = STRtree(gem_geoms)

    candidates = []
    buiten_zh = 0
    for f in onderzoeksgebieden:
        omschrijving = f["properties"].get("omschrijving") or ""
        match = GRAFTERM_PATTERN.search(omschrijving)
        if not match:
            continue

        geom = shape(f["geometry"])
        point_rd = transform(to_rd, geom.centroid if geom.geom_type != "Point" else geom)
        gemeente = gemeente_for_point(point_rd, gem_tree, gemeenten, gem_geoms)
        if gemeente is None:
            buiten_zh += 1
            continue

        i = bp_tree.nearest(point_rd)
        afstand = round(point_rd.distance(bp_geoms[i]), 1)

        centroid_wgs84 = geom.centroid if geom.geom_type != "Point" else geom
        fragment = snippet(omschrijving, match)
        candidates.append({
            "objectnummer": f["properties"].get("objectnummer"),
            "registratiedatum": f["properties"].get("registratiedatum"),
            "cho_uri": f["properties"].get("cho_uri"),
            "gemeente": gemeente,
            "gevonden_term": match.group(0),
            "fragment": fragment,
            "zekerheid": "onzeker/verwacht" if HEDGE_PATTERN.search(fragment) else "concreet genoemd",
            "afstand_tot_bekende_bp_m": afstand,
            "dichtstbijzijnde_bp": f"{begraafplaatsen[i]['properties']['naam']}, {begraafplaatsen[i]['properties']['plaats']}",
            "lon": round(centroid_wgs84.x, 6),
            "lat": round(centroid_wgs84.y, 6),
        })

    # Concreet genoemd eerst (sterkere kandidaten), dan op afstand -- ver
    # van een bekende begraafplaats en concreet genoemd is het interessantst.
    candidates.sort(key=lambda c: (c["zekerheid"] != "concreet genoemd", -c["afstand_tot_bekende_bp_m"]))

    kloosters, kloosters_buiten_zh = rijksmonument_kandidaten(
        rijksmonumenten, KLOOSTER_PATTERN, gem_tree, gemeenten, gem_geoms, bp_tree, bp_geoms, begraafplaatsen
    )
    synagoges, synagoges_buiten_zh = rijksmonument_kandidaten(
        rijksmonumenten, SYNAGOGE_PATTERN, gem_tree, gemeenten, gem_geoms, bp_tree, bp_geoms, begraafplaatsen
    )

    out = {
        "waarschuwing": (
            "EXPERIMENTEEL. Automatische tekstzoekactie op archeologische "
            "onderzoeksrapporten, geen verificatie. Elke kandidaat moet "
            "handmatig beoordeeld worden voordat er conclusies aan worden "
            "verbonden. Zie scripts/compute_kandidaat_begraafplaatsen.py."
        ),
        "aantal_onderzoeksgebieden_doorzocht": len(onderzoeksgebieden),
        "aantal_treffers": len(candidates) + buiten_zh,
        "aantal_buiten_zuid_holland_bbox_rand": buiten_zh,
        "kandidaten": candidates,
        "kloosters": {
            "waarschuwing": KLOOSTER_WAARSCHUWING,
            "aantal_buiten_zuid_holland_bbox_rand": kloosters_buiten_zh,
            "kandidaten": kloosters,
        },
        "synagoges": {
            "waarschuwing": SYNAGOGE_WAARSCHUWING,
            "aantal_buiten_zuid_holland_bbox_rand": synagoges_buiten_zh,
            "kandidaten": synagoges,
        },
    }
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    concreet = sum(1 for c in candidates if c["zekerheid"] == "concreet genoemd")
    print(f"kandidaten geschreven -> {OUT_PATH}")
    print(f"  {len(onderzoeksgebieden)} onderzoeksgebieden doorzocht, {len(candidates) + buiten_zh} treffers "
          f"({buiten_zh} daarvan buiten Zuid-Holland, bbox-rand-effect)")
    print(f"  {len(candidates)} kandidaten in Zuid-Holland, {concreet} concreet genoemd (niet als hypothese), "
          f"{sum(1 for c in candidates if c['afstand_tot_bekende_bp_m'] > 250)} daarvan >250m van een bekende begraafplaats")
    print(f"  {len(kloosters)} kloostercomplexen in Zuid-Holland ({kloosters_buiten_zh} buiten bbox-rand)")
    print(f"  {len(synagoges)} synagoges in Zuid-Holland ({synagoges_buiten_zh} buiten bbox-rand)")


if __name__ == "__main__":
    main()
