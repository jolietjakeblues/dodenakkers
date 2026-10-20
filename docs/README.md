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

**Begraafplaatsen** - 450 terreinen, samen circa **550 ha**:

- 400 niet-geruimd, 50 geruimd, 0 statusconflicten (komt exact overeen met de Excel van de domeinexpert: 316 in gebruik + 84 gesloten, 50 geruimd; NH Kerkhof Middelharnis en NH kerkhof Hoogblokland zijn op 2026-10-19 op geruimd gezet, zie [003](data/003-csv-bron-en-koppeling.md));
- 64 gemeentelijk beschermd en 386 niet, volgens de Excel van de domeinexpert (filter in de viewer; elk terrein is aan zijn Excel-rij gekoppeld, zie [007](data/007-datering-bevindingen.md));
- kleinste terrein 13,49 m², grootste 301.096,18 m² (30,1 ha, Natuurbegraafplaats Staelduinen), mediaan 3.220,27 m².

**Tegenover beschermde gezichten** (105 rijksbeschermde stads-/dorpsgezichten in de Zuid-Holland-bbox):

- 44 begraafplaatsen liggen volledig binnen een beschermd gezicht;
- 5 overlappen een beschermd gezicht deels;
- 401 hebben geen relatie met een beschermd gezicht.

**Tegenover archeologische rijksmonumenten** (99 in de bbox):

- 0 begraafplaatsen overlappen een archeologisch rijksmonument;
- dichtstbijzijnste niet-overlappende geval: NH kerkhof, Heenvliet, **6,2 m** van een archeologisch rijksmonument - een randgeval, geen "ver weg", zie sectie "Bijna-overlap" in de erfgoedrelaties-audit.

**Tegenover (gebouwde) rijksmonumenten** (14.204 in de bbox):

- 248 begraafplaatsen hebben minstens één rijksmonument binnen 100 m (318 binnen 250 m -- de dataset bewaart relaties tot 250 m zodat de schuifregelaar in de viewer verder dan 100 m kan verkennen; categorieën `inside_on_site`/`touches`/`intersects`/`0-25m`/`25-100m`/`100-250m` - voorlopige werkhypothesen, ruwe afstand blijft altijd bewaard).

Los daarvan, als voorbeeld van wat de functiefilter in de viewer oplevert (geen vaste systeemcategorie, gewoon een zoekopdracht op het echte RCE-label): 65 van de 14.204 rijksmonumenten in de bbox hebben een oorspronkelijke functie waar "begraafplaats" of "kerkhof" in voorkomt - ongeacht of ze bij een van de 450 begraafplaatsen in de buurt liggen.

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
- [007 Datering - bevindingen](data/007-datering-bevindingen.md)
- [008 Datering - ontbrekend](data/008-datering-ontbrekend.md)
- [009 Vragen aan de domeinexpert](data/009-vragen-domeinexpert.md)
- [010 Oude kaarten (Allmaps)](data/010-oude-kaarten.md)

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
- de legenda dimt items waarvan de bijbehorende laag uit staat, zodat de legenda meteen laat zien wat er op de kaart te zien is;
- "Verdwenen begraafplaatsen" is een zelfstandige, gegeocodeerde puntenlaag uit een eigen bron van de domeinexpert (KMZ), bewust zonder koppeling aan de 450 hoofdterreinen -- zie [methode.html](../src/methode.html) voor de zes datacategorieën en waarom een koppeling hier bewust is afgewezen;
- "Datering" (jaartal/periode per begraafplaats, eigen CSV-bron van de domeinexpert) is wél gekoppeld aan de hoofddataset -- op het dichtstbijzijnde adres via de ingang-coördinaat, met een afstandsdrempel van 300m (`nearest_datering()` in `scripts/analyse_spatial.py`) -- en zichtbaar als veld in het begraafplaats-popup en als klikbare periode-filter in het paneel, niet als eigen kaartlaag.

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
faalt met een assertion zodra de bekende invarianten (899/450/449,
438/11/1/0 koppelwijzen, 0 statusconflicten) niet meer kloppen.

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
