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

**Nieuwe vragen:**

| # | Vraag | Antwoord |
|---|---|---|
| 7a | Tombe Bisdom van Vliet, Haastrecht (Excel nr 334, rijksmonument 512498): het terrein op de kaart ligt 285 m van het rijksmonument zelf (het Grafmonument). Staat het terrein op de kaart op de goede plek, of ligt het monument in een andere begraafplaats (bijvoorbeeld het NH kerkhof in Haastrecht)? | |
| 7b | De Excel kent ook 64 begraafplaatsen met *Gemeentelijk monument* = Ja (58 alleen gemeentelijk, 4 ook rijksmonument, 2 zonder beschermd deel); ook daar is *Beschermd deel* ingevuld. De kaart toont alleen rijksmonumenten. Wil je gemeentelijke monumenten ook als telling of filter? | |
| 7c | Drie rijksmonumentnummers uit de Excel (516118 Aarlanderveen, 512186 Ouderkerk aan den IJssel, 524448 Voorburg) zitten niet in onze RCE-gegevens. Zijn dit complexnummers met onderdelen (hek, baarhuisje, poortgebouw) op de begraafplaats? Zo ja, dan halen we die onderdelen erbij uit de RCE-gegevens. | |
