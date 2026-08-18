# Data 001: Audit van de begraafplaatsen-KML

## Bronbestanden

In de repository staan momenteel drie bestanden onder `data/`:

- `Begraafplaatsen Zuid-Holland-1.kmz`
- `Begraafplaatsen Zuid-Holland-2.kml`
- `Begraafplaatsen Zuid-Holland.kml`

De tweede KML is veruit het grootste bronbestand en lijkt de feitelijke dataset te bevatten.

## Wat al is vastgesteld

De KML bevat:

- een document met de naam `Begraafplaatsen Zuid-Holland`;
- een map `Zuid-Holland`;
- placemarks;
- polygonen van begraafplaatsen;
- WGS84-coördinaten;
- Google My Maps-stijlinformatie.

Voorbeelden die in het bestand zichtbaar zijn:

- `Vm. Geref. kerkhof, Oude Wetering`
- `NH Kerkhof, Oude Wetering`

Dit bevestigt dat we echte vlakgeometrieën kunnen gebruiken voor ruimtelijke intersecties.

## Audit die nu moet worden uitgevoerd

Zodra het volledige KML-bestand lokaal in de analyseomgeving staat, berekenen we:

- aantal placemarks;
- aantal polygonen;
- aantal punten;
- aantal lijnen;
- aantal multigeometrieën;
- aantal unieke namen;
- dubbele namen;
- lege namen;
- ongeldige geometrieën;
- zelfintersecties;
- lege geometrieën;
- bounding box;
- oppervlakte per begraafplaats;
- mogelijke uitschieters;
- eventueel aanwezige ExtendedData/attributen.

## Gewenste output

```text
data/generated/begraafplaatsen.geojson
data/generated/begraafplaatsen.csv
docs/data/kml-audit-resultaten.md
```

## Conversie

Bij conversie verwijderen we My Maps-opmaak die geen inhoudelijke waarde heeft.

Minimale eigenschappen:

```json
{
  "id": "stabiele-id",
  "naam": "NH Kerkhof, Oude Wetering",
  "bron": "Bureau Funeraire Adviezen",
  "source_file": "Begraafplaatsen Zuid-Holland-2.kml"
}
```

## Nog niet doen

- geen geometrieën automatisch repareren zonder logging;
- geen namen automatisch normaliseren zonder originele waarde te bewaren;
- geen ontbrekende locaties raden;
- geen objecten samenvoegen alleen omdat de namen op elkaar lijken.

## Eerstvolgende stap

Maak een script `scripts/audit_kml.py` dat de bovenstaande controles uitvoert en een Markdown-rapport plus GeoJSON genereert.
