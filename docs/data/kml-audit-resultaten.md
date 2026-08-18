# Data: auditresultaten basisdataset

## Samenvatting

De genormaliseerde CSV bevat **924 bronrecords**:

- **463** begraafplaatsterreinen;
- **461** ingangen;
- **462** terreinpolygonen;
- **1** terreinrecord met een `GeometryCollection`;
- **80** bronrecords met status `geruimd`.

De basisdataset bevat **463 begraafplaatsrecords**, één record per terrein.

## Koppeling terrein en ingang

Koppeling is uitgevoerd met behoud van de bronwaarden.

| Koppelwijze | Terreinen |
|---|---:|
| Exacte genormaliseerde naam + opgeschoonde plaats | 449 |
| Ruimtelijke koppeling bij naamvariant | 12 |
| Gedeelde ingang, ruimtelijk gekoppeld | 1 |
| Geen ingang gevonden | 1 |

### Gedeelde ingang

Bij **Katwijk aan Zee** heeft het ingangspunt `Gem. begraafplaats Duinrust en NH begraafplaats` twee nabijgelegen terreinrecords:

- `Gem. begraafplaats Duinrust`;
- `NH begraafplaats Duinrust`.

Dezelfde ingang wordt daarom aan beide terreinen gekoppeld en gemarkeerd met `ingang_gedeeld = true`.

### Ontbrekende ingang

Voor de volgende terreinrecord is geen ingangspunt gevonden:

- `zh-0368`: Gem. begraafplaats, Oudenhoorn

## Statusconflicten

Er zijn **4** gevallen waarin terrein en ingang een verschillende bronwaarde voor `geruimd` hebben.

In deze gevallen krijgt het afgeleide veld `geruimd` voorlopig `null` en `status_conflict = true`.

- RK begraafplaats, Oude Wetering: terrein = `false`, ingang = `true`
- Oud NH kerkhof, Schoonhoven: terrein = `false`, ingang = `true`
- NH Kerkhof, Zwammerdam: terrein = `true`, ingang = `false`
- Vm. NH kerkhof, Maasland: terrein = `false`, ingang = `true`

## Oppervlakte en omtrek

Oppervlakte en omtrek zijn berekend na transformatie van WGS84 naar RD New (`EPSG:28992`).

- kleinste oppervlakte: **15.84 m²**;
- mediaan oppervlakte: **3,123.17 m²**;
- grootste oppervlakte: **268,823.91 m²**;
- kleinste omtrek: **15.95 m**;
- mediaan omtrek: **242.20 m**;
- grootste omtrek: **2,084.91 m**.

Deze extremen zijn signalen voor controle en niet automatisch fouten.

## Gegenereerde bestanden

- `data/generated/begraafplaatsen.geojson`
- `data/generated/begraafplaatsen.csv`

De GeoJSON gebruikt het **terrein als feature geometry**. De ingang wordt daarnaast als Point-object in `properties.ingang` bewaard. Hierdoor blijft de terreinpolygoon direct bruikbaar voor kaartweergave en ruimtelijke analyse, zonder de betekenis van de ingang te verliezen.
