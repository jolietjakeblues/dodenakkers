# Data 009: vragen aan de domeinexpert

Stand: 2026-10-16, na verwerking van de nieuwste levering (Excel met 450 rijen
in tabblad "Alle begraafplaatsen", plus de kmz voor NH Kerkhof, Noordwijk). De kaart
toont nu 450 begraafplaatsen. Bij het naast elkaar leggen van de Excel en de
kaart bleven een paar punten over waar alleen jij het antwoord weet. Er is niets
aangepast op basis van aannames: alles hieronder staat nog zoals het in de bron
zat.

Je kunt per vraag je antwoord in de laatste kolom of eronder zetten. Kijk bij
twijfel op de kaart via [de site](../../src/index.html). De id's (`zh-0229`) zijn
interne nummers en staan niet in het popup; zoek de begraafplaats daar op naam en
plaats.

## Overzicht

| # | Onderwerp | Aantal | Prioriteit |
|---|---|---:|---|
| 1 | Status geruimd: Excel en kaart zeggen iets anders | 2 | hoog |
| 2 | Datering: twee Excel-rijen op dezelfde plek, kaart kan niet kiezen | 14 begraafplaatsen (8 locaties) | hoog |
| 3 | Terreinen zonder (zekere) datering | 3 | middel |
| 4 | Nummering: hetzelfde nummer bij twee begraafplaatsen | 3 nummers | middel |
| 5 | Gemeente: Excel en kaart verschillen | 2 | laag |
| 6 | Weergave op de kaart (ME, gesloten) | 2 | laag |

## 1. Status geruimd

De Excel telt **50** begraafplaatsen met status "Geruimd", de kaart **48**. Twee
daarvan zijn met zekerheid aan te wijzen (naam en plaats komen exact overeen).
De kaartstatus komt uit de kmz/CSV die je eerder aanleverde, de Excel is een
andere levering.

| Excel Nr | Naam, plaats | Kaart (id) | Excel zegt | Kaart zegt | Antwoord |
|---:|---|---|---|---|---|
| 75 | NH Kerkhof, Middelharnis | `zh-0229` | Geruimd | niet geruimd | |
| 241 | NH kerkhof, Hoogblokland | `zh-0425` | Geruimd | niet geruimd | |

Is de Excel hier de juiste, dan zetten we beide op geruimd. De totalen komen dan
overeen met de Excel: 50 geruimd en 400 niet-geruimd (316 in gebruik + 84
gesloten).

*Ter controle, geen actie nodig tenzij het fout is:* negen andere geruimde
Excel-rijen hebben een andere naam dan op de kaart, maar in hetzelfde dorp staat
precies één geruimde begraafplaats op de kaart. We hebben ze zo aan elkaar
gekoppeld:

| Excel Nr, naam | Plaats | Kaart (id, naam) |
|---|---|---|
| 39, Kerkhof | Aarlanderveen | `zh-0313`, NH Kerkhof |
| 116, HH Michael en Bernarduskerkhof (Scheepjeskerk) | Hazerswoude Rijndijk | `zh-0303`, H. Michael en Bernarduskerkhof |
| 170, Oude kerkhof Scheveningen | Scheveningen | `zh-0416`, NH kerkhof |
| 235, NH kerkkhof | Dirksland | `zh-0423`, NH kerkhof |
| 67, H Jacobusbegraafplaats (later gemeentelijk) | Oude Wetering | `zh-0003`, RK begraafplaats |
| 128, Oude Kerkhof | Woubrugge | `zh-0440`, NH kerkhof |
| 26, Voormalig Kerkhof | Maasland | `zh-0332`, Vm. NH kerkhof |
| 277, Hervormd Kerkhof | Schipluiden | `zh-0430`, NH kerkhof |
| 207, Gem. begraafplaats | Monster | `zh-0417`, Oude gem. begraafplaats |

## 2. Datering: twee Excel-rijen op dezelfde plek

Bij 14 begraafplaatsen liggen in de Excel twee rijen op (vrijwel) hetzelfde punt,
met een verschillend jaartal of periode. De kaart koppelt de dichtstbijzijnde
rij en kan dan niet kiezen: bij beide begraafplaatsen van een paar toont hij nu
**dezelfde** waarde, dus minstens één van de twee is waarschijnlijk fout. De
kolom "Voorstel" is een vermoeden op basis van de naam, geen besluit.

| Kaart (id, naam) | Excel-rijen op die plek (Nr, naam, jaar/periode) | Kaart toont nu | Voorstel | Antwoord |
|---|---|---|---|---|
| `zh-0034` Grafkelder Van Wassenaar, Katwijk aan den Rijn | 1363 Grafkelder Van Wassenaar, 1858 · 1386 NH Kerkhof, ME | ME | 1858 | |
| `zh-0035` NH Kerkhof, Katwijk aan den Rijn | (dezelfde twee) | ME | ME | |
| `zh-0038` Gem. begraafplaats De Bleekerij, Katwijk aan den Rijn | 4189 Joodse Begraafplaats, 1758 · 1409 Begraafplaats de Bleekerij, 2010 | 1758 | 2010 | |
| `zh-0058` Joodse begraafplaats, Maassluis | 1389 Gemeentelijke + Joodse Begraafplaats, 1887 · 4140 Joodse Begraafplaats op Algemene Begraafplaats, 1950 | 1950 | 1950 | |
| `zh-0059` Gemeentelijke begraafplaats, Maassluis | (dezelfde twee) | 1950 | 1887 | |
| `zh-0076` Joods deel op Oud Rijswijk, Rijswijk | 3023 Begraafplaats Oud-Rijswijk (oude gemeentelijke), 1916 · 874 Joodse Begraafplaats op Algemene Begraafplaats, 1937 | 1937 | 1937 | |
| `zh-0077` Begraafplaats Oud-Rijswijk, Rijswijk | (dezelfde twee) | 1937 | 1916 | |
| `zh-0078` Liberaal Joodse begraafplaats, Rijswijk | 243 Liberaal Joodse Begraafplaats Beth Hachaim, 1990 · 3245 Yardenhuis van Rijswijk, 1972 | 1990 | 1990 | |
| `zh-0079` Gem. begraafplaats Eikelenburg, Rijswijk | (dezelfde twee) | 1990 | geen voorstel | |
| `zh-0161` RK Kerkhof, Voorhout | 1483 Algemene particuliere Begraafplaats, 1976 · 1349 Kerkhof St Bartholomeus, 1882 | 1976 | 1882 | |
| `zh-0231` Gem. Begraafplaats, Stad aan 't Haringvliet | 2153 Algemene Begraafplaats, 1877 · 280 NH kerkhof, ME | 1877 | 1877 | |
| `zh-0434` NH kerkhof, Stad aan 't Haringvliet | (dezelfde twee) | 1877 | ME | |
| `zh-0389` Oude alg. begraafplaats, Puttershoek | 1943 Nieuwe gemeentelijke begraafplaats, 1880 · 1948 Oude gemeentelijke begraafplaats, 1827 | 1827 | 1827 | |
| `zh-0390` NH begraafplaats, Puttershoek | (dezelfde twee) | 1827 | geen voorstel | |

Als je de juiste waarde bevestigt, leggen we dat vast in
`data/datering-correcties.json` (zoals eerder voor de 17 gevallen uit
[008](008-datering-ontbrekend.md)); het overschrijft dan de automatische keuze
voor precies die begraafplaats.

## 3. Terreinen zonder zekere datering

Voor drie begraafplaatsen vindt de kaart geen Excel-rij binnen 300 m van de
ingang.

| Kaart (id, naam, plaats) | Dichtstbijzijnde Excel-rij | Vraag | Antwoord |
|---|---|---|---|
| `zh-0138` Nieuwe gem. begraafplaats, Brielle | 1733 Nieuwe Begraafplaats, Brielle (947 m, geen jaartal in de Excel) | Is dit dezelfde begraafplaats? Zo ja: het jaartal is ook in de Excel leeg, is dat bekend? | |
| `zh-0234` Gem. begraafplaats Westduin, Den Haag | 3019 Gemeentelijke Begraafplaats Westduin, 's-Gravenhage, 1929 (301 m, 1 m boven de drempel) | Klopt 1929 voor deze begraafplaats? | |
| `zh-0431` Asurn Hazelhoff Roelfsema bij monument gevallenen Wassenaarseslag, Wassenaar | 4337, zelfde naam, 2007 (332 m) | Klopt 2007? | |

## 4. Nummering in de Excel

In de kolom Nr komen drie nummers twee keer voor, steeds bij twee verschillende
begraafplaatsen. We gebruiken Nr daardoor niet als sleutel, maar het is goed om
te weten of dit zo bedoeld is.

| Nr | Eerste rij | Tweede rij | Bedoeld? |
|---:|---|---|---|
| 66 | Begraafplaats Slachtoffers Watersnoodramp 1953, Oude-Tonge | NH Kerkhof, Zwammerdam | |
| 67 | Nieuwe Algemene Begraafplaats, Oude-Tonge | H Jacobusbegraafplaats (later gemeentelijk), Oude Wetering | |
| 74 | RK Begraafplaats, Oude-Tonge | NH Kerkhof, 's-Gravendeel | |

## 5. Gemeente

De kaart bepaalt de gemeente ruimtelijk uit de actuele gemeentegrenzen (PDOK), de
Excel heeft een eigen kolom. Over het geheel komen de aantallen per gemeente
overeen, op één verschuiving na:

| Begraafplaats (id) | Excel-gemeente | Kaart-gemeente | Juist? |
|---|---|---|---|
| `zh-0353` NH Kerkhof, Oudenhoorn (Excel Nr 162) | Nissewaard | Voorne aan Zee | |
| `zh-0354` Gem. begraafplaats, Oudenhoorn (Excel Nr 1712) | Nissewaard | Voorne aan Zee | |

## 6. Weergave op de kaart

- **Periode "ME".** In de nieuwe Excel staat bij 116 rijen alleen de periode
  `ME` (vroeger stond er `Middeleeuwen`). In het popup staat nu letterlijk
  "Periode: ME". Is ME = Middeleeuwen, en mogen we dat voluit tonen?
- **Status "gesloten".** De Excel kent drie statussen: in gebruik (316), gesloten
  (84) en geruimd (50). De kaart toont alleen geruimd of niet-geruimd, dus
  "gesloten" is niet te zien of te filteren. Is dat onderscheid voor het
  onderzoek bruikbaar als filter?

## Wat al klopt (geen actie)

- NH Kerkhof, Noordwijk (geruimd) uit de nieuwe kmz staat op de kaart (`zh-0450`).
- De Excel (450 rijen) en de kaart (450 begraafplaatsen) komen per gemeente
  overeen, behalve punt 5.
- Het tabblad "Verdwenen" van de Excel (92 rijen) komt overeen met de laag
  "Verdwenen begraafplaatsen" (92 punten).
- De overige tabbladen van de Excel (Per Gem., Statistiek, TOTALEN, Grondvorm,
  Ontwerpers, Veldnamen) gebruiken we niet op de kaart; laat het weten als er iets
  uit nodig is.
