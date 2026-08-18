# MVP 001: Eerste werkende onderzoekskaart

## Onderzoeksvraag

Kunnen we voor iedere begraafplaats betrouwbaar bepalen of deze:

1. binnen of overlappend met een beschermd stads- of dorpsgezicht ligt;
2. een relatie heeft met een rijksmonument;
3. een relatie heeft met een archeologisch rijksmonument?

Als dat werkt, is de kern van Leons opdracht bewezen.

## Scope

### Wel

- begraafplaatsen uit de KML;
- opschoning en validatie;
- beschermd stads- en dorpsgezicht;
- rijksmonumenten;
- archeologische rijksmonumenten;
- ruimtelijke analyse;
- kaart;
- drie tot vijf filters;
- detailvenster;
- CSV/GeoJSON-export;
- bronvermelding.

### Niet in MVP

- Kadaster/percelen;
- historische kaarten;
- gebruikersaccounts;
- database;
- beheerinterface;
- handmatige editing in de viewer;
- CARTO;
- server-side API.

## Werkvolgorde

### Stap 1: KML auditen en converteren

Output:

```text
data/generated/begraafplaatsen.geojson
docs/data/kml-audit-resultaten.md
```

### Stap 2: RCE-datamodel verkennen

Onderzoek:

- beschermde gezichten;
- monumentaanwijzingen;
- geometrieën;
- onderscheid gebouwd/archeologisch.

Output:

```text
docs/data/rce-query-notes.md
queries/
```

### Stap 3: RCE/PDOK-data ophalen

Maak reproduceerbare scripts.

Output bijvoorbeeld:

```text
data/generated/rce-monumenten.geojson
data/generated/beschermde-gezichten.geojson
```

### Stap 4: Spatial joins

Genereer per begraafplaats:

```text
protected_view
monument_count
archaeology_count
relations[]
```

### Stap 5: Steekproef

Controleer enkele gevallen handmatig op de kaart.

Leg fouten en uitzonderingen vast.

### Stap 6: Viewer

Bouw een kleine MapLibre-viewer met:

- laag begraafplaatsen;
- filter beschermd gezicht;
- filter rijksmonument;
- filter archeologie;
- detailvenster.

### Stap 7: Publiceren

Publiceer de statische viewer met GitHub Pages.

## Definition of done

Het MVP is geslaagd wanneer Leon:

- een locatie kan aanklikken;
- de drie kernrelaties kan zien;
- erop kan filteren;
- een selectie kan exporteren;
- kan zien waar de conclusies vandaan komen.
