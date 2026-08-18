// Dodenakkers Zuid-Holland — onderzoeksviewer (MVP)
//
// Laadt de gebouwde basisdataset en RCE-extracten rechtstreeks als
// statische GeoJSON. Geen live SPARQL vanuit de browser (zie sectie 15
// van de briefing) — alle data komt uit data/generated/ en data/rce/,
// zoals gegenereerd door scripts/build_base_dataset.py en
// scripts/fetch_rce.py.

const DATA = {
  // analyse.geojson = begraafplaatsen.geojson verrijkt met erfgoedrelaties
  // (scripts/analyse_spatial.py). Zelfde basisvelden, dus deze viewer werkt
  // ook (met minder functionaliteit) als je terugzet op begraafplaatsen.geojson.
  begraafplaatsen: "../data/generated/analyse.geojson",
  gezichten: "../data/rce/beschermde-gezichten.geojson",
  monumenten: "../data/rce/rijksmonumenten.geojson",
};

const statusEl = document.getElementById("status");

// PDOK BRT-achtergrondkaart (grijs), zelfde ondergrond als
// https://github.com/jolietjakeblues/doorzoeker-v2a (app/HeritageMap.tsx).
// WMTS, EPSG:3857 -- de tilematrix/tilerow/tilecol-parameters komen 1-op-1
// overeen met MapLibre's {z}/{x}/{y}-tileschema.
const map = new maplibregl.Map({
  container: "map",
  style: {
    version: 8,
    sources: {
      "pdok-brt-grijs": {
        type: "raster",
        tiles: [
          "https://service.pdok.nl/kadaster/brt-achtergrondkaart/wmts/v2_0?service=WMTS&request=GetTile&version=1.0.0&layer=grijs&style=default&tilematrixset=EPSG:3857&format=image/png&tilematrix={z}&tilerow={y}&tilecol={x}",
        ],
        tileSize: 256,
        maxzoom: 19,
        attribution: 'Kaart: <a href="https://www.pdok.nl/">PDOK</a> · BRT Kadaster',
      },
    },
    layers: [{ id: "pdok-brt-grijs", type: "raster", source: "pdok-brt-grijs" }],
  },
  center: [4.5, 52.0],
  zoom: 9,
});

map.addControl(new maplibregl.NavigationControl(), "top-right");

function relevantMonumentUris(begraafplaatsenFc) {
  const uris = new Set();
  for (const f of begraafplaatsenFc.features) {
    for (const r of f.properties.rijksmonument_relations || []) {
      if (r.cho_uri) uris.add(r.cho_uri);
    }
  }
  return uris;
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
  // (section 2/4 of the briefing) — coordinates live on its sub-geometries.
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
  const [begraafplaatsen, gezichten, monumenten] = await Promise.all([
    loadJson(DATA.begraafplaatsen),
    loadJson(DATA.gezichten),
    loadJson(DATA.monumenten),
  ]);
  const ingangen = ingangenFromBegraafplaatsen(begraafplaatsen);

  if (!map.isStyleLoaded()) {
    await new Promise((resolve) => map.on("load", resolve));
  }

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

  // --- Rijksmonumenten (initieel uit, 14k punten) ---
  map.addSource("monumenten", { type: "geojson", data: monumenten });
  map.addLayer({
    id: "monumenten-punt",
    type: "circle",
    source: "monumenten",
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
  // Monumenten met polygoongeometrie (o.a. archeologische rijksmonumenten)
  // renderen niet via een circle-laag -- die tekent alleen Point-features.
  // Dezelfde bron, een fill+outline laag ernaast voor de Polygon-features.
  const monumentenKleur = [
    "case",
    ["==", ["get", "monument_aard"], "archeologisch"],
    "#e8590c",
    ["==", ["get", "monument_aard"], "onroerend gebouwd"],
    "#1971c2",
    "#868e96",
  ];
  map.addLayer({
    id: "monumenten-vlak",
    type: "fill",
    source: "monumenten",
    layout: { visibility: "none" },
    paint: { "fill-color": monumentenKleur, "fill-opacity": 0.4 },
  });
  map.addLayer({
    id: "monumenten-vlak-outline",
    type: "line",
    source: "monumenten",
    layout: { visibility: "none" },
    paint: { "line-color": monumentenKleur, "line-width": 1.5 },
  });

  const relevantUris = relevantMonumentUris(begraafplaatsen);
  const relevantMonumentenFilter = ["in", ["get", "cho_uri"], ["literal", Array.from(relevantUris)]];
  const monumentenLayerIds = ["monumenten-punt", "monumenten-vlak", "monumenten-vlak-outline"];
  function updateMonumentenFilter() {
    const showAll = document.getElementById("toggle-monumenten-alle").checked;
    const functieOnly = document.getElementById("filter-functie-begraafplaats").checked;
    const clauses = [];
    if (!showAll) clauses.push(relevantMonumentenFilter);
    if (functieOnly) clauses.push(["==", ["get", "oorspronkelijke_functie_begraafplaats"], true]);
    const filter = clauses.length === 0 ? null : clauses.length === 1 ? clauses[0] : ["all", ...clauses];
    monumentenLayerIds.forEach((id) => map.setFilter(id, filter));
  }
  updateMonumentenFilter();
  document.getElementById("monumenten-count").textContent = `(${relevantUris.size} relevant, ≤100m)`;

  // --- Begraafplaatsen terrein ---
  map.addSource("terrein", { type: "geojson", data: begraafplaatsen });
  map.addLayer({
    id: "terrein-fill",
    type: "fill",
    source: "terrein",
    paint: {
      "fill-color": [
        "case",
        ["==", ["get", "status_conflict"], true],
        "#f1f3f5",
        ["==", ["get", "geruimd"], true],
        "#adb5bd",
        "#40c057",
      ],
      "fill-opacity": 0.55,
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
              ? archRelaties.map((r) => `${r.naam || r.rijksmonumentnummer} (${r.relation})`).join(", ")
              : archNearest
              ? `geen overlap (dichtstbij: ${archNearest.distance_m} m)`
              : "geen",
          ],
          [
            "Rijksmonumenten &le;100m",
            rmRelaties.length
              ? rmRelaties.map((r) => `${r.naam || r.rijksmonumentnummer} (${r.relation}, ${r.distance_m}m)`).join(", ")
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
          ["Functie is begraafplaats/kerkhof", p.oorspronkelijke_functie_begraafplaats ? "ja" : "nee"],
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
    "toggle-terrein": ["terrein-fill", "terrein-outline"],
    "toggle-ingangen": ["ingangen-punt"],
    "toggle-gezichten": ["gezichten-fill", "gezichten-outline"],
    "toggle-monumenten": monumentenLayerIds,
  };
  for (const [checkboxId, layerIds] of Object.entries(layerToggles)) {
    document.getElementById(checkboxId).addEventListener("change", (e) => {
      const visibility = e.target.checked ? "visible" : "none";
      layerIds.forEach((id) => map.setLayoutProperty(id, "visibility", visibility));
    });
  }

  document.getElementById("toggle-monumenten-alle").addEventListener("change", updateMonumentenFilter);
  document.getElementById("filter-functie-begraafplaats").addEventListener("change", updateMonumentenFilter);

  // --- Filters (terrein/ingangen; werken via GeoJSON filter-expressies) ---
  function applyFilters() {
    const nietGeruimd = document.getElementById("filter-niet-geruimd").checked;
    const geruimdOnly = document.getElementById("filter-geruimd").checked;
    const conflictOnly = document.getElementById("filter-conflict").checked;
    const gezichtOnly = document.getElementById("filter-gezicht").checked;
    const archeologieOnly = document.getElementById("filter-archeologie").checked;
    const rijksmonumentOnly = document.getElementById("filter-rijksmonument").checked;
    const clauses = [];
    if (nietGeruimd) clauses.push(["==", ["get", "geruimd"], false]);
    if (geruimdOnly) clauses.push(["==", ["get", "geruimd"], true]);
    if (conflictOnly) clauses.push(["==", ["get", "status_conflict"], true]);
    if (gezichtOnly) clauses.push(["!=", ["get", "in_beschermd_gezicht"], "none"]);
    if (archeologieOnly) clauses.push([">", ["get", "archeologische_rm_count"], 0]);
    if (rijksmonumentOnly) clauses.push([">", ["get", "rijksmonument_count"], 0]);
    const filter = clauses.length ? ["all", ...clauses] : null;
    map.setFilter("terrein-fill", filter);
    map.setFilter("terrein-outline", filter);
  }
  for (const id of [
    "filter-niet-geruimd",
    "filter-geruimd",
    "filter-conflict",
    "filter-gezicht",
    "filter-archeologie",
    "filter-rijksmonument",
  ]) {
    document.getElementById(id).addEventListener("change", applyFilters);
  }

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
