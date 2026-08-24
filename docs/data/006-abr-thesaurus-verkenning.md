# Data 006: ABR2-thesaurus als SPARQL-verkenning

## Vraag

Is het mogelijk een SPARQL-query te maken die de gehele inhoud van het
Archeologisch Basisregister 2 (ABR2) toont als thesaurus? (gebruiker,
2026-08-24, met als startpunten
<https://linkeddata.cultureelerfgoed.nl/thesauri/archeologischbasisregister/graphs>
en
<https://api.linkeddata.cultureelerfgoed.nl/datasets/thesauri/archeologischbasisregister/sparql>)

## Antwoord

Ja. Opgeslagen als `queries/thesauri/archeologisch-basisregister.sparql`
(zelfde conventie als `queries/rce/*.sparql`), geverifieerd tegen het live
endpoint op 2026-08-24: **13.621 van de 13.622 ABR2-concepten** in één
resultaat, ~6 seconden, geen timeout.

Let op: dit is een ANDER endpoint dan `scripts/fetch_rce.py` gebruikt. De
ABR2-thesaurus heeft een eigen, dataset-specifiek SPARQL-endpoint:

```text
https://api.linkeddata.cultureelerfgoed.nl/datasets/thesauri/archeologischbasisregister/sparql
```

(het RCE CHO-endpoint uit `scripts/fetch_rce.py` is
`https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/sparql` -- een
los dataset, geen ABR2-content.)

## Wat er in dit endpoint zit

Geverifieerd via `SELECT DISTINCT ?g WHERE { GRAPH ?g {?s ?p ?o} }`:

- `abr/2/thesaurus` -- de huidige ABR2-data, **13.622 skos:Concept**
  (waarvan 13.621 met zowel `skos:prefLabel@nl` als `skos:inScheme`), 2
  SKOS-schemes:
  - "Archeologisch Basis Register" (7.706 concepten, de eigenlijke
    archeologische termen -- materiaal, vondsttype, periode-aanduidingen
    zoals "IJZL", complextypen, etc.);
  - "Algemene lijsten" (5.915 concepten, generieke statuswaarden zoals
    "definitief"/"vervallen");
- `abr/2/metadata/adms` / `abr/2/metadata/void` -- metadata bij bovenstaande;
- `abr/thesaurus` -- **legacy ABR1**, aparte, oudere concept-URI's (geen
  `/2/` in het pad), 322.627 triples. Zonder een expliciete `GRAPH`-restrictie
  op `abr/2/thesaurus` levert een query op dit endpoint zowel ABR2- als
  ABR1-concepten dooreen (27.240 `skos:Concept` totaal) -- dat is geen
  bruikbaar antwoord op "toon ABR2 als thesaurus", dus de opgeslagen query
  zet dit vast met een `GRAPH`-clausule;
- `abr/metadata/adms` / `abr/metadata/void` -- metadata bij de legacy graph.

Dit is een gewone SKOS-thesaurus (`skos:Concept`, `skos:prefLabel`,
`skos:altLabel`, `skos:hiddenLabel`, `skos:notation`, `skos:scopeNote`,
`skos:broader`/`narrower`, `skos:inScheme`/`topConceptOf`,
`skos:exactMatch`/`closeMatch`/`broadMatch`/`narrowMatch`/`related`), plus
RCE-eigen extensieproperties onder `https://data.cultureelerfgoed.nl/id/rnce#`
voor materiaal/periode/keramiekcategorie/Deventer-codes e.d.
(`hasMaterialAbr`, `hasBeginPeriodAbr`, `hasCeramicCategoryAbr`,
`hasConceptStatus`, ...) -- niet gebruikt in de opgeslagen query, zie
"Scope" hieronder.

## Vorm van de query

Eén rij per concept, niet één rij per triple: `skos:altLabel`,
`skos:notation` en `skos:broader` kunnen multi-valued zijn, en die los in
dezelfde `OPTIONAL` combineren geeft een cartesisch product (zelfde
valkuil als `scripts/fetch_rce.py` documenteert voor
`heeftOmschrijving`/functies, zie
[004 RCE-MCP querystrategie](004-rce-mcp-querystrategie.md)). Opgelost met
`GROUP BY ?concept`, `SAMPLE()` voor enkelvoudige velden (label, code,
scheme, scopeNote) en `GROUP_CONCAT(DISTINCT ...; separator=" | ")` voor de
echt multi-valued velden (altLabels, broaderConcepts) -- geen rijen
verdwijnen, wel netjes één regel per thesaurusterm.

Kolommen: `concept` (URI), `label` (prefLabel@nl), `altLabels`, `code`
(skos:notation), `broaderConcepts` (URI's, `|`-gescheiden), `scheme`
(schema-titel), `scopeNoteText`.

## Scope -- wat hier bewust niet in zit

- **Alleen `skos:notation`, niet `rnce:codeAbr`/`rnce:hasAbrCode`**: die
  laatste twee zijn RCE-eigen extensieproperties (resp. een losse literal en
  een koppeling naar een apart codeobject) die niet op elk concept
  voorkomen en een extra multi-valued tak zouden toevoegen; `skos:notation`
  is een standaard SKOS-property en dekt het gangbare ABR-codepatroon.
- **Geen `narrower`/matches (exactMatch/closeMatch/...)/RCE-periode- en
  materiaalrelaties**: dit zou de query verder uitbreiden met nog meer
  multi-valued takken. Voor "toon de thesaurus" (labels, codes, hiërarchie
  naar boven, scheme, definitie) is dit niet nodig; een latere,
  specifiekere vraag (bv. "alle materiaalrelaties per concept") kan als
  aparte query, zelfde patroon als Q1-Q4 in
  [004 RCE-MCP querystrategie](004-rce-mcp-querystrategie.md).
- **Niet geïntegreerd in `scripts/fetch_rce.py` of de viewer**: dit is een
  losstaande verkenning die de vraag "is het mogelijk" beantwoordt, geen
  aansluiting op een concrete behoefte van dit project (Zuid-Holland-
  begraafplaatsen). `abr-thesaurus` stond al genoemd als "nog niet gebruikt"
  in [004 RCE-MCP querystrategie](004-rce-mcp-querystrategie.md#primaire-rce-datasets--graphs);
  dat blijft zo totdat er een concrete toepassing is (bv. archeologische
  periode-/materiaallabels tonen bij Q3/Q4-objecten via hun
  `heeftMonumentAard`/vondsttype-relaties).

## Reproduceerbaarheid

```bash
curl -s -G "https://api.linkeddata.cultureelerfgoed.nl/datasets/thesauri/archeologischbasisregister/sparql" \
  --data-urlencode "query=$(cat queries/thesauri/archeologisch-basisregister.sparql | sed '/^#/d')" \
  -H "Accept: application/sparql-results+json"
```
