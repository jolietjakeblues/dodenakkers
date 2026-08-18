# Idee 003: Ruimtelijke analyse

## Doel

Bereken de relaties tussen de geometrie van een begraafplaats en erfgoedobjecten.

Alleen kaartlagen over elkaar tekenen is niet genoeg. We willen de relatie als data opslaan.

## Relaties

Voor een begraafplaats kunnen we onder andere bepalen:

- `intersects`: geometrieën raken of overlappen;
- `within`: de begraafplaats ligt volledig binnen een gebied;
- `contains`: het object ligt binnen de begraafplaats;
- `distance`: kleinste afstand tussen beide geometrieën.

## Voorgestelde resultaatvelden

```json
{
  "id": "begraafplaats-001",
  "naam": "NH Kerkhof, Oude Wetering",
  "protected_view": false,
  "monument_count": 2,
  "archaeology_count": 0,
  "relations": [
    {
      "target": "RCE-URI",
      "type": "intersects",
      "distance_m": 0
    }
  ]
}
```

## Belangrijk onderscheid

Een punt van een rijksmonument binnen een begraafplaatspolygoon betekent iets anders dan overlap tussen twee polygonen.

We moeten daarom per databron vastleggen:

- geometrie-type;
- nauwkeurigheid;
- gebruikte ruimtelijke relatie;
- eventuele afstandsdrempel.

## Mogelijke classificatie

Voor de viewer kunnen we technische relaties vertalen naar:

| Technische relatie | Label voor Leon |
|---|---|
| object binnen begraafplaats | op het terrein |
| polygonen overlappen | overlapt |
| afstand 0 tot 25 m | direct aangrenzend |
| afstand 25 tot 100 m | nabij |
| geen relatie | geen relatie gevonden |

De afstandsgrenzen moeten we samen met Leon valideren voordat we ze als onderzoekscriterium gebruiken.

## Analyseproces

1. valideer de begraafplaatsgeometrieën;
2. zet alle lagen in een geschikt coördinatenstelsel;
3. voer spatial joins uit;
4. bereken relevante afstanden;
5. sla de bronobjecten en relaties op;
6. exporteer GeoJSON en CSV;
7. test een steekproef visueel.

## Gereedschap

Eerste kandidaten:

- GeoPandas + Shapely;
- DuckDB Spatial.

Voor een eerste dataset van deze omvang is eenvoud belangrijker dan schaal.
