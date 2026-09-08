# Data 007: datering - bevindingen

Voor de domeinexpert: wat de nieuwe jaartal/periode-data (eigen bron,
2026-09-07) oplevert, en waar voorzichtigheid op zijn plaats is. Technische
achtergrond over de koppeling zelf staat in `scripts/analyse_spatial.py`
(`nearest_datering()`) en `src/methode.html` (categorie 5); dit document
gaat over de inhoudelijke uitkomst. Bijgewerkt op 2026-09-08 na een
controleronde van de domeinexpert op de eerder ontbrekende gevallen (zie
[008 Datering - ontbrekend](008-datering-ontbrekend.md)) -- de cijfers
hieronder zijn de actuele stand, niet meer de eerste versie.

## Dekking

Van de 448 begraafplaatsen:

- **304** hebben een exact jaartal;
- **116** hebben alleen een periode ("Middeleeuwen"), geen jaartal;
- **28** hebben geen van beide (geen bruikbare match binnen 300m en ook de
  domeinexpert kent het jaartal niet, of de brondata zelf had niets
  ingevuld).

Samen dus **420 van de 448 (94%)** met een jaartal of periode.

## Verdeling over de tijd

| Periode | Aantal |
|---|---|
| Middeleeuws (periode bekend, geen jaartal) | 116 |
| voor 1829 | 62 |
| 1829-1849 | 38 |
| 1850-1899 | 74 |
| 1900-1949 | 62 |
| 1950-1999 | 55 |
| 2000-heden | 13 |

Dezelfde tabel staat als klikbare filter in het paneel en als balkjesgrafiek
op de statistiekenpagina.

## De cesuur van 1829

De knip bij 1829 is bewust geen ronde eeuwgrens. Vanaf 1 januari 1829 was
begraven in en rond de kerk binnen de bebouwde kom in Nederland wettelijk
verboden (Koninklijk Besluit); plaatsen met meer dan duizend inwoners
moesten een algemene begraafplaats buiten de bebouwde kom inrichten. Dat
keerpunt is in onze eigen data ook terug te zien: 62 begraafplaatsen met een
jaartal vóór 1829, tegenover 37 in de twintig jaar erna (1829-1849) - een
duidelijke knik, geen toeval van de bucketgrenzen.

## Oudste bekende begraafplaatsen

| Jaartal | Naam | Plaats |
|---|---|---|
| 1524 | Gem. kerkhof | Piershil |
| 1613 | Portugees-Joodse Begraafplaats | Rotterdam |
| 1615 | Alg. begraafplaats | Cillaarshoek |
| 1615 | NH Kerkhof Cillaarshoek | Strijen |
| 1646 | NH Kerkhof | Den Bommel |
| 1694 | Joodse begraafplaats | Den Haag |
| 1696 | Joodse begraafplaats Oostzeedijk | Rotterdam |
| 1719 | H Adrianusbegraafplaats | Langeraar |
| 1720 | NH Kerkhof | Ter Heijde |
| 1758 | Joodse begraafplaats | Katwijk aan den Rijn |

De twee treffers op 1615 (Cillaarshoek/Strijen) zijn geen toeval in de data,
maar een concreet voorbeeld van de matching-onzekerheid hieronder: twee
dicht bij elkaar gelegen begraafplaatsen die hetzelfde, dichtstbijzijnde
datering-punt toegewezen kregen. Het jaartal zelf kan best kloppen voor
allebei (kleine plaatsen deelden destijds soms een gemeenschappelijke
oorsprong), maar is niet apart geverifieerd per begraafplaats - de moeite
waard om te controleren als dit ergens toe doet.

## Betrouwbaarheid van de koppeling

De koppeling loopt via het bezoekadres uit de brondata, gegeocodeerd met de
PDOK Locatieserver en vervolgens gekoppeld aan de dichtstbijzijnde ingang
van de hoofddataset (drempel 300m). Dat werkt in verreweg de meeste
gevallen goed - 96% van de 448 valt binnen die drempel - maar twee dingen
zijn de moeite van het weten waard:

**Geen automatische match gevonden voor 18 begraafplaatsen** (dus geen
jaartal/periode getoond, ook al stond het soms wel in de brondata): meestal
plaatsen met meerdere begraafplaatsen dicht bij elkaar, waarbij het adres
uit de brondata net bij een andere, niet in onze 448 voorkomende locatie
uitkwam, of het brongegeven zelf ontbrak. Deze lijst is inmiddels door de
domeinexpert nagelopen ([008 Datering - ontbrekend](008-datering-ontbrekend.md)):
voor 17 van de 18 kon hij het echte jaartal bevestigen (soms omdat de
kandidaat net buiten de 300m-drempel viel, zoals Strijen op 402m), voor 1
(Nieuwe gem. begraafplaats, Brielle) is het jaartal ook bij hem onbekend --
een echte lege waarde in de bron, geen matchingprobleem. Die 17
bevestigingen staan nu als handmatige correctie in
`data/datering-correcties.json` en overschrijven de automatische koppeling
voor precies deze terreinen.

**13 matches op 200-300m** (dus wel getoond, maar met meer onzekerheid dan
de gemiddelde 34m): de moeite waard om steekproefsgewijs te controleren of
het jaartal echt bij het juiste terrein hoort. De verste (280m): Grafkelder
Herkenrath (Monster, jaartal 1844). Volledige lijst op aanvraag.

## Waar te vinden op de site

- **Kaart**: jaartal/periode staan in het begraafplaats-popup (alleen als
  bekend), en zijn te filteren via klikbare periode-balkjes onder "Filters".
- **Statistieken**: histogram + tabel met de oudste bekende jaartallen.
- **Methode**: `src/methode.html`, categorie 5, voor de volledige
  toelichting op de koppelmethode en de bekende beperking.
