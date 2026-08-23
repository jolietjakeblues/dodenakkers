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
draaien.

### Eerste poging: GitHub Action + API-token (verworpen)

Eerst opgelost met een GitHub Action (`.github/workflows/deploy.yml`) die
bij elke push `wrangler pages deploy` draaide met een `CLOUDFLARE_API_TOKEN`-
en `CLOUDFLARE_ACCOUNT_ID`-secret. Dat werkte (geverifieerd: de build-stap
slaagde, de deploy-stap faalde precies op de ontbrekende secrets, geen
andere fout), maar was de verkeerde vergelijking: doorzoekerfgoed.nl draait
al probleemloos op Cloudflare zonder ooit zo'n token-gedoe nodig te hebben
gehad, omdat dat project via Cloudflare's eigen Git-integratie draait in
plaats van via `wrangler` + GitHub Actions. De Action voegde dus precies het
soort handmatig beheer toe dat we probeerden te elimineren. Verwijderd
nadat bleek dat de eenvoudiger route (hieronder) hetzelfde bereikt zonder
tokens.

### Gekozen oplossing: Cloudflare Git-integratie

`dodenakkers-zh` is nu direct aan deze GitHub-repo gekoppeld, hetzelfde
patroon als doorzoekerfgoed.nl: Cloudflare's eigen build-systeem (niet
GitHub Actions) checkt de repo uit, draait het build command en publiceert
de output directory bij elke push naar `main`. Geen GitHub-secrets, geen
API-token, geen `wrangler`-commando meer nodig van wie dan ook.

Eenmalige setup (via het Cloudflare-dashboard, ook op mobiel):

1. dash.cloudflare.com -> Workers & Pages -> project `dodenakkers-zh` ->
   Settings -> "Builds and deployments" (bij een Direct Upload-project staat
   hier een optie om alsnog een Git-repository te koppelen; is die er niet,
   dan een nieuw Pages-project aanmaken met "Connect to Git" en de oude
   Direct Upload-project verwijderen zodra de nieuwe live staat, zodat de
   naam/URL vrijkomt).
2. GitHub-autorisatie volgen, repository `jolietjakeblues/dodenakkers`
   selecteren, branch `main`.
3. Build-instellingen:
   - Framework preset: None
   - Build command: `python scripts/build_site.py`
   - Build output directory: `site`
4. Opslaan -- Cloudflare deployt meteen de huidige `main`, en daarna
   automatisch bij elke volgende push.
