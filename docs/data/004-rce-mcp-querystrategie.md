# Data 004: RCE-MCP querystrategie

## Doel

Voor elk begraafplaatsterrein willen we vanuit de RCE-MCP bepalen:

- ligt het terrein in een beschermd stads- of dorpsgezicht?
- overlapt het terrein een archeologisch rijksmonument?
- liggen er gebouwde rijksmonumenten op of direct aan het terrein?
- welke RCE-objecten en URI's horen bij die relaties?

## Status

Q1, Q2 en Q3 zijn geïmplementeerd als opgeslagen SPARQL in `queries/rce/` en
uitgevoerd via `scripts/fetch_rce.py`. De ruwe extracten staan in
`data/rce/*.geojson`, met provenance per extract in `data/rce/metadata/*.json`.

De extracten voeden al de ruimtelijke join en de viewer (zie hieronder), maar
dit zijn nog niet de definitieve productiequery's: zie "Open punten" voor
bekende beperkingen.

## Primaire RCE-datasets / graphs

Geverifieerd via de RCE-MCP (`graphs_list`, `ontology_describe_class`,
`explore_class`, `semantics_describe_topic`):

- `instanties-rce` - actuele instantiedata, inclusief `heeftJuridischeStatus`
  en `heeftMonumentAard` (alle triples voor deze twee properties leven
  uitsluitend in deze graph);
- `gezicht_hvdl` - polygonen van beschermde stads- en dorpsgezichten
  (`ceo:Gezicht`);
- `owms` - gemeenten/provincies, alleen relevant als we later alsnog op
  gemeente willen filteren (zie "Waarom bounding box, geen gemeentelijst"
  hieronder).

`ceo-ontology`, `cht-thesaurus` en `abr-thesaurus` zijn nog niet gebruikt in
deze eerste extractie.

## Q1. Beschermde stads- en dorpsgezichten

Bestand: `queries/rce/beschermde-gezichten.sparql`

`ceo:Gezicht` heeft drie mogelijke statuswaarden via `heeftGezichtsstatus`:

- `rijksbeschermd stads- of dorpsgezicht` (472 stuks nationaal);
- `gewaardeerd, niet beschermd`;
- `in procedure`.

De query selecteert uitsluitend de eerste, vastgezet op de concept-URI
(niet op labeltekst). Omdat 472 nationaal klein genoeg is om in zijn geheel
op te halen, filtert de query zelf niet op regio; `fetch_rce.py` filtert
lokaal op de bounding box van de begraafplaatsendataset (via de centroid
van elke polygon).

Resultaat: **105 rijksbeschermde gezichten** in de Zuid-Holland bbox, alle
105 met een naam.

## Q2. Rijksmonumenten

Bestand: `queries/rce/rijksmonumenten.sparql`

`heeftJuridischeStatus` vastgezet op de concept-URI voor `rijksmonument`
(niet `voorbeschermd` of `geen rijksmonument`). Nationaal 63.103 stuks - te
veel om zoals Q1 in zijn geheel op te halen. `geof:sfWithin`/`sfIntersects`
veroorzaken structurele timeouts op dit Virtuoso-endpoint (bekende
RCE-MCP-valkuil), dus de bounding box wordt server-side toegepast door de
WKT-string zelf te ontleden (`STRAFTER`/`STRBEFORE` + `xsd:double`). Dat kan
alleen betrouwbaar per geometrietype, dus het bestand bevat twee losse
SELECT-queries (punten, polygonen) die `fetch_rce.py` los uitvoert en per
CHO samenvoegt - de polygoon wint van het punt wanneer een monument beide
heeft (zie sectie 21 van de briefing).

Bounding box (WGS84, extent van `data/generated/begraafplaatsen.geojson`
plus buffer): lon 3.90–5.14, lat 51.66–52.32.

Resultaat: **14.204 rijksmonumenten** in de Zuid-Holland bbox, waarvan
**2.289** met een polygoongeometrie (de overige 11.915 alleen een punt).

### Naam is onvolledig - bekende beperking

`ceo:naam` heeft in de ontologie `rdfs:domain ceo:Naam`, niet
`ceo:Rijksmonument`: een rijksmonument heeft dus geen eigen `ceo:naam`,
alleen optioneel `ceo:heeftNaam -> ceo:Naam -> ceo:naam`. Empirisch heeft
slechts **8.263 van de 63.103** rijksmonumenten (13%, geverifieerd
2026-08-18) zo'n naam-relatie; in het Zuid-Holland-extract is dat
**1.726 van de 14.204 (12%)**.

De overige monumenten hebben doorgaans wel een `ceo:heeftOmschrijving`
(vrije tekst, bv. "Bouwvallig doch schilderachtig dwarshuisje van alleen
begane grond..."). Deze is in deze extractie bewust nog niet meegenomen:
een CHO kan meerdere omschrijvingen hebben, en die in dezelfde OPTIONAL
combineren met een andere multi-valued tak riskeert een cartesisch product
(hetzelfde patroon dat de RCE-MCP beschrijft voor BAG-adressen). Dit moet
als aparte, losse query worden opgehaald en in code samengevoegd voordat de
viewer een presentabel label per monument kan tonen.

## Q3. Archeologische rijksmonumenten

Bestand: `queries/rce/archeologische-rijksmonumenten.sparql`

Semantische selectie via `ceo:heeftMonumentAard` vastgezet op de
concept-URI voor `archeologisch` (niet via keyword-classificatie op naam of
omschrijving - zie sectie 13 van de briefing). Nationaal 1.499 archeologische
rijksmonumenten (1.492 met puntcoördinaten), geverifieerd via de RCE-MCP
semantics-topic `monument_aard`.

Let op het onderscheid met de bredere archeologische registerclasses
(`ceo:ArcheologischTerrein`, `ceo:ArcheologischComplex`,
`ceo:ArcheologischOnderzoeksgebied`, `ceo:Vondstlocatie`, `ceo:Vondsten`,
`ceo:Grondsporen`): dit zijn aparte classes naast `ceo:Rijksmonument`,
onderling gekoppeld via `ceo:bevatObject`/`ceo:ligtInObject`. Deze query
haalt uitsluitend de rijksmonumenten-subset op - dat is de subset die de
briefing "archeologische rijksmonumenten" noemt. De bredere archeologische
registerdata (vondstlocaties, grondsporen, etc.) is niet opgehaald; dat is
een mogelijke latere uitbreiding, geen onderdeel van deze extractie.

Resultaat: **99 archeologische rijksmonumenten** in de Zuid-Holland bbox,
waarvan 76 met een polygoongeometrie. Slechts 8 hebben een naam (dezelfde
beperking als bij Q2).

## Q4. Archeologische onderzoeksgebieden (2026-08-20)

Bestand: `queries/rce/archeologische-onderzoeksgebieden.sparql`

Wens van de gebruiker: de bredere archeologische registerdata die bij Q3
bewust nog niet was opgehaald, specifiek `ceo:ArcheologischOnderzoeksgebied`
(zie semantics-topic "archaeology"). Andere class dan `ceo:Rijksmonument`,
geen `heeftMonumentAard`/`heeftJuridischeStatus` op deze class.

Schaal bleek veel groter dan verwacht: **22.454 onderzoeksgebieden** in de
Zuid-Holland bbox (individuele archeologische vooronderzoeken/opgravings-
projecten, niet een handvol benoemde regio's), vrijwel allemaal polygonen.

**Vertrouwelijkheid**: elk onderzoeksgebied heeft `ceo:heeftVertrouwelijk-
Aanduiding` (2 landelijke waarden: "openbaar"/"vertrouwelijk"). Binnen de
ZH-bbox zijn **200 gebieden gemarkeerd "vertrouwelijk"** - deze worden in
`scripts/fetch_rce.py` (`build_onderzoeksgebieden()`) uitgesloten van de
publieke GeoJSON-extractie: precieze locaties die de bron zelf als
vertrouwelijk aanmerkt horen niet met exacte geometrie op een publieke
kaart (plunderingsrisico op nog niet volledig onderzochte vindplaatsen).
Alleen het aantal wordt bijgehouden (in de extract-metadata), geen
identificerende gegevens van de uitgesloten gebieden zelf. **22.254 van de
22.454** worden gepubliceerd.

**Bestandsgrootte**: op volle precisie was het GeoJSON-bestand 68MB - boven
Cloudflare Pages' limiet van 25MB per bestand. Opgelost met (uitsluitend
voor deze extract, de andere blijven op volle precisie omdat ze klein
genoeg zijn): geometrievereenvoudiging (Douglas-Peucker, tolerantie 0.0001
graad / ~11m - onmerkbaar op de provincie-/stadsschaal waarop deze
referentielaag wordt bekeken, geen bron voor precisiemetingen), coördinaten
afgerond op 6 decimalen, en compacte JSON (geen indent). Resultaat: 17MB.

`ceo:heeftOmschrijving` bleek multi-valued voor een klein deel van de
gebieden binnen de ZH-bbox (22.603 rijen voor 22.454 distincte CHO's) -
alle omschrijvingen worden in code samengevoegd (`" | "`-gescheiden), niet
willekeurig een gekozen.

**Viewer**: laadt lazy (pas bij het aanzetten van de laag, niet standaard
mee bij het openen van de pagina) gezien de bestandsgrootte.

## Functies en type

Q2 en Q3 bevatten drie parallelle velden, alle drie via de RCE-MCP
semantics-topic "functions" geverifieerd op 2026-08-18:

- `oorspronkelijke_functie` - `ceo:heeftOorspronkelijkeFunctie -> ceo:heeftFunctieNaam -> skos:prefLabel`;
- `huidige_functie` - `ceo:heeftHuidigeFunctie -> ceo:heeftFunctieNaam -> skos:prefLabel` (dekking **3,2%**,
  te laag voor een zinvol filter, wordt alleen meegegeven als data);
- `type` - `ceo:heeftType -> ceo:heeftTypeNaam -> skos:prefLabel` (dekking 13,8%).

`skos:prefLabel` voor deze concepten leeft niet in de graph `instanties-rce`
(net als bij `heeftJuridischeStatus`/`heeftMonumentAard`) - de labelopzoeking
moet dus buiten de `GRAPH`-restrictie staan, anders geeft de query stil 0
resultaten. Kostte eerder een debug-ronde voor `oorspronkelijke_functie`.

Alle drie kunnen multi-valued zijn (net als `heeftOmschrijving`): bij
samenvoegen in `fetch_rce.py` "wint" willekeurig een van de waarden. Voor
deze presentatie-/filtervelden is dat geaccepteerd (zelfde afweging als bij
`naam`); zie sectie "Naam is onvolledig" hierboven voor de volledige
redenering.

### Filteren: alleen op oorspronkelijke functie, geen gecureerde boolean

Een eerdere versie had een apart, filterbaar booleanveld
`oorspronkelijke_functie_begraafplaats`, met een handmatig samengestelde
lijst van 9 thesaurusconcepten waarvan het label "begraafplaats"/"kerkhof"
bevat. Dat bleek zelf de platslag die sectie 37 van de briefing afraadt —
de keuze welke functiewaarden "meetellen" hoort bij Leon, niet in een
SPARQL-VALUES-lijst. Dat veld is verwijderd.

In plaats daarvan filtert de viewer nu rechtstreeks op het echte label via
`oorspronkelijke_functie_kort` - `oorspronkelijke_functie` met de RCE-
subtypecode aan het einde afgeknipt (`"Woonhuis(K)"` -> `"Woonhuis"`,
`"Boerderij (M1)"` -> `"Boerderij"`; regex `\s*\([^)]*\)\s*$`, in
`fetch_rce.py`, niet in SPARQL). Dat brengt het aantal distincte
functiewaarden in de Zuid-Holland-extractie terug van 511 naar 483 zonder
er inhoudelijk iets van weg te laten - de ruwe `oorspronkelijke_functie`
blijft ernaast bewaard voor weergave. De viewer bouwt de filterlijst
dynamisch op uit de daadwerkelijk voorkomende waarden (zie
`src/app.js`), dus geen vaste lijst meer om te onderhouden of te herzien.

## Waarom bounding box, geen gemeentelijst

Overwogen alternatief: filteren op `ceo:gemeentenaam` (BRK-relatie, platte
string) met een lijst van Zuid-Hollandse gemeenten uit de `owms`-graph
(`owms:overlapsWith owms:Zuid-Holland`, 110 resultaten inclusief historische,
inmiddels gefuseerde gemeenten).

Bounding box is gekozen omdat:

- geen aanname nodig is over welke *huidige* BRK-gemeentenaam bij welke
  (mogelijk gefuseerde) historische gemeente in de begraafplaatsenbron hoort;
- begraafplaatsen/monumenten vlak over een provinciegrens niet stilzwijgend
  worden uitgesloten;
- de bbox direct is afgeleid van de feitelijke brondata-extent in plaats van
  een handmatig samengestelde lijst.

Nadeel: de extractie bevat ook monumenten die strikt buiten Zuid-Holland
liggen maar wel binnen de bbox vallen (de bbox is een rechthoek, geen
provinciegrens). Dat is voor dit doel onschadelijk: de uiteindelijke
ruimtelijke relatie met een begraafplaats wordt sowieso lokaal met Shapely
bepaald, dus overtollige monumenten ver van elke begraafplaats vallen daar
vanzelf af.

## Reproduceerbaarheid

`scripts/fetch_rce.py` voert de opgeslagen queries opnieuw uit tegen
`https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/sparql` en
overschrijft `data/rce/*.geojson` + `data/rce/metadata/*.json`. Elk
metadata-bestand bevat: bron, endpoint, querybestand, extractiedatum
(`retrieved_at`), featuretelling, ruwe tellingen per deelquery en de
gebruikte bbox. Vereiste Python-pakketten staan in `requirements.txt`.

## Al gebouwd op deze extracten

De lokale ruimtelijke join tussen `data/generated/begraafplaatsen.geojson`
en Q1/Q2/Q3 draait via `scripts/analyse_spatial.py` (output
`data/generated/analyse.geojson`), zie
[005 Erfgoedrelaties resultaten](005-erfgoedrelaties-resultaten.md).

## Aanwijzingsinformatie (opgelost, 2026-08-19)

Onderzocht of de graph `aanwijzingenmonumenten` zinvolle per-monument
aanwijzingsinformatie bevat, zoals gevraagd. Antwoord: nee -- die graph
bevat in totaal maar 19 triples, en dat zijn allemaal generieke landelijke
beleidsprogramma's/wetten ("Monumentenwet 1961", "MIP",
"Beleidsregel aanwijzing beschermde monumenten 2009", ...), niet gekoppeld
aan individuele CHO's. Bewust niet gebruikt.

In plaats daarvan is `?datumInschrijving`
(`ceo:datumInschrijvingInMonumentenregister`) toegevoegd aan Q2/Q3 -- die
staat rechtstreeks op elk Rijksmonument, 97% dekking nationaal (65.575 van
67.494), 100% in de Zuid-Holland-bbox. Dat is de bruikbare
aanwijzingsinformatie per monument, nu zichtbaar in de viewer-popup als
"Datum inschrijving monumentenregister".

## Open punten

1. `heeftOmschrijving` als naam-fallback ophalen voor rijksmonumenten
   zonder `heeftNaam` (los van de geometrie-query, om cartesisch product te
   vermijden).
