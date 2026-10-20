#!/usr/bin/env python3
"""
Controle (GEEN bron) van de gemeentelijk-monument-vlag in de Excel tegen de
lijsten van gemeentelijke monumenten op Wikipedia (2026-10-20, op verzoek).

De Excel van de domeinexpert is leidend voor `gemeentelijk_monument`; Wikipedia
wordt hier alleen gebruikt om te zien of er iets opvalt dat de domeinexpert
kan nakijken. Wikipedia is onvolledig (sommige gemeenten ontbreken of hebben een
onvolledige lijst) en de coordinaten bij "ong."-adressen kunnen honderden meters
tot ruim een kilometer afwijken. Er wordt dus niets in data/ geschreven: alleen
een rapport op stdout.

Werkwijze:
 1. Volg de links van de overzichtspagina "Lijst van gemeentelijke monumenten in
    Zuid-Holland" (inclusief deellijsten, bv. Delft/Binnenstad), via de
    Wikipedia-API. Alleen pagina's met een Zuid-Holland-tabel (prov-iso=nl-zh).
 2. Lees de rijen van de tabelsjablonen (object, adres, coordinaten, functie).
 3. Selecteer rijen over begraafplaatsen/kerkhoven (heel) en graf-onderdelen
    (grafkelder, aula, baarhuisje, ...), en zoek per rij het dichtstbijzijnde
    terrein op de kaart (RD, meters).
 4. Rapporteer: Wikipedia noemt iets op/aan een terrein dat in de Excel "niet
    gemeentelijk" is, en hoeveel van de Excel-"ja"-terreinen Wikipedia bevestigt.

Draaien: python scripts/controle_wikipedia_gemeentelijke_monumenten.py
(netwerk nodig; ~100 verzoeken met korte pauzes).
"""
from __future__ import annotations

import json
import re
import time
from collections import defaultdict
from pathlib import Path

import requests
from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform
from shapely.strtree import STRtree

REPO_ROOT = Path(__file__).resolve().parent.parent
API = "https://nl.wikipedia.org/w/api.php"
UA = {"User-Agent": "dodenakkers-controle/1.0 (controle van gemeentelijke monumenten; contact via repository)"}
INDEX = "Lijst van gemeentelijke monumenten in Zuid-Holland"
PREFIX = "Lijst van gemeentelijke monumenten in "
ANDERE_PROVINCIES = ("Flevoland", "Drenthe", "Groningen", "Overijssel", "Zeeland", "Utrecht", "Limburg", "Brabant", "Noord-Holland", "Gelderland", "Friesland", "Fryslân", "Nederland")
HEEL = ("begraafplaats", "kerkhof", "dodenakker")
ONDERDEEL = ("grafkelder", "grafkapel", "grafmonument", "graftombe", "grafzerk", "mortuarium", "lijkenhuis", "baarhuis", "doodgraver",
             "columbarium", "urnenmuur", "rouwkamer", "aula", "grafteken", "mausoleum", "bidkapel")
SLEUTELS = ("object", "adres", "lat", "lon", "oorspr_fun", "objnr")
OP_TERREIN_M, DICHTBIJ_M = 30, 150

to_rd = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True).transform


def api(params: dict) -> dict:
    r = requests.get(API, params={**params, "format": "json", "formatversion": "2"}, headers=UA, timeout=60)
    r.raise_for_status()
    return r.json()


def lijst_links(tekst: str) -> set[str]:
    return {m.group(1).strip()[0].upper() + m.group(1).strip()[1:] for m in re.finditer(r"\[\[\s*([Ll]ijst van gemeentelijke monumenten in [^\]\|#]+)", tekst)}


def overslaan(titel: str) -> bool:
    return titel == INDEX or any(p in titel[len(PREFIX):] for p in ANDERE_PROVINCIES)


def haal_pagina_s() -> dict[str, str]:
    index = api({"action": "parse", "page": INDEX, "prop": "wikitext"})["parse"]["wikitext"]
    wachtrij = sorted(t for t in lijst_links(index) if not overslaan(t))
    gezien, pagina = set(wachtrij), {}
    while wachtrij and len(pagina) < 300:
        groep, wachtrij = wachtrij[:20], wachtrij[20:]
        d = api({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main", "titles": "|".join(groep), "redirects": "1"})
        for p in d["query"]["pages"]:
            if p.get("missing"):
                continue
            tekst = p["revisions"][0]["slots"]["main"]["content"]
            pagina[p["title"]] = tekst
            for t in lijst_links(tekst):
                if t not in gezien and not overslaan(t):
                    gezien.add(t)
                    wachtrij.append(t)
        time.sleep(0.4)
    return {t: s for t, s in pagina.items() if "nl-zh" in s}


def sjabloon_blok(tekst: str, start: int) -> str:
    diepte, i = 0, start
    while i < len(tekst) - 1:
        if tekst[i:i + 2] == "{{":
            diepte += 1
            i += 2
        elif tekst[i:i + 2] == "}}":
            diepte -= 1
            i += 2
            if diepte == 0:
                return tekst[start:i]
        else:
            i += 1
    return tekst[start:]


def parameters(sjabloon: str) -> dict[str, str]:
    delen, huidig, ds, db, i, inhoud = [], [], 0, 0, 0, sjabloon[2:-2]
    while i < len(inhoud):
        t2 = inhoud[i:i + 2]
        if t2 in ("[[", "]]", "{{", "}}"):
            ds += (t2 == "[[") - (t2 == "]]")
            db += (t2 == "{{") - (t2 == "}}")
            huidig.append(t2)
            i += 2
            continue
        if inhoud[i] == "|" and ds == 0 and db == 0:
            delen.append("".join(huidig))
            huidig = []
        else:
            huidig.append(inhoud[i])
        i += 1
    delen.append("".join(huidig))
    return {k.strip().lower(): v.strip() for k, _, v in (d.partition("=") for d in delen[1:]) if _}


def schoon(v: str | None) -> str:
    v = re.sub(r"<[^>]+>", "", v or "")
    v = re.sub(r"\[\[(?:[^\]\|]*\|)?([^\]]*)\]\]", r"\1", v)
    return re.sub(r"\s+", " ", re.sub(r"'{2,}", "", v)).strip()


def rijen_uit(paginas: dict[str, str]) -> list[dict]:
    rijen = []
    for titel, t in paginas.items():
        for m in re.finditer(r"\{\{\s*Tabelrij gemeentelijk monument", t, flags=re.I):
            p = parameters(sjabloon_blok(t, m.start()))
            rijen.append({**{k: schoon(p.get(k)) for k in SLEUTELS}, "pagina": titel[len(PREFIX):]})
    return rijen


def soort(r: dict) -> str | None:
    tekst = f"{r['object']} {r['oorspr_fun']}".lower()
    if any(k in tekst for k in HEEL):
        return "heel"
    if any(k in tekst for k in ONDERDEEL):
        return "onderdeel"
    return None


def main() -> None:
    feats = json.loads((REPO_ROOT / "data" / "generated" / "analyse.geojson").read_text(encoding="utf-8"))["features"]
    props = [f["properties"] for f in feats]
    geoms = [transform(to_rd, shape(f["geometry"])) for f in feats]
    tree = STRtree(geoms)

    paginas = haal_pagina_s()
    rijen = rijen_uit(paginas)
    print(f"{len(paginas)} Wikipedia-lijsten met Zuid-Holland-tabel, {len(rijen)} gemeentelijke monumenten")

    kandidaten, zonder_coord = [], []
    for r in rijen:
        s = soort(r)
        if not s:
            continue
        try:
            lat, lon = float(r["lat"].replace(",", ".")), float(r["lon"].replace(",", "."))
        except ValueError:
            zonder_coord.append(r)
            continue
        pt = transform(to_rd, Point(lon, lat))
        i = int(tree.nearest(pt))
        kandidaten.append({**r, "soort": s, "terrein": i, "afstand_m": round(pt.distance(geoms[i]), 1)})
    print(f"begraafplaats-gerelateerd: {len(kandidaten)} met coordinaten, {len(zonder_coord)} zonder")

    op_terrein = defaultdict(list)
    dichtbij_nee, ver = [], []
    for k in kandidaten:
        p = props[k["terrein"]]
        if k["afstand_m"] <= OP_TERREIN_M:
            op_terrein[k["terrein"]].append(k)
        elif k["afstand_m"] <= DICHTBIJ_M and p["gemeentelijk_monument"] is False:
            dichtbij_nee.append(k)
        elif k["afstand_m"] > DICHTBIJ_M:
            ver.append(k)

    print(f"\nWikipedia noemt iets OP of AAN (<= {OP_TERREIN_M} m) een terrein: {len(op_terrein)} terreinen")
    tegenspraak = [(i, l) for i, l in op_terrein.items() if props[i]["gemeentelijk_monument"] is not True]
    print(f"  daarvan in de Excel NIET gemeentelijk beschermd: {len(tegenspraak)}")
    for i, l in tegenspraak:
        print(f"    {props[i]['id']} {props[i]['naam']} ({props[i]['plaats']}): " + "; ".join(k["object"][:60] for k in l))

    print(f"\nWikipedia noemt iets op {OP_TERREIN_M}-{DICHTBIJ_M} m van een terrein dat in de Excel NIET gemeentelijk is: {len(dichtbij_nee)}")
    for k in sorted(dichtbij_nee, key=lambda k: k["afstand_m"]):
        p = props[k["terrein"]]
        print(f"    [{k['soort']}] {k['object'][:70]} | {k['adres'][:30]} | {k['pagina']} | {k['afstand_m']} m van {p['id']} {p['naam']} ({p['plaats']})")

    bevestigd = {i for i, l in op_terrein.items() if props[i]["gemeentelijk_monument"] is True}
    ja = [i for i, p in enumerate(props) if p["gemeentelijk_monument"]]
    print(f"\nExcel zegt gemeentelijk beschermd: {len(ja)} terreinen; Wikipedia bevestigt met een coordinaat op het terrein: {len(bevestigd)}")
    print("(de rest staat niet of niet nauwkeurig op Wikipedia: onvolledige lijsten, coordinaten bij 'ong.'-adressen, of rijen zonder coordinaten)")
    print(f"{len(ver)} begraafplaatsrijen liggen > {DICHTBIJ_M} m van elk terrein; controleer die op het niveau van aantallen per gemeente, niet per coordinaat.")


if __name__ == "__main__":
    main()
