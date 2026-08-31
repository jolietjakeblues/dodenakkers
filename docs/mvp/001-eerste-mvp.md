# MVP 001: Eerste werkende versie

## Status (2026-08-19)

Alle punten onder "Definition of done" zijn gehaald: volledige reproduceerbare
keten (CSV -> `build_base_dataset.py` -> `fetch_rce.py` -> `analyse_spatial.py`
-> viewer), live op **https://dodenakkers-zh.pages.dev/** voor de domeinexpert om te
bekijken en te testen. Publicatie loopt via **Cloudflare Pages**, niet GitHub
Pages zoals hieronder nog vermeld staat -- zie
[006 Hosting](../ideas/006-hosting.md) voor het herziene besluit.

## Onderzoeksvraag

Kan de domeinexpert per begraafplaats snel zien:

1. wat het terrein is en waar de ingang ligt;
2. of de begraafplaats geruimd of niet-geruimd is;
3. wat oppervlakte en omtrek zijn;
4. of het terrein binnen een beschermd stads- of dorpsgezicht ligt;
5. of er rijksmonumenten op of aan het terrein liggen;
6. of het terrein overlapt met archeologische rijksmonumenten?

## Binnen scope

- genormaliseerde CSV als primaire build-bron;
- KML als oorspronkelijke kaartbron en controlebron;
- terreinpolygonen en ingangspunten koppelen;
- `geruimd` als expliciet statusveld;
- oppervlakte en omtrek berekenen;
- bronconflicten rapporteren;
- RCE-data voor monumenten, archeologie en beschermde gezichten;
- waar nuttig PDOK voor geometrie;
- vooranalyse naar GeoJSON/JSON;
- eenvoudige MapLibre-viewer;
- statische publicatie via GitHub Pages.

## Buiten scope eerste MVP

- uitgebreid kadastraal onderzoek;
- historische perceelsreconstructies;
- gebruikersaccounts;
- database/backend;
- handmatige GIS-bewerkingen in de browser;
- automatisch oplossen van onzekere bronconflicten.

## Werkvolgorde

### 1. KML audit en basismodel

- polygonen als terrein herkennen;
- punten als ingang herkennen;
- terrein en ingang koppelen;
- expliciet CSV-veld `geruimd` verwerken;
- statusconflicten markeren;
- oppervlakte en omtrek berekenen;
- schone basisdataset maken.

### 2. RCE-datamodel onderzoeken

- beschermde stads- en dorpsgezichten;
- rijksmonumenten;
- archeologische rijksmonumenten;
- relevante classificaties en geometrieën.

### 3. RCE-MCP/LDV-data ophalen

Alleen de data die nodig is voor Zuid-Holland en de gekozen onderzoeksvragen.

### 4. Ruimtelijke joins

Per terrein bepalen:

- beschermd gezicht;
- monumenten op/in/aan het terrein;
- archeologische overlap;
- relevante afstanden.

### 5. Validatie

Controleer een representatieve selectie met onder andere:

- geruimde en niet-geruimde begraafplaatsen;
- grote en kleine terreinen;
- begraafplaatsen binnen en buiten beschermd gezicht;
- bekende monumentlocaties;
- de vier bekende statusconflicten uit de bron.

### 6. Viewer

Toon:

- terreinpolygonen met verschillende stijl voor geruimd/niet-geruimd;
- ingangspunten;
- erfgoedlagen;
- filters;
- oppervlakte en omtrek;
- detailinformatie en bronverwijzingen.

### 7. Publicatie

GitHub Actions bouwt de afgeleide data en viewer. GitHub Pages serveert het statische resultaat.

## Definition of done

De eerste MVP is geslaagd wanneer de domeinexpert zonder GIS-software een begraafplaats kan selecteren en direct kan zien:

- terrein en ingang;
- geruimd/niet-geruimd;
- oppervlakte en omtrek;
- beschermd gezicht ja/nee;
- relevante rijksmonumenten;
- archeologische relatie;
- bron en eventuele datakwaliteitswaarschuwing.
