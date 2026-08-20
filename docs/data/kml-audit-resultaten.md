# Data: auditresultaten basisdataset

*Gegenereerd door `scripts/build_base_dataset.py` -- niet handmatig bewerken.*

## Samenvatting

De genormaliseerde CSV bevat **884 bronrecords**:

- **443** begraafplaatsterreinen;
- **441** ingangen;
- **442** terreinpolygonen;
- **1** terreinrecord met een `GeometryCollection`;
- **82** bronrecords met status `geruimd`.

De basisdataset bevat **443 begraafplaatsrecords**, één record per terrein.

## Koppeling terrein en ingang

Koppeling is uitgevoerd met behoud van de bronwaarden.

| Koppelwijze | Terreinen |
|---|---:|
| Exacte genormaliseerde naam + opgeschoonde plaats | 430 |
| Ruimtelijke koppeling bij naamvariant | 11 |
| Gedeelde ingang, ruimtelijk gekoppeld | 1 |
| Geen ingang gevonden | 1 |

### Gedeelde ingang

- `zh-0039` NH begraafplaats Duinrust (Katwijk aan Zee), koppelwijze `shared_entrance_spatial`
- `zh-0343` Gem. begraafplaats Duinrust (Katwijk aan Zee), koppelwijze `spatial_name_variant`

### Ontbrekende ingang

- `zh-0354`: Gem. begraafplaats, Oudenhoorn

## Statusconflicten

Er zijn **0** gevallen waarin terrein en ingang een verschillende bronwaarde
voor `geruimd` hebben.

In deze gevallen krijgt het afgeleide veld `geruimd` voorlopig `null` en `status_conflict = true`.


## Oppervlakte en omtrek

Oppervlakte en omtrek zijn berekend na transformatie van WGS84 naar RD New (`EPSG:28992`).

- kleinste oppervlakte: **15.84 m²**;
- mediaan oppervlakte: **3,260.05 m²**;
- grootste oppervlakte: **268,823.91 m²**;
- kleinste omtrek: **15.95 m**;
- mediaan omtrek: **243.73 m**;
- grootste omtrek: **2,084.91 m**.

Deze extremen zijn signalen voor controle en niet automatisch fouten.

## Gegenereerde bestanden

- `data/generated/begraafplaatsen.geojson`
- `data/generated/begraafplaatsen.csv`

De GeoJSON gebruikt het **terrein als feature geometry**. De ingang wordt daarnaast als Point-object in `properties.ingang` bewaard. Hierdoor blijft de terreinpolygoon direct bruikbaar voor kaartweergave en ruimtelijke analyse, zonder de betekenis van de ingang te verliezen.
