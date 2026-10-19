#!/usr/bin/env python3
"""
One-time source corrections after the answers of de domeinexpert on the
question list docs/data/009-vragen-domeinexpert.md (2026-10-19).

1. Status: NH Kerkhof Middelharnis and NH kerkhof Hoogblokland are geruimd
   ("de excel gaat hier boven wat er op de kaart staat"). Both had a blank
   geruimd value in the source CSV, in both the terrein and the ingang row.
   The existing "(geruimd)" suffix convention on `plaats (origineel)` is kept.
2. Name: the "NH begraafplaats" in Puttershoek is, per de domeinexpert, the
   "Nieuwe gemeentelijke begraafplaats" (1880) -- "dus ook de naam dient
   aangepast te worden". The Excel's own name for this cemetery is used.
   Terrein and ingang row are renamed together, otherwise the name+place
   match between the two would break.

The datering answers (jaartallen, periode) do NOT go through this script:
they are direct confirmations and live in data/datering-correcties.json.

Run once. Re-run scripts/build_base_dataset.py afterwards.

Let op bij hergebruik van dit patroon: pandas' to_csv schrijft CRLF-regeleinden,
terwijl de bron-CSV LF gebruikt (de rijen die door de add_*.py-scripts zijn
toegevoegd hebben CRLF). Dit script is daarna met een eenmalige
regeleinde-correctie nagelopen zodat het diff alleen de 6 echte cellen toont;
gebruik bij een volgende keer `lineterminator="\\n"` en controleer met
`git diff --stat`.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_base_dataset as b  # noqa: E402

STATUS_GERUIMD = [
    ("NH Kerkhof", "Middelharnis"),
    ("NH kerkhof", "Hoogblokland"),
]
RENAMES = [
    # (oude naam, plaats (opgeschoond), nieuwe naam)
    ("NH begraafplaats", "Puttershoek", "Nieuwe gemeentelijke begraafplaats"),
]


def main() -> None:
    df = b.load_source()
    changed = []

    for naam, plaats in STATUS_GERUIMD:
        rows = df[(df["naam"] == naam) & (df["plaats (opgeschoon)"] == plaats)]
        assert len(rows) == 2, f"{naam}/{plaats}: verwacht 2 rijen (terrein+ingang), gevonden {len(rows)}"
        assert len(rows[rows["begraafplaats"] == "begraafplaats"]) == 1 and len(rows[rows["ingang"] == "ingang"]) == 1
        for idx in rows.index:
            assert df.at[idx, "geruimd"] != "geruimd", f"{naam}/{plaats}: staat al op geruimd"
            df.at[idx, "geruimd"] = "geruimd"
            orig = df.at[idx, "plaats (origineel)"]
            if isinstance(orig, str) and "(geruimd)" not in orig:
                df.at[idx, "plaats (origineel)"] = f"{orig} (geruimd)"
            changed.append(f"geruimd: {naam} ({plaats}), csv-index {idx}")

    for oud, plaats, nieuw in RENAMES:
        rows = df[(df["naam"] == oud) & (df["plaats (opgeschoon)"] == plaats)]
        assert len(rows) == 2, f"{oud}/{plaats}: verwacht 2 rijen (terrein+ingang), gevonden {len(rows)}"
        assert not ((df["naam"] == nieuw) & (df["plaats (opgeschoon)"] == plaats)).any(), f"{nieuw}/{plaats} bestaat al"
        for idx in rows.index:
            df.at[idx, "naam"] = nieuw
            changed.append(f"hernoemd: {oud!r} -> {nieuw!r} ({plaats}), csv-index {idx}")

    assert len(changed) == 6, f"verwacht 6 aangepaste rijen (2x2 status + 2 hernoeming), gevonden {len(changed)}"
    print("Aangepaste rijen:")
    for line in changed:
        print("  -", line)

    df.drop(columns=["orig_idx"]).to_csv(b.SOURCE_CSV, index=False, encoding="utf-8-sig")
    print(f"\nGeschreven naar {b.SOURCE_CSV}")


if __name__ == "__main__":
    main()
