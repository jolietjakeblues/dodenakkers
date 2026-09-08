# Data 008: begraafplaatsen zonder jaartal - te checken door de domeinexpert

Vervolg op [007 Datering - bevindingen](007-datering-bevindingen.md), naar
aanleiding van een concrete vraag van de opdrachtgever: "Kun jij nog de
begraafplaatsen aanleveren waar nu geen jaartal bij gegeven is. Ik zag de
Joodse in Strijen, maar daar is van bekend dat die van 1896 is. Waarom die
niet kan plaatsen is mij een raadsel..."

## Wat hieronder staat

De **18 begraafplaatsen zonder jaartal én zonder periode** (de "onbekend"-
groep uit 007 -- niet de 116 die wel een periode als "Middeleeuws" hebben,
die tonen al iets). Voor elk: naam/plaats/gemeente, een grove denominatie-
indicatie op basis van de naam, de ingang-coördinaat (te plakken in Google
Maps of te zoeken op de kaart via [de site](../../src/index.html)), en -
nieuw voor dit document - de **dichtstbijzijnde eigen datering-kandidaat uit
de bron, ongeacht de 300m-drempel**, met de werkelijke afstand. Dat laatste
is precies waarom de Joodse begraafplaats in Strijen niet gekoppeld werd: er
staat wél een "Joodse Begraafplaats" met jaartal 1896 in de bron, alleen op
402m van onze ingang-coördinaat - 102m te ver voor de koppeling in
`scripts/analyse_spatial.py` (drempel 300m, zie 007 voor de onderbouwing van
die drempel).

Denominatie is hier alleen een tekstpatroon op de naam (RK/NH/Gereformeerd/
Joods/Doopsgezind/Evangelisch-Luthers/Remonstrants) - geen apart veld in de
data (die kolom is eerder bewust weer verwijderd van de statistiekenpagina,
zie `docs/geschiedenis.md`, 2026-08-26). Puur ter herkenning hier, geen
nieuwe sitefunctie.

**Duiding** is een korte, automatische inschatting op basis van hoe sterk de
naam overeenkomt en hoe ver de kandidaat weg ligt - geen conclusie, alleen
een leeswijzer om te zien waar snel te controleren winst zit.

## De 18, gesorteerd op afstand tot de dichtstbijzijnde eigen kandidaat

| Naam | Plaats (gemeente) | Denominatie | Ingang (lat, lon) | Dichtstbijzijnde kandidaat | Afstand | Duiding |
|---|---|---|---|---|---|---|
| Gem. begraafplaats | Schipluiden (Midden-Delfland) | - | 51,97634, 4,31049 | Gemeentelijke Begraafplaats (1873) | 309 m | Naam komt vrijwel overeen, net 9m buiten de drempel - waarschijnlijk dezelfde locatie. |
| Nieuwe begraafplaats | Rockanje (Voorne aan Zee) | - | 51,87201, 4,05814 | Nieuwe Begraafplaats (1950) | 334 m | Naam is identiek - waarschijnlijk dezelfde locatie, net buiten de drempel. |
| Gem. begraafplaats | Benthuizen (Alphen aan den Rijn) | - | 52,07449, 4,54426 | Gemeentelijke Begraafplaats Vrederust (geen jaartal/periode in bron) | 335 m | Kandidaat zelf heeft geen jaartal/periode in de bron - koppelen zou hier niets extra tonen. |
| Nieuwe gem. begraafplaats | Piershil (Hoeksche Waard) | - | 51,79373, 4,31999 | Kerkhof (1524) | 351 m | Die kandidaat is al gekoppeld aan een ander terrein in Piershil ("Gem. kerkhof", 69m afstand) - de bron lijkt geen apart gegeven voor dit "Nieuwe" terrein te hebben. |
| **Joodse begraafplaats** | **Strijen (Hoeksche Waard)** | **Joods** | **51,74719, 4,55647** | **Joodse Begraafplaats (1896)** | **402 m** | **De casus uit de vraag: naam is identiek, jaartal 1896 klopt met wat bekend is - net buiten de drempel.** |
| Gem. begraafplaats | Ooltgensplaat (Goeree-Overflakkee) | - | 51,68705, 4,34725 | Oude NH Kerkhof (Middeleeuwen) | 421 m | Andere naam/soort, kandidaat heeft alleen een periode, geen jaartal. |
| Begraafplaats Sancta Maria | Noordwijk (Noordwijk) | - | 52,27720, 4,48757 | Begraafplaats Sancta Maria centrum voor Psychiatrie (1928) | 450 m | Kandidaat heeft een extra toevoeging - mogelijk een specifiekere/andere locatie dan bedoeld. |
| Oude gem. begraafplaats | Brielle (Voorne aan Zee) | - | 51,89827, 4,15964 | Nieuwe Begraafplaats (geen jaartal/periode in bron) | 457 m | Naam wijkt af (Oude vs Nieuwe) - twijfelachtig. |
| Gem. begraafplaats | Giessenburg (Molenlanden) | - | 51,84227, 4,89412 | Begraafplaats (geen jaartal/periode in bron) | 519 m | Generieke naam, kandidaat zelf zonder jaartal/periode. |
| Nieuwe algemene begraafplaats | Wijngaarden (Molenlanden) | - | 51,84509, 4,77097 | Oude algemene Kerkhof (Middeleeuwen) | 522 m | Naam wijkt af (Nieuwe vs Oude), kandidaat heeft alleen een periode. |
| RK Kerkhof H. Johannes Onthoofding | Moordrecht (Zuidplas) | Rooms-Katholiek | 51,99197, 4,67706 | Kerkhof H. Johannes' Onthoofding (1852) | 570 m | Naam komt vrijwel overeen - plausibel dezelfde locatie, iets verder weg. |
| Begraafplaats De Dijk | Maassluis (Maassluis) | - | 51,90904, 4,26807 | De Dijk (2015) | 650 m | Naam is identiek - plausibel, maar het gevonden jaartal (2015) lijkt laat voor een bestaand terrein; de moeite van het checken waard. |
| Nieuwe gem. begraafplaats | Leiderdorp (Leiderdorp) | - | 52,15320, 4,53349 | Nieuwe Algemene Begraafplaats met RK gedeelte (1950) | 653 m | Gedeeltelijke naamovereenkomst, jaartal 1950. |
| Uitbreiding nw. Gem. begraafplaats (overzijde weg) | Leiderdorp (Leiderdorp) | - | 52,15310, 4,53367 | Nieuwe Algemene Begraafplaats met RK gedeelte (1950) | 658 m | Zelfde kandidaat als hierboven - logisch, dit is een latere uitbreiding van diezelfde begraafplaats. |
| RK begraafplaats | Brielle (Voorne aan Zee) | Rooms-Katholiek | 51,89624, 4,15278 | Nieuwe Begraafplaats (geen jaartal/periode in bron) | 666 m | Andere naam/soort (RK vs algemeen) - twijfelachtig. |
| Joodse begraafplaats | Vlaardingen (Vlaardingen) | Joods | 51,90972, 4,35895 | Joodse Begraafplaats (1862) | 943 m | Naam is identiek maar ver weg - mogelijk een onnauwkeurig adres in de bron, waardoor het gegeocodeerde punt afwijkt. |
| Nieuwe gem. begraafplaats | Brielle (Voorne aan Zee) | - | 51,88598, 4,16342 | Nieuwe Begraafplaats (geen jaartal/periode in bron) | 946 m | Naam komt overeen maar ver weg. |
| Begraafplaats De Essenhof | Puttershoek (Hoeksche Waard) | - | 51,79845, 4,56548 | Nieuwe gemeentelijke begraafplaats (1880) | 1016 m | Andere naam, de verste afstand - waarschijnlijk geen bruikbare kandidaat in de bron. |

## Patroon dat opvalt

Van deze 18 hebben er **8 een (bijna) identieke of sterk overeenkomende
naam** met hun dichtstbijzijnde kandidaat (Schipluiden, Rockanje, Strijen,
Moordrecht, Maassluis, Vlaardingen, en de twee Leiderdorp-terreinen die
dezelfde kandidaat delen) - dat zijn de kansrijkste om te checken. Bij
Schipluiden, Rockanje en Strijen scheelt het zelfs maar honderd meter of
minder met de 300m-drempel. Bij de overige 10 wijkt de naam af (vaak
Oude/Nieuwe-verwarring bij Brielle en Wijngaarden) of heeft de kandidaat
zelf niets ingevuld in de bron - daar is de kans groter dat er simpelweg
geen bruikbaar brongegeven voor dit specifieke terrein bestaat.

## Hoe dit tot stand kwam

Zelfde matchingprincipe als `nearest_datering()` in
`scripts/analyse_spatial.py` (dichtstbijzijnde punt in
`data/generated/datering.geojson` bij de ingang-coördinaat), maar dan zonder
de 300m-afkap toe te passen, puur om te laten zien wát er wel dichtbij ligt
en hoe ver het misten. Eenmalige analyse voor dit document, geen aanpassing
aan de site of de build - de 300m-drempel zelf staat niet ter discussie
(zie de onderbouwing in 007), dit is bedoeld om per geval te laten
beoordelen of de bron zelf een correctie nodig heeft (bv. een preciezer
adres) in plaats van de drempel te verruimen.
