# Idee 002: Viewer voor de domeinexpert

## Doel

Geef de domeinexpert een kaart waarmee hij onderzoeksvragen kan beantwoorden zonder GIS-software te gebruiken.

De viewer maakt onderscheid tussen het **terrein van een begraafplaats** en de **ingang**.

## Weergave begraafplaatsen

### Terrein

De polygoon toont de feitelijke omvang van de begraafplaats.

De kaartstijl maakt minimaal onderscheid tussen:

- niet-geruimd;
- geruimd;
- eventueel onbekend/conflict.

`geruimd` is een inhoudelijke status en geen onderdeel van de naam in de uiteindelijke interface.

### Ingang

Het punt toont de ingang/toegang.

De ingang kan als afzonderlijke marker worden getoond en blijft ook beschikbaar als de terreinpolygoon zichtbaar is.

## Kaartlagen

- begraafplaatsterreinen;
- ingangen;
- rijksmonumenten;
- archeologische rijksmonumenten;
- beschermde stads- en dorpsgezichten;
- optioneel kadastrale percelen.

## Filters

Minimaal:

- geruimd / niet-geruimd / statusconflict;
- gemeente;
- binnen beschermd stads- of dorpsgezicht;
- overlap met rijksmonument;
- overlap met archeologisch rijksmonument;
- geen van deze beschermingen.

Later mogelijk:

- oppervlakteklasse;
- afstand tot rijksmonument;
- type begraafplaats;
- beschermingsstatus;
- periode;
- bron.

## Detailvenster

Bij een klik op een begraafplaats tonen we bijvoorbeeld:

```text
NH Kerkhof, Oude Wetering

Status
Niet geruimd

Oppervlakte
3.421 m² / 0,34 ha

Omtrek
248 m

Ingang
Aanwezig

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
- bron en datum van ophalen;
- waarschuwing wanneer bronstatussen conflicteren.

## Onderzoeksmodus

De viewer moet selecties kunnen maken zoals:

- alle geruimde begraafplaatsen;
- alle niet-geruimde begraafplaatsen;
- alle begraafplaatsen binnen een beschermd gezicht;
- alle begraafplaatsen met een rijksmonument op het terrein;
- alle begraafplaatsen boven een archeologisch rijksmonument;
- alle begraafplaatsen zonder deze vormen van bescherming.

## Export

Gewenste exports:

- CSV voor analyse;
- GeoJSON voor GIS;
- later eventueel RDF/Turtle.

Exports bevatten zowel terrein- als ingangsgeometrie en de berekende oppervlakte/omtrek.

## Ontwerpprincipe

Gebruik gewone onderzoekstaal in de interface.

Dus liever:

> Binnen beschermd gezicht

of:

> Geruimd

in plaats van technische broncoderingen zoals `(geruimd)` in de naam of `ST_Within = true`.


## Stijlregel status

De terreinlaag gebruikt het afgeleide veld `geruimd` als primaire statusstijl.

Minimaal drie visuele categorieën:

- `geruimd = false`: actieve/niet-geruimde stijl;
- `geruimd = true`: duidelijk afwijkende stijl;
- `status_conflict = true`: neutrale waarschuwingsstijl totdat de bron is gevalideerd.

De exacte kleuren kiezen we in de implementatie op voldoende contrast en leesbaarheid. Status van erfgoedbescherming krijgt een andere visuele codering, zodat `geruimd` niet wordt verward met monumentstatus.
