# Dodenakkers Zuid-Holland - programmeerbriefing

Dit document is de centrale briefing voor AI en andere ontwikkelaars die aan deze repository werken.

Het beschrijft:

- wat de opdracht inhoudt;
- welke bronnen leidend zijn;
- hoe de begraafplaatsen-data semantisch moet worden geïnterpreteerd;
- welke afgeleide data we willen bouwen;
- welke ruimtelijke analyses nodig zijn;
- welke uitzonderingen al bekend zijn;
- hoe de viewer moet werken;
- welke technische keuzes voorlopig zijn gemaakt;
- welke aannames nadrukkelijk niet gemaakt mogen worden.

Dit document gaat vóór losse technische aannames in code.

---

## 1. Doel van het project

De opdracht draait om begraafplaatsen in Zuid-Holland.

De kernvraag is niet alleen "toon begraafplaatsen op een kaart", maar:

> maak een kleine ruimtelijke onderzoeksomgeving waarmee snel zichtbaar wordt hoe begraafplaatsen zich verhouden tot beschermd erfgoed.

De domeinexpert wil onder meer kunnen zien:

- welke begraafplaatsen binnen een beschermd stads- of dorpsgezicht liggen;
- welke begraafplaatsen overlappen met archeologische rijksmonumenten;
- welke gebouwde rijksmonumenten op of direct bij een begraafplaats liggen;
- welke begraafplaatsen zelf beschermd of onbeschermd zijn;
- waar mogelijk welke kadastrale percelen relevant zijn.

De kaart is dus een onderzoeksinterface. De echte waarde zit in de onderliggende ruimtelijke analyse en de reproduceerbare dataset.

---

## 2. Belangrijkste domeinregel: terrein en ingang zijn verschillende dingen

De bron bevat voor een begraafplaats twee soorten geometrieën.

### Terrein

Een `Polygon` of in één geval een `GeometryCollection` stelt het fysieke terrein van de begraafplaats voor.

Dit is de geometrie die gebruikt moet worden voor:

- oppervlakte;
- omtrek;
- overlap;
- `within`;
- `intersects`;
- afstand tot erfgoedobjecten;
- kaartvlak;
- ruimtelijke selectie.

### Ingang

Een `Point` stelt de echte ingang of toegang tot de begraafplaats voor.

Dit punt is dus:

- geen centroid;
- geen labelpunt;
- geen duplicaat van het terrein;
- geen geometrie die mag worden afgeleid uit het terrein.

Het ingangspunt is functionele broninformatie en moet behouden blijven.

Mogelijke toepassingen:

- marker in de viewer;
- popup;
- navigatie;
- koppeling aan weg/openbare ruimte;
- later eventueel bereikbaarheid.

### Belangrijk

Nooit een ontbrekende ingang vervangen door een centroid zonder dat expliciet als afgeleide/fallback te markeren.

In de huidige dataset blijft een ontbrekende ingang gewoon `null`.

---

## 3. Primaire bron voor begraafplaatsen

Voor de reproduceerbare build gebruiken we de genormaliseerde CSV:

`Begraafplaatsen Zuid-Holland- Zuid-Holland.csv`

De KML blijft behouden als oorspronkelijke kaartbron en controlemateriaal.

De CSV bevat de velden:

```text
WKT
naam
plaats (origineel)
plaats (opgeschoon)
geruimd
ingang
begraafplaats
```

### Betekenis

`WKT`
: geometrie in WGS84.

`naam`
: bronnaam van het object.

`plaats (origineel)`
: plaatsnaam zoals oorspronkelijk vastgelegd.

`plaats (opgeschoon)`
: genormaliseerde plaatsnaam voor verwerking en matching.

`geruimd`
: expliciete bronstatus.

`ingang`
: markeert dat het record een ingangspunt is.

`begraafplaats`
: markeert dat het record een begraafplaatsterrein is.

---

## 4. Huidige bronstatistiek

De genormaliseerde bron bevat:

- 924 bronrecords;
- 463 begraafplaatsterreinen;
- 461 ingangspunten;
- 462 terreinpolygonen;
- 1 terrein-`GeometryCollection`.

De gegenereerde basisdataset bevat daarom:

- 463 logische begraafplaatsrecords;
- één record per terrein.

Dit is een belangrijke invariant.

Bij nieuwe builds moet code deze aantallen controleren zolang de bron niet bewust is gewijzigd.

---

## 5. Matching van terrein en ingang

Terrein en ingang worden samengevoegd tot één logisch begraafplaatsrecord.

### Volgorde van matching

1. Exacte unieke combinatie van:
   - genormaliseerde `naam`;
   - `plaats (opgeschoon)`.

2. Voor resterende gevallen:
   - ruimtelijke nabijheid;
   - controle van naamvariant;
   - controle van plaats.

3. Bekende uitzonderingen expliciet modelleren.

4. Nooit stilzwijgend een onzekere koppeling forceren.

### Huidige resultaten

Van 463 terreinen:

- 449 koppelen exact via naam + opgeschoonde plaats;
- 12 koppelen via ruimtelijke nabijheid bij een naamvariant;
- 1 terrein gebruikt een ingang die ook voor een ander terrein wordt gebruikt;
- 1 terrein heeft geen ingang.

De gegenereerde dataset bevat per record een veld dat de koppelwijze documenteert.

Gebruik bijvoorbeeld waarden als:

```text
exact_name_place
spatial_name_variant
shared_entrance_spatial
missing
```

---

## 6. Bekende uitzonderingen

### 6.1 Duinrust, Katwijk aan Zee

Er is één ingangspunt:

`Gem. begraafplaats Duinrust en NH begraafplaats`

Dit punt hoort functioneel bij twee aangrenzende terreinrecords:

- `Gem. begraafplaats Duinrust`;
- `NH begraafplaats Duinrust`.

De ingang moet dus aan beide logische begraafplaatsrecords gekoppeld kunnen worden.

Markeer:

```text
ingang_gedeeld = true
```

Niet samenvoegen tot één terrein tenzij later expliciet uit brononderzoek blijkt dat dit gewenst is.

### 6.2 Oudenhoorn

Voor:

`Gem. begraafplaats, Oudenhoorn`

is in de huidige bron geen ingang gevonden.

Regel:

```text
ingang = null
```

Geen centroid verzinnen.

---

## 7. Status `geruimd`

`geruimd` is een domeinstatus en moet een expliciet veld in de afgeleide dataset zijn.

Gebruik niet alleen de tekst in de naam.

De genormaliseerde CSV bevat al een apart veld `geruimd`.

### Status op recordniveau

Terrein en ingang kunnen allebei een bronwaarde hebben.

Bewaar daarom:

```text
geruimd_bron_terrein
geruimd_bron_ingang
status_conflict
geruimd
```

### Samenvoegregel

Als terrein en ingang dezelfde status hebben:

```text
geruimd = true | false
status_conflict = false
```

Als terrein en ingang elkaar tegenspreken:

```text
geruimd = null
status_conflict = true
```

Geen automatische voorkeur voor terrein of ingang zonder inhoudelijke validatie.

### Bekende statusconflicten

Er zijn momenteel vier bekende conflicten:

- RK begraafplaats, Oude Wetering;
- Oud NH kerkhof, Schoonhoven;
- Vm. NH kerkhof, Maasland;
- NH Kerkhof, Zwammerdam.

Deze moeten als controlecases in tests of auditoutput terugkomen.

---

## 8. Oppervlakte en omtrek

Oppervlakte en omtrek komen niet als betrouwbare expliciete bronvelden uit de KML/CSV.

Ze worden berekend uit de terrein-geometrie.

### Projectie

Brongeometrie:

```text
EPSG:4326
```

Voor metrische berekeningen transformeren naar:

```text
EPSG:28992
RD New
```

Daarna berekenen:

```text
oppervlakte_m2
oppervlakte_ha
omtrek_m
```

### Regels

- niet rekenen in graden;
- geen Web Mercator gebruiken voor nauwkeurige oppervlakteberekening;
- waarden afronden voor presentatie, maar intern liefst voldoende precisie bewaren;
- extreem kleine/grote waarden als audit-signaal behandelen, niet automatisch als fout.

---

## 9. Gewenst logisch datamodel

Conceptueel:

```text
Begraafplaats
├── id
├── naam
├── plaats
├── status
│   ├── geruimd
│   └── status_conflict
│
├── terrein
│   ├── geometry
│   ├── oppervlakte_m2
│   ├── oppervlakte_ha
│   └── omtrek_m
│
├── ingang
│   ├── point
│   ├── lon
│   ├── lat
│   ├── koppelwijze
│   └── gedeeld
│
├── erfgoedrelaties
│   ├── beschermd_gezicht
│   ├── archeologische_rijksmonumenten
│   └── rijksmonumenten
│
└── provenance
```

---

## 10. GeoJSON-model

De hoofdgeometrie van een feature is altijd het terrein.

Voorbeeld:

```json
{
  "type": "Feature",
  "properties": {
    "id": "zh-0001",
    "naam": "NH Kerkhof, Oude Wetering",
    "plaats": "Oude Wetering",
    "geruimd": false,
    "status_conflict": false,
    "oppervlakte_m2": 1234.56,
    "oppervlakte_ha": 0.1235,
    "omtrek_m": 156.78,
    "ingang": {
      "type": "Point",
      "coordinates": [4.645, 52.212]
    },
    "ingang_lon": 4.645,
    "ingang_lat": 52.212,
    "ingang_koppelwijze": "exact_name_place",
    "ingang_gedeeld": false
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": []
  }
}
```

### Waarom de ingang in properties staat

GeoJSON heeft per Feature één hoofdgeometrie.

Voor de ruimtelijke analyse is het terrein de logische hoofdgeometrie.

De ingang blijft daarom als apart GeoJSON Point-object in de properties aanwezig.

Een alternatieve output met aparte lagen mag later worden toegevoegd, maar de basisdataset moet één record per begraafplaatsterrein houden.

---

## 11. IDs

Gebruik stabiele IDs.

Huidige gegenereerde vorm:

```text
zh-0001
zh-0002
...
```

Let op:

sequentiële IDs zijn alleen stabiel als de bronvolgorde stabiel blijft.

Voor productie verdient een deterministische ID op basis van bron-identiteit mogelijk de voorkeur.

Bijvoorbeeld een slug/hash op:

```text
naam + plaats + terrein-geometrie
```

Maar verander de ID-strategie niet stilzwijgend nadat andere datasets eraan gekoppeld zijn.

Als IDs eenmaal extern gebruikt worden, is migratie expliciet nodig.

---

## 12. Primaire erfgoedbron: RCE-MCP / LDV

Voor erfgoeddata gebruiken we de RCE-MCP / Linked Data Voorziening van de Rijksdienst voor het Cultureel Erfgoed als primaire bron.

Niet eerst PDOK gebruiken om RCE-erfgoed opnieuw te reconstrueren.

De RCE-MCP moet waar mogelijk leveren:

- rijksmonumenten;
- archeologische rijksmonumenten;
- beschermde stads- en dorpsgezichten;
- monumentnummers;
- identifiers;
- persistente RCE-URI's;
- classificaties;
- thesaurusconcepten;
- aanwijzingsinformatie;
- geometrieën;
- provenance.

### Bekende relevante graphs uit eerdere verkenning

Onder andere:

```text
cho-default
gezicht-hvdl
aanwijzingenmonumenten
punten
ceo-ontology
cht-thesaurus
abr-thesaurus
```

Gebruik deze lijst als startpunt, niet als gegarandeerde volledige productspecificatie.

Inspecteer predicates en klassen eerst via de MCP voordat queries definitief worden vastgezet.

---

## 13. RCE-querystrategie

We hebben minimaal drie reproduceerbare extracties nodig.

### Q1. Beschermde stads- en dorpsgezichten

Benodigde output:

```text
id
naam
type
RCE URI
geometry
eventuele aanwijzingsinformatie
```

Doel:

bepalen of een begraafplaatsterrein binnen of gedeeltelijk binnen een beschermd gezicht ligt.

### Q2. Rijksmonumenten

Benodigde output:

```text
monumentnummer
RCE URI
naam / omschrijving
type / classificatie
geometry
aanwijzingsinformatie
```

Doel:

bepalen welke rijksmonumenten:

- op het terrein liggen;
- het terrein overlappen;
- direct aan het terrein grenzen;
- eventueel binnen een instelbare afstand liggen.

### Q3. Archeologische rijksmonumenten

Zelfde basisgegevens als Q2, maar de selectie moet semantisch reproduceerbaar zijn.

Belangrijk:

niet classificeren als "archeologisch" op basis van losse tekstzoekwoorden als er RCE-concepten of formele relaties beschikbaar zijn.

Gebruik RCE-thesauri/typen/relaties.

---

## 14. GeoJSON uit de RCE-MCP

Waar mogelijk de RCE-MCP direct GeoJSON laten produceren.

Voordelen:

- minder clientcode;
- URI, semantiek en geometrie uit dezelfde bronketen;
- reproduceerbaarheid;
- eenvoudig lokaal spatial joinen.

Bewaar per extract:

```text
query.sparql
raw.geojson
metadata.json
```

`metadata.json` kan bevatten:

```json
{
  "source": "RCE Linked Data Voorziening",
  "graphs": [],
  "retrieved_at": "",
  "query_file": "",
  "notes": ""
}
```

---

## 15. Geen live SPARQL vanuit de browser als basisarchitectuur

De viewer moet zo min mogelijk afhankelijk zijn van live externe queries.

Voorkeursarchitectuur:

```text
CSV begraafplaatsen
        +
RCE-MCP extracts
        │
        ▼
build / enrichment
        │
        ▼
statische GeoJSON / JSON / CSV
        │
        ▼
viewer
```

Voordelen:

- snel;
- reproduceerbaar;
- GitHub Pages-vriendelijk;
- minder runtime-fouten;
- geen CORS-afhankelijkheid;
- onderzoeksresultaten blijven controleerbaar;
- wijzigingen in de bron kunnen bewust als nieuwe build worden verwerkt.

Live RCE-links in popups zijn prima.

Live analyse als kernlogica is voorlopig niet gewenst.

---

## 16. Ruimtelijke analyse

Gebruik terreinpolygonen als linker dataset.

Mogelijke operaties:

```text
ST_Intersects
ST_Within
ST_Contains
ST_Touches
ST_Distance
```

In Python bijvoorbeeld via:

- GeoPandas;
- Shapely.

Alternatief:

- DuckDB Spatial.

### Belangrijk onderscheid

Een erfgoedobject kan geometrisch als:

- punt;
- polygoon;
- multipolygoon

beschikbaar zijn.

Een punt in een begraafplaats is niet hetzelfde bewijs als een polygonale overlap.

Bewaar daarom liefst de feitelijke ruimtelijke relatie.

---

## 17. Gewenste afgeleide erfgoedvelden

Minimaal:

```text
in_beschermd_gezicht
beschermd_gezicht_ids
beschermd_gezicht_uris

archeologische_rm_count
archeologische_rm_ids
archeologische_rm_uris
archeologische_rm_relations

rijksmonument_count
rijksmonument_ids
rijksmonument_uris
rijksmonument_relations
```

Een relationeel subobject is mogelijk beter dan alleen platte arrays.

Bijvoorbeeld:

```json
{
  "rijksmonumenten": [
    {
      "id": "...",
      "uri": "...",
      "relation": "inside",
      "distance_m": 0
    }
  ]
}
```

---

## 18. Betekenis van "op", "aangrenzend" en "nabij"

Geen semantische betekenis afleiden uit één afstand zonder documentatie.

Voor onderzoeksgebruik willen we de feitelijke meetwaarden bewaren.

Mogelijke presentatiecategorieën:

```text
inside / on_site
intersects
touches
0–25 m
25–100 m
none
```

Deze grenzen zijn voorlopig werkhypothesen.

De domeinexpert moet kunnen aangeven of bijvoorbeeld "annex aan een rijksmonument" betekent:

- zelfde terrein;
- grenscontact;
- binnen 25 meter;
- functioneel/historisch verbonden.

Bewaar daarom altijd de ruwe afstand en geometrische relatie zodat categorieën later opnieuw kunnen worden berekend.

---

## 19. Beschermd stads- of dorpsgezicht

Voor een terrein willen we minimaal onderscheiden:

```text
within
intersects
none
```

Een terrein dat deels over de grens van een beschermd gezicht ligt is inhoudelijk anders dan een terrein dat volledig binnen het gezicht ligt.

Maak dit niet plat tot alleen een boolean als de geometrie beschikbaar is.

Presentatie mag een boolean tonen, maar de bronrelatie moet behouden blijven.

---

## 20. Archeologisch rijksmonument

de domeinexpert wil onder meer zien waar een begraafplaats "boven archeologie" ligt.

Technisch interpreteren we dit eerst als een ruimtelijke relatie tussen:

- terreinpolygoon begraafplaats;
- geometrie archeologisch rijksmonument.

Bewaar bijvoorbeeld:

```text
within
contains
intersects
overlap_area_m2
overlap_pct_cemetery
```

Wanneer alleen een puntgeometrie beschikbaar is:

```text
point_inside = true
```

maar presenteer dit niet alsof er een bewezen polygonale overlap is.

---

## 21. Gebouwde rijksmonumenten

Voor gebouwde rijksmonumenten zijn verschillende relaties interessant:

- monumentpunt of -vlak binnen het terrein;
- monumentvlak overlapt terrein;
- monument raakt terreingrens;
- monument ligt zeer nabij ingang;
- monument ligt zeer nabij terrein.

Bewaar de feitelijke afstand en relatietype.

De viewer kan daarna eenvoudige labels tonen.

---

## 22. Kadaster en PDOK

PDOK/Kadaster zijn aanvullend.

Niet de primaire bron voor de RCE-erfgoedlagen.

Mogelijke toepassingen:

### Kadaster

- percelen die begraafplaatsterrein overlappen;
- perceelnummers;
- meerdere percelen per begraafplaats;
- zelfde perceel als kerk/monument;
- grenssituaties.

Dit is waarschijnlijk fase 2.

### PDOK

Mogelijk voor:

- basiskaart;
- kadastrale API;
- aanvullende geometrische fallback;
- contextlagen.

Gebruik alleen wat het onderzoek daadwerkelijk nodig heeft.

---

## 23. Viewer

Voorkeursrichting:

- MapLibre GL JS;
- statische assets;
- GitHub Pages voor MVP.

Leaflet is mogelijk, maar MapLibre heeft voorkeur als vector tiles, dynamische styling en meer lagen waarschijnlijk worden.

De keuze mag worden herzien als implementatiecomplexiteit onnodig groot blijkt.

---

## 24. Kaartlagen

Minimaal:

### Begraafplaatsen terrein

Polygonale terreinlaag.

### Ingangen

Puntlaag.

### Beschermde gezichten

RCE-laag.

### Rijksmonumenten

RCE-laag.

### Archeologische rijksmonumenten

RCE-laag of subset/style van de monumentlaag.

Later eventueel:

- kadastrale percelen;
- andere contextlagen.

---

## 25. Statuskleur `geruimd`

Geruimd/niet-geruimd moet duidelijk visueel onderscheiden worden.

Minimaal drie toestanden:

```text
geruimd = false
geruimd = true
status_conflict = true
```

Exacte kleuren zijn nog geen domeinbesluit.

Eisen:

- voldoende contrast;
- status mag niet verward worden met erfgoedbescherming;
- kleur is niet het enige signaal als toegankelijkheid belangrijk is;
- legenda toont expliciet wat de stijl betekent.

Erfgoedstatus moet een andere visuele dimensie gebruiken, bijvoorbeeld:

- outline;
- hatch/pattern;
- icoon;
- aparte laag.

Niet alle betekenis in fillkleur stoppen.

---

## 26. Filters

MVP-filters kunnen zijn:

```text
geruimd
niet-geruimd
statusconflict

binnen beschermd gezicht
overlap archeologisch rijksmonument
rijksmonument op terrein
rijksmonument aangrenzend

plaats / gemeente
```

Later mogelijk:

```text
oppervlakteklasse
afstand tot monument
type begraafplaats
perceel
```

---

## 27. Popup / detailpaneel

Per begraafplaats minimaal:

```text
naam
plaats
geruimd
oppervlakte
omtrek
ingang
beschermd gezicht
archeologische relaties
rijksmonumenten
RCE URI's
bron / build-datum
```

Bij statusconflict:

duidelijk tonen dat de bronwaarden elkaar tegenspreken.

Niet doen alsof `null` betekent `false`.

---

## 28. Export

de domeinexpert moet onderzoeksselecties kunnen meenemen.

Minimaal interessant:

- CSV;
- GeoJSON.

Een filterselectie exporteren is nuttiger dan alleen een volledige download.

Later eventueel:

- TTL/RDF;
- permalink naar filterstand.

---

## 29. Provenance

Alle afgeleide data moet herleidbaar zijn.

Bewaar waar mogelijk:

```text
bronbestand
bronrij
RCE URI
RCE graph
querybestand
extractiedatum
buildversie / commit
koppelwijze
```

Geen afgeleide classificatie zonder zichtbaar spoor naar de bron.

---

## 30. Voorgestelde repositorystructuur

Richting:

```text
dodenakkers/
├── CODEX.md
├── README.md
│
├── data/
│   ├── source/
│   │   ├── Begraafplaatsen Zuid-Holland- Zuid-Holland.csv
│   │   └── Begraafplaatsen Zuid-Holland-2.kml
│   │
│   ├── rce/
│   │   ├── beschermde-gezichten.geojson
│   │   ├── rijksmonumenten.geojson
│   │   ├── archeologische-rijksmonumenten.geojson
│   │   └── metadata/
│   │
│   └── generated/
│       ├── begraafplaatsen.geojson
│       ├── begraafplaatsen.csv
│       └── analyse.geojson
│
├── queries/
│   └── rce/
│       ├── beschermde-gezichten.sparql
│       ├── rijksmonumenten.sparql
│       └── archeologische-rijksmonumenten.sparql
│
├── scripts/
│   ├── build_base_dataset.py
│   ├── fetch_rce.py
│   ├── analyse_spatial.py
│   └── build.py
│
├── src/
│   ├── index.html
│   ├── app.js
│   ├── map.js
│   ├── filters.js
│   └── style.css
│
├── docs/
│   ├── ideas/
│   ├── data/
│   ├── mvp/
│   └── methodologie.md
│
└── .github/
    └── workflows/
        └── pages.yml
```

Niet alle directories hoeven direct in MVP aanwezig te zijn.

---

## 31. Build-pipeline

Gewenste keten:

```text
1. lees genormaliseerde CSV
2. valideer bronstructuur
3. splits terrein / ingang
4. koppel terrein ↔ ingang
5. bereken oppervlakte / omtrek
6. schrijf basis GeoJSON + audit
7. verkrijg RCE-extracts via MCP/LDV
8. valideer RCE-extracts
9. voer spatial joins uit
10. schrijf verrijkte dataset
11. bouw viewer
12. publiceer statisch
```

Elke stap moet apart testbaar zijn.

---

## 32. Validaties en assertions

Codex moet liever vroeg falen dan stil data verliezen.

Voor de huidige bron bijvoorbeeld:

```text
assert bronrecords == 924
assert terreinen == 463
assert ingangen == 461
assert logische_records == 463
assert status_conflicten == 4
assert ontbrekende_ingangen == 1
```

Als een bron bewust wordt bijgewerkt, moeten deze checks bewust worden aangepast.

Andere controles:

- elke feature heeft een ID;
- IDs zijn uniek;
- terrein-geometrie is niet leeg;
- oppervlak > 0;
- omtrek > 0;
- WGS84-geometrie ligt plausibel in/om Zuid-Holland;
- ingang is Point;
- ingang is niet automatisch vervangen door centroid;
- RCE URI's zijn niet leeg wanneer een relatie bestaat;
- geen duplicaten door spatial join.

---

## 33. Geometriekwaliteit

Valideer:

```text
is_valid
is_empty
geometry_type
```

Log reparaties.

Als een geometrie gerepareerd wordt:

- behoud bron-WKT;
- leg methode vast;
- schrijf auditregel;
- verander bronbestand niet stilzwijgend.

Geen automatische `buffer(0)` of `make_valid` zonder logging.

---

## 34. Performance

463 begraafplaatsen is klein.

RCE-lagen kunnen groter zijn.

Gebruik:

- spatial index;
- bounding-box prefilter;
- lokale GeoJSON/Parquet indien nuttig.

Voor MVP is extreme optimalisatie niet nodig.

Wel vermijden:

- per click een volledige SPARQL-query;
- honderden losse HTTP-verzoeken vanuit browser;
- brute-force N×M zonder spatial index als datasets groeien.

---

## 35. Reproduceerbaarheid

Belangrijker dan realtime.

Een onderzoeker moet later kunnen vaststellen:

- welke begraafplaatsenbron is gebruikt;
- welke RCE-query is gebruikt;
- op welke datum;
- welke codeversie;
- welke ruimtelijke regels;
- welke uitzonderingen.

Schrijf daarom buildmetadata.

Bijvoorbeeld:

```json
{
  "built_at": "...",
  "git_commit": "...",
  "cemetery_source": "...",
  "rce_extracts": [],
  "crs_analysis": "EPSG:28992",
  "software": {}
}
```

---

## 36. Hosting

MVP:

```text
GitHub Pages
```

Waarom:

- repository is al op GitHub;
- statische viewer;
- data kan tijdens build worden gegenereerd;
- eenvoudig reproduceerbaar;
- geen server nodig.

Cloudflare kan later relevant worden bij:

- server-side functies;
- proxy;
- caching;
- API;
- grotere dynamische datasets.

Niet introduceren zonder concrete behoefte.

---

## 37. Wat Codex niet moet doen

### Niet

- punt behandelen als centroid;
- punt weggooien omdat er al een polygoon is;
- terrein en ingang als dubbele records beschouwen;
- `geruimd` alleen uit naamtekst afleiden;
- statusconflicten automatisch oplossen;
- ontbrekende ingang verzinnen;
- archeologisch classificeren via ongedocumenteerde keyword search;
- live SPARQL in de browser als enige analysebron bouwen;
- geometrieën in WGS84-graden gebruiken voor oppervlakte;
- RCE-URI's vervangen door alleen labels;
- bronwaarden overschrijven zonder provenance;
- aannemen dat "aangrenzend" hetzelfde is als "binnen 25 meter";
- beschermde gezichten reduceren tot alleen `true/false` als de echte relatie beschikbaar is;
- één gedeelde ingang dwingen tot één terrein;
- stil geometrieën repareren;
- PDOK als primaire bron gebruiken voor informatie die al via RCE-MCP/LDV beschikbaar is.

---

## 38. Wat Codex juist wel moet doen

### Wel

- bron en afgeleide velden scheiden;
- terrein en ingang semantisch verschillend behandelen;
- alle automatische matching traceerbaar maken;
- uitzonderingen expliciet modelleren;
- metrische berekeningen in RD New uitvoeren;
- RCE Linked Data URI's bewaren;
- queries versioneren;
- ruwe RCE-extracts bewaren;
- spatial joins buiten de browser uitvoeren;
- onderzoekscategorieën terug te voeren maken op feitelijke geometrische relaties;
- auditbestanden genereren;
- tests schrijven rond bekende uitzonderingen;
- statische output voor de viewer produceren.

---

## 39. Eerste programmeerbare mijlpaal

Voordat de volledige viewer wordt gebouwd moet de repository reproduceerbaar dit kunnen:

```text
input:
  genormaliseerde begraafplaatsen-CSV

output:
  data/generated/begraafplaatsen.geojson
  data/generated/begraafplaatsen.csv
  docs/data/audit-resultaten.md
```

Met:

- 463 records;
- terrein als hoofdgeometrie;
- ingang gekoppeld waar aanwezig;
- gedeelde ingang ondersteund;
- ontbrekende ingang behouden;
- oppervlakte;
- hectare;
- omtrek;
- geruimd;
- statusconflict;
- provenance;
- matchingmethode.

Pas daarna de RCE-enrichment automatiseren.

---

## 40. Tweede programmeerbare mijlpaal

Via de RCE-MCP reproduceerbare extracten maken voor:

```text
beschermde gezichten
rijksmonumenten
archeologische rijksmonumenten
```

Inclusief opgeslagen SPARQL en provenance.

Daarna lokaal spatial joinen.

---

## 41. Derde programmeerbare mijlpaal

Een statische onderzoeksviewer:

```text
MapLibre
+
verrijkte GeoJSON
+
filters
+
detailpaneel
+
legenda
+
export
```

De viewer mag pas categorieën tonen die door de build expliciet zijn berekend.

Geen verborgen business rules in frontend-JavaScript als die analytisch relevant zijn.

---

## 42. Open inhoudelijke vragen

Deze vragen zijn nog niet definitief beantwoord en moeten niet stiekem in code worden vastgelegd:

1. Welke exacte RCE-concepten bepalen "archeologisch rijksmonument"?
2. Wat bedoelt de domeinexpert precies met "annex aan een rijksmonument"?
3. Welke afstand geldt als "direct aangrenzend" als er geen topologisch grenscontact is?
4. Moeten gebouwde rijksmonumenten op hetzelfde perceel apart worden geclassificeerd?
5. Hoe wil de domeinexpert statusconflicten `geruimd` inhoudelijk oplossen?
6. Moet een gedeeltelijke overlap met beschermd gezicht anders worden gepresenteerd dan volledig `within`?
7. Wil de domeinexpert percelen standaard of alleen als optionele onderzoeklaag?

Bewaar technische flexibiliteit zodat deze antwoorden later zonder datamigratie kunnen worden verwerkt.

---

## 43. Huidige aanbevolen stack

### Data/build

```text
Python
pandas
Shapely
pyproj
GeoPandas of DuckDB Spatial
```

Gebruik niet alles tegelijk zonder reden.

### Erfgoed

```text
RCE-MCP / Linked Data Voorziening
SPARQL
GeoJSON
RCE URI's
```

### Viewer

```text
MapLibre GL JS
HTML/CSS/JavaScript
```

Een eenvoudig frameworkloos MVP is acceptabel.

### Hosting

```text
GitHub Pages
GitHub Actions
```

---

## 44. Ontwikkelstijl

Houd het project klein, controleerbaar en uitlegbaar.

Voorkeur:

- simpele modules;
- expliciete functies;
- type hints waar nuttig;
- logging;
- kleine tests;
- geen premature abstrahering;
- geen zware backend zonder noodzaak.

Dit is primair een onderzoeksdataset met viewer, geen generiek GIS-platform.

---

## 45. Definitie van succes

Het project is geslaagd als de domeinexpert:

1. een begraafplaats kan selecteren;
2. het echte terrein en de echte ingang ziet;
3. oppervlakte en omtrek kan bekijken;
4. geruimd/niet-geruimd kan onderscheiden;
5. kan zien of het terrein binnen een beschermd gezicht ligt;
6. kan zien welke archeologische rijksmonumenten ermee overlappen;
7. kan zien welke rijksmonumenten op of direct bij het terrein liggen;
8. kan doorklikken naar de RCE-bron;
9. kan filteren en exporteren;
10. de uitkomst later reproduceerbaar opnieuw kan laten bouwen.

De kaart is de interface.

De reproduceerbare ruimtelijke kennislaag is het product.
