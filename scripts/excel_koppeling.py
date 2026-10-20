#!/usr/bin/env python3
"""
Koppeling van elk begraafplaatsterrein aan zijn rij in de Excel van de
domeinexpert (via de PII-vrije datering-CSV).

Waarom dit apart bestaat (2026-10-20): de domeinexpert wil kunnen filteren op
"gemeentelijk beschermd ja/nee", en dat staat alleen in de Excel
(kolom "Gemeentelijk monument"). Terrein en Excel-rij hebben geen gedeelde
sleutel: de kolom Nr is niet uniek en de namen verschillen ("oud handwerk",
zonder het belang van een exacte match te zien, aldus de domeinexpert).

Aanpak: Excel en kaart hebben evenveel begraafplaatsen (450 -- per gemeente
komt het ook overeen), dus elke Excel-rij hoort bij precies EEN terrein. Per
groep onderling bereikbare kandidaten (zelfde plaats, of een gegeocodeerd
adres binnen 400 m van de ingang) wordt een optimale een-op-een-toewijzing
bepaald (Hongaarse methode) op naamovereenkomst, plaats en afstand. Dat is
robuuster dan per terrein de beste rij kiezen: een rij die bij de ene buur
past, is dan niet meer beschikbaar voor de andere (de oorzaak van de eerdere
datering-koppelfouten). Wat onder de drempel blijft, blijft leeg: onbekend is
eerlijker dan een gok.

Uitzonderingen kunnen worden vastgezet met `excel_nr` in
data/datering-correcties.json.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATERING_CSV = REPO_ROOT / "data" / "Begraafplaatsen Zuid-Holland - datering.csv"

_NAAM_AFKORTINGEN = {
    "gem": "gemeentelijke", "gemeentelijk": "gemeentelijke", "alg": "algemene", "algemeen": "algemene",
    "nw": "nieuwe", "nieuw": "nieuwe", "vm": "voormalig", "hh": "heilige", "h": "heilige", "st": "sint",
}
_NAAM_STOPWOORDEN = {"begraafplaats", "kerkhof", "de", "het", "en", "van", "bij", "op", "in", "met", "later", "deel", "kerk"}

AFSTAND_BEREIK_M = 400.0       # verder weg dan dit is geen kandidaat (tenzij zelfde plaats)
MIN_SCORE = 1.5                # onder deze score blijft een terrein zonder Excel-rij
GEWICHT_NAAM, GEWICHT_PLAATS, GEWICHT_AFSTAND = 2.0, 1.0, 1.0


def naam_woorden(naam: str | None) -> frozenset[str]:
    woorden = [_NAAM_AFKORTINGEN.get(w, w) for w in re.findall(r"[a-zà-ÿ]+", (naam or "").lower())]
    return frozenset(w for w in woorden if w not in _NAAM_STOPWOORDEN)


def plaats_sleutel(plaats: str | None) -> str:
    sleutel = re.sub(r"[^a-z]", "", re.sub(r"\(geruimd\)", "", plaats or "", flags=re.I).lower())
    return "denhaag" if sleutel == "sgravenhage" else sleutel


def load_excel_rijen() -> list[dict]:
    if not DATERING_CSV.exists():
        return []
    with DATERING_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter="|"))
    kop, data = rows[0], rows[1:]
    i = {n: kop.index(n) for n in ("Nr", "Naam", "Plaats", "Gemeente", "Rijksmonument", "Gemeentelijk monument", "Rmonr.", "Beschermd deel", "Jaartal", "Circa", "Periode")}
    rijen = []
    for r in data:
        rmonr = r[i["Rmonr."]].strip()
        jaartal = r[i["Jaartal"]].strip()
        rijen.append(
            {
                "nr": r[i["Nr"]].strip(),
                "naam": r[i["Naam"]].strip(),
                "plaats": r[i["Plaats"]].strip(),
                "gemeente": r[i["Gemeente"]].strip(),
                "rijksmonument": r[i["Rijksmonument"]].strip().lower() == "ja",
                "gemeentelijk_monument": r[i["Gemeentelijk monument"]].strip().lower() == "ja",
                "rmonr": rmonr if rmonr.isdigit() else None,
                "beschermd_deel": r[i["Beschermd deel"]].strip() or None,
                "jaartal": int(float(jaartal)) if jaartal else None,
                "jaartal_circa": r[i["Circa"]].strip().lower() == "ja",
                "periode": r[i["Periode"]].strip() or None,
            }
        )
    return rijen


def _naam_score(a: frozenset[str], b: frozenset[str]) -> float:
    if not a and not b:
        return 0.6          # alleen generieke woorden aan beide kanten ("Begraafplaats" / "Kerkhof")
    if not a or not b:
        return 0.1
    return len(a & b) / len(a | b)


def score(terrein: dict, rij: dict, rij_punt) -> float:
    s_naam = _naam_score(naam_woorden(terrein["naam"]), naam_woorden(rij["naam"]))
    s_plaats = 1.0 if plaats_sleutel(terrein["plaats"]) == plaats_sleutel(rij["plaats"]) else 0.0
    s_afstand = 0.0
    if terrein["ingang_rd"] is not None and rij_punt is not None:
        s_afstand = max(0.0, 1.0 - terrein["ingang_rd"].distance(rij_punt) / AFSTAND_BEREIK_M)
    return GEWICHT_NAAM * s_naam + GEWICHT_PLAATS * s_plaats + GEWICHT_AFSTAND * s_afstand


def _hongaars(kosten: list[list[float]]) -> list[int]:
    """Minimale kosten, rijen <= kolommen. Geeft per rij de gekozen kolom."""
    n, m = len(kosten), len(kosten[0])
    INF = float("inf")
    u, v, p, way = [0.0] * (n + 1), [0.0] * (m + 1), [0] * (m + 1), [0] * (m + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv, used = [INF] * (m + 1), [False] * (m + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], INF, 0
            for j in range(1, m + 1):
                if not used[j]:
                    cur = kosten[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    resultaat = [0] * n
    for j in range(1, m + 1):
        if p[j]:
            resultaat[p[j] - 1] = j - 1
    return resultaat


def koppel_terreinen(terreinen: list[dict], rijen: list[dict], rij_punten: list, correcties: dict) -> dict:
    """terreinen: [{id, naam, plaats, ingang_rd (shapely Point of None)}];
    rijen: load_excel_rijen(); rij_punten: per rij het gegeocodeerde punt (RD) of None.
    Geeft {terrein-id: {"rij": rij, "via": ..., "score": ...}} voor de gekoppelde terreinen."""
    vast: dict = {}
    for t in terreinen:
        nr = (correcties.get(t["id"]) or {}).get("excel_nr")
        if nr is not None:
            # Nr is niet uniek (66, 67, 74 komen dubbel voor): bij meerdere rijen
            # beslist de plaats. De plaats van de Excel wijkt soms af van die op
            # de kaart (Scheveningen / 's-Gravenhage, Meije / Bodegraven).
            kandidaten = [j for j, r in enumerate(rijen) if r["nr"] == str(nr)]
            if len(kandidaten) > 1:
                kandidaten = [j for j in kandidaten if plaats_sleutel(rijen[j]["plaats"]) == plaats_sleutel(t["plaats"])]
            assert len(kandidaten) == 1, f"{t['id']}: excel_nr {nr} is niet eenduidig ({len(kandidaten)} rijen)"
            vast[t["id"]] = kandidaten[0]
    bezet = set(vast.values())

    # kandidaatparen + samenhangende groepen (union-find)
    ouder = list(range(len(terreinen) + len(rijen)))

    def vind(x: int) -> int:
        while ouder[x] != x:
            ouder[x] = ouder[ouder[x]]
            x = ouder[x]
        return x

    paar_score: dict = {}
    for ti, t in enumerate(terreinen):
        if t["id"] in vast:
            continue
        for rj, r in enumerate(rijen):
            if rj in bezet:
                continue
            nabij = t["ingang_rd"] is not None and rij_punten[rj] is not None and t["ingang_rd"].distance(rij_punten[rj]) <= AFSTAND_BEREIK_M
            if plaats_sleutel(t["plaats"]) == plaats_sleutel(r["plaats"]) or nabij:
                paar_score[(ti, rj)] = score(t, r, rij_punten[rj])
                ouder[vind(ti)] = vind(len(terreinen) + rj)

    groepen: dict = {}
    for (ti, rj) in paar_score:
        groepen.setdefault(vind(ti), ([], []))
    for (ti, rj) in paar_score:
        g = groepen[vind(ti)]
        if ti not in g[0]:
            g[0].append(ti)
        if rj not in g[1]:
            g[1].append(rj)

    resultaat = {tid: {"rij": rijen[rj], "via": "vastgezet door ons (excel_nr)", "score": None} for tid, rj in vast.items()}
    for ts, rs in groepen.values():
        # kolommen: echte rijen, plus een "geen koppeling"-kolom per terrein met score MIN_SCORE
        kosten = []
        for ti in ts:
            regel = [-paar_score.get((ti, rj), -1e6) for rj in rs]
            regel += [-MIN_SCORE] * len(ts)
            kosten.append(regel)
        keuze = _hongaars(kosten)
        for rij_i, kol in enumerate(keuze):
            if kol < len(rs):
                ti, rj = ts[rij_i], rs[kol]
                resultaat[terreinen[ti]["id"]] = {"rij": rijen[rj], "via": "toewijzing op naam, plaats en afstand", "score": round(paar_score[(ti, rj)], 2)}
    return resultaat
