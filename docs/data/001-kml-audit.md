# Data 001: Audit van de begraafplaatsen-KML

## Bronbestanden

De oorspronkelijke kaartbron is:

`Begraafplaatsen Zuid-Holland-2.kml`

Voor de reproduceerbare build gebruiken we de genormaliseerde CSV:

`Begraafplaatsen Zuid-Holland- Zuid-Holland.csv`

De CSV bevat expliciete velden voor `geruimd`, `ingang` en `begraafplaats` en is daarom de primaire verwerkingsbron.

## Betekenis van de geometrieën

De KML bevat twee inhoudelijk verschillende geometrieën per begraafplaats:

- **Polygon**: het terrein van de begraafplaats;
- **Point**: de ingang/toegang tot de begraafplaats.

Het punt is dus geen centroid en geen duplicaat van de polygoon. Beide moeten behouden blijven.

## Eerste telling uit het bestand

De KML bevat:

- 924 placemarks;
- 463 placemarks met een polygoon;
- 461 punten;
- 1 placemark met `MultiGeometry` waarin polygonen voorkomen.

De aantallen terreinpolygonen en ingangen zijn niet exact gelijk. Dat is een expliciet auditpunt.

## Status `geruimd`

In de genormaliseerde CSV staat `geruimd` als expliciet veld. We leiden de status dus niet meer uit de naam af.

Terrein en ingang kunnen in de bron toch verschillende statuswaarden hebben. Zulke gevallen worden als conflict gemarkeerd en niet automatisch opgelost.

De vier bekende conflicten zijn:

- RK begraafplaats, Oude Wetering;
- Oud NH kerkhof, Schoonhoven;
- Vm. NH kerkhof, Maasland;
- NH Kerkhof, Zwammerdam.

## Oppervlakte en omtrek

De bron bevat geen afzonderlijke attributen voor oppervlakte of omtrek.

Beide kunnen wel uit de terreinpolygoon worden berekend.

Werkwijze:

1. lees de KML-geometrie in WGS84;
2. transformeer naar RD New (`EPSG:28992`);
3. bereken `area` in m²;
4. bereken `length` van de buitengrens in meter;
5. leid hectare af uit m².

Voor een begraafplaatsrecord bewaren we minimaal:

```text
oppervlakte_m2
oppervlakte_ha
omtrek_m
```

## Audit die moet worden uitgevoerd

- aantal placemarks;
- aantal terreinpolygonen;
- aantal ingangspunten;
- aantal multigeometrieën;
- ontbrekende terreinpolygonen;
- ontbrekende ingangspunten;
- unieke en dubbele namen;
- naamvarianten tussen punt en polygoon;
- status `geruimd` per punt en polygoon;
- statusconflicten;
- lege namen;
- ongeldige geometrieën;
- zelfintersecties;
- lege geometrieën;
- ingang binnen/op/nabij het juiste terrein;
- oppervlakte per terrein;
- omtrek per terrein;
- mogelijke geometrische uitschieters;
- bounding box;
- eventueel aanwezige ExtendedData/attributen.

## Gewenste output

```text
data/generated/begraafplaatsen.geojson
data/generated/begraafplaatsen.csv
docs/data/kml-audit-resultaten.md
```

## Conversieprincipes

- originele geometrieën bewaren;
- originele namen bewaren in bronvelden;
- My Maps-opmaak verwijderen waar die geen inhoudelijke waarde heeft;
- `(geruimd)` omzetten naar een expliciet statusveld;
- punt en polygoon koppelen tot één logisch begraafplaatsrecord;
- geen centroid gebruiken als vervanging van een ingang;
- alle automatische reparaties en mappings loggen.

## Nog niet doen

- geen statusconflicten stil oplossen;
- geen geometrieën automatisch repareren zonder logging;
- geen namen normaliseren zonder de bronwaarde te bewaren;
- geen ontbrekende ingangen raden;
- geen objecten samenvoegen uitsluitend op naamovereenkomst.

## Eerstvolgende stap

Maak `scripts/audit_kml.py` dat:

1. terreinpolygonen en ingangspunten apart uitleest;
2. ze koppelt;
3. oppervlakte en omtrek berekent;
4. het expliciete CSV-veld `geruimd` overneemt en conflicten controleert;
5. conflicten rapporteert;
6. een Markdown-audit en een schone afgeleide dataset genereert.
