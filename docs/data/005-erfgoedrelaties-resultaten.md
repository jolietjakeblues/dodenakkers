# Data 005: erfgoedrelaties resultaten

## Samenvatting

- 448 begraafplaatsen geanalyseerd tegen de RCE-extracten uit `data/rce/`;
- **43** volledig binnen een rijksbeschermd gezicht (`in_beschermd_gezicht = within`);
- **5** deels overlappend met een rijksbeschermd gezicht (`intersects`);
- **0** met minstens één overlappend archeologisch rijksmonument;
- **247** met minstens één gebouwd rijksmonument binnen 100 m (**316** binnen 250 m -- de dataset bewaart relaties tot 250 m zodat de schuifregelaar in de viewer verder dan 100 m kan verkennen). Categorieën `inside_on_site`/`touches`/`intersects`/`0-25m`/`25-100m`/`100-250m`, zie sectie 18 van de briefing - voorlopige werkhypothesen, ruwe afstand blijft altijd bewaard.

0 rijksmonumenten zonder `monument_aard` zijn uitgesloten van de 'gebouwd'-set in `data/rce/rijksmonumenten.geojson` (noch als gebouwd, noch als archeologisch geteld).

## Voorbeelden binnen een beschermd gezicht

- `zh-0007` Gemeentelijk kerkhof (Geervliet) - gezicht: Geervliet
- `zh-0008` Joodse begraafplaats (Geervliet) - gezicht: Geervliet
- `zh-0010` Oude gem. begraafplaats Haagpoort (Delft) - gezicht: Delft
- `zh-0011` Gemeentelijke begraafplaats Jaffa (Delft) - gezicht: Delft - TU-Noord
- `zh-0016` RK St. Petrus Banden (Den Haag) - gezicht: 's-Gravenhage - Archipelbuurt
- `zh-0018` Vm. kerkhof Nieuwe Kerk (Den Haag) - gezicht: 's-Gravenhage Uitbreiding
- `zh-0019` Joodse begraafplaats (Den Haag) - gezicht: 's-Gravenhage - Archipelbuurt
- `zh-0024` NH Kerkhof (Dalem) - gezicht: Gorinchem
- `zh-0046` Gem. begraafplaats Groenesteeg (Leiden) - gezicht: Leiden
- `zh-0047` RK begraafplaats Zijlpoort (Leiden) - gezicht: Leiden

## Voorbeelden met archeologische overlap

Geen enkel terrein overlapt een archeologisch rijksmonument (zie 'Bijna-overlap' hieronder voor de dichtstbijzijnde niet-overlappende gevallen).

## Bijna-overlap met archeologische rijksmonumenten

Geen overlap (dus niet in `archeologische_rm_relations`), maar wel de dichtstbijzijnde archeologische rijksmonumenten per terrein - puur informatief (`archeologische_rm_nearest`), om te laten zien wanneer 'geen overlap' een randgeval is in plaats van 'ver weg'.

- `zh-0428` NH kerkhof (Heenvliet) - 6.2 m tot 45080
- `zh-0115` Gem. begraafplaats (Groot-Ammers) - 13.6 m tot 47106
- `zh-0248` Gem. begraafplaats (Wateringen) - 27.6 m tot 46175
- `zh-0094` NH Kerkhof Oude Toren (Warmond) - 46.9 m tot 46177
- `zh-0045` Militair Ereveld (Valkenburg) - 65.4 m tot 46140
- `zh-0025` Gemeentelijke begraafplaats (Dalem) - 114.4 m tot Dalemse Donk
- `zh-0044` Gemeentelijke begraafplaats (Valkenburg) - 122.3 m tot 46140
- `zh-0024` NH Kerkhof (Dalem) - 149.6 m tot Dalemse Donk
- `zh-0174` Uitbreiding nw. Gem. begraafplaats (overzijde weg) (Leiderdorp) - 151.0 m tot Nederzetting
- `zh-0173` Nieuwe gem. begraafplaats (Leiderdorp) - 155.2 m tot Nederzetting

## Gegenereerde bestanden

- `data/generated/analyse.geojson` - `begraafplaatsen.geojson` verrijkt met `in_beschermd_gezicht`, `beschermd_gezicht_relaties`, `archeologische_rm_*` en `rijksmonument_*`.

## Open punten

1. De 100 m-grens voor 'nabij gebouwd rijksmonument' is een werkhypothese (sectie 18), nog niet door de domeinexpert bevestigd. Wel al bevestigd (2026-08-19): 'annex aan een rijksmonument' betekent grenscontact -- de relatie `touches` -- niet zomaar 'binnen X meter'; de viewer toont dit nu als 'annex (grenst aan)'.
2. `rijksmonument_relations` gebruikt alleen de punt/polygoon-geometrie uit `data/rce/rijksmonumenten.geojson`; monumenten zonder geometrie in die extractie ontbreken hier per definitie.
3. Kadastrale percelen (fase 2, sectie 22) zijn nog niet meegenomen. Zonder percelen kunnen we ook niet zien of meerdere rijksmonumenten (zoals de cluster bij NH Kerkhof Wassenaar) op hetzelfde perceel liggen en dus als 1 site geclusterd zouden moeten worden i.p.v. als losse punten -- dat is precies waar sectie 42-vraag 4 van de briefing over gaat.
