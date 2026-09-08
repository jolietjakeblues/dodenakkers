# Data 008: begraafplaatsen zonder jaartal - gecontroleerd door de domeinexpert

Vervolg op [007 Datering - bevindingen](007-datering-bevindingen.md), naar
aanleiding van een concrete vraag van de opdrachtgever: "Kun jij nog de
begraafplaatsen aanleveren waar nu geen jaartal bij gegeven is. Ik zag de
Joodse in Strijen, maar daar is van bekend dat die van 1896 is. Waarom die
niet kan plaatsen is mij een raadsel..."

## Update 2026-09-08: opgelost voor 17 van de 18

De domeinexpert heeft de lijst hieronder nagelopen en voor **17 van de 18**
het echte jaartal bevestigd (kolom "Bevestigd jaartal"). Alleen bij de
Nieuwe gem. begraafplaats in Brielle is het jaartal ook bij hem onbekend --
een echte lege waarde in de bron, geen matchingprobleem. De 17
bevestigingen staan nu in `data/datering-correcties.json` en overschrijven
de automatische koppeling in `scripts/analyse_spatial.py` voor precies deze
terreinen -- ze zijn dus al zichtbaar in het begraafplaats-popup, de
periode-filter en de statistiekenpagina (cijfers bijgewerkt in 007). Het
patroon dat hieronder al vermoed werd, klopte overwegend: bij bijna alle
gevallen met een (bijna) identieke naam als de dichtstbijzijnde kandidaat
kwam het bevestigde jaartal exact overeen met dat van de kandidaat
(Schipluiden, Rockanje, Strijen, Noordwijk, Moordrecht, Maassluis,
Leiderdorp, Vlaardingen) -- de rest (Piershil, Ooltgensplaat, Brielle,
Giessenburg, Wijngaarden, Puttershoek) bleek inderdaad een ander jaartal te
hebben dan de kandidaat suggereerde -- precies de gevallen die bij de
eerste analyse al als "twijfelachtig" waren aangemerkt vanwege een
afwijkende naam of een kandidaat zonder jaartal.

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

De denominatie-kolom is oorspronkelijk een tekstpatroon op de naam (RK/NH/
Gereformeerd/Joods/Doopsgezind/Evangelisch-Luthers/Remonstrants) geweest -
geen apart veld in de data (die kolom is eerder bewust weer verwijderd van
de statistiekenpagina, zie `docs/geschiedenis.md`, 2026-08-26). De
domeinexpert heeft "Gemeentelijk" als aanvullende categorie toegevoegd bij
zijn terugkoppeling; dat staat nu in de tabel, maar is puur ter herkenning
hier, geen nieuwe sitefunctie.

## De 18, gesorteerd op afstand tot de dichtstbijzijnde eigen kandidaat

"Bevestigd jaartal" is de terugkoppeling van de domeinexpert (2026-09-08).
**Vet** = het bevestigde jaartal komt overeen met de kandidaat die hieronder
toch al gevonden was (de koppeling zat inhoudelijk goed, alleen de drempel
of het adres zat in de weg); gewoon lettertype = een ander jaartal dan de
kandidaat suggereerde, of de kandidaat had zelf niets ingevuld.

| Naam | Plaats (gemeente) | Denominatie | Ingang (lat, lon) | Dichtstbijzijnde kandidaat | Afstand | Bevestigd jaartal |
|---|---|---|---|---|---|---|
| Gem. begraafplaats | Schipluiden (Midden-Delfland) | Gemeentelijk | 51,97634, 4,31049 | Gemeentelijke Begraafplaats (1873) | 309 m | **1873** |
| Nieuwe begraafplaats | Rockanje (Voorne aan Zee) | Gemeentelijk | 51,87201, 4,05814 | Nieuwe Begraafplaats (1950) | 334 m | **1950** |
| Gem. begraafplaats | Benthuizen (Alphen aan den Rijn) | Gemeentelijk | 52,07449, 4,54426 | Gemeentelijke Begraafplaats Vrederust (geen jaartal/periode in bron) | 335 m | 1968 (circa) |
| Nieuwe gem. begraafplaats | Piershil (Hoeksche Waard) | Gemeentelijk | 51,79373, 4,31999 | Kerkhof (1524, al gekoppeld aan een ander terrein) | 351 m | 1970 |
| **Joodse begraafplaats** | **Strijen (Hoeksche Waard)** | **Joods** | **51,74719, 4,55647** | **Joodse Begraafplaats (1896)** | **402 m** | **1896** |
| Gem. begraafplaats | Ooltgensplaat (Goeree-Overflakkee) | Gemeentelijk | 51,68705, 4,34725 | Oude NH Kerkhof (Middeleeuwen) | 421 m | 1960 |
| Begraafplaats Sancta Maria | Noordwijk (Noordwijk) | Rooms-Katholiek | 52,27720, 4,48757 | Begraafplaats Sancta Maria centrum voor Psychiatrie (1928) | 450 m | **1928** |
| Oude gem. begraafplaats | Brielle (Voorne aan Zee) | Gemeentelijk | 51,89827, 4,15964 | Nieuwe Begraafplaats (geen jaartal/periode in bron) | 457 m | 1842 |
| Gem. begraafplaats | Giessenburg (Molenlanden) | Gemeentelijk | 51,84227, 4,89412 | Begraafplaats (geen jaartal/periode in bron) | 519 m | 1977 |
| Nieuwe algemene begraafplaats | Wijngaarden (Molenlanden) | Gemeentelijk | 51,84509, 4,77097 | Oude algemene Kerkhof (Middeleeuwen) | 522 m | 1984 |
| RK Kerkhof H. Johannes Onthoofding | Moordrecht (Zuidplas) | Rooms-Katholiek | 51,99197, 4,67706 | Kerkhof H. Johannes' Onthoofding (1852) | 570 m | **1852** |
| Begraafplaats De Dijk | Maassluis (Maassluis) | Gemeentelijk | 51,90904, 4,26807 | De Dijk (2015) | 650 m | **2015** |
| Nieuwe gem. begraafplaats | Leiderdorp (Leiderdorp) | Gemeentelijk | 52,15320, 4,53349 | Nieuwe Algemene Begraafplaats met RK gedeelte (1950) | 653 m | **1950** |
| Uitbreiding nw. Gem. begraafplaats (overzijde weg) | Leiderdorp (Leiderdorp) | Gemeentelijk | 52,15310, 4,53367 | Nieuwe Algemene Begraafplaats met RK gedeelte (1950) | 658 m | 2009 (latere uitbreiding) |
| RK begraafplaats | Brielle (Voorne aan Zee) | Rooms-Katholiek | 51,89624, 4,15278 | Nieuwe Begraafplaats (geen jaartal/periode in bron) | 666 m | 1900 |
| **Joodse begraafplaats** | **Vlaardingen (Vlaardingen)** | **Joods** | **51,90972, 4,35895** | **Joodse Begraafplaats (1862)** | **943 m** | **1862** |
| Nieuwe gem. begraafplaats | Brielle (Voorne aan Zee) | Gemeentelijk | 51,88598, 4,16342 | Nieuwe Begraafplaats (geen jaartal/periode in bron) | 946 m | onbekend (ook bij de domeinexpert) |
| Begraafplaats De Essenhof | Puttershoek (Hoeksche Waard) | Gemeentelijk | 51,79845, 4,56548 | Nieuwe gemeentelijke begraafplaats (1880) | 1016 m | 1993 |

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
