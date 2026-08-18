# Idee 004: RCE Linked Data

## Doel

Gebruik de RCE-MCP / LDV-voorziening voor de betekenis achter de geometrie.

PDOK kan geometrie leveren. RCE Linked Data kan de erfgoedobjecten semantisch verrijken.

## Relevante RCE-graphs

De huidige RCE-MCP toont onder andere deze graphs:

- `cho-default`
- `instanties-rce`
- `bebouwdeomgeving`
- `gezicht-hvdl`
- `punten`
- `aanwijzingenmonumenten`
- `oudeomschrijving`
- `abr-thesaurus`
- `cht-thesaurus`
- `owms`

Voor dit project lijken vooral relevant:

### Beschermde stads- en dorpsgezichten

```text
https://linkeddata.cultureelerfgoed.nl/graph/gezicht_hvdl
```

### Aanwijzingen monumenten

```text
https://linkeddata.cultureelerfgoed.nl/graph/aanwijzingenmonumenten
```

### Puntgeometrie

```text
https://linkeddata.cultureelerfgoed.nl/graph/punten
```

### Gebouwde omgeving

```text
https://linkeddata.cultureelerfgoed.nl/graph/bebouwdeomgeving
```

## Gebruik in de pipeline

We willen niet alleen een kaartlaag ophalen.

Per gevonden erfgoedobject willen we waar mogelijk bewaren:

- URI;
- naam;
- monumentnummer;
- monumentaard of categorie;
- functie/type;
- gemeente/plaats;
- geometrie;
- bron;
- relevante thesaurustermen.

## GeoJSON via MCP

De RCE-MCP kan SPARQL-resultaten met WKT-geometrie rechtstreeks als GeoJSON teruggeven.

Dat maakt deze route interessant:

```text
SPARQL
  |
  v
RCE GeoJSON
  |
  v
spatial join met begraafplaatsen
```

## Eerst uitzoeken

Voordat we definitieve queries schrijven:

1. inspecteer predicates in `gezicht-hvdl`;
2. inspecteer predicates in `aanwijzingenmonumenten`;
3. bepaal waar de bruikbare geometrieën staan;
4. bepaal hoe gebouwd en archeologisch betrouwbaar worden onderscheiden;
5. koppel labels via concept-URI's, niet via losse labelstrings;
6. maak kleine voorbeeldqueries voor Zuid-Holland;
7. valideer de resultaten met enkele bekende locaties.

## Uitgangspunt

Gebruik Linked Data voor identificatie en betekenis.

Gebruik ruimtelijke geometrie voor de feitelijke overlapberekening.

We vermijden daarmee dat naamvergelijking of tekstmatching bepaalt of twee objecten bij elkaar horen.
