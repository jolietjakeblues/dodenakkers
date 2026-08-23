# Data 003: CSV als genormaliseerde bronlaag

## Besluit

Voor de verdere verwerking gebruiken we de aangeleverde CSV als primaire genormaliseerde invoerlaag.

De KML blijft behouden als oorspronkelijke kaartbron en controlemateriaal.

## Beschikbare velden

De CSV bevat:

```text
WKT
naam
plaats (origineel)
plaats (opgeschoon)
geruimd
ingang
begraafplaats
```

Hierdoor hoeven drie betekenissen niet meer uit naam of geometrie te worden geraden:

- `geruimd`: bronstatus;
- `ingang`: het record is een toegangspunt;
- `begraafplaats`: het record is een terrein.

## Brongeometrie

- record met `begraafplaats` bevat de terreinpolygoon;
- record met `ingang` bevat het toegangspunt;
- terrein en ingang blijven afzonderlijke geometrieën met een eigen betekenis.

## Koppelstrategie

We koppelen in deze volgorde:

1. unieke combinatie van genormaliseerde `naam` + `plaats (opgeschoon)`;
2. voor resterende naamvarianten: ruimtelijke nabijheid van ingang tot terrein;
3. bijzondere gevallen expliciet markeren;
4. geen ontbrekende ingang verzinnen.

De bronvelden blijven altijd bewaard zodat elke automatische koppeling controleerbaar is.

## Bijzondere gevallen

### Duinrust, Katwijk aan Zee

Eén ingangspunt heet:

`Gem. begraafplaats Duinrust en NH begraafplaats`

Dit punt ligt bij twee afzonderlijke terreinrecords. We behandelen dit als een gedeelde ingang en bewaren beide terreinen als afzonderlijke records.

### Oudenhoorn (2026-08-23, opgelost -- in twee stappen, tweede stap definitief)

Voor `Gem. begraafplaats, Oudenhoorn` was in de bron geen ingangspunt
gevonden (`koppelwijze = missing`). Bij het uitzoeken bleek de bron wél een
ingangpunt te bevatten, maar verkeerd gelabeld: getagd als `NH Kerkhof,
Oudenhoorn` (koppelde dus via exacte naam+plaats aan het NH Kerkhof-terrein),
terwijl het punt ruimtelijk 132 m van het NH Kerkhof-terrein ligt en 0 m van
-- dus binnen -- het terrein van Gem. begraafplaats.

**Eerste poging** (Joop, tegen zijn eigen database bevestigd): het
verkeerd-gelabelde punt hernoemd naar `Gem. begraafplaats, Oudenhoorn` en
`Gem. begraafplaats` op `geruimd` gezet (dit was zelf al een eerdere
correctie, van 2026-08-22, zie hieronder), met een nieuwe tweede ingang op
de zuidwesthoek van het terrein (`POINT (4.191578 51.826529)`, "ter
linkerzijde (west)"). Uitgevoerd via `scripts/fix_oudenhoorn_ingang.py`.
Dit vereiste tijdelijk een `EXTRA_INGANG_EXCEPTIONS`-mechanisme in
`scripts/build_base_dataset.py` (één terrein met twee eigen ingangen).

**Leon corrigeerde dit dezelfde dag** na het zien van de live kaart (WhatsApp
naar Joop, met een satellietscreenshot van beide terreinen): "De groene moet
geruimd en de bruine niet. Ingang aan westzijde van de bruine moet naar de
groene, nagenoeg zelfde locatie." Groen = `NH Kerkhof`, bruin = `Gem.
begraafplaats`. Uitgevoerd via `scripts/fix_oudenhoorn_reversed.py`
(eenmalig gedraaid):

1. `NH Kerkhof, Oudenhoorn` -> `geruimd`; `Gem. begraafplaats, Oudenhoorn`
   -> niet-geruimd (de omgekeerde van de eerdere, foutieve
   2026-08-22-correctie -- "Kerkhof" in Leons oorspronkelijke foutmelding
   bleek dus letterlijk `NH Kerkhof` te betekenen, niet `Gem.
   begraafplaats`);
2. de nieuwe west-ingang (`POINT (4.191578 51.826529)`) hertoegewezen van
   `Gem. begraafplaats` naar `NH Kerkhof`, geruimd-status volgt het nieuwe
   terrein;
3. de andere ingang (`POINT (4.192397 51.826557)`, de oorspronkelijk
   verkeerd-gelabelde) blijft bij `Gem. begraafplaats` (Leon noemde alleen
   "de ingang aan westzijde"), nu terug naar niet-geruimd.

Resultaat: beide terreinen hebben weer precies 1 eigen ingang, zoals elk
ander record in de dataset. Het `EXTRA_INGANG_EXCEPTIONS`-mechanisme was
dus niet meer nodig en is teruggedraaid (`properties.ingang_extra` bestaat
niet meer). `NH Kerkhof, Oudenhoorn` heeft nu wél een ingang, ~130 m van
zijn eigen terrein -- geografisch ongebruikelijk, maar expliciet bevestigd
door Leon, dus behouden zoals aangeleverd.

### Vijfheerenlanden (2026-08-19, bronwijziging)

Bij de gemeentelijke herindeling van 2019 ging Vijfheerenlanden (Ameide,
Hei en Boeicop, Kedichem, Leerbroek, Leerdam, Lexmond, Meerkerk, Nieuwland,
Oosterwijk, Schoonrewoerd, Tienhoven) van provincie Zuid-Holland naar
provincie Utrecht. Leon had deze 20 begraafplaatsen destijds al uit een
Excel-versie van de bron verwijderd, maar die correctie had de KML/CSV die
deze build leest nooit bereikt.

Verwijderd via `scripts/fix_vijfheerenlanden.py` (eenmalig gedraaid,
2026-08-19): 20 terreinen + hun 20 gekoppelde ingangen (40 bronregels),
op naam+plaats geverifieerd tegen Leons opgave voordat er iets verwijderd
werd. Bron ging van 924 naar 884 records; basisdataset van 463 naar 443
begraafplaatsen. Zie `git log -- "data/Begraafplaatsen Zuid-Holland- Zuid-Holland.csv"`
voor de exacte verwijderde rijen (provenance via git-historie, niet apart
gearchiveerd).

## Statusconflicten

Wanneer de status van terrein en ingang verschilt:

```text
geruimd = null
status_conflict = true
```

Beide bronwaarden blijven aanwezig:

```text
geruimd_bron_terrein
geruimd_bron_ingang
```

Dit maakt handmatige validatie mogelijk zonder informatieverlies.

### Statusconflicten (2026-08-20, opgelost)

De 4 conflicten die zich in de bron voordeden (RK begraafplaats Oude
Wetering, Oud NH kerkhof Schoonhoven, NH Kerkhof Zwammerdam, Vm. NH kerkhof
Maasland) zijn door Leon bevestigd als geruimd. Opgelost via
`scripts/fix_statusconflicten.py` (eenmalig gedraaid, 2026-08-20): voor elk
conflict is de rij (terrein of ingang) die nog niet `geruimd` had daarop
gezet, en heeft `plaats (origineel)` de bestaande `(geruimd)`-suffixconventie
gekregen. `data/generated/statusconflicten.csv` is nu leeg; het mechanisme
in `scripts/build_base_dataset.py` blijft bestaan voor eventuele toekomstige
conflicten.

### Losse geruimd-correcties (2026-08-22)

Opdrachtgever Leon meldde twee losstaande fouten in de bron (niet gerelateerd
aan de statusconflicten hierboven -- deze twee hadden helemaal geen
`geruimd`-waarde, dus geen conflict, gewoon een ontbrekende waarde):

- Oudenhoorn, `Gem. begraafplaats` (de variant zonder ingang, zie "Bijzondere
  gevallen" hieronder -- niet de andere Oudenhoorn-begraafplaats, `NH
  Kerkhof`, die wel een ingang heeft);
- Stad aan 't Haringvliet, `NH kerkhof` (niet de andere begraafplaats in dat
  dorp, `Gem. Begraafplaats`).

Beide zijn nu `geruimd`. Opgelost via
`scripts/fix_geruimd_oudenhoorn_haringvliet.py` (eenmalig gedraaid).

### Tijdelijk Zuid-Holland.kmz (2026-08-23, bronwijziging)

Leon leverde een aparte KMZ (`data/Tijdelijk Zuid-Holland.kmz`, bewaard voor
provenance naast de KML) met 3 nieuwe begraafplaatsen die nog niet in de
hoofdbron zaten:

- Nieuwe Joodse begraafplaats, Schiedam (geruimd);
- Grafmonument juffrouw Begeer, Voorschoten (niet geruimd);
- NH Kerkhof, Oud-Alblas (geruimd).

Elk placemark leverde een terrein-Polygon en een ingang-Point, dezelfde
structuur als de bestaande bron. Toegevoegd via
`scripts/add_tijdelijk_zuidholland_kmz.py` (eenmalig gedraaid, 2026-08-23):
6 rijen (3 terreinen + 3 ingangen) achteraan de CSV. Alle 3 koppelen exact
op naam + opgeschoonde plaats (geen van de drie botst met een bestaande
naam+plaats-combinatie in de bron). Bron ging van 884 naar 890 records;
basisdataset van 443 naar 446 begraafplaatsen.

## Rol van de KML

De KML blijft nuttig voor:

- vergelijking met de oorspronkelijke My Maps-weergave;
- controle dat geometrieën correct zijn overgenomen;
- provenance;
- eventueel reproduceren van oorspronkelijke styling.

Voor de build gebruiken we echter de expliciet gestructureerde CSV.
