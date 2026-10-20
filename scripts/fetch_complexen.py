#!/usr/bin/env python3
"""
Zoek de rijksmonumentnummers uit de Excel van de domeinexpert op in de RCE en
haal bij een COMPLEXNUMMER de onderdelen op.

Aanleiding (2026-10-20, antwoord van de domeinexpert): de kolom "Rmonr." in de
Excel bevat soms een rijksmonumentnummer en soms een complexnummer ("het
lastige is dat een monumentnummer kiezen de lading niet dekt, dus inclusief
complexnummers zou mooi zijn"). 13 van de 54 nummers bleken een complex, met
samen 50 onderdelen (rijksmonumenten). Die onderdelen zitten al in
data/rce/rijksmonumenten.geojson (met geometrie), maar waren daar niet aan het
complexnummer uit de Excel te koppelen -- dat is wat dit script oplost.

Leest: data/Begraafplaatsen Zuid-Holland - datering.csv (kolommen
Rijksmonument = Ja en Rmonr.; PII-vrij).
Query: queries/rce/rmon-lookup.sparql ({NUMMERS} wordt hier ingevuld met
.replace(), niet met str.format -- SPARQL zit vol accolades).
Schrijft: data/rce/complexen.json + data/rce/metadata/complexen.json.

Niet onderdeel van scripts/fetch_rce.py: dat haalt alle 14.204 rijksmonumenten
opnieuw op en geeft bij elke run veel volgorde-ruis in het bestand; dit is een
kleine, stabiele aanvulling. Draai opnieuw na een nieuwe Excel.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

ENDPOINT = "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/sparql"
REPO_ROOT = Path(__file__).resolve().parent.parent
QUERY_FILE = REPO_ROOT / "queries" / "rce" / "rmon-lookup.sparql"
DATERING_CSV = REPO_ROOT / "data" / "Begraafplaatsen Zuid-Holland - datering.csv"
OUT_PATH = REPO_ROOT / "data" / "rce" / "complexen.json"
META_PATH = REPO_ROOT / "data" / "rce" / "metadata" / "complexen.json"


def excel_nummers() -> list[str]:
    with DATERING_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter="|"))
    kop, data = rows[0], rows[1:]
    i_rm, i_nr = kop.index("Rijksmonument"), kop.index("Rmonr.")
    return sorted({r[i_nr].strip() for r in data if r[i_rm].strip().lower() == "ja" and r[i_nr].strip().isdigit()})


def main() -> None:
    nummers = excel_nummers()
    query = QUERY_FILE.read_text(encoding="utf-8").replace("{NUMMERS}", " ".join(f'"{n}"' for n in nummers))
    resp = requests.post(
        ENDPOINT, data={"query": query}, headers={"Accept": "application/sparql-results+json"}, timeout=180
    )
    resp.raise_for_status()
    bindings = resp.json()["results"]["bindings"]

    gevonden: dict[str, dict] = defaultdict(lambda: {"soorten": set(), "naam": None, "onderdelen": set(), "hoofdobject": set()})
    for b in bindings:
        d = gevonden[b["nummer"]["value"]]
        d["soorten"].add(b["soort"]["value"])
        if "naam" in b:
            d["naam"] = b["naam"]["value"]
        if "onderdeelNummer" in b:
            d["onderdelen"].add(b["onderdeelNummer"]["value"])
        if "hoofdobjectNummer" in b:
            d["hoofdobject"].add(b["hoofdobjectNummer"]["value"])

    niet_gevonden = [n for n in nummers if n not in gevonden]
    assert not niet_gevonden, f"nummers die de RCE niet kent (als object of complex): {niet_gevonden}"
    beide = [n for n, d in gevonden.items() if len(d["soorten"]) > 1]
    assert not beide, f"nummer is tegelijk rijksmonument en complex, handmatig bekijken: {beide}"

    complexen = {
        n: {
            "naam": d["naam"],
            "hoofdobject": sorted(d["hoofdobject"])[0] if d["hoofdobject"] else None,
            "onderdelen": sorted(d["onderdelen"]),
        }
        for n, d in sorted(gevonden.items())
        if "complex" in d["soorten"]
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    META_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"complexen": complexen}, ensure_ascii=False, indent=1), encoding="utf-8")
    META_PATH.write_text(
        json.dumps(
            {
                "source": "RCE Linked Data Voorziening (CHO)",
                "endpoint": ENDPOINT,
                "query_file": "queries/rce/rmon-lookup.sparql",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "nummers_uit_excel": len(nummers),
                "complexen": len(complexen),
                "onderdelen_totaal": sum(len(c["onderdelen"]) for c in complexen.values()),
                "gewone_rijksmonumenten": len(nummers) - len(complexen),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"{len(nummers)} nummers: {len(complexen)} complexen ({sum(len(c['onderdelen']) for c in complexen.values())} onderdelen), "
          f"{len(nummers) - len(complexen)} gewone rijksmonumenten -> {OUT_PATH}")


if __name__ == "__main__":
    main()
