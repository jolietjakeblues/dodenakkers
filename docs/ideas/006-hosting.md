# Idee 006: Hosting en publicatie

## Doel

Publiceer de onderzoeksviewer met zo weinig mogelijk beheer.

## Eerste keuze: GitHub Pages

Voor het MVP past GitHub Pages goed omdat:

- de broncode al in GitHub staat;
- de viewer statisch kan zijn;
- GeoJSON en andere gegenereerde bestanden mee kunnen;
- GitHub Actions de data en site kunnen bouwen;
- er geen eigen server nodig is.

## Gewenste flow

```text
brondata of scripts wijzigen
        |
        v
git push
        |
        v
GitHub Action
        |
        +-- data genereren
        +-- analyse uitvoeren
        +-- site bouwen
        |
        v
GitHub Pages
```

## Wanneer Cloudflare interessant wordt

Cloudflare wordt relevanter als we later nodig hebben:

- server-side functies;
- een API-proxy;
- caching voor externe databronnen;
- scheduled jobs buiten GitHub Actions;
- fijnere infrastructuurcontrole;
- een andere deploymentstrategie.

## Besluit voor MVP (oorspronkelijk)

Start statisch op GitHub Pages.

Voeg geen extra platform toe voordat daar een concrete functionele reden voor bestaat.

## Herzien besluit (2026-08-19): Cloudflare Pages

Bovenstaande "geen extra platform zonder concrete reden" bleek de verkeerde
vraag zodra bleek dat Cloudflare al bestaande, bewezen infrastructuur is: de
gebruiker draait doorzoekerfgoed.nl (een zwaarder RCE-project, met
server-side API-routes) al probleemloos op Cloudflare. Dan is de vraag niet
"heeft dit project Cloudflare nodig" maar "waarom een tweede
hostingpatroon optuigen naast wat je al hebt en kent" — geen nieuw
platform, hergebruik van bestaand platform.

Live op **https://dodenakkers-zh.pages.dev/** (project `dodenakkers-zh`).
De architectuur zelf is ongewijzigd: nog steeds volledig statisch, geen
live SPARQL vanuit de browser. Alleen het deploy-doel is anders. Zie
[docs/README.md](../README.md) sectie "Hosting" voor de deploy-commando's;
`scripts/build_site.py` bouwt een gitignored `site/`-map met alleen wat de
viewer nodig heeft (niet de hele repo). Nog geen GitHub Action/CI-koppeling
-- deploys zijn nu handmatig via `wrangler pages deploy`.
