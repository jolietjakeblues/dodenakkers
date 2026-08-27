#!/usr/bin/env python3
"""
Assemble a clean, minimal static site for deployment (Cloudflare Pages).

Only copies what the viewer actually needs -- not the whole repository
(docs, queries, scripts, source CSV stay out of the deployed site). Flattens
src/ + data/ + images/ into a single site/ root so the page is reachable at
"/" instead of "/src/index.html": app.js's DATA paths and index.html's
logo/favicon paths are rewritten from "../data/..."/"../images/..."
(correct for src/index.html, one level down from the repo root) to
"data/..."/"images/..." (correct once index.html sits at the site root
next to data/ and images/ siblings).

Output: site/ (gitignored, rebuilt by this script -- not committed).
"""
from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"

FILES_TO_COPY = [
    (REPO_ROOT / "src" / "style.css", SITE_DIR / "style.css"),
    (REPO_ROOT / "data" / "generated" / "analyse.geojson", SITE_DIR / "data" / "generated" / "analyse.geojson"),
    (REPO_ROOT / "data" / "generated" / "statistieken.json", SITE_DIR / "data" / "generated" / "statistieken.json"),
    (
        REPO_ROOT / "data" / "generated" / "kandidaat_begraafplaatsen.json",
        SITE_DIR / "data" / "generated" / "kandidaat_begraafplaatsen.json",
    ),
    (REPO_ROOT / "data" / "rce" / "beschermde-gezichten.geojson", SITE_DIR / "data" / "rce" / "beschermde-gezichten.geojson"),
    (REPO_ROOT / "data" / "rce" / "rijksmonumenten.geojson", SITE_DIR / "data" / "rce" / "rijksmonumenten.geojson"),
    (
        REPO_ROOT / "data" / "rce" / "archeologische-onderzoeksgebieden.geojson",
        SITE_DIR / "data" / "rce" / "archeologische-onderzoeksgebieden.geojson",
    ),
    (
        REPO_ROOT / "data" / "pdok" / "provincie-zuid-holland.geojson",
        SITE_DIR / "data" / "pdok" / "provincie-zuid-holland.geojson",
    ),
    (
        REPO_ROOT / "data" / "pdok" / "gemeenten-zuid-holland.geojson",
        SITE_DIR / "data" / "pdok" / "gemeenten-zuid-holland.geojson",
    ),
    (
        REPO_ROOT / "data" / "zuid-holland" / "chs-archeologie-provinciaal-belang.geojson",
        SITE_DIR / "data" / "zuid-holland" / "chs-archeologie-provinciaal-belang.geojson",
    ),
    (
        REPO_ROOT / "images" / "Dodenakkers-logo-68015ff5.webp",
        SITE_DIR / "images" / "Dodenakkers-logo-68015ff5.webp",
    ),
    # Cloudflare Pages leest _headers uit de root van de build-output (geen
    # paden erin, dus geen REWRITES nodig -- gewoon 1-op-1 kopieren).
    (REPO_ROOT / "_headers", SITE_DIR / "_headers"),
]

REWRITES = [
    ("../data/generated/", "data/generated/"),
    ("../data/rce/", "data/rce/"),
    ("../data/pdok/", "data/pdok/"),
    ("../data/zuid-holland/", "data/zuid-holland/"),
    ("../images/", "images/"),
]


def copy_with_rewrites(src: Path, dst: Path) -> None:
    text = src.read_text(encoding="utf-8")
    rewritten = text
    for old, new in REWRITES:
        rewritten = rewritten.replace(old, new)
    if rewritten == text:
        raise RuntimeError(f"{src.relative_to(REPO_ROOT)}: geen paden gevonden om te herschrijven -- gewijzigd?")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(rewritten, encoding="utf-8")
    print(f"{src.relative_to(REPO_ROOT)} -> {dst.relative_to(REPO_ROOT)} (paden herschreven)")


def main() -> None:
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    for src, dst in FILES_TO_COPY:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"{src.relative_to(REPO_ROOT)} -> {dst.relative_to(REPO_ROOT)}")

    copy_with_rewrites(REPO_ROOT / "src" / "index.html", SITE_DIR / "index.html")
    copy_with_rewrites(REPO_ROOT / "src" / "app.js", SITE_DIR / "app.js")
    copy_with_rewrites(REPO_ROOT / "src" / "statistieken.html", SITE_DIR / "statistieken.html")
    copy_with_rewrites(REPO_ROOT / "src" / "statistieken.js", SITE_DIR / "statistieken.js")
    copy_with_rewrites(REPO_ROOT / "src" / "kandidaten.html", SITE_DIR / "kandidaten.html")
    copy_with_rewrites(REPO_ROOT / "src" / "kandidaten.js", SITE_DIR / "kandidaten.js")

    total_bytes = sum(f.stat().st_size for f in SITE_DIR.rglob("*") if f.is_file())
    print(f"\nsite/ klaar, {total_bytes / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
