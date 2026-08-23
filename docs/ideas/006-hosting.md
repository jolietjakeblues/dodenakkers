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
hostingpatroon optuigen naast wat je al hebt en kent" - geen nieuw
platform, hergebruik van bestaand platform.

Live op **https://dodenakkers-zh.pages.dev/** (project `dodenakkers-zh`).
De architectuur zelf is ongewijzigd: nog steeds volledig statisch, geen
live SPARQL vanuit de browser. Alleen het deploy-doel is anders. Zie
[docs/README.md](../README.md) sectie "Hosting" voor de deploy-commando's;
`scripts/build_site.py` bouwt een gitignored `site/`-map met alleen wat de
viewer nodig heeft (niet de hele repo).

## Automatische deploy (2026-08-23)

Handmatige deploys bleken in de praktijk niet te gebeuren: drie PR's zijn op
2026-08-23 binnen één sessie gemerged naar `main` (KMZ-toevoeging,
filterfix/zoekveld/legenda, mobiele paneel-toggle), maar de live site bleef
op de commit van vóór die sessie staan omdat niemand `wrangler pages deploy`
had gedraaid -- en dat commando is sowieso niet vanaf een telefoon te
draaien. Opgelost met `.github/workflows/deploy.yml`: bouwt en deployt
automatisch bij elke push naar `main`, en is ook handmatig te starten via de
"Run workflow"-knop op de Actions-tab in GitHub (geen CLI nodig).

### Eenmalige setup: twee repository-secrets

De workflow heeft twee GitHub-secrets nodig (repo -> Settings -> Secrets and
variables -> Actions -> "New repository secret"). Beide zijn te verkrijgen
via de Cloudflare-dashboard in de browser, ook op mobiel:

**`CLOUDFLARE_ACCOUNT_ID`**
: dash.cloudflare.com -> een willekeurige site/project openen -> de
  Account ID staat rechts in de zijbalk op het overzicht.

**`CLOUDFLARE_API_TOKEN`**
: dash.cloudflare.com -> profielicoon rechtsboven -> "My Profile" ->
  "API Tokens" -> "Create Token" -> template "Edit Cloudflare Workers" (dekt
  ook Pages) of een custom token met permissie "Account > Cloudflare Pages >
  Edit" -> aanmaken -> token direct kopiëren (wordt daarna niet meer getoond).

Zodra beide secrets bestaan, deployt elke push naar `main` automatisch; een
mislukte run vóór het toevoegen van de secrets is zichtbaar in de
Actions-tab (rode kruis) maar beschadigt niets -- gewoon opnieuw draaien
via "Re-run" nadat de secrets zijn toegevoegd.
