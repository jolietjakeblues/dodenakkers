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

## Besluit voor MVP

Start statisch op GitHub Pages.

Voeg geen extra platform toe voordat daar een concrete functionele reden voor bestaat.
