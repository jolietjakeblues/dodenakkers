# Idee 002: Viewer voor Leon

## Doel

Geef Leon een kaart waarmee hij onderzoeksvragen kan beantwoorden zonder GIS-software te gebruiken.

## Hoofdfuncties

### Kaartlagen

- begraafplaatsen;
- rijksmonumenten;
- archeologische rijksmonumenten;
- beschermde stads- en dorpsgezichten;
- optioneel kadastrale percelen.

### Filters

Minimaal:

- gemeente;
- binnen beschermd stads- of dorpsgezicht;
- overlap met rijksmonument;
- overlap met archeologisch rijksmonument;
- geen van deze beschermingen.

Later mogelijk:

- afstand tot rijksmonument;
- type begraafplaats;
- beschermingsstatus;
- periode;
- bron.

## Detailvenster

Bij een klik op een begraafplaats tonen we bijvoorbeeld:

```text
NH Kerkhof, Oude Wetering

Gemeente
Kaag en Braassem

Beschermd gezicht
Nee

Rijksmonumenten
2

Archeologie
Geen overlap

Bronnen
RCE
PDOK
Bureau Funeraire Adviezen
```

Waar beschikbaar tonen we ook:

- monumentnummer;
- RCE URI;
- naam van het monument;
- relevante omschrijving;
- type ruimtelijke relatie;
- bron en datum van ophalen.

## Onderzoeksmodus

De viewer moet selecties kunnen maken zoals:

- alle begraafplaatsen binnen een beschermd gezicht;
- alle begraafplaatsen met een rijksmonument op het terrein;
- alle begraafplaatsen boven een archeologisch rijksmonument;
- alle begraafplaatsen zonder deze vormen van bescherming.

## Export

Gewenste exports:

- CSV voor analyse;
- GeoJSON voor GIS;
- later eventueel RDF/Turtle.

## Ontwerpprincipe

Gebruik gewone onderzoekstaal in de interface.

Dus liever:

> Binnen beschermd gezicht

dan:

> `ST_Within = true`

De technische details horen in de methodologie en data, niet in de hoofdinterface.
