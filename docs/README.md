# Dodenakkers: ontwerp- en onderzoeksnotities

Deze map bevat losse Markdown-notities voor ideeën, data-audits en MVP-beslissingen.
Voor het chronologische logboek van elke wijziging (met datum, aanleiding en
achterliggende afwegingen) zie [geschiedenis.md](geschiedenis.md).

## Kerncijfers

*Bijgewerkt bij elke build (`scripts/build_base_dataset.py` +
`scripts/analyse_spatial.py`); zie de onderliggende audits voor detail en
methodiek: [Auditresultaten basisdataset](data/kml-audit-resultaten.md) en
[005 Erfgoedrelaties resultaten](data/005-erfgoedrelaties-resultaten.md). Zie
[geschiedenis.md](geschiedenis.md) voor hoe deze aantallen tot stand kwamen
(brondata-updates, correcties).*

**Begraafplaatsen** - 448 terreinen, samen circa **520 ha**:

- 401 niet-geruimd, 47 geruimd, 0 statusconflicten;
- kleinste terrein 13,49 m², grootste 268.823,91 m² (26,9 ha), mediaan 3.177,55 m².

**Tegenover beschermde gezichten** (105 rijksbeschermde stads-/dorpsgezichten in de Zuid-Holland-bbox):

- 43 begraafplaatsen liggen volledig binnen een beschermd gezicht;
- 5 overlappen een beschermd gezicht deels;
- 400 hebben geen relatie met een beschermd gezicht.

**Tegenover archeologische rijksmonumenten** (99 in de bbox):

- 0 begraafplaatsen overlappen een archeologisch rijksmonument;
- dichtstbijzijnste niet-overlappende geval: NH kerkhof, Heenvliet, **6,2 m** van een archeologisch rijksmonument - een randgeval, geen "ver weg", zie sectie "Bijna-overlap" in de erfgoedrelaties-audit.

**Tegenover (gebouwde) rijksmonumenten** (14.204 in de bbox):

- 247 begraafplaatsen hebben minstens één rijksmonument binnen 100 m (316 binnen 250 m -- de dataset bewaart relaties tot 250 m zodat de schuifregelaar in de viewer verder dan 100 m kan verkennen; categorieën `inside_on_site`/`touches`/`intersects`/`0-25m`/`25-100m`/`100-250m` - voorlopige werkhypothesen, ruwe afstand blijft altijd bewaard).

Los daarvan, als voorbeeld van wat de functiefilter in de viewer oplevert (geen vaste systeemcategorie, gewoon een zoekopdracht op het echte RCE-label): 65 van de 14.204 rijksmonumenten in de bbox hebben een oorspronkelijke functie waar "begraafplaats" of "kerkhof" in voorkomt - ongeacht of ze bij een van de 448 begraafplaatsen in de buurt liggen.

**Archeologische onderzoeksgebieden** (`ceo:ArcheologischOnderzoeksgebied`, andere class dan rijksmonumenten): 22.254 gebieden in de bbox gepubliceerd als losse, standaard uitgeschakelde kaartlaag (200 gebieden met een "vertrouwelijk"-vlag in de bron zijn uitgesloten, zie [004 RCE-MCP querystrategie](data/004-rce-mcp-querystrategie.md#q4-archeologische-onderzoeksgebieden-2026-08-20)). Geen spatiale koppeling met de begraafplaatsendataset, puur een informatieve referentielaag.

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
- [006 ABR2-thesaurus verkenning](data/006-abr-thesaurus-verkenning.md)

## MVP

- [001 Eerste MVP](mvp/001-eerste-mvp.md)

## Architectuur en huidige stand van zaken

- de genormaliseerde CSV is de primaire build-bron; de KML blijft oorspronkelijke kaartbron;
- polygoon = terrein van de begraafplaats;
- punt = ingang/toegang;
- oppervlakte en omtrek worden uit de terreinpolygoon berekend;
- `geruimd` wordt als expliciet statusveld gemodelleerd;
- statusconflicten tussen punt en polygoon worden gerapporteerd en niet stil gecorrigeerd;
- RCE-extracten (beschermde gezichten, rijksmonumenten, archeologische rijksmonumenten) worden opgehaald via `scripts/fetch_rce.py` met opgeslagen SPARQL in `queries/rce/`, zie [004 RCE-MCP querystrategie](data/004-rce-mcp-querystrategie.md);
- de ruimtelijke join tussen begraafplaatsen en de RCE-extracten draait via `scripts/analyse_spatial.py` (output `data/generated/analyse.geojson`), zie [005 Erfgoedrelaties resultaten](data/005-erfgoedrelaties-resultaten.md);
- de MapLibre-viewer (`src/index.html`/`app.js`) toont terrein, ingangen, beschermde gezichten en rijksmonumenten met filters op geruimd/statusconflict/erfgoedrelaties en een doorzoekbaar filter op oorspronkelijke functie (dynamisch opgebouwd uit de data, geen vaste lijst), tegen de PDOK BRT-achtergrondkaart (grijs) als ondergrond;
- de provinciegrens van Zuid-Holland (`scripts/fetch_provinciegrens.py`, PDOK bestuurlijkegebieden WFS, opgeslagen in `data/pdok/`) ligt als toggelbare referentielijn onder alle andere lagen, puur ter oriëntatie;
- archeologische onderzoeksgebieden (`ceo:ArcheologischOnderzoeksgebied`, 22.254 in de bbox) zijn een losse, standaard uitgeschakelde laag die pas bij het aanzetten wordt opgehaald (17MB), zie [004 RCE-MCP querystrategie](data/004-rce-mcp-querystrategie.md#q4-archeologische-onderzoeksgebieden-2026-08-20);
- `scripts/export_statusconflicten.py` exporteert eventuele `geruimd`-statusconflicten naar `data/generated/statusconflicten.csv` (met CSV-regelnummers) zodat de domeinexpert ze handmatig kan annoteren; het bestand is momenteel leeg;
- de filters in het paneel zijn twee groepen met andere combinatielogica: de drie status-checkboxes (geruimd/niet-geruimd/statusconflict) verbreden de selectie (OR/unie) omdat het elkaar uitsluitende toestanden van hetzelfde veld zijn, de drie erfgoed-checkboxes versmallen (AND) omdat een begraafplaats meerdere erfgoedrelaties tegelijk kan hebben -- zie de toelichting bij `applyFilters()` in `src/app.js`;
- het paneel heeft een naam/plaats-zoekveld (los van de facet-filters, versmalt er altijd bovenop) en de secties zijn inklapbaar (`<details>`), met Zoeken/Ondergrond/Lagen/Filters standaard open en Functie/Legenda standaard dicht om het paneel compacter te maken;
- de legenda dimt items waarvan de bijbehorende laag uit staat, zodat de legenda meteen laat zien wat er op de kaart te zien is.

Voor de volledige chronologische geschiedenis van hoe dit tot stand kwam
(elke wijziging met datum, aanleiding en de afwegingen erachter, inclusief
teruggedraaide experimenten) zie [geschiedenis.md](geschiedenis.md).

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
faalt met een assertion zodra de bekende invarianten (891/446/445,
434/11/1/0 koppelwijzen, 0 statusconflicten) niet meer kloppen.

## Hosting

Live voor de domeinexpert op **https://dodenakkers-zh.pages.dev/** (Cloudflare Pages,
project `dodenakkers-zh`, account jolietjakeblues64@gmail.com). Gekozen
boven GitHub Pages omdat dat account al draait voor doorzoekerfgoed.nl —
zie [006 Hosting](ideas/006-hosting.md) voor de oorspronkelijke afweging
(die inmiddels is herzien).

`site/` is een build-artefact (gitignored, niet committen) dat alleen bevat
wat de viewer nodig heeft - niet de hele repo.

`scripts/build_site.py` kopieert `src/index.html`/`style.css`/`app.js` en de
GeoJSON-bestanden die de viewer nodig heeft naar `site/`, en herschrijft
`app.js`'s `../data/...`-paden naar `data/...` (index.html staat in `site/`
op het root-niveau, niet onder `src/`).

### Automatische deploy

De Cloudflare Pages-project `dodenakkers-zh` is direct aan deze GitHub-repo
gekoppeld (Cloudflare's eigen Git-integratie, hetzelfde patroon als
doorzoekerfgoed.nl). Cloudflare bouwt en deployt zelf bij elke push naar
`main` — build command `python scripts/build_site.py`, output directory
`site`. Geen GitHub Action, geen API-token, geen handmatig `wrangler`-
commando meer nodig.

Handmatig blijft ook mogelijk (bv. om een niet-main-branch te testen):

```bash
python scripts/build_site.py
npx wrangler pages deploy site --project-name dodenakkers-zh --branch main
```

### Dependabot

`.github/dependabot.yml` bewaakt wekelijks de `pip`-dependencies in
`requirements.txt` (root). Geen `npm`/`github-actions`-ecosysteem, want die
zijn hier niet van toepassing (maplibre-gl is lokaal gevendord, geen
CI-workflows).

## Licentie

Deze projectcode en -teksten zijn gelicenseerd onder Creative Commons
Attribution 4.0 International (CC BY 4.0), zie [`LICENSE`](../LICENSE) in de
repository-root. De onderliggende brondata (RCE Linked Data, PDOK, CHS
Provincie Zuid-Holland, Kadaster) valt onder de licentievoorwaarden van die
bronnen zelf.

## Nummering

Nieuwe ideeën krijgen een oplopend nummer zodat beslissingen en denkrichtingen later goed terug te vinden zijn.
