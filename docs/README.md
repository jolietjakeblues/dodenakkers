# Dodenakkers: ontwerp- en onderzoeksnotities

Deze map bevat losse Markdown-notities voor ideeën, data-audits en MVP-beslissingen.

## Kerncijfers

*Bijgewerkt bij elke build (`scripts/build_base_dataset.py` +
`scripts/analyse_spatial.py`); zie de onderliggende audits voor detail en
methodiek: [Auditresultaten basisdataset](data/kml-audit-resultaten.md) en
[005 Erfgoedrelaties resultaten](data/005-erfgoedrelaties-resultaten.md).*

**Begraafplaatsen** - 443 terreinen, samen circa **519 ha**:

- 400 niet-geruimd, 43 geruimd, 0 statusconflicten (de eerdere 4 zijn op 2026-08-20 door Leon bevestigd als geruimd en opgelost in de bron, zie [003 CSV als genormaliseerde bronlaag](data/003-csv-bron-en-koppeling.md#statusconflicten-2026-08-20-opgelost); 2 losstaande correcties -- Oudenhoorn/Gem. begraafplaats en Stad aan 't Haringvliet/NH kerkhof -- kwamen er op 2026-08-22 bij van de opdrachtgever zelf);
- kleinste terrein 15,84 m², grootste 268.823,91 m² (26,9 ha), mediaan 3.260,05 m².
- was 463 tot 2026-08-19: 20 begraafplaatsen in Vijfheerenlanden-dorpen (nu provincie Utrecht, niet Zuid-Holland) verwijderd uit de bron, zie [003 CSV als genormaliseerde bronlaag](data/003-csv-bron-en-koppeling.md#vijfheerenlanden-2026-08-19-bronwijziging).

**Tegenover beschermde gezichten** (105 rijksbeschermde stads-/dorpsgezichten in de Zuid-Holland-bbox):

- 43 begraafplaatsen liggen volledig binnen een beschermd gezicht;
- 5 overlappen een beschermd gezicht deels;
- 395 hebben geen relatie met een beschermd gezicht.

**Tegenover archeologische rijksmonumenten** (99 in de bbox):

- 0 begraafplaatsen overlappen een archeologisch rijksmonument;
- dichtstbijzijnste niet-overlappende geval: NH kerkhof, Heenvliet, **6,2 m** van een archeologisch rijksmonument - een randgeval, geen "ver weg", zie sectie "Bijna-overlap" in de erfgoedrelaties-audit.

**Tegenover (gebouwde) rijksmonumenten** (14.204 in de bbox):

- 243 begraafplaatsen hebben minstens één rijksmonument binnen 100 m (1.043 relaties in totaal, categorieën `inside_on_site`/`touches`/`intersects`/`0-25m`/`25-100m` - voorlopige werkhypothesen, ruwe afstand blijft altijd bewaard).

Los daarvan, als voorbeeld van wat de functiefilter in de viewer oplevert (geen vaste systeemcategorie, gewoon een zoekopdracht op het echte RCE-label): 65 van de 14.204 rijksmonumenten in de bbox hebben een oorspronkelijke functie waar "begraafplaats" of "kerkhof" in voorkomt - ongeacht of ze bij een van de 443 begraafplaatsen in de buurt liggen.

**Archeologische onderzoeksgebieden** (`ceo:ArcheologischOnderzoeksgebied`, andere class dan rijksmonumenten, wens van de gebruiker, 2026-08-20): 22.254 gebieden in de bbox gepubliceerd als losse, standaard uitgeschakelde kaartlaag (200 gebieden met een "vertrouwelijk"-vlag in de bron zijn uitgesloten, zie [004 RCE-MCP querystrategie](data/004-rce-mcp-querystrategie.md#q4-archeologische-onderzoeksgebieden-2026-08-20)). Geen spatiale koppeling met de begraafplaatsendataset (nog niet gevraagd), puur een informatieve referentielaag.

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
- de provinciegrens van Zuid-Holland (`scripts/fetch_provinciegrens.py`, PDOK bestuurlijkegebieden WFS, opgeslagen in `data/pdok/`) ligt als toggelbare referentielijn onder alle andere lagen, puur ter oriëntatie;
- archeologische onderzoeksgebieden (`ceo:ArcheologischOnderzoeksgebied`, 22.254 in de bbox) zijn een losse, standaard uitgeschakelde laag die pas bij het aanzetten wordt opgehaald (17MB), zie [004 RCE-MCP querystrategie](data/004-rce-mcp-querystrategie.md#q4-archeologische-onderzoeksgebieden-2026-08-20);
- `scripts/export_statusconflicten.py` exporteert eventuele `geruimd`-statusconflicten naar `data/generated/statusconflicten.csv` (met CSV-regelnummers) zodat Leon ze handmatig kan annoteren; de 4 die zich hebben voorgedaan zijn op 2026-08-20 opgelost, het bestand is nu leeg.

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
faalt met een assertion zodra de bekende invarianten (884/443/441,
430/11/1/1 koppelwijzen, 0 statusconflicten) niet meer kloppen. Geverifieerd
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
wat de viewer nodig heeft - niet de hele repo. Opnieuw bouwen en deployen:

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
