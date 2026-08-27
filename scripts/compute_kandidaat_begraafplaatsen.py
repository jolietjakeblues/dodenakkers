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
from shapely.geometry import shape
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
    r"crematieresten|crematiegraf|inhumatiegraf|beenderen|necropool|"
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


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)["features"]


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
    }
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    concreet = sum(1 for c in candidates if c["zekerheid"] == "concreet genoemd")
    print(f"kandidaten geschreven -> {OUT_PATH}")
    print(f"  {len(onderzoeksgebieden)} onderzoeksgebieden doorzocht, {len(candidates) + buiten_zh} treffers "
          f"({buiten_zh} daarvan buiten Zuid-Holland, bbox-rand-effect)")
    print(f"  {len(candidates)} kandidaten in Zuid-Holland, {concreet} concreet genoemd (niet als hypothese), "
          f"{sum(1 for c in candidates if c['afstand_tot_bekende_bp_m'] > 250)} daarvan >250m van een bekende begraafplaats")


if __name__ == "__main__":
    main()
