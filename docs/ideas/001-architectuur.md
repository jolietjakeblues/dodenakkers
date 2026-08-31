# Idee 001: Architectuur

## Doel

Bouw een kleine ruimtelijke onderzoeksomgeving voor begraafplaatsen en erfgoed in Zuid-Holland.

De kaart is de interface. De kern is een reproduceerbare analyse van ruimtelijke relaties tussen:

- begraafplaatsen;
- rijksmonumenten;
- archeologische rijksmonumenten;
- beschermde stads- en dorpsgezichten;
- later eventueel kadastrale percelen.

## Voorgestelde architectuur

```text
KML begraafplaatsen
        |
        v
conversie en opschoning
        |
        +-------- RCE Linked Data / MCP
        |
        +-------- PDOK geometrie
        |
        +-------- Kadaster / percelen, fase 2
        |
        v
ruimtelijke analyse
        |
        v
verrijkte GeoJSON / CSV
        |
        v
MapLibre viewer
        |
        v
GitHub Pages
```

## Kernkeuzes

1. Voer de zware ruimtelijke analyse tijdens de build uit.
2. Gebruik de browser vooral voor tonen, zoeken en filteren.
3. Bewaar brondata en afgeleide data gescheiden.
4. Maak elke afleiding reproduceerbaar met scripts.
5. Bewaar bron-URI's en herkomstinformatie bij de resultaten.

## Waarom vooraf verrijken?

De domeinexpert wil onderzoeksresultaten kunnen filteren. Hij hoeft niet bij iedere klik opnieuw SPARQL- of GIS-berekeningen uit te voeren.

Een vooraf verrijkte dataset maakt de viewer:

- snel;
- statisch hostbaar;
- controleerbaar;
- exporteerbaar;
- eenvoudiger te onderhouden.

## Voorlopige stack

- MapLibre GL JS voor de viewer
- GeoJSON voor kleine en middelgrote eigen lagen
- RCE MCP / LDV voor semantische verrijking
- PDOK voor overheidsgeometrie en kaartdiensten
- Python met GeoPandas/Shapely of DuckDB Spatial voor de analyse
- GitHub Actions voor de build
- GitHub Pages voor publicatie

## Open beslissingen

- GeoPandas/Shapely of DuckDB Spatial voor de eerste analyse
- welke PDOK-laag als ondergrond
- hoe archeologische rijksmonumenten precies uit RCE-data worden onderscheiden
- of de viewer later een eigen API nodig heeft
