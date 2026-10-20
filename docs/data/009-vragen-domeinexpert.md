# Data 009: vragen aan de domeinexpert

Vragenlijst van 2026-10-16, na verwerking van de nieuwste levering (Excel met 450
rijen in tabblad "Alle begraafplaatsen", plus de kmz voor NH Kerkhof, Noordwijk).
**Beantwoord en verwerkt op 2026-10-19.** Deze pagina bewaart per vraag het
antwoord en wat ermee gedaan is. Een verzendklare tekstversie van de oorspronkelijke
vragen staat in [009-vragen-domeinexpert.txt](009-vragen-domeinexpert.txt).
Nieuwe vragen staan onderaan (sectie 7).

Uitgangspunt van de domeinexpert bij elk verschil tussen Excel en kaart: **de
Excel is leidend.**

## 1. Status geruimd

De Excel telde 50 begraafplaatsen met status "Geruimd", de kaart 48.

| Begraafplaats | Antwoord | Verwerkt |
|---|---|---|
| NH Kerkhof, Middelharnis (Excel nr 75) | "De excel gaat hier boven wat er op de kaart staat! Dus geruimd." | Bron-CSV aangepast (terrein- en ingangrij), zie [003](003-csv-bron-en-koppeling.md). |
| NH kerkhof, Hoogblokland (Excel nr 241) | "Idem als vorige." | Idem. |
| Negen andere geruimde Excel-rijen met een andere naam dan op de kaart (Aarlanderveen, Hazerswoude Rijndijk, Scheveningen, Dirksland, Oude Wetering, Woubrugge, Maasland, Schipluiden, Monster) | "Helemaal goed, aantal in excel aangepast" | Geen actie: onze koppeling klopte. |

Resultaat: 50 geruimd en 400 niet-geruimd (316 in gebruik + 84 gesloten), exact
gelijk aan de Excel.

## 2. Datering: twee Excel-rijen op dezelfde plek

De koppeling kon bij 14 begraafplaatsen niet kiezen en gaf beide dezelfde waarde.
Per begraafplaats is nu het bevestigde jaartal vastgelegd in
`data/datering-correcties.json` (zie [007](007-datering-bevindingen.md)).

| Begraafplaats | Antwoord | Verwerkt als |
|---|---|---|
| Grafkelder Van Wassenaar, Katwijk aan den Rijn | voorstel prima, "de excel heeft het laatste woord" | 1858 |
| NH Kerkhof, Katwijk aan den Rijn | idem | Middeleeuwen |
| Gem. begraafplaats De Bleekerij, Katwijk aan den Rijn | "geldt inderdaad 2010 als jaar van aanleg" | 2010 |
| Joodse begraafplaats, Maassluis | "Correct, de Joodse begraafplaats is hier in 1950 naar toe overgebracht" | 1950 |
| Gemeentelijke begraafplaats, Maassluis | idem (voorstel 1887) | 1887 |
| Joods deel op Oud Rijswijk, Rijswijk | "Ook correct zo, het Joodse deel is later daar aangelegd" | 1937 |
| Begraafplaats Oud-Rijswijk, Rijswijk | idem (voorstel 1916) | 1916 |
| Liberaal Joodse begraafplaats, Rijswijk | "de excel heeft altijd het laatste woord" | 1990 |
| Gem. begraafplaats Eikelenburg, Rijswijk | "bij begraafplaats Eikelenburg moet 1972 komen" | 1972 |
| RK Kerkhof, Voorhout | "De katholieke St. Bartholomeus is van 1882 (afgesplitst) en de particuliere begraafplaats kwam er in 1976 bij" | 1882 |
| Particuliere alg. begraafplaats, Voorhout (niet gevraagd, bleek uit het antwoord) | idem | 1976 (kreeg ten onrechte "Middeleeuwen") |
| Gem. Begraafplaats, Stad aan 't Haringvliet | "Correct" | 1877 |
| NH kerkhof, Stad aan 't Haringvliet | "Correct" | Middeleeuwen |
| Oude alg. begraafplaats, Puttershoek | voorstel 1827 | 1827 |
| NH begraafplaats, Puttershoek | "inderdaad de nieuwe gemeentelijke begraafplaats uit 1880, dus graag dat jaartal meegeven. Let op, dus ook de naam dient aangepast te worden!" | 1880 en hernoemd naar "Nieuwe gemeentelijke begraafplaats" |

## 3. Begraafplaatsen zonder zekere datering

| Begraafplaats | Antwoord | Verwerkt als |
|---|---|---|
| Nieuwe gem. begraafplaats, Brielle | "Het is niet dezelfde begraafplaats maar ligt wel aan dezelfde straat. De oude (1717) is van 1842 en de nieuwe (1733) van circa 1994. Jaartal was niet bekend, maar onderzoek wijst op deze datum!" | circa 1994 (de oude, 1842, stond al vast) |
| Gem. begraafplaats Westduin, Den Haag | "Ja, 1929 is het jaartal" | 1929 |
| Asurn Hazelhoff Roelfsema, Wassenaar | "4337 is correct. De urn is hier inderdaad in 2007 geplaatst" | 2007 |

## 4. Nummering in de Excel

De nummers 66, 67 en 74 komen elk twee keer voor. Antwoord: dat klopt; de geruimde
begraafplaatsen (NH Kerkhof Zwammerdam, H Jacobusbegraafplaats Oude Wetering,
NH Kerkhof 's-Gravendeel) komen uit een aparte lijst en zijn in de Excel geel
gemarkeerd. **Verwerkt:** geen actie. Nr blijft ongeschikt als unieke sleutel en
wordt niet als zodanig gebruikt.

## 5. Gemeente

Oudenhoorn (beide begraafplaatsen): "Moet inderdaad Voorne aan Zee zijn! Gecorrigeerd
in excel." **Verwerkt:** geen actie, de kaart zei al Voorne aan Zee.

## 6. Weergave op de kaart

| Onderwerp | Antwoord | Verwerkt |
|---|---|---|
| Periode "ME" | "Er stond nooit middeleeuwen, maar dat mag je er wel van maken" | Voluit "Middeleeuwen" getoond, ruwe waarde bewaard als `periode_bron`. |
| Status "gesloten" | "Het mag meegenomen worden als status, maar omdat niet altijd duidelijk is of het klopt eerst niet opgenomen." | Niet opgenomen. Staat in de Excel (84), kan later alsnog. |

## 7. Rijksmonumenten: de telling "22 begraafplaatsen zelf rijksmonument"

**Vraag van de domeinexpert:** de statistiek zegt dat 22 begraafplaatsen zelf een
rijksmonument zijn. Als 'begraafplaats' kan dat kloppen, maar ook onderdelen kunnen
beschermd zijn: de Excel nog eens bekijken, welke begraafplaatsen beschermd zijn of
een beschermd onderdeel bevatten.

**Bevinding.** De 22 komt uit de RCE-gegevens en telt alleen een rijksmonument
met een begraafplaats-functie (begraafplaats zelf, hek, aula, ...) dat op of aan het
terrein ligt. De Excel (kolom *Rijksmonument* = Ja) kent **54** begraafplaatsen die
zelf rijksmonument zijn of een beschermd onderdeel bevatten. Gekoppeld aan de kaart
(indicatief; per Excel-rij gekoppeld op naam en adres):

| Wat | Aantal |
|---|---:|
| Staat in de bestaande telling van 22 | 22 |
| Monument ligt op of aan het terrein, maar met een andere functie (poortgebouw, kapel, kerk, ...) | 8 |
| Monument bestaat in onze RCE-gegevens, maar ligt 1 tot 42 m naast de terreingrens (vooral hekken, baarhuisjes, grafkapellen) | 19 |
| Monument bestaat in onze RCE-gegevens, maar ligt 285 m van het terrein (zie vraag 7a) | 1 |
| Rijksmonumentnummer zit niet in onze RCE-gegevens (waarschijnlijk een complex; zie vraag 7c) | 3 |
| Rij niet aan een terrein te koppelen: de naam in de Excel wijkt te veel af van de kaart (Grafkelder familie Herckenrath, Monster) | 1 |

De kolom *Beschermd deel* zegt wat er precies beschermd is (bijvoorbeeld
"Begraafplaats", "Toegangshek", "Grafkapel", "Poortgebouw").

**Verwerkt.** De statistiekenpagina heeft een nieuwe sectie "Rijksmonument of
beschermd onderdeel volgens de Excel" met alle 54 rijen en de tekst van *Beschermd
deel* ongewijzigd uit de Excel (geen eigen indeling). De uitleg bij de 22 is
aangescherpt: die telling is smaller en bedoeld als RCE-controle.

**Antwoord op het geheel (2026-10-20):** "Veel rijksmonumenten staan inderdaad bij
de RCE niet goed. Veel begraafplaatsen zelf hebben geen adres en dan wordt de
puntlocatie wel op een adres gezet, maar dat is vaak niet op de begraafplaats
zelf. Het zij zo!" De naamconventie tussen Excel en kmz "kan inderdaad beter,
maar is allemaal oud handwerk waarvan destijds nog niet zo het belang van een
exacte match werd gezien".

| # | Vraag | Antwoord | Verwerkt |
|---|---|---|---|
| 7a | Tombe Bisdom van Vliet, Haastrecht: terrein op de kaart 285 m van het rijksmonument. Goede plek, of ligt het monument in een andere begraafplaats? | "Ligt in werkelijkheid nog iets verder op het terrein en dat is in de bron gecorrigeerd. Hoeft niet op deze kaart. Het punt van het rijksmonument staat inderdaad op het adres Hoogstraat 164, maar ligt daar dus totaal verkeerd." | Geen kaartwijziging. De statistiek toont "geen monument binnen 250 m"; de uitleg in [004](004-rce-mcp-querystrategie.md) noemt dit als voorbeeld van een RCE-puntlocatie op een adres. |
| 7b | Gemeentelijke monumenten (64 in de Excel) ook als telling of filter? | "Kunnen filteren op gemeentelijk beschermd ja of nee, zou leuk zijn. Dat kan ik nu niet in mijn Google Maps, alleen in de excel." | Gebouwd: filtergroep "Gemeentelijk monument" (Gemeentelijk beschermd / Niet gemeentelijk beschermd), plus popupregels "Gemeentelijk monument", "Rijksmonument volgens Excel" en "Beschermd deel (Excel)". Zie hieronder. |
| 7c | Drie nummers (516118, 512186, 524448) niet in onze RCE-gegevens: complexnummers? | "Dat zijn inderdaad complexnummers met meerdere beschermde onderdelen nabij. Het lastige is dat een monumentnummer kiezen de lading niet dekt. Dus inclusief complexnummers zou mooi zijn." | Gebouwd: `scripts/fetch_complexen.py` zoekt alle nummers op als rijksmonument en complex. 13 van de 54 zijn een complex (samen 50 onderdelen); de statistiekenpagina toont per complex de onderdelen en hoeveel daarvan op of aan het terrein liggen, zie [004](004-rce-mcp-querystrategie.md). |

**Hoe het gemeentelijke filter aan de Excel gekoppeld is.** Een terrein en een Excel-rij
hebben geen gedeelde sleutel (Nr is niet uniek, de namen verschillen). Omdat Excel en kaart
evenveel begraafplaatsen hebben, wijst `scripts/excel_koppeling.py` ze een-op-een aan elkaar toe
op naamovereenkomst, plaats en afstand. Alle 450 terreinen zijn gekoppeld: 64 zijn gemeentelijk
beschermd, 386 niet, en alle 64 komen overeen met de Excel. De Excel-status (geruimd) komt bij
alle terreinen die de controle kon nalopen overeen met de kaart, wat een onafhankelijke toets op
de toewijzing is. Bij de koppeling kwamen drie datering-fouten naar boven die nu zijn gecorrigeerd:
Oude gem. begraafplaats Voorburg stond op "Middeleeuwen" (nu 1874, de Oude Algemene
Begraafplaats met poortgebouw), de Gem. begraafplaats in Oude Tonge op 1867 (nu circa 1952) en
de Oude gem. begraafplaats in Middelharnis op 1865 (nu 1895).

**Nieuwe vragen aan de domeinexpert (ter bevestiging):**

| # | Vraag | Antwoord |
|---|---|---|
| 8a | Voorburg: klopt het dat "NH Kerkhof" bij Excel-rij 346 "Kerkhof Oude Kerk" hoort (Middeleeuwen) en "Oude gem. begraafplaats" bij rij 3000 "Oude Algemene Begraafplaats" (rijksmonument 524448, 1874)? We hadden die twee verwisseld. | |
| 8b | Leiderdorp: klopt het dat "Nieuwe gem. begraafplaats" bij rij 1338 "Nieuwe Algemene Begraafplaats met RK gedeelte" hoort, en "Gem. kerkhof" bij rij 670 "Oude Algemene kerkhof"? | |
| 8c | Vijf andere koppelingen hebben we vastgezet omdat de naamvorm te veel afwijkt: Oude Tonge "Gem. begraafplaats" = rij 67 "Nieuwe Algemene Begraafplaats"; Capelle-West "Gem. begraafplaats" = rij 3664; Meije "RK begraafplaats" = rij 2899 "Onze Lieve Vrouw Geboortebegraafplaats"; Bergambacht "Gem. begraafplaats" = rij 2255 "Algemene Begraafplaats"; Scheveningen "NH kerkhof" = rij 170 "Oude kerkhof Scheveningen". Klopt dat? | |

## 9. Controle van "gemeentelijk beschermd" tegen Wikipedia

Op verzoek van de opdrachtgever is de gemeentelijk-monument-vlag uit de Excel (64 ja) naast de
Wikipedia-lijsten "Lijst van gemeentelijke monumenten in Zuid-Holland" gelegd
(`scripts/controle_wikipedia_gemeentelijke_monumenten.py`). **Wikipedia is alleen een controle,
geen bron:** de Excel blijft leidend en er is niets in de data of op de kaart veranderd. Wikipedia
is onvolledig en geeft bij adressen met "ong." een grove locatie.

**Uitkomst.** Van 88 Wikipedia-lijsten (8.913 gemeentelijke monumenten) gaan er 71 over
begraafplaatsen of onderdelen daarvan, waarvan 64 met coördinaten. Bij 38 terreinen staat een
gemeentelijk monument op of aan het terrein (binnen 30 m); alle 38 zijn in de Excel
"gemeentelijk beschermd". Er is dus geen tegenspraak. Voor de overige 26 van de 64 Excel-"ja"-terreinen
is op Wikipedia geen bruikbare vermelding te vinden; dat zegt niets over de Excel. Wel liggen er bij
drie terreinen die de Excel "niet gemeentelijk" noemt monumenten op 100 tot 116 m afstand:

| # | Vraag | Antwoord |
|---|---|---|
| 9a | Den Haag, Gem. begraafplaats Westduin: Wikipedia noemt het gemeentelijk monument "Aula bij Begraafplaats Westduin" (Wijndaelersingel 3-5), 116 m van het terrein. De Excel zegt hier "Nee". Is de aula een gemeentelijk monument, en hoort die bij de begraafplaats? | |
| 9b | Hardinxveld-Giessendam, Gem. begraafplaats Krommegat: Wikipedia noemt "Grafkelder van de familie Wisboom" (Kromme Gat 12), 99 m van het terrein. Excel: "Nee". Is die grafkelder een gemeentelijk monument op deze begraafplaats? | |
| 9c | Katwijk aan Zee, Hervormde begraafplaats: Wikipedia noemt "Kosterij/rouwkamer" (Zuidstraat 103), 100 m van het terrein. Waarschijnlijk de kosterij van de kerk en geen onderdeel van de begraafplaats; klopt dat? | |
| 9d | Maasland: Wikipedia noemt drie begraafplaatsen (Hammerdreef 1, Hofsingel, Commandeurskade), de Excel geeft "Ja" aan de RK begraafplaats, de Oude gemeentelijke en de Nieuwe gemeentelijke Begraafplaats. Zijn dat dezelfde drie? De Hofsingel ligt het dichtst bij de Vm. NH kerkhof (Excel: "Nee"). | |

Pas bij een bevestiging wordt de Excel-waarde (of het beschermde deel) aangepast.
