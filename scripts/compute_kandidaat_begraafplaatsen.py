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
drie kleinere signalen op basis van rijksmonumenten (data/rce/rijksmonumenten.geojson,
oorspronkelijke_functie_kort): kloosters, synagoges en kapellen. Zelfde
bbox-fetch kanttekening als bij de eerdere kerk-analyse (scripts/analyse_spatial.py) --
ook hier eerst filteren op de echte ZH-gemeentegrenzen. Complexen met
meerdere apart geregistreerde rijksmonumentnummers (bv. losse vleugels)
worden geclusterd binnen CLUSTER_AFSTAND_M om dubbele kandidaten voor
hetzelfde fysieke gebouw te voorkomen. Zie de losse waarschuwingsteksten
per categorie verderop in dit bestand voor waarom "afstand tot een
bekende begraafplaats" bij synagoges NIET hetzelfde betekent als bij
kloosters/kerken/kapellen, en voor de "kapel" gebruikt zelf ook geen
eenduidige categorie is (Grafkapel/Bidkapel/Bedevaartkapel zitten er
ongefilterd in).

Voor diezelfde drie categorieen (klooster/synagoge/kapel) wordt er ook
live tegen de Kadaster Kennisgraaf (KKG, SPARQL) gecheckt hoeveel BAG-
gebouwen er nu binnen BEBOUWING_RADIUS_M van het punt staan (wens van
Joop, 2026-08-27: "het kan zijn dat al gebouwd is"). Vereist netwerktoegang
tot KKG_ENDPOINT; run met --no-kadaster-check om dit over te slaan (bv.
zonder netwerktoegang). Zie BEBOUWING_WAARSCHUWING voor de interpretatie
-- dit is een extra aanwijzing, geen bevestiging in welke richting dan ook.

Vierde bron: data/zuid-holland/chs-archeologie-provinciaal-belang.geojson
(Provincie Zuid-Holland CHS, zie scripts/fetch_chs_archeologie.py), 662
"archeologische terreinen van provinciaal belang", zelfde grafterm-patroon
maar gezocht in de kortere Toponiem/WAARDE/Beschrijving-velden i.p.v.
lange rapporttekst. Geen bbox-rand-effect (provinciale dienst, dekt per
definitie alleen Zuid-Holland) dus geen gemeentegrenzen-filter nodig hier.
Zie CHS_ARCHEOLOGIE_WAARSCHUWING voor de kanttekeningen.

Output:
  data/generated/kandidaat_begraafplaatsen.json

Run los, niet als onderdeel van de reguliere build (experimenteel, geen
onderdeel van de "vertrouwde" statistieken).
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests
from pyproj import Transformer
from shapely.geometry import MultiPoint, Point, shape
from shapely.ops import transform
from shapely.strtree import STRtree

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = REPO_ROOT / "data" / "generated"
RCE_DIR = REPO_ROOT / "data" / "rce"
PDOK_DIR = REPO_ROOT / "data" / "pdok"
ZH_DIR = REPO_ROOT / "data" / "zuid-holland"
OUT_PATH = GENERATED_DIR / "kandidaat_begraafplaatsen.json"

to_rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True).transform
to_wgs84 = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True).transform

# Kadaster Kennisgraaf (KKG) SPARQL-endpoint, gebruikt om te checken of een
# rijksmonument-kandidaat nu nog in open terrein staat of inmiddels omringd
# is door (latere) bebouwing -- wens van Joop (2026-08-27): "het kan zijn
# dat al gebouwd is". Zie BEBOUWING_WAARSCHUWING voor de interpretatiegrens.
KKG_ENDPOINT = "https://api.labs.kadaster.nl/datasets/kadaster/kkg/services/kkg/sparql"
BEBOUWING_RADIUS_M = 30

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
KAPEL_PATTERN = re.compile(r"kapel", re.IGNORECASE)

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

KAPEL_WAARSCHUWING = (
    "EXPERIMENTEEL. Kapellen (oorspronkelijke_functie_kort bevat 'kapel') uit "
    "de rijksmonumenten, gefilterd op echte Zuid-Holland-gemeentegrenzen "
    "(zelfde bbox-rand-effect als bij kerk/klooster/synagoge). Net als bij "
    "kloosters is een grote afstand tot een bekende begraafplaats een "
    "aanwijzing, geen bevestiging: kapellen (vaak van een parochie of gasthuis) "
    "hadden soms een eigen kerkhofrecht, en zijn net als kloosters vaak al "
    "eeuwen geleden verdwenen of herbestemd. LET OP: deze categorie is minder "
    "eenduidig dan klooster/synagoge -- 'kapel' omvat ook een handvol "
    "'Grafkapel' (een grafmonument dat per definitie al bij een begraafplaats "
    "hoort, dus eerder een bevestiging dan een nieuwe kandidaat) en 'Bidkapel'/"
    "'Bedevaartkapel' (wegkapellen voor gebed/bedevaart, zonder duidelijke "
    "begraaftraditie). Geen van beide is eruit gefilterd -- zie zelf de naam/"
    "functie in de brontekst voordat je een rij serieus neemt."
)

BEBOUWING_WAARSCHUWING = (
    "Extra check via de Kadaster Kennisgraaf (KKG), geen aparte kandidatenlijst: "
    "per klooster/synagoge/kapel-kandidaat hierboven is opgezocht hoeveel "
    "gebouwen (BAG/KKG imxgeo:Gebouw) er nu binnen 30m van het punt staan, en "
    "wat het oudste/nieuwste bouwjaar daarvan is. GEEN gebouwen binnen 30m is "
    "een aanwijzing dat de locatie nog open terrein is (consistent met een "
    "bewaard gebleven kerkhof); WEL gebouwen betekent niet per se dat een "
    "eventueel kerkhof weg is (het monument zelf staat er nog, een kerkhof "
    "ernaast kan een tuin/plein zijn geworden zonder dat er iets gebouwd is, "
    "of juist onder latere bebouwing verdwenen -- dat laatste kun je hier niet "
    "van onderscheiden). Puur extra context, geen bevestiging in beide "
    "richtingen."
)

CHS_ARCHEOLOGIE_WAARSCHUWING = (
    "EXPERIMENTEEL. Vierde bron, andere aard dan de rest van deze pagina: "
    "geen RCE-data maar de eigen Cultuurhistorische Hoofdstructuur (CHS) van "
    "Provincie Zuid-Holland -- 662 'archeologische terreinen van "
    "provinciaal belang', dezelfde data als de kaartlaag op de hoofdkaart "
    "(zie toggle-chs-archeologie). Geen bbox-rand-effect (provinciale "
    "dienst, dekt per definitie alleen Zuid-Holland), dus geen "
    "gemeentegrenzen-filter nodig zoals bij de andere drie bronnen. Zelfde "
    "grafterm-patroon als de archeologie-tekstzoekactie, nu gezocht in de "
    "kortere 'Toponiem'/'WAARDE'/'Beschrijving'-velden i.p.v. lange "
    "rapporttekst -- minder kans op fout-positieven zoals 'Kerkhof' als "
    "achternaam, maar ook geen garantie: sommige treffers zijn Romeinse of "
    "prehistorische grafvelden, geen begraafplaats zoals Leons dataset die "
    "verzamelt (zelfde kanttekening als bij de archeologie-tekstzoekactie "
    "hierboven). Kan overlappen met kandidaten die al via de "
    "archeologie-tekstzoekactie gevonden zijn (andere bron, dus niet "
    "automatisch ontdubbeld). Geen directe brontekst-link beschikbaar (deze "
    "open dataset publiceert geen detailpagina per record) -- gebruik de "
    "kaartlink om het terrein zelf te bekijken."
)


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)["features"]


def run_kkg_query(sparql_query: str, max_retries: int = 4) -> list[dict]:
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                KKG_ENDPOINT,
                data={"query": sparql_query},
                headers={"Accept": "application/sparql-results+json"},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                {var: val["value"] for var, val in binding.items()}
                for binding in data["results"]["bindings"]
            ]
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
    raise last_exc


def bebouwing_bij_punt(lon: float, lat: float) -> dict:
    """Aantal BAG/KKG-gebouwen binnen BEBOUWING_RADIUS_M van (lon, lat), plus
    het oudste/nieuwste bouwjaar daarvan. Zie BEBOUWING_WAARSCHUWING voor de
    interpretatie. Geeft {"fout": ...} terug i.p.v. te crashen als het
    KKG-endpoint (tijdelijk) niet bereikbaar is -- dit is een aanvulling,
    geen kernonderdeel van de output."""
    point_rd = transform(to_rd, Point(lon, lat))
    buffer_wgs84 = transform(to_wgs84, point_rd.buffer(BEBOUWING_RADIUS_M, resolution=8))
    sparql = f"""
PREFIX imxgeo: <http://modellen.geostandaarden.nl/def/imx-geo#>
PREFIX ext: <https://modellen.kkg.kadaster.nl/def/imxgeo-ext#>
PREFIX geosparql: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
SELECT ?g ?bouwjaar WHERE {{
  ?g a imxgeo:Gebouw .
  ?g ext:maaiveldgeometrie ?geomres .
  ?geomres geosparql:asWKT ?wkt .
  FILTER(geof:sfIntersects(?wkt, "{buffer_wgs84.wkt}"^^geosparql:wktLiteral))
  OPTIONAL {{ ?g imxgeo:bouwjaar ?bouwjaar }}
}}
"""
    try:
        rows = run_kkg_query(sparql)
    except requests.RequestException as exc:
        return {"fout": str(exc)}

    gebouwen: dict[str, str | None] = {}
    for row in rows:
        uri = row.get("g")
        if uri and uri not in gebouwen:
            gebouwen[uri] = row.get("bouwjaar")
    bouwjaren = sorted(int(j) for j in gebouwen.values() if j and j.isdigit())
    return {
        "aantal_gebouwen_binnen_30m": len(gebouwen),
        "oudste_bouwjaar_nabij": bouwjaren[0] if bouwjaren else None,
        "nieuwste_bouwjaar_nabij": bouwjaren[-1] if bouwjaren else None,
    }


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
            "functie": functie,
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
        functies = sorted({c["functie"] for c in cluster})
        results.append({
            "naam": named[0] if named else None,
            "functie": ", ".join(functies),
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


def chs_archeologie_kandidaten(
    terreinen: list[dict],
    bp_tree: STRtree,
    bp_geoms: list,
    begraafplaatsen: list[dict],
) -> list[dict]:
    candidates = []
    for f in terreinen:
        props = f["properties"]
        # Volgorde bepaalt welk veld als eerste een match oplevert (voor het
        # fragment): Toponiem is het kortst en meest to-the-point, dan WAARDE,
        # dan de langere Beschrijving.
        velden = [("Toponiem", props.get("Toponiem")), ("WAARDE", props.get("WAARDE")), ("Beschrijving", props.get("Beschrijving"))]
        match = None
        veldnaam = None
        tekst = None
        for naam, waarde in velden:
            if not waarde:
                continue
            m = GRAFTERM_PATTERN.search(waarde)
            if m:
                match, veldnaam, tekst = m, naam, waarde
                break
        if not match:
            continue

        geom = shape(f["geometry"])
        centroid = geom.centroid
        point_rd = transform(to_rd, centroid)
        i = bp_tree.nearest(point_rd)
        afstand = round(point_rd.distance(bp_geoms[i]), 1)
        fragment = snippet(tekst, match)
        candidates.append({
            "monumentnr": props.get("MONUMENTNR"),
            "gemeente": props.get("Gemeente"),
            "plaats": props.get("Plaats"),
            "toponiem": props.get("Toponiem"),
            "datering": props.get("Datering"),
            "waarde": props.get("WAARDE"),
            "gevonden_veld": veldnaam,
            "gevonden_term": match.group(0),
            "fragment": fragment,
            "zekerheid": "onzeker/verwacht" if HEDGE_PATTERN.search(fragment) else "concreet genoemd",
            "afstand_tot_bekende_bp_m": afstand,
            "dichtstbijzijnde_bp": f"{begraafplaatsen[i]['properties']['naam']}, {begraafplaatsen[i]['properties']['plaats']}",
            "lon": round(centroid.x, 6),
            "lat": round(centroid.y, 6),
        })

    candidates.sort(key=lambda c: (c["zekerheid"] != "concreet genoemd", -c["afstand_tot_bekende_bp_m"]))
    return candidates


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
    chs_terreinen = load(ZH_DIR / "chs-archeologie-provinciaal-belang.geojson")
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
    kapellen, kapellen_buiten_zh = rijksmonument_kandidaten(
        rijksmonumenten, KAPEL_PATTERN, gem_tree, gemeenten, gem_geoms, bp_tree, bp_geoms, begraafplaatsen
    )
    chs_archeologie = chs_archeologie_kandidaten(chs_terreinen, bp_tree, bp_geoms, begraafplaatsen)

    if "--no-kadaster-check" in sys.argv:
        print("kadaster-bebouwingscheck overgeslagen (--no-kadaster-check)")
    else:
        totaal = len(kloosters) + len(synagoges) + len(kapellen)
        gedaan = 0
        for lijst in (kloosters, synagoges, kapellen):
            for k in lijst:
                k["bebouwing"] = bebouwing_bij_punt(k["lon"], k["lat"])
                gedaan += 1
                print(f"  kadaster-check {gedaan}/{totaal}: {k.get('naam') or k['gemeente']} -> {k['bebouwing']}")
                time.sleep(0.3)

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
        "bebouwing_check": {
            "waarschuwing": BEBOUWING_WAARSCHUWING,
            "radius_m": BEBOUWING_RADIUS_M,
        },
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
        "kapellen": {
            "waarschuwing": KAPEL_WAARSCHUWING,
            "aantal_buiten_zuid_holland_bbox_rand": kapellen_buiten_zh,
            "kandidaten": kapellen,
        },
        "chs_archeologie": {
            "waarschuwing": CHS_ARCHEOLOGIE_WAARSCHUWING,
            "aantal_terreinen_doorzocht": len(chs_terreinen),
            "kandidaten": chs_archeologie,
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
    print(f"  {len(kapellen)} kapellen(complexen) in Zuid-Holland ({kapellen_buiten_zh} buiten bbox-rand)")
    print(f"  {len(chs_archeologie)} CHS-archeologiekandidaten (van {len(chs_terreinen)} terreinen van provinciaal belang)")


if __name__ == "__main__":
    main()
