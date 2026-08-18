# Data 002: Datamodel begraafplaatsen

## Kerninzicht

Een begraafplaats bestaat in de bron uit twee verschillende geometrieën met elk een eigen betekenis:

1. **terrein**: de polygoon van de begraafplaats;
2. **ingang**: het punt van de toegang/ingang tot de begraafplaats.

Deze geometrieën mogen niet als duplicaten worden beschouwd.

## Terrein

De polygoon is de autoritatieve geometrie voor het fysieke terrein van de begraafplaats.

Uit deze geometrie leiden we minimaal af:

- oppervlakte in vierkante meter;
- oppervlakte in hectare;
- omtrek in meter;
- centroid, uitsluitend als technisch afgeleid hulpmiddel;
- ruimtelijke relaties met RCE- en PDOK-objecten.

Voor oppervlakte en omtrek rekenen we de WGS84-geometrie om naar RD New (`EPSG:28992`) voordat we meten.

## Ingang

Het punt stelt de feitelijke ingang/toegang tot de begraafplaats voor.

Het punt gebruiken we voor:

- een herkenbare marker op de kaart;
- navigatie en route-links;
- locatie van de toegang;
- eventueel latere bereikbaarheidsonderzoeken.

Het ingangspunt mag niet worden vervangen door het centroid van de terreinpolygoon.

## Status `geruimd`

`geruimd` wordt een expliciet attribuut in de afgeleide dataset.

Voorbeeld:

```json
{
  "id": "zh-0001",
  "naam": "NH Kerkhof, Oude Wetering",
  "geruimd": false,
  "oppervlakte_m2": 1234.5,
  "oppervlakte_ha": 0.12345,
  "omtrek_m": 156.8,
  "ingang": {
    "type": "Point",
    "coordinates": [4.6454, 52.2122]
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": []
  }
}
```

### Huidige broncodering

In de genormaliseerde CSV is `geruimd` een expliciet veld. Dit veld is leidend als bronwaarde.

We bewaren afzonderlijk:

- `geruimd_bron_terrein`;
- `geruimd_bron_ingang`;
- `geruimd`: de samengevoegde status wanneer beide bronrecords consistent zijn;
- `status_conflict`: `true` wanneer terrein en ingang verschillen.

Bij een conflict krijgt `geruimd` voorlopig `null`, zodat de viewer geen onbevestigde keuze als feit presenteert.

## Koppeling terrein en ingang

Punt en polygoon worden gekoppeld tot één begraafplaatsrecord.

Koppeling gebeurt niet alleen op exacte naam. We gebruiken minimaal:

1. genormaliseerde naam;
2. ruimtelijke nabijheid van ingang tot terrein;
3. handmatige controle bij conflicten of ambiguïteit.

Idealiter ligt een ingang op of vlak bij de rand van het bijbehorende terrein. Dat maakt ruimtelijke matching bruikbaar als extra controle.

## Datakwaliteitsregel voor status

De status van punt en polygoon kan in de huidige bron verschillen. In de eerste audit zijn vier naamparen gevonden waarbij `(geruimd)` slechts aan één van beide geometrieën is toegevoegd:

- RK begraafplaats, Oude Wetering;
- Oud NH kerkhof, Schoonhoven;
- Vm. NH kerkhof, Maasland;
- NH Kerkhof, Zwammerdam.

Deze gevallen worden gemarkeerd als conflict en niet automatisch overschreven.

## Gewenste afgeleide velden

```text
id
naam
naam_bron_polygoon
naam_bron_ingang
geruimd
geruimd_bron_polygoon
geruimd_bron_ingang
status_conflict
oppervlakte_m2
oppervlakte_ha
omtrek_m
terrein_geometry
ingang_geometry
bron
source_file
```

Later komen daar de verrijkte RCE/PDOK-velden bij.


## Geometriekeuze in GeoJSON

Een GeoJSON Feature kan één hoofdgeometrie hebben. Voor ruimtelijke analyse is dat het terrein.

Daarom:

- `geometry` = terreinpolygoon of terrein-GeometryCollection;
- `properties.ingang` = GeoJSON Point van de toegang;
- `ingang_lon` en `ingang_lat` = eenvoudige coördinaten voor viewer/navigatie.

Zo blijft één feature één begraafplaatsterrein voorstellen en blijft de echte ingang behouden.
