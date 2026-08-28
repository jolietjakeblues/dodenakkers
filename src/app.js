// Dodenakkers Zuid-Holland - onderzoeksviewer (MVP)
//
// Laadt de gebouwde basisdataset en RCE-extracten rechtstreeks als
// statische GeoJSON. Geen live SPARQL vanuit de browser (zie sectie 15
// van de briefing) - alle data komt uit data/generated/ en data/rce/,
// zoals gegenereerd door scripts/build_base_dataset.py en
// scripts/fetch_rce.py.

const DATA = {
  // analyse.geojson = begraafplaatsen.geojson verrijkt met erfgoedrelaties
  // (scripts/analyse_spatial.py). Zelfde basisvelden, dus deze viewer werkt
  // ook (met minder functionaliteit) als je terugzet op begraafplaatsen.geojson.
  begraafplaatsen: "../data/generated/analyse.geojson",
  gezichten: "../data/rce/beschermde-gezichten.geojson",
  // Ook lazy sinds 2026-08-28 (16.135.605 bytes / 14.204 features, zie
  // setupMonumentenLayers() in main() en toggle-monumenten) -- was de enige
  // van de zeven losse lagen die nog standaard meeladen, ook met de laag
  // uitgezet (die staat zelfs standaard al uit in index.html).
  monumenten: "../data/rce/rijksmonumenten.geojson",
  provinciegrens: "../data/pdok/provincie-zuid-holland.geojson",
  // Niet in de initiele Promise.all: 22.254 features / 17MB, alleen ophalen
  // zodra de gebruiker de laag daadwerkelijk aanzet (zie toggle-onderzoeksgebieden).
  onderzoeksgebieden: "../data/rce/archeologische-onderzoeksgebieden.geojson",
  // Ook lazy (2,7MB, 50 gemeenten) -- alleen gebruikt voor de gemeente-koppeling
  // in scripts/analyse_spatial.py, maar Joop wilde de grenzen ook als
  // toggelbare referentielaag op de kaart (2026-08-27), zie toggle-gemeentegrenzen.
  gemeentegrenzen: "../data/pdok/gemeenten-zuid-holland.geojson",
  // Ook lazy (464KB, klein genoeg om eager te laden, maar zelfde
  // "standaard uit, referentielaag"-principe als de twee hierboven). Eigen
  // provinciale bron (Provincie Zuid-Holland CHS), geen RCE-bbox-fetch dus
  // geen bbox-rand-effect (wens van Joop, 2026-08-27, na het vinden van
  // https://data.overheid.nl/dataset/32677).
  chsArcheologie: "../data/zuid-holland/chs-archeologie-provinciaal-belang.geojson",
  // Lazy, klein (92 punten): Leons eigen KMZ met verdwenen begraafplaatsen
  // (data/Verdwenen.kmz, scripts/build_verdwenen_begraafplaatsen.py), wens
  // van Joop (2026-08-27) nadat Leon de KMZ deelde.
  verdwenen: "../data/generated/verdwenen-begraafplaatsen.geojson",
};

const statusEl = document.getElementById("status");

// --- Mobiel paneel-toggle (los van main()/de data-load, zodat de knop ook
// werkt terwijl de data nog laadt of als het laden faalt). Alleen zichtbaar
// onder de 700px-breakpoint in style.css -- op desktop blijft het paneel
// gewoon altijd zichtbaar zoals voorheen.
const panelEl = document.getElementById("panel");
const panelToggleEl = document.getElementById("panel-toggle");
let panelOpen = true;
function updatePanelToggle() {
  panelEl.classList.toggle("collapsed", !panelOpen);
  panelToggleEl.textContent = panelOpen ? "×" : "☰";
  panelToggleEl.setAttribute("aria-label", panelOpen ? "Paneel sluiten" : "Paneel openen");
  panelToggleEl.setAttribute("aria-expanded", String(panelOpen));
}
panelToggleEl.addEventListener("click", () => {
  panelOpen = !panelOpen;
  updatePanelToggle();
});

// Ondergronden, allemaal PDOK WMTS in EPSG:3857 (tilematrix/tilerow/tilecol
// komen 1-op-1 overeen met MapLibre's {z}/{x}/{y}-tileschema). "grijs" is de
// standaard, zelfde ondergrond als https://github.com/jolietjakeblues/doorzoeker-v2a
// (app/HeritageMap.tsx). De overige drie op verzoek (2026-08-19), net als de
// ondergrondkeuze bij WatWasHier: luchtfoto, BRK-percelen (overlay, transparant
// -- géén eigen basemap), BGT. Alle vier vooraf geverifieerd met een losse
// tile-request (HTTP 200, echte beeldinhoud) voordat ze hier terechtkwamen.
const BASEMAPS = {
  grijs: {
    tiles: [
      "https://service.pdok.nl/kadaster/brt-achtergrondkaart/wmts/v2_0?service=WMTS&request=GetTile&version=1.0.0&layer=grijs&style=default&tilematrixset=EPSG:3857&format=image/png&tilematrix={z}&tilerow={y}&tilecol={x}",
    ],
    attribution: 'Kaart: <a href="https://www.pdok.nl/">PDOK</a> · BRT Kadaster',
  },
  luchtfoto: {
    tiles: [
      "https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0?service=WMTS&request=GetTile&version=1.0.0&layer=Actueel_orthoHR&style=default&tilematrixset=EPSG:3857&format=image/jpeg&tilematrix={z}&tilerow={y}&tilecol={x}",
    ],
    attribution: 'Luchtfoto: <a href="https://www.pdok.nl/">PDOK</a> · Beeldmateriaal.nl',
  },
  bgt: {
    tiles: [
      "https://service.pdok.nl/kadaster/bgt/wmts/v1_0?service=WMTS&request=GetTile&version=1.0.0&layer=standaardvisualisatie&style=default&tilematrixset=EPSG:3857&format=image/png&tilematrix={z}&tilerow={y}&tilecol={x}",
    ],
    attribution: 'Kaart: <a href="https://www.pdok.nl/">PDOK</a> · BGT Kadaster',
    // BGT geeft tot en met zoom 16 een lege (maar geldige, HTTP 200) tegel
    // terug -- geverifieerd op meerdere locaties (Delft, Amsterdam Dam),
    // pas vanaf zoom 17 komt er echt beeld. Geen bug, een servergrens.
    minzoom: 17,
  },
};
const BRK_PERCELEN_OVERLAY = {
  tiles: [
    "https://service.pdok.nl/kadaster/kadastralekaart/wmts/v5_0?service=WMTS&request=GetTile&version=1.0.0&layer=Kadastralekaart&style=default&tilematrixset=EPSG:3857&format=image/png&tilematrix={z}&tilerow={y}&tilecol={x}",
  ],
  attribution: 'Percelen: <a href="https://www.pdok.nl/">PDOK</a> · BRK Kadaster',
  // Zelfde servergrens als BGT hierboven, zelfde manier geverifieerd.
  minzoom: 17,
};

function basemapStyleLayers() {
  const sources = {};
  const layers = [];
  for (const [id, cfg] of Object.entries(BASEMAPS)) {
    sources[`base-${id}`] = {
      type: "raster",
      tiles: cfg.tiles,
      tileSize: 256,
      minzoom: cfg.minzoom || 0,
      maxzoom: 19,
      attribution: cfg.attribution,
    };
    layers.push({
      id: `base-${id}`,
      type: "raster",
      source: `base-${id}`,
      layout: { visibility: id === "grijs" ? "visible" : "none" },
    });
  }
  sources["overlay-brk-percelen"] = {
    type: "raster",
    tiles: BRK_PERCELEN_OVERLAY.tiles,
    tileSize: 256,
    minzoom: BRK_PERCELEN_OVERLAY.minzoom,
    maxzoom: 19,
    attribution: BRK_PERCELEN_OVERLAY.attribution,
  };
  layers.push({
    id: "overlay-brk-percelen",
    type: "raster",
    source: "overlay-brk-percelen",
    layout: { visibility: "none" },
  });
  return { sources, layers };
}
const { sources: baseSources, layers: baseLayers } = basemapStyleLayers();

const map = new maplibregl.Map({
  container: "map",
  style: { version: 8, sources: baseSources, layers: baseLayers },
  center: [4.5, 52.0],
  zoom: 9,
});

map.addControl(new maplibregl.NavigationControl(), "top-right");

function polygonVertexCentroid(geometry) {
  // Cheap vertex-average centroid, only used to place a marker for gebouwde
  // monumenten die alleen een polygoongeometrie hebben -- geen vervanging
  // voor een echte (oppervlakte-gewogen) centroid, en niet gebruikt voor
  // ruimtelijke analyse (dat gebeurt met de echte geometrie in
  // scripts/analyse_spatial.py).
  const coords = [];
  const collectRing = (ring) => coords.push(...ring);
  if (geometry.type === "Polygon") {
    collectRing(geometry.coordinates[0]);
  } else if (geometry.type === "MultiPolygon") {
    geometry.coordinates.forEach((poly) => collectRing(poly[0]));
  }
  const lon = coords.reduce((s, c) => s + c[0], 0) / coords.length;
  const lat = coords.reduce((s, c) => s + c[1], 0) / coords.length;
  return [lon, lat];
}

function deriveMonumentPoints(monumentenFc) {
  // Gebouwde monumenten blijven altijd een punt (centroid als de bron een
  // polygoon is); archeologische monumenten met een polygoon laten we hier
  // weg -- die tonen we als vlak (zie monumenten-vlak-laag), niet ook nog
  // als punt erbovenop.
  const features = [];
  for (const f of monumentenFc.features) {
    if (f.geometry.type === "Point") {
      features.push(f);
    } else if (f.properties.monument_aard !== "archeologisch") {
      features.push({
        type: "Feature",
        properties: f.properties,
        geometry: { type: "Point", coordinates: polygonVertexCentroid(f.geometry) },
      });
    }
  }
  return { type: "FeatureCollection", features };
}

function functieCounts(monumentenFc) {
  const counts = new Map();
  for (const f of monumentenFc.features) {
    const label = f.properties.oorspronkelijke_functie_kort;
    if (!label) continue;
    counts.set(label, (counts.get(label) || 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

// data/generated/analyse.geojson bewaart rijksmonument-relaties tot 250m
// (scripts/analyse_spatial.py); de viewer filtert daaronder client-side op
// de gekozen drempel (schuifregelaar, sectie 18 van de briefing -- 100m
// was een werkhypothese, dit maakt 'm verkenbaar i.p.v. hardgecodeerd).
function relevantMonumentUris(begraafplaatsenFc, maxDistance) {
  const uris = new Set();
  for (const f of begraafplaatsenFc.features) {
    for (const r of f.properties.rijksmonument_relations || []) {
      if (r.cho_uri && r.distance_m <= maxDistance) uris.add(r.cho_uri);
    }
  }
  return uris;
}

function idsWithRijksmonumentWithin(begraafplaatsenFc, maxDistance) {
  const ids = new Set();
  for (const f of begraafplaatsenFc.features) {
    const has = (f.properties.rijksmonument_relations || []).some((r) => r.distance_m <= maxDistance);
    if (has) ids.add(f.properties.id);
  }
  return ids;
}

function ingangenFromBegraafplaatsen(fc) {
  const features = [];
  for (const f of fc.features) {
    const ingang = f.properties.ingang;
    if (!ingang) continue;
    features.push({
      type: "Feature",
      geometry: ingang,
      properties: {
        begraafplaats_id: f.properties.id,
        naam: f.properties.naam,
        plaats: f.properties.plaats,
        koppelwijze: f.properties.ingang_koppelwijze,
        gedeeld: f.properties.ingang_gedeeld,
      },
    });
  }
  return { type: "FeatureCollection", features };
}

function extendBoundsWithGeometry(bounds, geometry) {
  if (!geometry) return;
  // One terrain record is a GeometryCollection rather than a Polygon
  // (section 2/4 of the briefing) - coordinates live on its sub-geometries.
  if (geometry.type === "GeometryCollection") {
    geometry.geometries.forEach((g) => extendBoundsWithGeometry(bounds, g));
    return;
  }
  const extendCoords = (coords) => {
    if (typeof coords[0] === "number") {
      bounds.extend(coords);
    } else {
      coords.forEach(extendCoords);
    }
  };
  extendCoords(geometry.coordinates);
}

function boundsOfFeatureCollection(fc) {
  const bounds = new maplibregl.LngLatBounds();
  for (const f of fc.features) {
    extendBoundsWithGeometry(bounds, f.geometry);
  }
  return bounds;
}

// Leon bevestigde 2026-08-19: "annex aan een rijksmonument" betekent
// grenscontact (touches), niet zomaar "binnen X meter". Andere relaties
// blijven de ruwe categorie tonen (zie sectie 18 van de briefing --
// werkhypothesen, geen definitieve indeling).
const RELATION_LABELS = {
  touches: "annex (grenst aan)",
  inside_on_site: "op het terrein",
  intersects: "overlapt",
  contains: "omvat het monument",
  within: "monument omvat het terrein",
  point_inside: "punt binnen terrein",
};
function relationLabel(relation) {
  return RELATION_LABELS[relation] || relation;
}

// Popup-inhoud komt uit onze eigen brondata (RCE/PDOK/CSV), dus vandaag geen
// echt aanvalsvector -- maar toch escapen i.p.v. kaal interpoleren, puur
// defensief tegen toekomstige externe/minder gecontroleerde bronnen en
// tegen brontekst met &/</>/aanhalingstekens die de HTML anders al zou
// breken (geen kwaadaardige input nodig, alleen een naam met een &).
// SafeHtml markeert de enkele plek (het monumentenregister-linkje
// hieronder) waar we zelf bewust HTML opbouwen en dat niet nogmaals
// geëscaped mag worden.
class SafeHtml {
  constructor(html) {
    this.html = html;
  }
}
function rawHtml(html) {
  return new SafeHtml(html);
}
const HTML_ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (c) => HTML_ESCAPES[c]);
}

function popupHtml(title, rows) {
  const dl = rows
    .filter(([, v]) => v !== null && v !== undefined && v !== "")
    .map(([k, v]) => `<dt>${escapeHtml(k)}</dt><dd>${v instanceof SafeHtml ? v.html : escapeHtml(v)}</dd>`)
    .join("");
  return `<h3>${escapeHtml(title)}</h3><dl>${dl}</dl>`;
}

async function loadJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  return res.json();
}

async function main() {
  const [begraafplaatsen, gezichten, provinciegrens] = await Promise.all([
    loadJson(DATA.begraafplaatsen),
    loadJson(DATA.gezichten),
    loadJson(DATA.provinciegrens),
  ]);
  const ingangen = ingangenFromBegraafplaatsen(begraafplaatsen);
  // Rijksmonumenten (16.135.605 bytes) staan hier bewust niet meer bij --
  // zie setupMonumentenLayers() en toggle-monumenten verderop, zelfde lazy
  // patroon als de andere losse lagen.
  let monumenten = null;
  let monumentenLoaded = false;

  if (!map.isStyleLoaded()) {
    await new Promise((resolve) => map.on("load", resolve));
  }

  // --- Provinciegrens Zuid-Holland (referentielijn, onderste laag van alles) ---
  // scripts/fetch_provinciegrens.py, PDOK bestuurlijkegebieden WFS. Puur ter
  // oriëntatie (wens van de gebruiker, 2026-08-20) -- geen eigen data, geen
  // klikinteractie, geen fill.
  map.addSource("provinciegrens", { type: "geojson", data: provinciegrens });
  map.addLayer({
    id: "provinciegrens-lijn",
    type: "line",
    source: "provinciegrens",
    paint: { "line-color": "#495057", "line-width": 2, "line-dasharray": [4, 2] },
  });

  // --- Gemeentegrenzen Zuid-Holland (lazy: 50 gemeenten, 2,7MB -- pas
  // ophalen bij het aanzetten, net als de onderzoeksgebieden hieronder).
  // Dunner/lichter dan de provinciegrens zodat ze duidelijk een ander,
  // fijnmaziger niveau zijn i.p.v. met elkaar te wedijveren. Puur ter
  // oriëntatie, geen klikinteractie (wens van Joop, 2026-08-27 -- de
  // geometrie werd al gebruikt voor de gemeente-koppeling in
  // scripts/analyse_spatial.py, dit toont 'm ook op de kaart).
  let gemeentegrenzenLoaded = false;
  document.getElementById("toggle-gemeentegrenzen").addEventListener("change", async (e) => {
    updateLegendActivity();
    syncUrl();
    if (!e.target.checked) {
      if (gemeentegrenzenLoaded) map.setLayoutProperty("gemeentegrenzen-lijn", "visibility", "none");
      return;
    }
    if (gemeentegrenzenLoaded) {
      map.setLayoutProperty("gemeentegrenzen-lijn", "visibility", "visible");
      return;
    }
    statusEl.textContent = "Gemeentegrenzen laden (2,7MB)…";
    const gemeentegrenzen = await loadJson(DATA.gemeentegrenzen);
    map.addSource("gemeentegrenzen", { type: "geojson", data: gemeentegrenzen });
    map.addLayer({
      id: "gemeentegrenzen-lijn",
      type: "line",
      source: "gemeentegrenzen",
      paint: { "line-color": "#868e96", "line-width": 1, "line-dasharray": [1, 2] },
    });
    gemeentegrenzenLoaded = true;
    statusEl.textContent = `${gemeentegrenzen.features.length} gemeentegrenzen geladen.`;
  });

  // --- Archeologische onderzoeksgebieden (lazy: 22.254 polygonen, 17MB --
  // pas ophalen zodra de gebruiker de laag echt aanzet, niet standaard mee-
  // laden bij elke paginabezoek). Wens van de gebruiker (2026-08-20).
  let onderzoeksgebiedenLoaded = false;
  document.getElementById("toggle-onderzoeksgebieden").addEventListener("change", async (e) => {
    updateLegendActivity();
    syncUrl();
    if (!e.target.checked) {
      if (onderzoeksgebiedenLoaded) {
        map.setLayoutProperty("onderzoeksgebieden-fill", "visibility", "none");
        map.setLayoutProperty("onderzoeksgebieden-outline", "visibility", "none");
      }
      return;
    }
    if (onderzoeksgebiedenLoaded) {
      map.setLayoutProperty("onderzoeksgebieden-fill", "visibility", "visible");
      map.setLayoutProperty("onderzoeksgebieden-outline", "visibility", "visible");
      return;
    }
    statusEl.textContent = "Archeologische onderzoeksgebieden laden (17MB)…";
    const onderzoeksgebieden = await loadJson(DATA.onderzoeksgebieden);
    map.addSource("onderzoeksgebieden", { type: "geojson", data: onderzoeksgebieden });
    map.addLayer({
      id: "onderzoeksgebieden-fill",
      type: "fill",
      source: "onderzoeksgebieden",
      paint: { "fill-color": "#0c8599", "fill-opacity": 0.2 },
    });
    map.addLayer({
      id: "onderzoeksgebieden-outline",
      type: "line",
      source: "onderzoeksgebieden",
      paint: { "line-color": "#0c8599", "line-width": 1 },
    });
    map.on("click", "onderzoeksgebieden-fill", (ev) => {
      const p = ev.features[0].properties;
      new maplibregl.Popup()
        .setLngLat(ev.lngLat)
        .setHTML(
          popupHtml(`Archeologisch onderzoeksgebied ${p.objectnummer}`, [
            ["Registratiedatum", p.registratiedatum],
            ["Omschrijving", p.omschrijving],
          ])
        )
        .addTo(map);
    });
    map.on("mouseenter", "onderzoeksgebieden-fill", () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", "onderzoeksgebieden-fill", () => (map.getCanvas().style.cursor = ""));
    onderzoeksgebiedenLoaded = true;
    statusEl.textContent = `${onderzoeksgebieden.features.length} archeologische onderzoeksgebieden geladen.`;
  });

  // --- Archeologische terreinen van provinciaal belang (lazy: 662 polygonen,
  // 464KB -- klein genoeg om eager te laden, maar zelfde "standaard uit,
  // referentielaag"-principe als de twee lagen hierboven). Provincie
  // Zuid-Holland CHS, andere bron dan de RCE-lagen (wens van Joop, 2026-08-27).
  let chsArcheologieLoaded = false;
  document.getElementById("toggle-chs-archeologie").addEventListener("change", async (e) => {
    updateLegendActivity();
    syncUrl();
    if (!e.target.checked) {
      if (chsArcheologieLoaded) {
        map.setLayoutProperty("chs-archeologie-fill", "visibility", "none");
        map.setLayoutProperty("chs-archeologie-outline", "visibility", "none");
      }
      return;
    }
    if (chsArcheologieLoaded) {
      map.setLayoutProperty("chs-archeologie-fill", "visibility", "visible");
      map.setLayoutProperty("chs-archeologie-outline", "visibility", "visible");
      return;
    }
    statusEl.textContent = "Archeologische terreinen van provinciaal belang laden…";
    const chsArcheologie = await loadJson(DATA.chsArcheologie);
    map.addSource("chs-archeologie", { type: "geojson", data: chsArcheologie });
    map.addLayer({
      id: "chs-archeologie-fill",
      type: "fill",
      source: "chs-archeologie",
      // #997404 (olijfgeel/goud) i.p.v. het al gebruikte #e8590c (rijksmonument
      // archeologisch) of #0c8599 (RCE-onderzoeksgebieden) -- eigen, goed te
      // onderscheiden kleur nodig (Rene, kleurenblind).
      paint: { "fill-color": "#997404", "fill-opacity": 0.25 },
    });
    map.addLayer({
      id: "chs-archeologie-outline",
      type: "line",
      source: "chs-archeologie",
      paint: { "line-color": "#997404", "line-width": 1 },
    });
    map.on("click", "chs-archeologie-fill", (ev) => {
      const p = ev.features[0].properties;
      new maplibregl.Popup()
        .setLngLat(ev.lngLat)
        .setHTML(
          popupHtml(p.Toponiem || `Archeologisch terrein ${p.MONUMENTNR}`, [
            ["Gemeente", p.Gemeente],
            ["Plaats", p.Plaats],
            ["Waarde", p.WAARDE],
            ["Datering", p.Datering],
            ["Beschrijving", p.Beschrijving],
            ["Zichtbaar", p.Zichtbaarh],
          ])
        )
        .addTo(map);
    });
    map.on("mouseenter", "chs-archeologie-fill", () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", "chs-archeologie-fill", () => (map.getCanvas().style.cursor = ""));
    chsArcheologieLoaded = true;
    statusEl.textContent = `${chsArcheologie.features.length} archeologische terreinen van provinciaal belang geladen.`;
  });

  // --- Verdwenen begraafplaatsen (lazy, klein: 92 punten) -- Leons eigen
  // KMZ (data/Verdwenen.kmz, scripts/build_verdwenen_begraafplaatsen.py),
  // andere aard dan de rest van de kaart: geen terrein meer (alleen de
  // historische locatie), en geen automatische heuristiek zoals de
  // kandidatenpagina maar Leons eigen kennis. Kleur onderscheidt of de
  // locatie al herkenbaar is in de hoofddataset (grijs, minder interessant)
  // of niet (donker, de "echt onbekende" gevallen -- wens van Joop,
  // 2026-08-27). Was eerst rood (#c92a2a), maar dat viel qua kleur te
  // dicht bij de al bestaande roze ingangen (#e64980) -- door elkaar te
  // halen gemeld door Joop (2026-08-28). #212529 (bijna zwart, ook al de
  // hoofdtekstkleur van het paneel) is qua hue niet te verwarren met welke
  // andere kleur op de kaart dan ook, en het contrast blijft ook voor Rene
  // (kleurenblind) overeind omdat het op lichtheid werkt, niet op hue.
  let verdwenenLoaded = false;
  document.getElementById("toggle-verdwenen").addEventListener("change", async (e) => {
    updateLegendActivity();
    syncUrl();
    if (!e.target.checked) {
      if (verdwenenLoaded) map.setLayoutProperty("verdwenen-punt", "visibility", "none");
      return;
    }
    if (verdwenenLoaded) {
      map.setLayoutProperty("verdwenen-punt", "visibility", "visible");
      return;
    }
    statusEl.textContent = "Verdwenen begraafplaatsen laden…";
    const verdwenen = await loadJson(DATA.verdwenen);
    map.addSource("verdwenen", { type: "geojson", data: verdwenen });
    map.addLayer({
      id: "verdwenen-punt",
      type: "circle",
      source: "verdwenen",
      paint: {
        "circle-radius": 5,
        "circle-color": ["case", ["get", "in_hoofddataset"], "#adb5bd", "#212529"],
        "circle-stroke-width": 1,
        "circle-stroke-color": "#ffffff",
      },
    });
    map.on("click", "verdwenen-punt", (ev) => {
      const p = ev.features[0].properties;
      new maplibregl.Popup()
        .setLngLat(ev.lngLat)
        .setHTML(
          popupHtml(p.naam, [
            ["Plaats", p.plaats],
            ["Vermelde status", p.status_vermeld],
            ["In hoofddataset", p.in_hoofddataset ? "lijkt al bekend (naam+plaats-heuristiek)" : "niet gevonden -- mogelijk ontbrekend"],
          ])
        )
        .addTo(map);
    });
    map.on("mouseenter", "verdwenen-punt", () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", "verdwenen-punt", () => (map.getCanvas().style.cursor = ""));
    verdwenenLoaded = true;
    statusEl.textContent = `${verdwenen.features.length} verdwenen begraafplaatsen geladen.`;
  });

  // --- Beschermde gezichten (onderste laag: grote polygonen) ---
  map.addSource("gezichten", { type: "geojson", data: gezichten });
  map.addLayer({
    id: "gezichten-fill",
    type: "fill",
    source: "gezichten",
    paint: { "fill-color": "#5f3dc4", "fill-opacity": 0.12 },
  });
  map.addLayer({
    id: "gezichten-outline",
    type: "line",
    source: "gezichten",
    paint: { "line-color": "#5f3dc4", "line-width": 1.5, "line-dasharray": [2, 1] },
  });

  // --- Rijksmonumenten (lazy: zie de toelichting bij DATA.monumenten
  // hierboven en toggle-monumenten verderop) ---
  const archeologischFilter = ["==", ["get", "monument_aard"], "archeologisch"];
  const monumentenBaseFilters = {
    "monumenten-punt": null,
    "monumenten-vlak": archeologischFilter,
    "monumenten-vlak-outline": archeologischFilter,
  };

  function setupMonumentenLayers(fc) {
    // Gebouwde monumenten altijd als punt (ook wanneer de bron een
    // polygoongeometrie heeft -- dan een client-side centroid, alleen voor
    // de marker-positie, geen vervanging van de echte geometrie). Archeologische
    // rijksmonumenten juist als vlak wanneer de bron een polygoon heeft (anders
    // als punt, want er is dan geen polygoon om te tonen).
    const monumentenPunten = deriveMonumentPoints(fc);
    map.addSource("monumenten", { type: "geojson", data: fc });
    map.addSource("monumenten-punten", { type: "geojson", data: monumentenPunten });
    map.addLayer({
      id: "monumenten-punt",
      type: "circle",
      source: "monumenten-punten",
      paint: {
        "circle-radius": 4,
        "circle-color": [
          "case",
          ["==", ["get", "monument_aard"], "archeologisch"],
          "#e8590c",
          ["==", ["get", "monument_aard"], "onroerend gebouwd"],
          "#1971c2",
          "#868e96",
        ],
        "circle-stroke-width": 1,
        "circle-stroke-color": "#ffffff",
      },
    });
    map.addLayer({
      id: "monumenten-vlak",
      type: "fill",
      source: "monumenten",
      filter: archeologischFilter,
      paint: { "fill-color": "#e8590c", "fill-opacity": 0.4 },
    });
    map.addLayer({
      id: "monumenten-vlak-outline",
      type: "line",
      source: "monumenten",
      filter: archeologischFilter,
      paint: { "line-color": "#e8590c", "line-width": 1.5 },
    });

    // Boven het terrein maar onder de ingangen -- ingangen-punt bestaat al
    // (eager geladen), dus moveLayer met een beforeId werkt ongeacht wanneer
    // deze laag alsnog wordt aangezet (zie ook "Ingangen" verderop).
    map.moveLayer("monumenten-vlak", "ingangen-punt");
    map.moveLayer("monumenten-vlak-outline", "ingangen-punt");
    map.moveLayer("monumenten-punt", "ingangen-punt");

    map.on("click", "monumenten-punt", showMonumentPopup);
    map.on("click", "monumenten-vlak", showMonumentPopup);
    for (const layerId of ["monumenten-punt", "monumenten-vlak"]) {
      map.on("mouseenter", layerId, () => (map.getCanvas().style.cursor = "pointer"));
      map.on("mouseleave", layerId, () => (map.getCanvas().style.cursor = ""));
    }

    functieOptions = functieCounts(fc);
    functieSearchEl.disabled = false;
    renderFunctieOptions();
    updateMonumentenFilter();
    statusEl.textContent = `${fc.features.length} rijksmonumenten geladen.`;
  }

  // Drie vaste stappen i.p.v. een doorlopende 50-250m-schaal (2026-08-27,
  // wens van Joop: "afstand aanpassen naar 25, 50 en 100 meter. > 100 is
  // niet interessant genoeg") -- een <input type="range"> ondersteunt geen
  // onregelmatige stapgrootte, dus de slider zelf loopt over de index
  // (0/1/2) en wordt hier vertaald naar de echte meterwaarde. rmThreshold
  // zelf blijft overal (predicates, label, permalink) gewoon in meters.
  const RM_THRESHOLD_STEPS = [25, 50, 100];
  let rmThreshold = 100;
  const rmThresholdEl = document.getElementById("rm-threshold");
  const rmThresholdLabelEl = document.getElementById("rm-threshold-label");
  function rmThresholdIndexFor(meters) {
    const exact = RM_THRESHOLD_STEPS.indexOf(meters);
    if (exact !== -1) return exact;
    // Onbekende waarde (bv. een oude permalink van vóór deze wijziging) --
    // dichtstbijzijnde stap kiezen i.p.v. de slider stuk laten gaan.
    let best = 0;
    for (let i = 1; i < RM_THRESHOLD_STEPS.length; i++) {
      if (Math.abs(RM_THRESHOLD_STEPS[i] - meters) < Math.abs(RM_THRESHOLD_STEPS[best] - meters)) best = i;
    }
    return best;
  }

  // --- Functiefilter: dynamisch opgebouwd uit de daadwerkelijk voorkomende
  // oorspronkelijke_functie_kort-waarden, geen vaste curatie (zie
  // docs/data/004-rce-mcp-querystrategie.md, "Filteren: alleen op
  // oorspronkelijke functie"). Selectie staat los van de zoekbalk zodat
  // filteren op tekst de selectie niet ongedaan maakt. De opties zijn pas
  // bekend zodra de rijksmonumenten-laag geladen is (setupMonumentenLayers
  // hierboven) -- tot die tijd toont het select-veld een uitleg i.p.v. een
  // lege lijst.
  let functieOptions = [];
  const selectedFunctie = new Set();
  const functieSelectEl = document.getElementById("functie-select");
  const functieSearchEl = document.getElementById("functie-search");
  functieSearchEl.disabled = true;
  function renderFunctieOptions() {
    const query = functieSearchEl.value.trim().toLowerCase();
    const prevScroll = functieSelectEl.scrollTop;
    functieSelectEl.innerHTML = "";
    if (!monumentenLoaded) {
      const placeholder = document.createElement("option");
      placeholder.disabled = true;
      placeholder.textContent = "Zet Rijksmonumenten aan (onder Lagen) om te filteren op functie";
      functieSelectEl.appendChild(placeholder);
      return;
    }
    for (const [label, count] of functieOptions) {
      if (query && !label.toLowerCase().includes(query)) continue;
      const opt = document.createElement("option");
      opt.value = label;
      opt.textContent = `${label} (${count})`;
      opt.selected = selectedFunctie.has(label);
      functieSelectEl.appendChild(opt);
    }
    functieSelectEl.scrollTop = prevScroll;
  }
  renderFunctieOptions();
  functieSearchEl.addEventListener("input", renderFunctieOptions);
  functieSelectEl.addEventListener("change", () => {
    selectedFunctie.clear();
    for (const opt of functieSelectEl.selectedOptions) selectedFunctie.add(opt.value);
    updateMonumentenFilter();
  });
  document.getElementById("functie-clear").addEventListener("click", () => {
    selectedFunctie.clear();
    functieSearchEl.value = "";
    renderFunctieOptions();
    updateMonumentenFilter();
  });

  function updateMonumentenFilter() {
    const relevantUris = relevantMonumentUris(begraafplaatsen, rmThreshold);
    document.getElementById("monumenten-count").textContent = `(${relevantUris.size} relevant, ≤${rmThreshold}m)`;
    // De daadwerkelijke laagfilters kunnen pas gezet worden zodra de
    // rijksmonumenten-laag bestaat (setupMonumentenLayers) -- de teller
    // hierboven werkt altijd, die komt uit begraafplaatsen zelf.
    if (monumentenLoaded) {
      const showAll = document.getElementById("toggle-monumenten-alle").checked;
      const relevantMonumentenFilter = ["in", ["get", "cho_uri"], ["literal", Array.from(relevantUris)]];
      const dynamicClauses = [];
      if (!showAll) dynamicClauses.push(relevantMonumentenFilter);
      if (selectedFunctie.size) {
        dynamicClauses.push(["in", ["get", "oorspronkelijke_functie_kort"], ["literal", [...selectedFunctie]]]);
      }
      // Aan/uit voor gebouwde vs archeologische monumenten (ceo:monumentAard,
      // wens van Joop 2026-08-27). Bij beide aan geen extra clausule (zelfde
      // gedrag als voorheen); bij een van beide uit filteren op de resterende
      // aard-waarde; bij beide uit een "in" met een lege literal-array, die
      // voor elke feature false oplevert en zo alles verbergt.
      const gebouwdAan = document.getElementById("toggle-monumenten-gebouwd").checked;
      const archeologischAan = document.getElementById("toggle-monumenten-archeologisch").checked;
      if (!gebouwdAan || !archeologischAan) {
        const aardWaarden = [];
        if (gebouwdAan) aardWaarden.push("onroerend gebouwd");
        if (archeologischAan) aardWaarden.push("archeologisch");
        dynamicClauses.push(["in", ["get", "monument_aard"], ["literal", aardWaarden]]);
      }
      for (const [id, base] of Object.entries(monumentenBaseFilters)) {
        const clauses = base ? [base, ...dynamicClauses] : dynamicClauses;
        const filter = clauses.length === 0 ? null : clauses.length === 1 ? clauses[0] : ["all", ...clauses];
        map.setFilter(id, filter);
      }
    }
    syncUrl();
  }

  // --- Begraafplaatsen terrein ---
  map.addSource("terrein", { type: "geojson", data: begraafplaatsen });
  map.addLayer({
    id: "terrein-fill",
    type: "fill",
    source: "terrein",
    paint: {
      // #adb5bd (geruimd) en #f1f3f5 (statusconflict) waren tegen OSM prima
      // te onderscheiden, maar vallen bijna weg tegen de grijze PDOK
      // BRT-achtergrondkaart -- vervangen door kleuren met genoeg verzadiging
      // om op een grijs/wit ondergrond te blijven opvallen.
      "fill-color": [
        "case",
        ["==", ["get", "status_conflict"], true],
        "#ffd43b",
        ["==", ["get", "geruimd"], true],
        "#a9713f",
        "#40c057",
      ],
      "fill-opacity": 0.65,
    },
  });
  map.addLayer({
    id: "terrein-outline",
    type: "line",
    source: "terrein",
    paint: {
      "line-color": ["case", ["==", ["get", "status_conflict"], true], "#e03131", "#2b8a3e"],
      "line-width": ["case", ["==", ["get", "status_conflict"], true], 3, 1],
    },
  });

  // --- Ingangen (bovenste laag: kleine punten) ---
  map.addSource("ingangen", { type: "geojson", data: ingangen });
  map.addLayer({
    id: "ingangen-punt",
    type: "circle",
    source: "ingangen",
    paint: {
      "circle-radius": 5,
      "circle-color": "#e64980",
      "circle-stroke-width": 1.5,
      "circle-stroke-color": "#ffffff",
    },
  });

  // --- Popups ---
  map.on("click", "terrein-fill", (e) => {
    const p = e.features[0].properties;
    const gezichtNamen = JSON.parse(p.beschermd_gezicht_relaties || "[]")
      .map((g) => `${g.naam || "?"} (${g.relation})`)
      .join(", ");
    const rmRelaties = JSON.parse(p.rijksmonument_relations || "[]");
    const archRelaties = JSON.parse(p.archeologische_rm_relations || "[]");
    const archNearest = p.archeologische_rm_nearest ? JSON.parse(p.archeologische_rm_nearest) : null;
    new maplibregl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(
        popupHtml(p.naam, [
          ["Plaats", p.plaats],
          ["Gemeente", p.gemeente],
          ["Geruimd", p.status_conflict ? "onbekend (statusconflict)" : p.geruimd ? "ja" : "nee"],
          ["Oppervlakte", `${p.oppervlakte_m2} m² (${p.oppervlakte_ha} ha)`],
          ["Omtrek", `${p.omtrek_m} m`],
          ["Beschermd gezicht", p.in_beschermd_gezicht === "none" ? "nee" : gezichtNamen],
          [
            "Archeologisch rijksmonument",
            archRelaties.length
              ? archRelaties.map((r) => `${r.naam || r.rijksmonumentnummer} (${relationLabel(r.relation)})`).join(", ")
              : archNearest
              ? `geen overlap (dichtstbij: ${archNearest.distance_m} m)`
              : "geen",
          ],
          [
            "Rijksmonumenten ≤100m",
            rmRelaties.length
              ? rmRelaties.map((r) => `${r.naam || r.rijksmonumentnummer} (${relationLabel(r.relation)}, ${r.distance_m}m)`).join(", ")
              : "geen",
          ],
        ])
      )
      .addTo(map);
  });

  map.on("click", "ingangen-punt", (e) => {
    const p = e.features[0].properties;
    // "Gedeelde ingang: false" als kale boolean was verwarrend voor bijna
    // elke ingang (alleen Duinrust deelt er echt een) -- vervangen door een
    // leesbaar type-label i.p.v. het technische veld te tonen.
    const type = p.gedeeld ? "Gedeeld (ook ingang van naburig terrein)" : "Hoofdingang";
    new maplibregl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(popupHtml(`Ingang: ${p.naam}`, [["Plaats", p.plaats], ["Type", type]]))
      .addTo(map);
  });

  map.on("click", "gezichten-fill", (e) => {
    const p = e.features[0].properties;
    new maplibregl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(popupHtml(p.naam || "Beschermd gezicht", [["Gezichtsnummer", p.gezichtsnummer], ["Status", p.status]]))
      .addTo(map);
  });

  function showMonumentPopup(e) {
    const p = e.features[0].properties;
    new maplibregl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(
        popupHtml(p.naam || `Rijksmonument ${p.rijksmonumentnummer}`, [
          ["Rijksmonumentnummer", p.rijksmonumentnummer],
          ["Aard", p.monument_aard],
          ["Oorspronkelijke functie", p.oorspronkelijke_functie],
          ["Huidige functie", p.huidige_functie],
          ["Type", p.type],
          ["Datum inschrijving monumentenregister", p.datum_inschrijving_monumentenregister],
          [
            "Register",
            p.monumentenregister_url
              ? rawHtml(`<a href="${escapeHtml(p.monumentenregister_url)}" target="_blank" rel="noopener">bekijk</a>`)
              : null,
          ],
        ])
      )
      .addTo(map);
  }
  // Klik-/hover-registratie voor monumenten-punt/-vlak gebeurt in
  // setupMonumentenLayers() hierboven (die layers bestaan pas zodra de
  // laag lazy geladen is).

  for (const layerId of ["terrein-fill", "ingangen-punt", "gezichten-fill"]) {
    map.on("mouseenter", layerId, () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", layerId, () => (map.getCanvas().style.cursor = ""));
  }

  // --- Laagtoggles ---
  const layerToggles = {
    "toggle-provinciegrens": ["provinciegrens-lijn"],
    "toggle-terrein": ["terrein-fill", "terrein-outline"],
    "toggle-ingangen": ["ingangen-punt"],
    "toggle-gezichten": ["gezichten-fill", "gezichten-outline"],
    // toggle-monumenten zit hier bewust niet bij -- die laag is lazy (zie
    // hieronder, na deze generieke lus) en heeft daarom een eigen listener.
  };
  // Legenda dimt items waarvan de laag uitstaat (data-layer verwijst naar de
  // checkbox-id hierboven), zodat de legenda meteen laat zien wat je nu op
  // de kaart ziet i.p.v. alle mogelijke stijlen zonder onderscheid.
  function updateLegendActivity() {
    document.querySelectorAll(".legend-item[data-layer]").forEach((el) => {
      const checkbox = document.getElementById(el.dataset.layer);
      // data-parent: voor sub-toggles die alleen zichtbaar zijn als hun
      // ouder-checkbox ook aanstaat (bv. toggle-monumenten-gebouwd onder
      // toggle-monumenten) -- anders blijft het legenda-item ten onrechte
      // actief ogen terwijl de hele laag uitstaat.
      const parentCheckbox = el.dataset.parent ? document.getElementById(el.dataset.parent) : null;
      const inactive = (checkbox ? !checkbox.checked : false) || (parentCheckbox ? !parentCheckbox.checked : false);
      el.classList.toggle("inactive", inactive);
    });
  }
  for (const [checkboxId, layerIds] of Object.entries(layerToggles)) {
    document.getElementById(checkboxId).addEventListener("change", (e) => {
      const visibility = e.target.checked ? "visible" : "none";
      layerIds.forEach((id) => map.setLayoutProperty(id, "visibility", visibility));
      updateLegendActivity();
      syncUrl();
    });
  }

  // Rijksmonumenten: zelfde lazy-patroon als de andere losse lagen
  // (onderzoeksgebieden/CHS/verdwenen) -- pas ophalen bij de eerste keer
  // aanzetten, daarna alleen nog zichtbaarheid wisselen (2026-08-28, na
  // een externe review: dit was de enige van de zeven losse lagen die nog
  // standaard meeladen, ook met de laag uitgezet).
  document.getElementById("toggle-monumenten").addEventListener("change", async (e) => {
    updateLegendActivity();
    syncUrl();
    if (!e.target.checked) {
      if (monumentenLoaded) {
        for (const id of Object.keys(monumentenBaseFilters)) map.setLayoutProperty(id, "visibility", "none");
      }
      return;
    }
    if (monumentenLoaded) {
      for (const id of Object.keys(monumentenBaseFilters)) map.setLayoutProperty(id, "visibility", "visible");
      return;
    }
    statusEl.textContent = "Rijksmonumenten laden (16MB)…";
    monumenten = await loadJson(DATA.monumenten);
    monumentenLoaded = true;
    setupMonumentenLayers(monumenten);
  });

  document.getElementById("toggle-monumenten-alle").addEventListener("change", updateMonumentenFilter);
  document.getElementById("toggle-monumenten-gebouwd").addEventListener("change", () => {
    updateLegendActivity();
    updateMonumentenFilter();
  });
  document.getElementById("toggle-monumenten-archeologisch").addEventListener("change", () => {
    updateLegendActivity();
    updateMonumentenFilter();
  });

  // --- Ondergrond ---
  for (const radio of document.querySelectorAll('input[name="basemap"]')) {
    radio.addEventListener("change", (e) => {
      for (const id of Object.keys(BASEMAPS)) {
        map.setLayoutProperty(`base-${id}`, "visibility", id === e.target.value ? "visible" : "none");
      }
      syncUrl();
    });
  }
  document.getElementById("toggle-brk-percelen").addEventListener("change", (e) => {
    map.setLayoutProperty("overlay-brk-percelen", "visibility", e.target.checked ? "visible" : "none");
    syncUrl();
  });

  // --- Filters (terrein/ingangen; werken via GeoJSON filter-expressies) ---
  // Eén predicate-set, gebruikt voor zowel de MapLibre-filter als de live
  // aantallen per checkbox (facet-stijl: "als je dit ook aanvinkt, gegeven
  // je huidige andere selectie").
  //
  // Twee groepen met andere combinatielogica:
  // - STATUS_FILTER_IDS zijn elkaar uitsluitende toestanden van hetzelfde veld
  //   (geruimd/niet-geruimd) -- samen aanvinken moet de resultaten VERBREDEN
  //   (OR/unie), niet versmallen. Met AND is de combinatie altijd
  //   tegenstrijdig (geruimd === false EN === true) en levert dat altijd 0
  //   resultaten op. Een losse "statusconflict"-optie stond hier ooit ook in,
  //   maar is verwijderd (2026-08-27, wens van Joop) nu de bron 0 conflicten
  //   meer heeft -- status_conflict blijft wel als dataveld/kleur bestaan
  //   (zie terrein-fill hieronder) als stille vangnet, mocht een toekomstige
  //   bronupdate er weer een introduceren.
  // - HERITAGE_FILTER_IDS zijn onafhankelijke facetten die een begraafplaats
  //   allemaal tegelijk kan hebben, dus die blijven VERSMALLEN (AND).
  const STATUS_FILTER_IDS = ["filter-niet-geruimd", "filter-geruimd"];
  const HERITAGE_FILTER_IDS = ["filter-gezicht", "filter-archeologie", "filter-rijksmonument"];
  const FILTER_IDS = [...STATUS_FILTER_IDS, ...HERITAGE_FILTER_IDS];
  const STATUS_FILTER_EXPR = {
    "filter-niet-geruimd": ["==", ["get", "geruimd"], false],
    "filter-geruimd": ["==", ["get", "geruimd"], true],
  };
  function terreinPredicates() {
    return {
      "filter-niet-geruimd": (p) => p.geruimd === false,
      "filter-geruimd": (p) => p.geruimd === true,
      "filter-gezicht": (p) => p.in_beschermd_gezicht !== "none",
      "filter-archeologie": (p) => p.archeologische_rm_count > 0,
      "filter-rijksmonument": (p) => (p.rijksmonument_relations || []).some((r) => r.distance_m <= rmThreshold),
    };
  }
  function statusMatch(predicates, statusIds, p) {
    if (statusIds.length === 0) return true;
    return statusIds.some((id) => predicates[id](p));
  }
  function heritageMatch(predicates, heritageIds, p) {
    return heritageIds.every((id) => predicates[id](p));
  }
  function activeIdsIn(group) {
    return group.filter((id) => document.getElementById(id).checked);
  }

  // --- Zoeken op naam/plaats (los van de facet-filters hierboven: versmalt
  // altijd extra, ongeacht status-/erfgoedselectie) ---
  const searchInputEl = document.getElementById("search-naam-plaats");
  const searchCountEl = document.getElementById("search-count");
  function searchQuery() {
    return searchInputEl.value.trim().toLowerCase();
  }
  function searchMatch(query, p) {
    if (!query) return true;
    return (p.naam && p.naam.toLowerCase().includes(query)) || (p.plaats && p.plaats.toLowerCase().includes(query));
  }

  // Bijgehouden voor de exportknoppen (zie verderop): de features die nu
  // daadwerkelijk aan alle actieve filters + zoekopdracht voldoen, zodat
  // "exporteer huidige selectie" niet de hele dataset opnieuw hoeft te
  // filteren en altijd exact overeenkomt met wat er op de kaart te zien is.
  let currentVisibleFeatures = begraafplaatsen.features;

  function applyFilters() {
    const predicates = terreinPredicates();
    const activeStatusIds = activeIdsIn(STATUS_FILTER_IDS);
    const activeHeritageIds = activeIdsIn(HERITAGE_FILTER_IDS);
    const query = searchQuery();

    const clauses = [];
    if (query) {
      clauses.push([
        "any",
        ["in", query, ["downcase", ["get", "naam"]]],
        ["in", query, ["downcase", ["coalesce", ["get", "plaats"], ""]]],
      ]);
    }
    if (activeStatusIds.length) {
      const statusExprs = activeStatusIds.map((id) => STATUS_FILTER_EXPR[id]);
      clauses.push(statusExprs.length === 1 ? statusExprs[0] : ["any", ...statusExprs]);
    }
    if (activeHeritageIds.includes("filter-gezicht")) clauses.push(["!=", ["get", "in_beschermd_gezicht"], "none"]);
    if (activeHeritageIds.includes("filter-archeologie")) clauses.push([">", ["get", "archeologische_rm_count"], 0]);
    if (activeHeritageIds.includes("filter-rijksmonument")) {
      const ids = idsWithRijksmonumentWithin(begraafplaatsen, rmThreshold);
      clauses.push(["in", ["get", "id"], ["literal", Array.from(ids)]]);
    }
    const filter = clauses.length ? ["all", ...clauses] : null;
    map.setFilter("terrein-fill", filter);
    map.setFilter("terrein-outline", filter);
    updateFilterCounts(predicates, activeStatusIds, activeHeritageIds, query);
    currentVisibleFeatures = begraafplaatsen.features.filter(
      (f) =>
        searchMatch(query, f.properties) &&
        statusMatch(predicates, activeStatusIds, f.properties) &&
        heritageMatch(predicates, activeHeritageIds, f.properties)
    );
    syncUrl();
  }
  function updateFilterCounts(predicates, activeStatusIds, activeHeritageIds, query) {
    predicates = predicates || terreinPredicates();
    activeStatusIds = activeStatusIds || activeIdsIn(STATUS_FILTER_IDS);
    activeHeritageIds = activeHeritageIds || activeIdsIn(HERITAGE_FILTER_IDS);
    query = query === undefined ? searchQuery() : query;
    const totalCount = begraafplaatsen.features.length;
    const allProps = begraafplaatsen.features.map((f) => f.properties).filter((p) => searchMatch(query, p));

    for (const id of STATUS_FILTER_IDS) {
      const hypothetical = activeStatusIds.includes(id) ? activeStatusIds : [...activeStatusIds, id];
      const count = allProps.filter(
        (p) => heritageMatch(predicates, activeHeritageIds, p) && statusMatch(predicates, hypothetical, p)
      ).length;
      document.getElementById(`count-${id}`).textContent = `(${count})`;
    }
    for (const id of HERITAGE_FILTER_IDS) {
      const hypothetical = activeHeritageIds.includes(id) ? activeHeritageIds : [...activeHeritageIds, id];
      const count = allProps.filter(
        (p) => statusMatch(predicates, activeStatusIds, p) && heritageMatch(predicates, hypothetical, p)
      ).length;
      document.getElementById(`count-${id}`).textContent = `(${count})`;
    }
    const visibleCount = allProps.filter(
      (p) => statusMatch(predicates, activeStatusIds, p) && heritageMatch(predicates, activeHeritageIds, p)
    ).length;
    document.getElementById("filter-summary").textContent = `${visibleCount} van ${totalCount} zichtbaar`;
    searchCountEl.textContent = query ? `${allProps.length} gevonden op "${query}"` : "";
  }
  for (const id of FILTER_IDS) {
    document.getElementById(id).addEventListener("change", applyFilters);
  }
  document.getElementById("filter-reset").addEventListener("click", () => {
    for (const id of FILTER_IDS) document.getElementById(id).checked = false;
    searchInputEl.value = "";
    applyFilters();
  });
  rmThresholdEl.addEventListener("input", () => {
    rmThreshold = RM_THRESHOLD_STEPS[Number(rmThresholdEl.value)];
    rmThresholdLabelEl.textContent = `≤${rmThreshold}m`;
    updateMonumentenFilter();
    applyFilters();
  });

  // Bij een korte, specifieke zoekmatch (1-20 begraafplaatsen) automatisch
  // inzoomen -- bij een brede match (bv. "gem.") blijft de kaart staan, dat
  // zou anders een verrassende sprong naar een provinciebrede bbox geven.
  let searchFlyDebounce = null;
  searchInputEl.addEventListener("input", () => {
    applyFilters();
    clearTimeout(searchFlyDebounce);
    const query = searchQuery();
    if (!query) return;
    const matches = begraafplaatsen.features.filter((f) => searchMatch(query, f.properties));
    if (matches.length >= 1 && matches.length <= 20) {
      searchFlyDebounce = setTimeout(() => {
        map.fitBounds(boundsOfFeatureCollection({ type: "FeatureCollection", features: matches }), {
          padding: 60,
          maxZoom: 15,
          duration: 500,
        });
      }, 300);
    }
  });

  // --- Permalink: huidige kaartweergave + filters/zoekopdracht in de URL,
  // zodat een gedeelde link exact dezelfde weergave reproduceert (wens van
  // Joop, 2026-08-26 -- "waarschijnlijk het nuttigste voor Leons workflow").
  // Alleen history.replaceState (nooit pushState), zodat elke checkbox/pan
  // geen eigen entry in de browser-terug-geschiedenis krijgt. Losse, korte
  // parameternamen i.p.v. de volledige checkbox-id's om de URL leesbaar te
  // houden.
  const LAYER_TOGGLE_CODES = {
    "toggle-provinciegrens": "prov",
    "toggle-gemeentegrenzen": "gem",
    "toggle-terrein": "terrein",
    "toggle-ingangen": "ingang",
    "toggle-gezichten": "gezicht",
    "toggle-monumenten": "mon",
    "toggle-monumenten-alle": "monalle",
    "toggle-onderzoeksgebieden": "arch",
    "toggle-chs-archeologie": "chsarch",
    "toggle-verdwenen": "verdwenen",
  };
  // De twee monumenten-aard-sub-toggles staan standaard AAN (index.html) --
  // omgekeerde polariteit t.o.v. LAYER_TOGGLE_CODES hierboven (code aanwezig
  // = UIT i.p.v. AAN). Anders zou een permalink van vóór deze toggles
  // bestonden (2026-08-27) ze bij het laden alsnog uitzetten, simpelweg
  // omdat de codes daar nooit in konden voorkomen -- precies wat er
  // gebeurde met een oude link met alleen "mon,monalle" erin: de generieke
  // lus zag "monbouwd"/"monarch" ontbreken en zette dus beide uit, wat de
  // rijksmonumentfilter herleidde tot een lege literal-array (alles
  // verborgen, geen rijksmonumenten meer zichtbaar). Gemeld door Joop,
  // 2026-08-28.
  const DEFAULT_ON_LAYER_TOGGLE_CODES = {
    "toggle-monumenten-gebouwd": "nomonbouwd",
    "toggle-monumenten-archeologisch": "nomonarch",
  };
  const STATUS_CODES = { "filter-niet-geruimd": "ng", "filter-geruimd": "g" };
  const HERITAGE_CODES = { "filter-gezicht": "gz", "filter-archeologie": "ar", "filter-rijksmonument": "rm" };

  function currentStateParams() {
    const params = new URLSearchParams();
    const center = map.getCenter();
    params.set("lon", center.lng.toFixed(5));
    params.set("lat", center.lat.toFixed(5));
    params.set("z", map.getZoom().toFixed(2));
    const basemap = document.querySelector('input[name="basemap"]:checked')?.value;
    if (basemap && basemap !== "grijs") params.set("bm", basemap);
    if (document.getElementById("toggle-brk-percelen").checked) params.set("brk", "1");
    const layers = Object.entries(LAYER_TOGGLE_CODES)
      .filter(([id]) => document.getElementById(id).checked)
      .map(([, code]) => code);
    const layersUit = Object.entries(DEFAULT_ON_LAYER_TOGGLE_CODES)
      .filter(([id]) => !document.getElementById(id).checked)
      .map(([, code]) => code);
    const alleLagen = [...layers, ...layersUit];
    if (alleLagen.length) params.set("lyr", alleLagen.join(","));
    const status = Object.entries(STATUS_CODES)
      .filter(([id]) => document.getElementById(id).checked)
      .map(([, code]) => code);
    if (status.length) params.set("st", status.join(","));
    const heritage = Object.entries(HERITAGE_CODES)
      .filter(([id]) => document.getElementById(id).checked)
      .map(([, code]) => code);
    if (heritage.length) params.set("hg", heritage.join(","));
    if (rmThreshold !== 100) params.set("rmt", String(rmThreshold));
    if (selectedFunctie.size) params.set("fn", [...selectedFunctie].join("|"));
    const query = searchInputEl.value.trim();
    if (query) params.set("q", query);
    return params;
  }

  function buildShareUrl() {
    const qs = currentStateParams().toString();
    return `${location.origin}${location.pathname}${qs ? "?" + qs : ""}`;
  }

  let urlSyncDebounce = null;
  function syncUrl() {
    clearTimeout(urlSyncDebounce);
    urlSyncDebounce = setTimeout(() => history.replaceState(null, "", buildShareUrl()), 300);
  }

  // Leest ?lon/lat/z/bm/brk/lyr/st/hg/rmt/fn/q uit de URL en zet de
  // bijbehorende controls, inclusief het versturen van "change"-events zodat
  // de bestaande listeners (laagzichtbaarheid, ondergrond, etc.) hun normale
  // werk doen -- geen aparte kopie van die logica hier. Draait sowieso 1x bij
  // het laden (ook zonder querystring) om de initiele filters/legenda/tellingen
  // te zetten; retourneert of er een expliciete camera-positie was.
  function applyStateFromUrl() {
    const params = new URLSearchParams(location.search);
    let hasView = false;
    if (params.toString()) {
      const lon = parseFloat(params.get("lon"));
      const lat = parseFloat(params.get("lat"));
      const z = parseFloat(params.get("z"));
      hasView = Number.isFinite(lon) && Number.isFinite(lat) && Number.isFinite(z);
      if (hasView) map.jumpTo({ center: [lon, lat], zoom: z });

      const bm = params.get("bm");
      if (bm && BASEMAPS[bm]) {
        const radio = document.querySelector(`input[name="basemap"][value="${bm}"]`);
        if (radio) {
          radio.checked = true;
          radio.dispatchEvent(new Event("change"));
        }
      }
      if (params.get("brk") === "1") {
        const cb = document.getElementById("toggle-brk-percelen");
        cb.checked = true;
        cb.dispatchEvent(new Event("change"));
      }
      const layerCodes = new Set((params.get("lyr") || "").split(",").filter(Boolean));
      for (const [id, code] of Object.entries(LAYER_TOGGLE_CODES)) {
        const cb = document.getElementById(id);
        const shouldCheck = layerCodes.has(code);
        if (cb.checked !== shouldCheck) {
          cb.checked = shouldCheck;
          cb.dispatchEvent(new Event("change"));
        }
      }
      for (const [id, code] of Object.entries(DEFAULT_ON_LAYER_TOGGLE_CODES)) {
        const cb = document.getElementById(id);
        const shouldCheck = !layerCodes.has(code);
        if (cb.checked !== shouldCheck) {
          cb.checked = shouldCheck;
          cb.dispatchEvent(new Event("change"));
        }
      }
      const statusCodes = new Set((params.get("st") || "").split(",").filter(Boolean));
      for (const [id, code] of Object.entries(STATUS_CODES)) {
        document.getElementById(id).checked = statusCodes.has(code);
      }
      const heritageCodes = new Set((params.get("hg") || "").split(",").filter(Boolean));
      for (const [id, code] of Object.entries(HERITAGE_CODES)) {
        document.getElementById(id).checked = heritageCodes.has(code);
      }
      const rmt = parseInt(params.get("rmt"), 10);
      if (Number.isFinite(rmt)) {
        const index = rmThresholdIndexFor(rmt);
        rmThreshold = RM_THRESHOLD_STEPS[index];
        rmThresholdEl.value = String(index);
        rmThresholdLabelEl.textContent = `≤${rmThreshold}m`;
      }
      const fn = params.get("fn");
      if (fn) {
        for (const label of fn.split("|")) selectedFunctie.add(label);
        renderFunctieOptions();
      }
      const q = params.get("q");
      if (q) searchInputEl.value = q;
    }

    updateMonumentenFilter();
    applyFilters();
    updateLegendActivity();
    return hasView;
  }
  map.on("moveend", syncUrl);

  // --- Data-export: knop om de huidige gefilterde selectie te downloaden
  // (wens van Joop, 2026-08-26 -- handig voor Leon om afwijkingen offline te
  // checken). Als eigen kaart-control i.p.v. paneelknoppen, zodat het
  // filterpaneel links niet voller wordt -- hoort qua functie toch bij "wat
  // zie ik nu op de kaart", net als de laagtoggles.
  const CSV_EXPORT_EXCLUDE_KEYS = new Set(["ingang"]);
  function toCsvValue(value) {
    if (value === null || value === undefined) return "";
    const s = typeof value === "object" ? JSON.stringify(value) : String(value);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  }
  function featuresToCsv(features) {
    const keys = [];
    const seen = new Set();
    for (const f of features) {
      for (const k of Object.keys(f.properties)) {
        if (CSV_EXPORT_EXCLUDE_KEYS.has(k) || seen.has(k)) continue;
        seen.add(k);
        keys.push(k);
      }
    }
    const lines = [keys.join(",")];
    for (const f of features) lines.push(keys.map((k) => toCsvValue(f.properties[k])).join(","));
    return lines.join("\r\n");
  }
  function featuresToGeoJson(features) {
    return JSON.stringify({ type: "FeatureCollection", features }, null, 2);
  }
  function downloadBlob(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function todayStamp() {
    return new Date().toISOString().slice(0, 10);
  }

  class ExportControl {
    onAdd() {
      const container = document.createElement("div");
      container.className = "maplibregl-ctrl maplibregl-ctrl-group dodenakkers-export-ctrl";
      const csvBtn = document.createElement("button");
      csvBtn.type = "button";
      csvBtn.textContent = "CSV";
      csvBtn.title = "Exporteer huidige selectie als CSV";
      csvBtn.setAttribute("aria-label", "Exporteer huidige selectie als CSV");
      csvBtn.addEventListener("click", () => {
        downloadBlob(`dodenakkers-zh-selectie-${todayStamp()}.csv`, featuresToCsv(currentVisibleFeatures), "text/csv;charset=utf-8");
      });
      const geoBtn = document.createElement("button");
      geoBtn.type = "button";
      geoBtn.textContent = "GeoJSON";
      geoBtn.title = "Exporteer huidige selectie als GeoJSON";
      geoBtn.setAttribute("aria-label", "Exporteer huidige selectie als GeoJSON");
      geoBtn.addEventListener("click", () => {
        downloadBlob(`dodenakkers-zh-selectie-${todayStamp()}.geojson`, featuresToGeoJson(currentVisibleFeatures), "application/geo+json");
      });
      container.append(csvBtn, geoBtn);
      this._container = container;
      return container;
    }
    onRemove() {
      this._container.remove();
    }
  }

  class LinkControl {
    onAdd() {
      const container = document.createElement("div");
      container.className = "maplibregl-ctrl maplibregl-ctrl-group dodenakkers-link-ctrl";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = "Link";
      btn.title = "Kopieer link naar huidige weergave";
      btn.setAttribute("aria-label", "Kopieer link naar huidige weergave");
      btn.addEventListener("click", async () => {
        const url = buildShareUrl();
        history.replaceState(null, "", url);
        try {
          await navigator.clipboard.writeText(url);
          btn.textContent = "✓";
          btn.setAttribute("aria-label", "Link gekopieerd");
        } catch (err) {
          console.error("Kopiëren naar klembord mislukt", err);
          btn.textContent = "✗";
        }
        setTimeout(() => {
          btn.textContent = "Link";
          btn.setAttribute("aria-label", "Kopieer link naar huidige weergave");
        }, 1500);
      });
      container.appendChild(btn);
      this._container = container;
      return container;
    }
    onRemove() {
      this._container.remove();
    }
  }

  map.addControl(new LinkControl(), "top-right");
  map.addControl(new ExportControl(), "top-right");

  const hadUrlView = applyStateFromUrl();
  if (!hadUrlView) {
    map.fitBounds(boundsOfFeatureCollection(begraafplaatsen), { padding: 40, duration: 0 });
  }

  statusEl.textContent =
    `${begraafplaatsen.features.length} begraafplaatsen · ` +
    `${ingangen.features.length} ingangen · ` +
    `${gezichten.features.length} beschermde gezichten`;
}

main().catch((err) => {
  console.error(err);
  statusEl.textContent = `Fout bij laden: ${err.message}`;
  statusEl.style.color = "#e03131";
});
