#!/usr/bin/env python3
"""
Assemble a clean, minimal static site for deployment (Cloudflare Pages).

Only copies what the viewer actually needs -- not the whole repository
(docs, queries, scripts, source CSV stay out of the deployed site). Flattens
src/ + data/ into a single site/ root so the page is reachable at "/"
instead of "/src/index.html": app.js's DATA paths are rewritten from
"../data/..." (correct for src/index.html) to "data/..." (correct once
index.html sits at the site root next to a data/ sibling).

Output: site/ (gitignored, rebuilt by this script -- not committed).
"""
from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"

FILES_TO_COPY = [
    (REPO_ROOT / "src" / "index.html", SITE_DIR / "index.html"),
    (REPO_ROOT / "src" / "style.css", SITE_DIR / "style.css"),
    (REPO_ROOT / "data" / "generated" / "analyse.geojson", SITE_DIR / "data" / "generated" / "analyse.geojson"),
    (REPO_ROOT / "data" / "rce" / "beschermde-gezichten.geojson", SITE_DIR / "data" / "rce" / "beschermde-gezichten.geojson"),
    (REPO_ROOT / "data" / "rce" / "rijksmonumenten.geojson", SITE_DIR / "data" / "rce" / "rijksmonumenten.geojson"),
    (
        REPO_ROOT / "images" / "Dodenakkers-logo-68015ff5.webp",
        SITE_DIR / "images" / "Dodenakkers-logo-68015ff5.webp",
    ),
]


def main() -> None:
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    for src, dst in FILES_TO_COPY:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"{src.relative_to(REPO_ROOT)} -> {dst.relative_to(REPO_ROOT)}")

    app_js = (REPO_ROOT / "src" / "app.js").read_text(encoding="utf-8")
    rewritten = app_js.replace("../data/generated/", "data/generated/").replace("../data/rce/", "data/rce/")
    if rewritten == app_js:
        raise RuntimeError("app.js: geen '../data/' paden gevonden om te herschrijven -- src/app.js gewijzigd?")
    (SITE_DIR / "app.js").write_text(rewritten, encoding="utf-8")
    print(f"src/app.js -> site/app.js (../data/ -> data/)")

    total_bytes = sum(f.stat().st_size for f in SITE_DIR.rglob("*") if f.is_file())
    print(f"\nsite/ klaar, {total_bytes / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
