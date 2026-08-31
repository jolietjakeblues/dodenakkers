# Idee 003: Ruimtelijke analyse

## Basisgeometrie

Voor erfgoedanalyse is de **terreinpolygoon** de primaire geometrie.

Het **ingangspunt** heeft een andere functie en wordt niet gebruikt als vervanging van het terrein.

## Afgeleide geometrische kenmerken

Per terrein berekenen we in RD New (`EPSG:28992`):

- oppervlakte in m²;
- oppervlakte in hectare;
- omtrek in meter.

## Relaties met erfgoedobjecten

We willen relaties expliciet vastleggen, bijvoorbeeld:

- `intersects`;
- `within`;
- `contains`;
- `touches`;
- `distance`.

Daarmee kunnen we onderscheid maken tussen:

- erfgoedobject op het begraafplaatsterrein;
- gedeeltelijke overlap;
- begraafplaats binnen beschermd gebied;
- object direct aan de grens;
- object alleen in de nabijheid.

## Archeologie

Voor de vraag of een begraafplaats "boven archeologie" ligt is de terreinpolygoon leidend.

Als de RCE-bron een vlakgeometrie heeft, berekenen we werkelijke vlakoverlap.

Als alleen een puntgeometrie beschikbaar is, registreren we dat als een andere soort relatie, bijvoorbeeld `point_in_cemetery`, en doen we niet alsof er een bewezen vlakoverlap is.

## Rijksmonumenten

Voor rijksmonumenten kunnen verschillende situaties voorkomen:

- monument binnen het terrein;
- monumentgeometrie overlapt het terrein;
- monument raakt de terreinrand;
- monument ligt vlak naast de begraafplaats.

De precieze betekenis van "annex aan een rijksmonument" moet op basis van deze meetbare relaties met de domeinexpert worden gevalideerd.

## Ingang als aanvullende geometrie

De ingang kan later gebruikt worden voor:

- afstand tot openbare weg;
- route-informatie;
- bereikbaarheid;
- toegang tot een terrein dat zelf veel groter is dan het ingangspunt.

## Status `geruimd`

`geruimd` is geen ruimtelijke relatie maar een eigenschap van de begraafplaats.

Daarom blijft deze status gescheiden van:

- monumentstatus;
- archeologische overlap;
- beschermd gezicht;
- afstandsrelaties.

Zo kunnen we bijvoorbeeld onderzoeken of geruimde begraafplaatsen vaker of juist minder vaak binnen beschermde gebieden liggen.

## Analyse-output

Per begraafplaats willen we uiteindelijk minimaal:

```json
{
  "id": "zh-0001",
  "geruimd": false,
  "oppervlakte_m2": 3421.0,
  "omtrek_m": 248.0,
  "protected_view": false,
  "monument_count": 2,
  "archaeology_count": 0,
  "relations": []
}
```

## Techniek

Voer ruimtelijke joins vooraf uit in de build-stap, bijvoorbeeld met:

- Python + GeoPandas/Shapely; of
- DuckDB Spatial.

De browser krijgt daarna een compacte, reproduceerbare dataset en hoeft niet zelf alle ruimtelijke analyses uit te voeren.

## Bron van de erfgoedgeometrie

Voor de eerste analyse gebruiken we geometrieën uit de RCE-MCP/LDV zelf waar die beschikbaar zijn.

Dat geeft één reproduceerbare keten:

```text
RCE object + classificatie + URI + geometrie
                    │
                    ▼
              GeoJSON / WKT
                    │
                    ▼
       ruimtelijke join met terrein
```

Alleen wanneer een benodigd RCE-object geen bruikbare geometrie heeft, onderzoeken we een aanvullende geometrische bron.

