# Dodenakkers: ontwerp- en onderzoeksnotities

Deze map bevat losse Markdown-notities voor ideeën, data-audits en MVP-beslissingen.

## Kerncijfers

*Bijgewerkt bij elke build (`scripts/build_base_dataset.py` +
`scripts/analyse_spatial.py`); zie de onderliggende audits voor detail en
methodiek: [Auditresultaten basisdataset](data/kml-audit-resultaten.md) en
[005 Erfgoedrelaties resultaten](data/005-erfgoedrelaties-resultaten.md).*

**Begraafplaatsen** — 463 terreinen, samen circa **527 ha**:

- 421 niet-geruimd, 38 geruimd, 4 met een statusconflict (bron spreekt zichzelf tegen, niet automatisch opgelost);
- kleinste terrein 15,84 m², grootste 268.823,91 m² (26,9 ha), mediaan 3.123,17 m².

**Tegenover beschermde gezichten** (105 rijksbeschermde stads-/dorpsgezichten in de Zuid-Holland-bbox):

- 47 begraafplaatsen liggen volledig binnen een beschermd gezicht;
- 6 overlappen een beschermd gezicht deels;
- 410 hebben geen relatie met een beschermd gezicht.

**Tegenover archeologische rijksmonumenten** (99 in de bbox):

- 0 begraafplaatsen overlappen een archeologisch rijksmonument;
- dichtstbijzijnde niet-overlappende geval: NH kerkhof, Heenvliet, **6,2 m** van een archeologisch rijksmonument — een randgeval, geen "ver weg", zie sectie "Bijna-overlap" in de erfgoedrelaties-audit.

**Tegenover (gebouwde) rijksmonumenten** (14.204 in de bbox):

- 257 begraafplaatsen hebben minstens één rijksmonument binnen 100 m (1.085 relaties in totaal, categorieën `inside_on_site`/`touches`/`intersects`/`0-25m`/`25-100m` — voorlopige werkhypothesen, ruwe afstand blijft altijd bewaard).

Los daarvan, als voorbeeld van wat de functiefilter in de viewer oplevert (geen vaste systeemcategorie, gewoon een zoekopdracht op het echte RCE-label): 65 van de 14.204 rijksmonumenten in de bbox hebben een oorspronkelijke functie waar "begraafplaats" of "kerkhof" in voorkomt — ongeacht of ze bij een van de 463 begraafplaatsen in de buurt liggen.

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
- een eerste MapLibre-viewer (`src/index.html`/`app.js`) toont terrein, ingangen, beschermde gezichten en rijksmonumenten met filters op geruimd/statusconflict/erfgoedrelaties en een doorzoekbaar filter op oorspronkelijke functie (dynamisch opgebouwd uit de data, geen vaste lijst), tegen de PDOK BRT-achtergrondkaart (grijs) als ondergrond, met een korte introtekst en het Dodenakkers-logo bovenaan het paneel voor Leon;
- de vier bekende `geruimd`-statusconflicten zijn exporteerbaar naar `data/generated/statusconflicten.csv` via `scripts/export_statusconflicten.py`, met CSV-regelnummers voor handmatige aanvulling door Leon.

## Reproduceerbaarheid

De volledige keten is nu werkende code, geen handmatige snapshot meer:

```text
CSV (data/Begraafplaatsen Zuid-Holland- Zuid-Holland.csv)
  -> scripts/build_base_dataset.py  -> data/generated/begraafplaatsen.geojson + .csv
  -> scripts/fetch_rce.py           -> data/rce/*.geojson
  -> scripts/analyse_spatial.py     -> data/generated/analyse.geojson
  -> src/index.html + app.js        -> viewer
```

`build_base_dataset.py` implementeert de matchingregels uit
[003 CSV als genormaliseerde bronlaag](data/003-csv-bron-en-koppeling.md) en
faalt met een assertion zodra de bekende invarianten (924/463/461,
449/12/1/1 koppelwijzen, 4 statusconflicten) niet meer kloppen. Geverifieerd
tegen de eerder handmatig gebouwde snapshot: identieke uitkomst, op de
opmaak van `bron_rij_ingang` na (voorheen `18.0`, nu `18` -- het brongegeven
was altijd een geheel getal).

## Hosting

Live voor Leon op **https://dodenakkers-zh.pages.dev/** (Cloudflare Pages,
project `dodenakkers-zh`, account jolietjakeblues64@gmail.com). Gekozen
boven GitHub Pages omdat dat account al draait voor doorzoekerfgoed.nl —
zie [006 Hosting](ideas/006-hosting.md) voor de oorspronkelijke afweging
(die inmiddels is herzien).

`site/` is een build-artefact (gitignored, niet committen) dat alleen bevat
wat de viewer nodig heeft — niet de hele repo. Opnieuw bouwen en deployen:

```bash
python scripts/build_site.py
npx wrangler pages deploy site --project-name dodenakkers-zh --branch main
```

`scripts/build_site.py` kopieert `src/index.html`/`style.css`/`app.js` en de
drie GeoJSON-bestanden die de viewer nodig heeft naar `site/`, en herschrijft
`app.js`'s `../data/...`-paden naar `data/...` (index.html staat in `site/`
op het root-niveau, niet onder `src/`). Nog geen automatische deploy bij
`git push` -- dat is een mogelijke volgende stap zodra dit meer dan een
testversie voor Leon hoeft te zijn.

## Nummering

Nieuwe ideeën krijgen een oplopend nummer zodat beslissingen en denkrichtingen later goed terug te vinden zijn.
