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
  monumenten: "../data/rce/rijksmonumenten.geojson",
  provinciegrens: "../data/pdok/provincie-zuid-holland.geojson",
  // Niet in de initiele Promise.all: 22.254 features / 17MB, alleen ophalen
  // zodra de gebruiker de laag daadwerkelijk aanzet (zie toggle-onderzoeksgebieden).
  onderzoeksgebieden: "../data/rce/archeologische-onderzoeksgebieden.geojson",
};

const statusEl = document.getElementById("status");

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

function popupHtml(title, rows) {
  const dl = rows
    .filter(([, v]) => v !== null && v !== undefined && v !== "")
    .map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`)
    .join("");
  return `<h3>${title}</h3><dl>${dl}</dl>`;
}

async function loadJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  return res.json();
}

async function main() {
  const [begraafplaatsen, gezichten, monumenten, provinciegrens] = await Promise.all([
    loadJson(DATA.begraafplaatsen),
    loadJson(DATA.gezichten),
    loadJson(DATA.monumenten),
    loadJson(DATA.provinciegrens),
  ]);
  const ingangen = ingangenFromBegraafplaatsen(begraafplaatsen);

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

  // --- Archeologische onderzoeksgebieden (lazy: 22.254 polygonen, 17MB --
  // pas ophalen zodra de gebruiker de laag echt aanzet, niet standaard mee-
  // laden bij elke paginabezoek). Wens van de gebruiker (2026-08-20).
  let onderzoeksgebiedenLoaded = false;
  document.getElementById("toggle-onderzoeksgebieden").addEventListener("change", async (e) => {
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

  // --- Rijksmonumenten ---
  // Gebouwde monumenten altijd als punt (ook wanneer de bron een
  // polygoongeometrie heeft -- dan een client-side centroid, alleen voor
  // de marker-positie, geen vervanging van de echte geometrie). Archeologische
  // rijksmonumenten juist als vlak wanneer de bron een polygoon heeft (anders
  // als punt, want er is dan geen polygoon om te tonen).
  const monumentenPunten = deriveMonumentPoints(monumenten);
  map.addSource("monumenten", { type: "geojson", data: monumenten });
  map.addSource("monumenten-punten", { type: "geojson", data: monumentenPunten });
  map.addLayer({
    id: "monumenten-punt",
    type: "circle",
    source: "monumenten-punten",
    layout: { visibility: "none" },
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
  const archeologischFilter = ["==", ["get", "monument_aard"], "archeologisch"];
  map.addLayer({
    id: "monumenten-vlak",
    type: "fill",
    source: "monumenten",
    layout: { visibility: "none" },
    filter: archeologischFilter,
    paint: { "fill-color": "#e8590c", "fill-opacity": 0.4 },
  });
  map.addLayer({
    id: "monumenten-vlak-outline",
    type: "line",
    source: "monumenten",
    layout: { visibility: "none" },
    filter: archeologischFilter,
    paint: { "line-color": "#e8590c", "line-width": 1.5 },
  });

  let rmThreshold = 100;
  const rmThresholdEl = document.getElementById("rm-threshold");
  const rmThresholdLabelEl = document.getElementById("rm-threshold-label");

  const monumentenBaseFilters = {
    "monumenten-punt": null,
    "monumenten-vlak": archeologischFilter,
    "monumenten-vlak-outline": archeologischFilter,
  };

  // --- Functiefilter: dynamisch opgebouwd uit de daadwerkelijk voorkomende
  // oorspronkelijke_functie_kort-waarden, geen vaste curatie (zie
  // docs/data/004-rce-mcp-querystrategie.md, "Filteren: alleen op
  // oorspronkelijke functie"). Selectie staat los van de zoekbalk zodat
  // filteren op tekst de selectie niet ongedaan maakt.
  const functieOptions = functieCounts(monumenten);
  const selectedFunctie = new Set();
  const functieSelectEl = document.getElementById("functie-select");
  const functieSearchEl = document.getElementById("functie-search");
  function renderFunctieOptions() {
    const query = functieSearchEl.value.trim().toLowerCase();
    const prevScroll = functieSelectEl.scrollTop;
    functieSelectEl.innerHTML = "";
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
    const showAll = document.getElementById("toggle-monumenten-alle").checked;
    const relevantUris = relevantMonumentUris(begraafplaatsen, rmThreshold);
    const relevantMonumentenFilter = ["in", ["get", "cho_uri"], ["literal", Array.from(relevantUris)]];
    const dynamicClauses = [];
    if (!showAll) dynamicClauses.push(relevantMonumentenFilter);
    if (selectedFunctie.size) {
      dynamicClauses.push(["in", ["get", "oorspronkelijke_functie_kort"], ["literal", [...selectedFunctie]]]);
    }
    for (const [id, base] of Object.entries(monumentenBaseFilters)) {
      const clauses = base ? [base, ...dynamicClauses] : dynamicClauses;
      const filter = clauses.length === 0 ? null : clauses.length === 1 ? clauses[0] : ["all", ...clauses];
      map.setFilter(id, filter);
    }
    document.getElementById("monumenten-count").textContent = `(${relevantUris.size} relevant, ≤${rmThreshold}m)`;
  }
  updateMonumentenFilter();

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
            "Rijksmonumenten &le;100m",
            rmRelaties.length
              ? rmRelaties.map((r) => `${r.naam || r.rijksmonumentnummer} (${relationLabel(r.relation)}, ${r.distance_m}m)`).join(", ")
              : "geen",
          ],
          ["Koppelwijze ingang", p.ingang_koppelwijze],
          ["ID", p.id],
        ])
      )
      .addTo(map);
  });

  map.on("click", "ingangen-punt", (e) => {
    const p = e.features[0].properties;
    new maplibregl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(popupHtml(`Ingang: ${p.naam}`, [["Plaats", p.plaats], ["Gedeelde ingang", p.gedeeld]]))
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
          ["Geometriebron", p.geometry_bron],
          ["Register", p.monumentenregister_url ? `<a href="${p.monumentenregister_url}" target="_blank" rel="noopener">bekijk</a>` : null],
        ])
      )
      .addTo(map);
  }
  map.on("click", "monumenten-punt", showMonumentPopup);
  map.on("click", "monumenten-vlak", showMonumentPopup);

  for (const layerId of ["terrein-fill", "ingangen-punt", "gezichten-fill", "monumenten-punt", "monumenten-vlak"]) {
    map.on("mouseenter", layerId, () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", layerId, () => (map.getCanvas().style.cursor = ""));
  }

  // --- Laagtoggles ---
  const layerToggles = {
    "toggle-provinciegrens": ["provinciegrens-lijn"],
    "toggle-terrein": ["terrein-fill", "terrein-outline"],
    "toggle-ingangen": ["ingangen-punt"],
    "toggle-gezichten": ["gezichten-fill", "gezichten-outline"],
    "toggle-monumenten": Object.keys(monumentenBaseFilters),
  };
  for (const [checkboxId, layerIds] of Object.entries(layerToggles)) {
    document.getElementById(checkboxId).addEventListener("change", (e) => {
      const visibility = e.target.checked ? "visible" : "none";
      layerIds.forEach((id) => map.setLayoutProperty(id, "visibility", visibility));
    });
  }

  document.getElementById("toggle-monumenten-alle").addEventListener("change", updateMonumentenFilter);

  // --- Ondergrond ---
  for (const radio of document.querySelectorAll('input[name="basemap"]')) {
    radio.addEventListener("change", (e) => {
      for (const id of Object.keys(BASEMAPS)) {
        map.setLayoutProperty(`base-${id}`, "visibility", id === e.target.value ? "visible" : "none");
      }
    });
  }
  document.getElementById("toggle-brk-percelen").addEventListener("change", (e) => {
    map.setLayoutProperty("overlay-brk-percelen", "visibility", e.target.checked ? "visible" : "none");
  });

  // --- Filters (terrein/ingangen; werken via GeoJSON filter-expressies) ---
  // Eén predicate-set, gebruikt voor zowel de MapLibre-filter als de live
  // aantallen per checkbox (facet-stijl: "als je dit ook aanvinkt, gegeven
  // je huidige andere selectie").
  const FILTER_IDS = [
    "filter-niet-geruimd",
    "filter-geruimd",
    "filter-conflict",
    "filter-gezicht",
    "filter-archeologie",
    "filter-rijksmonument",
  ];
  function terreinPredicates() {
    return {
      "filter-niet-geruimd": (p) => p.geruimd === false,
      "filter-geruimd": (p) => p.geruimd === true,
      "filter-conflict": (p) => p.status_conflict === true,
      "filter-gezicht": (p) => p.in_beschermd_gezicht !== "none",
      "filter-archeologie": (p) => p.archeologische_rm_count > 0,
      "filter-rijksmonument": (p) => (p.rijksmonument_relations || []).some((r) => r.distance_m <= rmThreshold),
    };
  }
  function applyFilters() {
    const predicates = terreinPredicates();
    const clauses = [];
    if (document.getElementById("filter-niet-geruimd").checked) clauses.push(["==", ["get", "geruimd"], false]);
    if (document.getElementById("filter-geruimd").checked) clauses.push(["==", ["get", "geruimd"], true]);
    if (document.getElementById("filter-conflict").checked) clauses.push(["==", ["get", "status_conflict"], true]);
    if (document.getElementById("filter-gezicht").checked) clauses.push(["!=", ["get", "in_beschermd_gezicht"], "none"]);
    if (document.getElementById("filter-archeologie").checked) clauses.push([">", ["get", "archeologische_rm_count"], 0]);
    if (document.getElementById("filter-rijksmonument").checked) {
      const ids = idsWithRijksmonumentWithin(begraafplaatsen, rmThreshold);
      clauses.push(["in", ["get", "id"], ["literal", Array.from(ids)]]);
    }
    const filter = clauses.length ? ["all", ...clauses] : null;
    map.setFilter("terrein-fill", filter);
    map.setFilter("terrein-outline", filter);
    updateFilterCounts(predicates);
  }
  function updateFilterCounts(predicates) {
    predicates = predicates || terreinPredicates();
    const allProps = begraafplaatsen.features.map((f) => f.properties);
    const activeIds = FILTER_IDS.filter((id) => document.getElementById(id).checked);
    for (const id of FILTER_IDS) {
      const others = activeIds.filter((otherId) => otherId !== id);
      const count = allProps.filter((p) => others.every((o) => predicates[o](p)) && predicates[id](p)).length;
      const el = document.getElementById(`count-${id}`);
      if (el) el.textContent = `(${count})`;
    }
    const visibleCount = allProps.filter((p) => activeIds.every((id) => predicates[id](p))).length;
    document.getElementById("filter-summary").textContent = `${visibleCount} van ${allProps.length} zichtbaar`;
  }
  for (const id of FILTER_IDS) {
    document.getElementById(id).addEventListener("change", applyFilters);
  }
  rmThresholdEl.addEventListener("input", () => {
    rmThreshold = Number(rmThresholdEl.value);
    rmThresholdLabelEl.textContent = `≤${rmThreshold}m`;
    updateMonumentenFilter();
    applyFilters();
  });
  applyFilters();

  map.fitBounds(boundsOfFeatureCollection(begraafplaatsen), { padding: 40, duration: 0 });

  statusEl.textContent =
    `${begraafplaatsen.features.length} begraafplaatsen · ` +
    `${ingangen.features.length} ingangen · ` +
    `${gezichten.features.length} beschermde gezichten · ` +
    `${monumenten.features.length} rijksmonumenten`;
}

main().catch((err) => {
  console.error(err);
  statusEl.textContent = `Fout bij laden: ${err.message}`;
  statusEl.style.color = "#e03131";
});
