# Idee 005: Kadaster en PDOK als aanvullende lagen

## Afbakening

De primaire erfgoedlagen komen uit de RCE-MCP/LDV.

PDOK is daarom **geen noodzakelijke tussenlaag** voor rijksmonumenten of beschermde gezichten. We gebruiken PDOK/Kadaster alleen wanneer het onderzoek een aanvullende ruimtelijke laag nodig heeft, vooral percelen en basiskaarten.

## Doel

Voeg kadastrale percelen toe als dat de domeinexpert helpt bij vragen over eigendomseenheden, begrenzing of de relatie tussen begraafplaats en monument.

## Mogelijke onderzoeksvragen

- Op welke percelen ligt een begraafplaats?
- Beslaat een begraafplaats meerdere percelen?
- Ligt een rijksmonument op hetzelfde perceel?
- Volgt de grens van de begraafplaats ongeveer de perceelsgrens?
- Welke delen van een begraafplaats liggen buiten het verwachte perceel?

## Voorstel

Kadaster is fase 2.

Eerst bewijzen we de kern:

```text
begraafplaats
+ rijksmonument
+ archeologie
+ beschermd gezicht
```

Daarna voegen we percelen toe.

## Technische aanpak

Voor de kaart:

- laad perceelgeometrie alleen als dat nodig is;
- toon percelen pas vanaf een geschikt zoomniveau;
- voorkom dat heel Zuid-Holland als zware GeoJSON in de browser belandt.

Voor de analyse:

- haal alleen percelen op die de begraafplaatsen raken of in de directe omgeving liggen;
- bewaar perceelidentificatie bij de afgeleide resultaten;
- houd brondata en afgeleide relaties gescheiden.

## Open vraag voor de domeinexpert

We moeten weten wat hij met percelen wil onderzoeken.

Alleen visualisatie vraagt om een andere oplossing dan:

- perceelidentificatie in exports;
- onderzoek naar eigendomsgrenzen;
- historische kadastrale analyse.

Historische kadastrale data valt buiten het eerste MVP.
