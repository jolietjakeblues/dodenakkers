#!/usr/bin/env python3
"""
One-time source correction: remove cemeteries in Vijfheerenlanden villages.

Vijfheerenlanden (Ameide, Hei en Boeicop, Kedichem, Leerbroek, Leerdam,
Lexmond, Meerkerk, Nieuwland, Oosterwijk, Schoonrewoerd, Tienhoven) moved
from provincie Zuid-Holland to provincie Utrecht at the 2019 gemeentelijke
herindeling. Leon had already excluded these in an old Excel pass, but the
correction never made it into the KML/CSV this project's build reads from
-- confirmed by Leon 2026-08-19, with exact per-plaats counts that matched
this CSV's actual row counts one-for-one before any change was made.

Removes each cemetery's terrain row AND its matched ingang row together
(reuses scripts/build_base_dataset.py's own matching logic, so the removed
ingang is provably the one actually paired with that terrain -- not just
"any row with a matching plaats").

Run once. Re-run scripts/build_base_dataset.py afterwards to rebuild
data/generated/*, and update its hardcoded invariant assertions (this
script prints the new expected values at the end).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_base_dataset as b  # noqa: E402

VIJFHEERENLANDEN_PLAATSEN = [
    "Tienhoven", "Ameide", "Lexmond", "Hei en Boeicop", "Schoonrewoerd",
    "Leerbroek", "Kedichem", "Leerdam", "Oosterwijk", "Nieuwland", "Meerkerk",
]

# Verified against this CSV 2026-08-19: matches Leon's reported counts exactly
# (Tienhoven 1, Ameide 2, Lexmond 1, Hei en Boeicop 2, Schoonrewoerd 2,
# Leerbroek 2, Kedichem 1, Leerdam 5, Oosterwijk 1, Nieuwland 1, Meerkerk 2 = 20).
EXPECTED_TERREIN_COUNT = 20


def main() -> None:
    df = b.load_source()
    terrein = b.prepare(df[df["begraafplaats"] == "begraafplaats"])
    ingang = b.prepare(df[df["ingang"] == "ingang"])
    matches, shared_ingang_idx = b.match_terrein_ingang(terrein, ingang)

    plaatsen_norm = {b.normalize(p) for p in VIJFHEERENLANDEN_PLAATSEN}

    remove_orig_idx: set[int] = set()
    removed = []
    for m in matches:
        trow = terrein.loc[m["terrein_idx"]]
        if trow["pkey"] not in plaatsen_norm:
            continue
        remove_orig_idx.add(int(trow["orig_idx"]))
        entry = {"naam": trow["naam"], "plaats": trow["plaats (opgeschoon)"], "koppelwijze": m["koppelwijze"]}
        if m["ingang_idx"] is not None:
            assert m["ingang_idx"] not in shared_ingang_idx, (
                f"{trow['naam']}/{trow['plaats (opgeschoon)']}: gedeelde ingang, "
                "handmatige controle nodig voordat je 'm verwijdert"
            )
            irow = ingang.loc[m["ingang_idx"]]
            remove_orig_idx.add(int(irow["orig_idx"]))
        removed.append(entry)

    assert len(removed) == EXPECTED_TERREIN_COUNT, (
        f"verwacht {EXPECTED_TERREIN_COUNT} Vijfheerenlanden-terreinen, gevonden {len(removed)} -- "
        "stop en controleer handmatig voordat je verder gaat"
    )

    print(f"{len(removed)} begraafplaatsen te verwijderen ({len(remove_orig_idx)} CSV-rijen, incl. ingangen):")
    for r in sorted(removed, key=lambda r: (r["plaats"], r["naam"])):
        print(f"  - {r['naam']} ({r['plaats']}), koppelwijze {r['koppelwijze']}")

    kept = df[~df["orig_idx"].isin(remove_orig_idx)].drop(columns=["orig_idx"])
    out_path = b.SOURCE_CSV
    kept.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\n{len(df)} -> {len(kept)} bronrecords geschreven naar {out_path}")

    new_terrein = len(terrein) - len(removed)
    new_ingang = len(ingang) - sum(1 for oi in remove_orig_idx if oi in set(ingang["orig_idx"]))
    counts = {}
    for m in matches:
        trow = terrein.loc[m["terrein_idx"]]
        if trow["pkey"] in plaatsen_norm:
            continue
        counts[m["koppelwijze"]] = counts.get(m["koppelwijze"], 0) + 1
    print("\nNieuwe verwachte invarianten voor scripts/build_base_dataset.py:")
    print(f"  bronrecords: {len(kept)}")
    print(f"  terreinen: {new_terrein}")
    print(f"  ingangen: {new_ingang}")
    print(f"  koppelwijzen: {counts}")


if __name__ == "__main__":
    main()
