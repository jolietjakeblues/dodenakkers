# Data 010: oude kaarten (Allmaps) bij verdwenen en kandidaat-begraafplaatsen

Stand: 2026-10-20. Gemaakt met `scripts/fetch_allmaps.py`; weergave op `oude-kaarten.html`; uitleg voor lezers op de pagina [Methode](../../src/methode.html) (sectie "Oude kaarten").

## Waarom

De verdwenen begraafplaatsen (92, van de domeinexpert) zijn punten bij benadering zonder jaartal of terrein. De kandidaat-begraafplaatsen (196, experimenteel) zijn automatische aanwijzingen uit tekst en rijksmonumenten die de gebruiker zelf moet controleren. Een historische kaart over het punt maakt dat controleren eenvoudiger: je ziet in een klik of er op een bepaald jaar een begraafplaats, kerkhof of kruisjesteken lag. Het idee komt uit het project Joodse Begraafplaatsen, waar dezelfde methode al gebruikt wordt.

## Bron en selectie

- **Allmaps** (<https://allmaps.org>): de open dump van alle gegeorefereerde kaarten (`maps.geojsonl`, CC0). Alleen de georeferentie (de plaatsing) komt uit Allmaps; het kaartbeeld blijft bij de instelling en wordt via de Allmaps Tile Server (`allmaps.xyz`) getoond.
- **Selectie per punt:** de omtrek van de kaart bevat het punt; kleiner dan 600 km² (geen overzichtskaarten); herkenbare titel; alleen collecties van bekende instellingen (TU Delft Library, Universiteitsbibliotheek Utrecht, Universitaire Bibliotheken Leiden, Nationaal Archief, Gouda Tijdmachine, Stadsarchief Rotterdam, ...); per scan de nieuwste georeferentie. Iedereen kan in Allmaps georefereren, vandaar de collectiefilter.
- **Jaartal:** bij de Bonnebladen uit de bestandsnaam van de scan, via `data/allmaps/bonnebladen_jaren.csv` (ingest-lijst van TU Delft Library); bij andere kaarten een jaartal in de titel, anders geen jaartal.
- **Sleutel per punt:** elk verdwenen punt en elke kandidaat heeft een vaste `id` in de brondata (`vd-<plaats>-<naam>`; `ka-<objectnummer>`; `rm-<laagste rijksmonumentnummer>`; `chs-<monumentnr>`, met `-2`, `-3` voor verdere delen van hetzelfde terrein).

## Dekking

| Soort | Punten | Met kaart | Mediaan aantal kaarten |
|---|---:|---:|---:|
| Verdwenen begraafplaatsen | 92 | 92 | 21 |
| Tekstzoek-kandidaten | 156 | 156 | 15 |
| Kloosters | 13 | 13 | 20 |
| Kapellen | 13 | 13 | 20 |
| Synagoges | 3 | 3 | 28 |
| CHS-archeologie | 11 | 11 | 15 |

Op elk punt ligt minstens een Bonneblad (1:25.000, ca. 1865 tot 1945); samen zijn het 788 verschillende kaarten. De oudste kaart per punt is mediaan van 1681. Van de 788 heeft ongeveer een kwart (204) geen jaartal.

## Wat het wel en niet zegt

- Een kaart waarop een begraafplaats staat is een aanwijzing dat die er in dat jaar lag.
- Een kaart waarop niets staat is **geen bewijs** van het tegendeel: kleine terreinen vallen op schaal 1:25.000 weg, en een terrein dat verdween voor het eerste blad verscheen, staat er nooit op.
- Georefereren is handwerk; afwijkingen van enkele tientallen meters zijn normaal.
- Bij Romeinse en middeleeuwse grafvelden en de meeste CHS-terreinen met een premoderne datering helpt dit nauwelijks, omdat de oudste bruikbare kaarten rond 1830 tot 1865 beginnen.
- Het is een hulpmiddel om een punt te beoordelen, geen controle van de bron en geen bevestiging.

## Nog niet gedaan

- Geen indeling per verdwenen begraafplaats (zichtbaar op het punt, mogelijk, verwacht maar niet te zien, niet te verwachten), zoals het Joodse project die voor zijn verdwenen begraafplaatsen heeft gemaakt. Daarvoor moet elk punt met de hand bekeken worden.
- De 450 bestaande begraafplaatsen hebben geen link naar oude kaarten. De oudste kaart waarop een terrein staat zou een "uiterlijk in gebruik rond"-jaar kunnen geven voor de 27 terreinen zonder datering; dat zou apart van de datering uit de Excel moeten blijven.
- De jaren bij de Bonnebladen komen uit een gespiegelde lijst; verversen kan met `python scripts/fetch_allmaps.py --vernieuw-jaren`.

## Verversen

```
python scripts/compute_kandidaat_begraafplaatsen.py --no-kadaster-check   # na wijziging van de kandidaten
python scripts/fetch_allmaps.py                                           # downloadt de dump (ca. 1 minuut)
python scripts/build_site.py
```
