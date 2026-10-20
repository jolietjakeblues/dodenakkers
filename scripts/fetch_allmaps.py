#!/usr/bin/env python3
"""
Koppel oude kaarten uit Allmaps (https://allmaps.org) aan de verdwenen
begraafplaatsen en de kandidaat-begraafplaatsen: welke gegeorefereerde
historische kaarten liggen over elk punt?

Afgeleid van scripts/fetch_allmaps.py in het project Joodse Begraafplaatsen
(zelfde selectieregels), maar met onze punten: de 92 verdwenen begraafplaatsen
(data/generated/verdwenen-begraafplaatsen.geojson) en de kandidaten uit
data/generated/kandidaat_begraafplaatsen.json (tekstzoek, kloosters,
synagoges, kapellen, CHS-archeologie). Elk punt heeft daarin een `id`.

Bron: de open dump van alle Allmaps-kaarten (https://files.allmaps.org/
maps.geojsonl, CC0, twee keer per dag ververst). Per kaart staat daarin de
omtrek (GeoJSON) en de IIIF-bron. Het kaartbeeld zelf blijft bij de instelling
en wordt in de viewer (src/oude-kaarten.html) via de Allmaps Tile Server
(allmaps.xyz) getoond. De dump wordt gestreamd en ter plekke gefilterd, er
wordt niets groots opgeslagen.

Selectie, zodat er alleen bruikbare kaarten bij een punt staan:
  - de omtrek bevat het punt;
  - detailkaart: omtrek kleiner dan MAX_KM2 (geen overzichtskaarten van
    Nederland of Europa);
  - herkenbare titel (geen "Canvas 3", "Image", lege labels);
  - alleen collecties van bekende instellingen (COLLECTIES, HOSTS);
  - per scan (IIIF-image) een keer: bij meerdere georeferenties de nieuwste.

Jaartal: bij de Bonnebladen (TU Delft) uit de bestandsnaam van de scan
(b169-1912_scan.tif), via data/allmaps/bonnebladen_jaren.csv. Die tabel komt
uit de ingest-lijst van TU Delft Library (gespiegeld in
github.com/ahhutama/download_bonnebladen); ververs met --vernieuw-jaren. Bij
andere kaarten: een jaartal in de titel, anders leeg.

Output: data/generated/oude_kaarten.json
  kaarten:   {map-id: {titel, collectie, jaar}}
  punten:    {punt-id: {soort, naam, plaats, lon, lat}}
  per_punt:  {punt-id: [map-id, ...]}  (Bonnebladen eerst, dan op jaar)

Een kaart die er niet staat is geen bewijs dat er niets lag: kleine terreinen
vallen op schaal 1:25.000 weg, en georefereren is handwerk (afwijkingen van
enkele tientallen meters zijn normaal).

Gebruik
  python scripts/fetch_allmaps.py                    # dump downloaden (~1 min)
  python scripts/fetch_allmaps.py --dump maps.geojsonl
  python scripts/fetch_allmaps.py --vernieuw-jaren   # Bonnebladen-jaren opnieuw ophalen
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import math
import re
from pathlib import Path

import requests
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATED = REPO_ROOT / "data" / "generated"
VERDWENEN = GENERATED / "verdwenen-begraafplaatsen.geojson"
KANDIDATEN = GENERATED / "kandidaat_begraafplaatsen.json"
JAREN = REPO_ROOT / "data" / "allmaps" / "bonnebladen_jaren.csv"
OUT = GENERATED / "oude_kaarten.json"

DUMP_URL = "https://files.allmaps.org/maps.geojsonl"
JAREN_URL = "https://raw.githubusercontent.com/ahhutama/download_bonnebladen/main/ingest-collection-min@1.json"

# Zuid-Holland ruim (lon/lat); kaarten daarbuiten worden niet eens ingelezen.
BBOX = (3.2, 51.5, 5.2, 52.5)
# Bonneblad ~ 62 km2, Waterstaatskaart-blad 250-500 km2; provinciekaarten
# (850+ km2) zijn te grof om een begraafplaats op te zien.
MAX_KM2 = 600
# Alleen collecties van bekende instellingen. Iedereen kan in Allmaps
# georefereren; daardoor staan er ook testkaarten en verkeerd geplaatste
# kaarten in (bv. een Amerikaanse verzekeringskaart boven Assen).
COLLECTIES = {
    "TU Delft Library", "Universiteitsbibliotheek Utrecht", "Universiteitsbibliotheek VU",
    "Universiteitsbibliotheek van Amsterdam", "Universitaire Bibliotheken Leiden", "Nationaal Archief",
    "4TU.ResearchData", "University of Groningen", "Stadsarchief Amsterdam", "Gouda Tijdmachine",
    "Rotterdams Publiek", "Erfgoed Leiden en Omstreken", "Wageningen University & Research",
    "Library of Congress", "David Rumsey Map Collection", "Harvard Library Digital Collections",
    "Stanford Libraries", "Yale University Library", "Bibliothèque nationale de France",
}
# Instellingen zonder provider-label in de IIIF-bron: herkend aan de host.
HOSTS = {
    "proxy.archieven.nl": "Stadsarchief Rotterdam",
    "preserve-iiif.archieven.nl": "Stadsarchief Rotterdam",
    "iiif.tresoar.nl": "Tresoar",
    "facsimile.ub.rug.nl": "University of Groningen",
}
GENERIEK = re.compile(r"^(canvas \d+|image|\d+|my manifest|generated from .*|iiif manifest.*|.*zonder metadata.*|\?)$", re.I)
# Bonnebladen-scan: https://dlc.services/iiif-img/[v3/]7/4/<hash>
BONNE = re.compile(r"dlc\.services/iiif-img/(?:v3/)?7/4/([0-9a-f]{32})$")


def label(v) -> str:
    """IIIF-label ({"nl": ["..."]}) naar tekst; soms is het label zelf JSON-tekst."""
    if isinstance(v, dict):
        v = next(iter(v.values()), [""])
        v = v[0] if v else ""
    v = str(v or "").strip()
    if v.startswith("{"):
        try:
            return label(json.loads(v))
        except ValueError:
            pass
    v = re.sub(r"\s+", " ", v).strip(" /")
    # catalogusnummers en vulteksten (UB Utrecht, BnF): "KAART: *VII*...",
    # "*VII*.B.a.795 (Dk36-14)", "Page Info:", "NP", "-"
    v = re.sub(r"\s*KAART: .*?(?=:?\s*Page Info:|$)", "", v)
    v = re.sub(r"\s*:?\s*Page Info:\s*\[(\d+)\]", lambda m: f" blad {m.group(1)}", v).strip()
    v = re.sub(r"\s*KAART: \*.*$", "", v)
    v = re.sub(r"\s*\*[IVX]+\*\S*(\s*\([^)]*\))?", "", v)
    v = re.sub(r"^(page info:?|np|-)$", "", v, flags=re.I)
    v = v.replace("Waterstaatskaart van Nederland : op de schaal van 1:50.000", "Waterstaatskaart van Nederland")
    v = v.replace("NL-HaNA 4.TOPO Topografische Dienst en Rechtsvoorgangers: A6.1 TMK: veldminuten", "TMK, veldminuut")
    return v.strip(" :")


def bruikbaar(t: str) -> bool:
    return bool(t) and not GENERIEK.match(t)


def titel_van(resource: dict) -> tuple[str, str]:
    """(serie, blad) uit canvas- en manifestlabels."""
    serie = blad = ""
    for canvas in resource.get("partOf") or []:
        c = label(canvas.get("label"))
        if bruikbaar(c) and not blad:
            blad = c
        for man in canvas.get("partOf") or []:
            m = label(man.get("label"))
            mid = man.get("id", "")
            if "river-map" in mid and bruikbaar(m):
                m = f"Rivierkaart, {m[0].lower()}{m[1:]}"
            if "luchtfotos-kadaster" in mid:
                m = "Luchtfoto Kadaster"
            if bruikbaar(m) and not serie:
                serie = m
    return serie, blad


def collectie_van(resource: dict) -> str | None:
    """Naam van de instelling, of None als die niet in de lijst staat."""
    prov = resource.get("provider") or []
    t = label(prov[0].get("label")) if prov else ""
    if t in COLLECTIES:
        return t
    return HOSTS.get(re.sub(r"^https?://([^/]+).*", r"\1", resource["id"]))


def km2(g) -> float:
    lat = g.centroid.y
    return g.area * 111.32 ** 2 * math.cos(math.radians(lat))


def jaar_uit(t: str) -> int | None:
    m = re.findall(r"\b(1[5-9]\d\d)\b", t)
    return int(m[0]) if m else None


def bonnebladen_jaren(vernieuw: bool) -> dict[str, tuple[str, int]]:
    if vernieuw or not JAREN.exists():
        rijen = []
        for x in requests.get(JAREN_URL, timeout=60).json():
            m = re.match(r"b(\d{3})([a-z]?)-(\d{4})", x["filename"])
            if m:
                rijen.append({"image": x["id"], "blad": str(int(m[1])) + m[2], "jaar": m[3]})
        JAREN.parent.mkdir(parents=True, exist_ok=True)
        with JAREN.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, ["image", "blad", "jaar"], lineterminator="\n")
            w.writeheader()
            w.writerows(sorted(rijen, key=lambda r: (r["image"])))
        print(f"{JAREN.relative_to(REPO_ROOT)}: {len(rijen)} scans")
    with JAREN.open(encoding="utf-8", newline="") as f:
        return {r["image"]: (r["blad"], int(r["jaar"])) for r in csv.DictReader(f)}


def regels(dump: str | None):
    if dump:
        with open(dump, encoding="utf-8") as f:
            yield from f
        return
    with requests.get(DUMP_URL, stream=True, timeout=900) as r:
        r.raise_for_status()
        for regel in r.iter_lines(chunk_size=1 << 20):
            if regel:
                yield regel


def laad_punten() -> dict[str, dict]:
    """{id: {soort, naam, plaats, lon, lat}} uit de verdwenen en de kandidaten."""
    punten: dict[str, dict] = {}

    def voeg_toe(id_: str, soort: str, naam: str, plaats: str, lon: float, lat: float) -> None:
        nieuw = {"soort": soort, "naam": naam, "plaats": plaats, "lon": lon, "lat": lat}
        # CHS-terreinen kunnen op meer dan een veld treffen (zelfde terrein, zelfde punt).
        assert punten.get(id_, nieuw) == nieuw, f"sleutel {id_} wijst naar twee verschillende punten"
        punten[id_] = nieuw

    for f in json.loads(VERDWENEN.read_text(encoding="utf-8"))["features"]:
        p, (lon, lat) = f["properties"], f["geometry"]["coordinates"]
        voeg_toe(p["id"], "verdwenen", p["naam"], p["plaats"], lon, lat)

    k = json.loads(KANDIDATEN.read_text(encoding="utf-8"))
    for x in k["kandidaten"]:
        voeg_toe(x["id"], "tekstzoek", f"Archeologisch onderzoek {x['objectnummer']} (zoekterm \"{x['gevonden_term']}\")", x["gemeente"], x["lon"], x["lat"])
    for sectie, soort in (("kloosters", "klooster"), ("synagoges", "synagoge"), ("kapellen", "kapel")):
        for x in k[sectie]["kandidaten"]:
            voeg_toe(x["id"], soort, x["naam"] or x["functie"], x["gemeente"], x["lon"], x["lat"])
    for x in k["chs_archeologie"]["kandidaten"]:
        voeg_toe(x["id"], "chs", x["toponiem"] or f"CHS-terrein {x['monumentnr']}", x["plaats"] or x["gemeente"], x["lon"], x["lat"])
    return punten


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", help="lokale kopie van maps.geojsonl")
    ap.add_argument("--vernieuw-jaren", action="store_true")
    args = ap.parse_args()

    jaren = bonnebladen_jaren(args.vernieuw_jaren)
    punten = laad_punten()
    ids = list(punten)
    tree = STRtree([Point(punten[i]["lon"], punten[i]["lat"]) for i in ids])

    # Per scan alleen de nieuwste georeferentie.
    per_scan: dict[str, dict] = {}
    for regel in regels(args.dump):
        f = json.loads(regel)
        try:
            g = shape(f["geometry"])
        except Exception:
            continue
        x0, y0, x1, y1 = g.bounds
        if x1 < BBOX[0] or x0 > BBOX[2] or y1 < BBOX[1] or y0 > BBOX[3]:
            continue
        if not g.is_valid:
            g = g.buffer(0)
        if g.is_empty:
            continue
        p = f["properties"]
        res = p["resource"]
        collectie = collectie_van(res)
        if not collectie or km2(g) > MAX_KM2:
            continue
        raakt = [ids[i] for i in tree.query(g) if g.contains(tree.geometries[i])]
        if not raakt:
            continue
        serie, blad = titel_van(res)
        bonne = BONNE.search(res["id"])
        jaar = None
        if bonne and bonne.group(1) in jaren:
            nr, jaar = jaren[bonne.group(1)]
            m = re.match(r"Blad \d+\w?: (.*)", blad)
            titel = f"Bonneblad {nr} {m.group(1).title() if m else ''}".strip()
        else:
            if serie and blad and serie not in blad and blad not in serie:
                titel = f"{serie}: {blad}"
            else:
                titel = max(serie, blad, key=len)
            jaar = jaar_uit(titel)
        if not bruikbaar(titel):
            continue
        oud = per_scan.get(res["id"])
        if oud and oud["modified"] >= p.get("modified", ""):
            continue
        per_scan[res["id"]] = {
            "map": p["id"].rsplit("/", 1)[-1],
            "raakt": raakt,
            "modified": p.get("modified", ""),
            "titel": titel,
            "collectie": collectie,
            "jaar": jaar,
            "bonne": bool(bonne),
        }

    per_punt: dict[str, list[dict]] = {i: [] for i in ids}
    for k in per_scan.values():
        for i in k["raakt"]:
            per_punt[i].append(k)
    gebruikt: dict[str, dict] = {}
    uit_per_punt: dict[str, list[str]] = {}
    for i, hits in per_punt.items():
        hits.sort(key=lambda k: (not k["bonne"], k["jaar"] or 9999, k["titel"]))
        if hits:
            uit_per_punt[i] = [k["map"] for k in hits]
            for k in hits:
                gebruikt[k["map"]] = {"titel": k["titel"], "collectie": k["collectie"], "jaar": k["jaar"]}

    out = {
        "gegenereerd": datetime.date.today().isoformat(),
        "bron": "Allmaps (https://allmaps.org), georeferenties CC0; kaartbeelden van de genoemde collecties",
        "kaarten": dict(sorted(gebruikt.items())),
        "punten": dict(sorted(punten.items())),
        "per_punt": dict(sorted(uit_per_punt.items())),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    zonder = [i for i in ids if i not in uit_per_punt]
    print(f"{OUT.relative_to(REPO_ROOT)}: {len(uit_per_punt)}/{len(ids)} punten, {len(gebruikt)} kaarten"
          + (f"; zonder: {', '.join(zonder)}" if zonder else ""))


if __name__ == "__main__":
    main()
