# Dodenakkers: ontwerp- en onderzoeksnotities

Deze map bevat losse Markdown-notities voor ideeën, data-audits en MVP-beslissingen.

## Ideeën

- [001 Architectuur](ideas/001-architectuur.md)
- [002 Viewer](ideas/002-viewer.md)
- [003 Ruimtelijke analyse](ideas/003-ruimtelijke-analyse.md)
- [004 RCE Linked Data](ideas/004-rce-linked-data.md)
- [005 Kadaster en PDOK](ideas/005-kadaster-pdok.md)
- [006 Hosting](ideas/006-hosting.md)

## Data

- [001 Audit van de KML](data/001-kml-audit.md)
- [002 Datamodel begraafplaatsen](data/002-datamodel.md)
- [003 CSV als genormaliseerde bronlaag](data/003-csv-bron-en-koppeling.md)
- [004 RCE-MCP querystrategie](data/004-rce-mcp-querystrategie.md)
- [Auditresultaten basisdataset](data/kml-audit-resultaten.md)
- [005 Erfgoedrelaties resultaten](data/005-erfgoedrelaties-resultaten.md)

## MVP

- [001 Eerste MVP](mvp/001-eerste-mvp.md)

## Belangrijkste huidige besluiten

- de genormaliseerde CSV is de primaire build-bron; de KML blijft oorspronkelijke kaartbron;
- polygoon = terrein van de begraafplaats;
- punt = ingang/toegang;
- oppervlakte en omtrek worden uit de terreinpolygoon berekend;
- `geruimd` wordt als expliciet statusveld gemodelleerd;
- statusconflicten tussen punt en polygoon worden gerapporteerd en niet stil gecorrigeerd;
- RCE-extracten (beschermde gezichten, rijksmonumenten, archeologische rijksmonumenten) worden opgehaald via `scripts/fetch_rce.py` met opgeslagen SPARQL in `queries/rce/`, zie [004 RCE-MCP querystrategie](data/004-rce-mcp-querystrategie.md);
- de ruimtelijke join tussen begraafplaatsen en de RCE-extracten draait via `scripts/analyse_spatial.py` (output `data/generated/analyse.geojson`), zie [005 Erfgoedrelaties resultaten](data/005-erfgoedrelaties-resultaten.md);
- een eerste MapLibre-viewer (`src/index.html`/`app.js`) toont terrein, ingangen, beschermde gezichten en rijksmonumenten met filters op geruimd/statusconflict/erfgoedrelaties, tegen de PDOK BRT-achtergrondkaart (grijs) als ondergrond;
- de vier bekende `geruimd`-statusconflicten zijn exporteerbaar naar `data/generated/statusconflicten.csv` via `scripts/export_statusconflicten.py`, met CSV-regelnummers voor handmatige aanvulling door Leon.

## Bekend openstaand punt

`scripts/build_base_dataset.py` is nog een stub: de huidige `data/generated/begraafplaatsen.geojson`/`analyse.geojson` zijn reproduceerbaar wat betreft de RCE-verrijking, maar de basisdataset zelf (terrein/ingang-koppeling vanuit de CSV) is nog niet als werkende code in de repository herbouwd — zie sectie 1 van [Auditresultaten basisdataset](data/kml-audit-resultaten.md) voor de bekende matching-regels die nog geïmplementeerd moeten worden.

## Nummering

Nieuwe ideeën krijgen een oplopend nummer zodat beslissingen en denkrichtingen later goed terug te vinden zijn.
