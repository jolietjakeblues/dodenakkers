# Data 007: datering - bevindingen

Voor de domeinexpert: wat de nieuwe jaartal/periode-data (eigen bron,
2026-09-07) oplevert, en waar voorzichtigheid op zijn plaats is. Technische
achtergrond over de koppeling zelf staat in `scripts/analyse_spatial.py`
(`nearest_datering()`) en `src/methode.html` (categorie 5); dit document
gaat over de inhoudelijke uitkomst. Bijgewerkt op 2026-09-08 na een
controleronde van de domeinexpert op de eerder ontbrekende gevallen (zie
[008 Datering - ontbrekend](008-datering-ontbrekend.md)), en opnieuw op
2026-10-16 na een volledig vernieuwde Excel van de domeinexpert (inclusief
twee nieuwe begraafplaatsen, Natuurbegraafplaats Staelduinen en NH Kerkhof
Noordwijk) -- de cijfers hieronder zijn de actuele stand, niet meer de
eerste versie. Opnieuw bijgewerkt op 2026-10-19 na de antwoorden van de
domeinexpert op [009 Vragen aan de domeinexpert](009-vragen-domeinexpert.md)
en een controle van de koppelmethode zelf (zie "Betrouwbaarheid van de
koppeling").

## Dekking

Van de 450 begraafplaatsen:

- **309** hebben een exact jaartal;
- **114** hebben alleen een periode ("Middeleeuwen"), geen jaartal;
- **27** hebben geen van beide (de Excel heeft er geen jaartal of periode
  voor ingevuld).

Samen dus **423 van de 450 (94%)** met een jaartal of periode. Elke
begraafplaats heeft een koppeling met de Excel; de 27 zijn echte lege
waarden in de bron, geen matchingprobleem.

## Verdeling over de tijd

| Periode | Aantal |
|---|---|
| Middeleeuws (periode bekend, geen jaartal) | 114 |
| voor 1829 | 61 |
| 1829-1849 | 39 |
| 1850-1899 | 79 |
| 1900-1949 | 62 |
| 1950-1999 | 54 |
| 2000-heden | 14 |

Dezelfde tabel staat als klikbare filter in het paneel en als balkjesgrafiek
op de statistiekenpagina.

## De cesuur van 1829

De knip bij 1829 is bewust geen ronde eeuwgrens. Vanaf 1 januari 1829 was
begraven in en rond de kerk binnen de bebouwde kom in Nederland wettelijk
verboden (Koninklijk Besluit); plaatsen met meer dan duizend inwoners
moesten een algemene begraafplaats buiten de bebouwde kom inrichten. Dat
keerpunt is in onze eigen data ook terug te zien: 61 begraafplaatsen met een
jaartal vóór 1829, tegenover 39 in de twintig jaar erna (1829-1849) - een
duidelijke knik, geen toeval van de bucketgrenzen.

## Oudste bekende begraafplaatsen

| Jaartal | Naam | Plaats |
|---|---|---|
| 1524 | Gem. kerkhof | Piershil |
| 1613 | Portugees-Joodse Begraafplaats | Rotterdam |
| 1615 | NH Kerkhof Cillaarshoek | Strijen |
| 1646 | NH Kerkhof | Den Bommel |
| 1694 | Joodse begraafplaats | Den Haag |
| 1696 | Joodse begraafplaats Oostzeedijk | Rotterdam |
| 1719 | H Adrianusbegraafplaats | Langeraar |
| 1720 | NH Kerkhof | Ter Heijde |
| 1758 | Joodse begraafplaats | Katwijk aan den Rijn |
| 1767 | Joodse begraafplaats | Schoonhoven |

Eerder stond hier ook de Alg. begraafplaats in Cillaarshoek met 1615. Dat was
een koppelfout (zie "Betrouwbaarheid van de koppeling"): de Excel geeft
daarvoor 1872. Alleen NH Kerkhof Cillaarshoek (Strijen) heeft 1615.

## Betrouwbaarheid van de koppeling

Sinds 2026-10-19 loopt de koppeling in drie stappen, in deze volgorde:

1. **Bevestiging door de domeinexpert** (35 begraafplaatsen, in
   `data/datering-correcties.json`): wint altijd.
2. **Naam en plaats** (217 begraafplaatsen): komen de naamwoorden van het
   terrein (zonder "begraafplaats"/"kerkhof", afkortingen als "Gem." en "Alg."
   uitgeschreven) en de plaats eenduidig overeen met een Excel-rij, dan is dat
   de rij. De Excel is leidend.
3. **Dichtstbijzijnde adres** (198 begraafplaatsen, mediaan 38 m): het
   bezoekadres uit de Excel, gegeocodeerd met de PDOK Locatieserver en
   gekoppeld aan de dichtstbijzijnde ingang (drempel 300m). Alleen voor
   terreinen waarvan de naam niet eenduidig te koppelen is.

Aanleiding voor stap 2 was een controle na de antwoorden op
[009](009-vragen-domeinexpert.md): de nabijheidskoppeling bleek bij vijf
begraafplaatsen de verkeerde Excel-rij te pakken, omdat het geocodeerde adres
dichter bij een buur lag. Kerkhof Groene Kerkje in Oegstgeest kreeg 2011 van de
Nieuwe Begraafplaats (de Excel zegt Middeleeuwen), de Joodse begraafplaats in
Wassenaar kreeg 1982 van de gemeentelijke begraafplaats ernaast (Excel: 1906),
Tombe Bisdom van Vliet in Haastrecht kreeg Middeleeuwen (Excel: 1881), Oude
gemeentelijke Begraafplaats Maasland kreeg 1933 (Excel: 1829) en Alg.
begraafplaats Cillaarshoek kreeg 1615 (Excel: 1872). Waar naam en plaats wel
eenduidig te koppelen waren, klopte de nabijheidskoppeling in 208 van de 213
gevallen. Bij ruim 200 andere terreinen (niet gecorrigeerd) is de naam niet
gelijk aan een Excel-naam of dubbelzinnig, zodat dit niet te controleren was.
Daar blijft de nabijheidskoppeling de enige bron en dus het zwakste deel.

Eerder, voor deze controle, gold alleen de nabijheid. Dat werkte in verreweg
de meeste gevallen goed, maar twee dingen zijn de moeite van het weten waard:

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

**5 nabijheidsmatches op 200-300m** (dus wel getoond, maar met meer
onzekerheid dan de mediaan van 38m): de moeite waard om steekproefsgewijs te
controleren of het jaartal echt bij het juiste terrein hoort. De verste
(281m): Grafkelder Herkenrath (Monster, jaartal 1844). Volledige lijst op
aanvraag.

**Op 2026-10-19 is ook de "twee Excel-rijen op dezelfde plek"-situatie
opgelost** (14 begraafplaatsen op 8 locaties, zoals Maassluis, Oud-Rijswijk en
Puttershoek): de koppeling kon daar niet kiezen en gaf bij beide terreinen
dezelfde waarde. De domeinexpert heeft per begraafplaats bevestigd welk
jaartal erbij hoort, en dat staat nu vast in de correcties. Daarbij kwam ook
Voorhout (Particuliere alg. begraafplaats, 1976) naar boven, die ten onrechte
"Middeleeuwen" kreeg.

**De twee nieuwe begraafplaatsen uit 2026-10-16** (Natuurbegraafplaats
Staelduinen, Hoek van Holland; NH Kerkhof, Noordwijk) stonden zelf ook in de
vernieuwde Excel en zijn zonder handmatige correctie automatisch gekoppeld:
Staelduinen op 79m (jaartal 2026), NH Kerkhof Noordwijk op 35m (periode
Middeleeuwen) -- allebei ruim binnen de drempel.

## Waar te vinden op de site

- **Kaart**: jaartal/periode staan in het begraafplaats-popup (alleen als
  bekend), en zijn te filteren via klikbare periode-balkjes onder "Filters".
- **Statistieken**: histogram + tabel met de oudste bekende jaartallen.
- **Methode**: `src/methode.html`, categorie 5, voor de volledige
  toelichting op de koppelmethode en de bekende beperking.
