# Dodenakkers: ontwerp- en onderzoeksnotities

Deze map bevat losse Markdown-notities voor ideeën, data-audits en MVP-beslissingen.

## Kerncijfers

*Bijgewerkt bij elke build (`scripts/build_base_dataset.py` +
`scripts/analyse_spatial.py`); zie de onderliggende audits voor detail en
methodiek: [Auditresultaten basisdataset](data/kml-audit-resultaten.md) en
[005 Erfgoedrelaties resultaten](data/005-erfgoedrelaties-resultaten.md).*

**Begraafplaatsen** - 448 terreinen, samen circa **520 ha**:

- 401 niet-geruimd, 47 geruimd, 0 statusconflicten (de eerdere 4 zijn op 2026-08-20 door Leon bevestigd als geruimd en opgelost in de bron, zie [003 CSV als genormaliseerde bronlaag](data/003-csv-bron-en-koppeling.md#statusconflicten-2026-08-20-opgelost); 2 losstaande correcties -- Oudenhoorn/Gem. begraafplaats en Stad aan 't Haringvliet/NH kerkhof -- kwamen er op 2026-08-22 bij van de opdrachtgever zelf);
- kleinste terrein 13,49 m², grootste 268.823,91 m² (26,9 ha), mediaan 3.177,55 m².
- was 463 tot 2026-08-19: 20 begraafplaatsen in Vijfheerenlanden-dorpen (nu provincie Utrecht, niet Zuid-Holland) verwijderd uit de bron, zie [003 CSV als genormaliseerde bronlaag](data/003-csv-bron-en-koppeling.md#vijfheerenlanden-2026-08-19-bronwijziging);
- 443 -> 446 op 2026-08-23: 3 begraafplaatsen (Nieuwe Joodse begraafplaats Schiedam, Grafmonument juffrouw Begeer Voorschoten, NH Kerkhof Oud-Alblas) toegevoegd uit Leons "Tijdelijk Zuid-Holland.kmz", zie [003 CSV als genormaliseerde bronlaag](data/003-csv-bron-en-koppeling.md#tijdelijk-zuid-holland-kmz-2026-08-23-bronwijziging);
- 446 -> 448 op 2026-08-26: nog 2 begraafplaatsen (NH kerkhof, De Lier; NH Kerkhof, Oostvoorne; beide geruimd) toegevoegd uit een tweede "Tijdelijk Zuid-Holland"-kmz van Leon, zie [003 CSV als genormaliseerde bronlaag](data/003-csv-bron-en-koppeling.md#tijdelijk-zuid-holland-2-kmz-2026-08-26-bronwijziging).

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
- [006 ABR2-thesaurus verkenning](data/006-abr-thesaurus-verkenning.md)

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
- `scripts/export_statusconflicten.py` exporteert eventuele `geruimd`-statusconflicten naar `data/generated/statusconflicten.csv` (met CSV-regelnummers) zodat Leon ze handmatig kan annoteren; de 4 die zich hebben voorgedaan zijn op 2026-08-20 opgelost, het bestand is nu leeg;
- de filters in het paneel zijn twee groepen met andere combinatielogica (2026-08-23): de drie status-checkboxes (geruimd/niet-geruimd/statusconflict) verbreden de selectie (OR/unie) omdat het elkaar uitsluitende toestanden van hetzelfde veld zijn, de drie erfgoed-checkboxes versmallen (AND) omdat een begraafplaats meerdere erfgoedrelaties tegelijk kan hebben -- zie de toelichting bij `applyFilters()` in `src/app.js`;
- het paneel heeft een naam/plaats-zoekveld (los van de facet-filters, versmalt er altijd bovenop) en de secties zijn inklapbaar (`<details>`), met Zoeken/Ondergrond/Lagen/Filters standaard open en Functie/Legenda standaard dicht om het paneel compacter te maken;
- de legenda dimt items waarvan de bijbehorende laag uit staat, zodat de legenda meteen laat zien wat er op de kaart te zien is;
- Oudenhoorn had kortstondig een terrein met twee eigen ingangen (`EXTRA_INGANG_EXCEPTIONS`), maar Leon draaide de geruimd-status en de ingangtoewijzing dezelfde dag om na het zien van de live kaart; sindsdien heeft elk terrein weer precies 1 ingang, zoals de rest van de dataset, zie [003 CSV als genormaliseerde bronlaag](data/003-csv-bron-en-koppeling.md#oudenhoorn-2026-08-23-opgelost----in-twee-stappen-tweede-stap-definitief).
- twee viewer-fixes uit Leons/Renes feedbacklijst (2026-08-26): de ingang-popup toont niet langer de kale boolean `Gedeelde ingang: false`, maar een leesbaar `Type`-veld (`Hoofdingang` of `Gedeeld (ook ingang van naburig terrein)`); de rijksmonumentlagen renderen nu boven de terreinvlak-fill (`map.moveLayer(...)` zonder tweede argument) zodat de puntmarkers niet verkleuren onder het halftransparante vlak, gemeld door Rene (kleurenblind).
- WCAG 2.1 AA-audit (2026-08-26, `axe-core` headless-scan + handmatige contrastcontrole): 3 echte issues opgelost -- de rijksmonument-afstandsslider (`#rm-threshold`) had geen toegankelijke naam (nu `aria-label`); `.hint`- en `.count`-tekst (`#999`/`#888` op wit, resp. 2,85:1 en 3,54:1) haalden de AA-drempel van 4,5:1 niet, nu `#767676` (4,54:1); de MapLibre-attributielinks rechtsonder waren alleen via kleur te onderscheiden van omringende tekst (2,02:1, SC 1.4.1), nu met underline. Geen andere echte violations gevonden; axe's resterende "incomplete" color-contrast-melding is een bekende beperking bij het halftransparante paneel bovenop de canvaskaart, niet een echt contrastprobleem (handmatig met de gebruikte hexkleuren tegen wit geverifieerd).
- security- en UX-ronde (2026-08-26): `_headers` toegevoegd (Cloudflare Pages leest dit uit de root van `site/`, zie `scripts/build_site.py`) met een CSP (`script-src`/`style-src` beperkt tot `'self'` + `unpkg.com`, `img-src`/`connect-src` beperkt tot `'self'` + `service.pdok.nl`, `worker-src`/`child-src blob:` voor MapLibre's workers, `frame-ancestors 'none'` tegen clickjacking naast `X-Frame-Options: DENY`), geverifieerd met een lokale server die de echte headers serveert (geen CSP-violations bij alle bestaande interacties); handmatige controle van `maplibre-gl@4.7.1` (geen npm/CDN-package, dus geen `npm audit`) leverde geen bekende CVE's op (Snyk-advisorydatabase), wel is de laatste versie inmiddels 6.6.0 -- een major-upgrade valt buiten deze ronde, geen acute reden om 'm nu te forceren. Permalink toegevoegd: kaartweergave (center/zoom), ondergrond, laagtoggles, filters, functieselectie en zoekopdracht staan nu in de URL (`history.replaceState`, geen extra terug-geschiedenis) en worden bij het laden teruggezet. Data-export toegevoegd: knop om de huidige gefilterde selectie als CSV of GeoJSON te downloaden. Permalink-kopieerknop en beide exportknoppen zijn eigen kaart-controls rechtsboven (onder de zoom-knoppen), niet in het filterpaneel, om dat niet voller te maken.
- paneel-/popup-opschoning (2026-08-26, wens van Joop): `Koppelwijze ingang` en `ID` weg uit het begraafplaats-popup, `Geometriebron` weg uit het rijksmonument-popup -- alle drie interne technische velden zonder betekenis voor Leon/Rene. Typografie in het paneel teruggebracht van 6 door elkaar lopende tekstgroottes (16/13/12.5/12/11.5/11px, organisch gegroeid) naar 3: 16px voor de titel, 13px (`#panel`'s basis) voor leestekst (labels, checkboxes), 11px voor alle "meta"-tekst (subtitel, hints, tellingen, kopjes, invoervelden, statusregel). `#panel input/select/button` krijgen nu expliciet `font-family: inherit` -- formuliervelden erven dat anders niet van `body` en konden in het systeem-UI-font afwijken van de rest van de tekst.
- statistiekenpagina (2026-08-26, wens van Joop: "zoveel mogelijk overzichten, tabellen enzo"): `src/statistieken.html`/`statistieken.js`, gelinkt vanaf het hoofdpaneel. `scripts/compute_statistics.py` berekent alles vooraf naar `data/generated/statistieken.json` (zelfde scheiding rekenen/tonen als de rest van de site) -- basisstatistieken, per-plaats-tabellen (meeste begraafplaatsen/geruimd/oppervlakte -- let op: "plaats" is dorp/stad, geen gemeente, die kolom bestaat niet in de bron), beschermde gezichten, rijksmonumenten-nabijheid (incl. meest voorkomende functie in de buurt), archeologie en ingangen. Twee tabellen buiten de bestaande 250m-relaties om, met een eigen ongelimiteerde `STRtree.nearest()`-berekening zoals `scripts/analyse_spatial.py`: nabijheid tot een molen (318 in de bbox, functiecategorie `Molen`/`Industrie- en poldermolen`/`Korenmolen`/`Ondermolen`/`Bovenmolen`/`Boezemmolen`) en tot een kasteel/buitenplaats (118). Ontdekt tijdens het bouwen: **22 begraafplaatsen zijn zelf (deels) een rijksmonument** (functie `Begraafplaats`/`-hek`/`-aula`/`Dierenbegraafplaats` op/grenzend aan het terrein) -- een eigen tabel. Bijvangst: 2 plaats-veldfouten in de bron gevonden en gecorrigeerd, zie [003 CSV als genormaliseerde bronlaag](data/003-csv-bron-en-koppeling.md#twee-plaats-velden-gecorrigeerd-2026-08-26-bijvangst).

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
434/11/1/0 koppelwijzen, 0 statusconflicten) niet meer kloppen. Geverifieerd
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
wat de viewer nodig heeft - niet de hele repo.

`scripts/build_site.py` kopieert `src/index.html`/`style.css`/`app.js` en de
drie GeoJSON-bestanden die de viewer nodig heeft naar `site/`, en herschrijft
`app.js`'s `../data/...`-paden naar `data/...` (index.html staat in `site/`
op het root-niveau, niet onder `src/`).

### Automatische deploy (2026-08-23)

De Cloudflare Pages-project `dodenakkers-zh` is direct aan deze GitHub-repo
gekoppeld (Cloudflare's eigen Git-integratie, hetzelfde patroon als
doorzoekerfgoed.nl). Cloudflare bouwt en deployt zelf bij elke push naar
`main` — build command `python scripts/build_site.py`, output directory
`site`. Geen GitHub Action, geen API-token, geen handmatig `wrangler`-
commando meer nodig. Zie
[006 Hosting](ideas/006-hosting.md#automatische-deploy-2026-08-23) voor de
aanloop (een eerdere, inmiddels verwijderde poging met een GitHub Action +
API-token werkte ook, maar was nodeloos ingewikkeld vergeleken met deze
Git-integratie).

Handmatig blijft ook mogelijk (bv. om een niet-main-branch te testen):

```bash
python scripts/build_site.py
npx wrangler pages deploy site --project-name dodenakkers-zh --branch main
```

## Nummering

Nieuwe ideeën krijgen een oplopend nummer zodat beslissingen en denkrichtingen later goed terug te vinden zijn.
