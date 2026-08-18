# Data 004: RCE-MCP querystrategie

## Doel

Voor elk begraafplaatsterrein willen we vanuit de RCE-MCP bepalen:

- ligt het terrein in een beschermd stads- of dorpsgezicht?
- overlapt het terrein een archeologisch rijksmonument?
- liggen er gebouwde rijksmonumenten op of direct aan het terrein?
- welke RCE-objecten en URI's horen bij die relaties?

## Primaire RCE-datasets / graphs

Uit de eerdere verkenning zijn onder andere relevant:

- `cho-default`;
- `gezicht-hvdl`;
- `aanwijzingenmonumenten`;
- `punten`;
- `ceo-ontology`;
- `cht-thesaurus`;
- `abr-thesaurus`.

De exacte predicates en klassen moeten via de RCE-MCP worden geïnspecteerd voordat de productiesparql wordt vastgezet.

## Queryreeks

### Q1. Beschermde stads- en dorpsgezichten

Doel:

- identifier;
- naam;
- type;
- RCE-URI;
- geometrie.

Uitvoer bij voorkeur direct als GeoJSON.

### Q2. Rijksmonumenten

Doel:

- monumentnummer;
- RCE-URI;
- naam/omschrijving;
- objecttype;
- geometrie;
- relevante aanwijzingsinformatie.

### Q3. Archeologische rijksmonumenten

Doel:

dezelfde basisvelden als Q2, maar met een reproduceerbare semantische selectie op archeologische monumenten.

Die selectie moet op RCE-concepten/relaties gebaseerd zijn, niet op losse tekstmatching.

## Ruimtelijke verwerking

De RCE-resultaten worden tijdens de build omgezet of direct opgevraagd als GeoJSON.

Daarna voeren we lokaal de ruimtelijke joins uit tegen `data/generated/begraafplaatsen.geojson`.

Voorbeeld afgeleide velden:

```text
in_beschermd_gezicht
beschermd_gezicht_ids
rijksmonumenten_op_terrein
archeologische_rm_overlap
rijksmonumenten_direct_aangrenzend
```

## Reproduceerbaarheid

Per RCE-extract bewaren we:

- gebruikte SPARQL-query;
- datum van extractie;
- graph(s);
- RCE-URI's;
- eventueel een ruwe JSON/GeoJSON snapshot.

Zo kunnen viewer en analyse statisch op GitHub Pages draaien zonder live SPARQL-verzoeken vanuit de browser.

## Open punt

De eerstvolgende technische stap is de daadwerkelijke predicate-inspectie via de RCE-MCP en vervolgens drie werkende productiesparqlqueries maken.
