// Dodenakkers Zuid-Holland - oude kaarten bij een verdwenen of kandidaat-begraafplaats
// (oude-kaarten.html?id=vd-leiden-oude-joodse-begraafplaats).
//
// Welke kaarten er over een punt liggen staat vooraf berekend in
// data/generated/oude_kaarten.json (scripts/fetch_allmaps.py). Het kaartbeeld
// komt als tegels van de Allmaps Tile Server: die vervormt de scan van de
// collectie (IIIF) naar de juiste plek. Geen extra bibliotheek nodig. Zelfde
// aanpak als de pagina Oude kaarten in het project Joodse Begraafplaatsen.
//
// URL-parameters
//   ?id=vd-...     het punt (verplicht): een verdwenen begraafplaats of kandidaat
//   &kaart=<id>    een bepaalde oude kaart (Allmaps map-id); anders de eerste

const OUDE_KAARTEN_URL = "../data/generated/oude_kaarten.json";

// Zelfde PDOK-ondergronden als app.js (BASEMAPS), alleen de twee die hier nuttig zijn.
const ONDERGRONDEN = {
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
};

const SOORT_LABEL = {
  verdwenen: "Verdwenen begraafplaats (bron: de domeinexpert)",
  tekstzoek: "Kandidaat uit archeologische rapporten (experimenteel)",
  klooster: "Kandidaat: klooster (rijksmonument, experimenteel)",
  synagoge: "Kandidaat: synagoge (rijksmonument, experimenteel)",
  kapel: "Kandidaat: kapel (rijksmonument, experimenteel)",
  chs: "Kandidaat: archeologisch terrein van provinciaal belang (experimenteel)",
};

const params = new URLSearchParams(location.search);
const ID = params.get("id");
const statusEl = document.getElementById("status");
const keuzeEl = document.getElementById("ok-keuze");
const bronEl = document.getElementById("ok-bron");
const dekkingEl = document.getElementById("ok-dekking");

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

const tegels = (kaart) => `https://allmaps.xyz/maps/${encodeURIComponent(kaart)}/{z}/{x}/{y}.png`;
const viewerUrl = (kaart) =>
  `https://viewer.allmaps.org/?url=${encodeURIComponent(`https://annotations.allmaps.org/maps/${kaart}`)}`;

function maakStijl() {
  const style = { version: 8, sources: {}, layers: [] };
  for (const [id, cfg] of Object.entries(ONDERGRONDEN)) {
    style.sources[`base-${id}`] = { type: "raster", tiles: cfg.tiles, tileSize: 256, maxzoom: 19, attribution: cfg.attribution };
    style.layers.push({
      id: `base-${id}`,
      type: "raster",
      source: `base-${id}`,
      layout: { visibility: id === "grijs" ? "visible" : "none" },
    });
  }
  return style;
}

// Cirkel van straal `meters` om een punt als GeoJSON-polygoon (vlakke benadering,
// ruim voldoende voor 100 en 250 m).
function ring(lon, lat, meters) {
  const stappen = 72;
  const dLat = meters / 111320;
  const dLon = meters / (111320 * Math.cos((lat * Math.PI) / 180));
  const coords = [];
  for (let i = 0; i <= stappen; i++) {
    const hoek = (i / stappen) * 2 * Math.PI;
    coords.push([lon + dLon * Math.cos(hoek), lat + dLat * Math.sin(hoek)]);
  }
  return coords;
}

function toonKaart(map, kaart, info) {
  if (map.getLayer("oud")) map.removeLayer("oud");
  if (map.getSource("oud")) map.removeSource("oud");
  map.addSource("oud", {
    type: "raster",
    tiles: [tegels(kaart)],
    tileSize: 256,
    // De tile server rekent elke tegel uit; boven zoom 18 vergroten we zelf.
    maxzoom: 18,
    attribution: `Oude kaart: ${info.collectie} · <a href="https://allmaps.org/">Allmaps</a>`,
  });
  map.addLayer(
    { id: "oud", type: "raster", source: "oud", paint: { "raster-opacity": dekkingEl.value / 100, "raster-fade-duration": 0 } },
    "ringen"
  );
  bronEl.replaceChildren(`${info.collectie}${info.jaar ? ` · ${info.jaar}` : ""} · `);
  const link = document.createElement("a");
  link.href = viewerUrl(kaart);
  link.target = "_blank";
  link.rel = "noopener";
  link.textContent = "hele kaart in Allmaps";
  bronEl.appendChild(link);
  const url = new URL(location.href);
  url.searchParams.set("kaart", kaart);
  history.replaceState(null, "", url);
}

async function main() {
  if (!ID) throw new Error("Geen plek gekozen. Open deze pagina via de kandidatenpagina of de kaart.");
  const res = await fetch(OUDE_KAARTEN_URL);
  if (!res.ok) throw new Error(`${OUDE_KAARTEN_URL}: HTTP ${res.status}`);
  const oud = await res.json();
  const p = oud.punten[ID];
  if (!p) throw new Error(`Onbekende plek: ${ID}`);
  const lijst = oud.per_punt[ID] || [];

  document.title = `Oude kaarten: ${p.naam}${p.plaats ? `, ${p.plaats}` : ""} - Dodenakkers Zuid-Holland`;
  document.getElementById("ok-naam").textContent = `${p.naam}${p.plaats ? `, ${p.plaats}` : ""}`;
  document.getElementById("ok-soort").textContent = SOORT_LABEL[p.soort] || "";
  const lyr = p.soort === "verdwenen" ? "terrein,ingang,gezicht,verdwenen" : "terrein,ingang,gezicht";
  document.getElementById("ok-kaartlink").href =
    `index.html?${new URLSearchParams({ lon: p.lon.toFixed(5), lat: p.lat.toFixed(5), z: "16.00", lyr })}`;

  for (const k of lijst) {
    const info = oud.kaarten[k];
    const optie = document.createElement("option");
    optie.value = k;
    optie.textContent = `${info.jaar ? info.jaar + " · " : ""}${info.titel}`;
    keuzeEl.appendChild(optie);
  }
  const gekozen = lijst.includes(params.get("kaart")) ? params.get("kaart") : lijst[0];
  if (gekozen) keuzeEl.value = gekozen;
  keuzeEl.disabled = !lijst.length;

  const map = new maplibregl.Map({
    container: "map",
    style: maakStijl(),
    center: [p.lon, p.lat],
    zoom: 15.5,
    maxPitch: 0,
    attributionControl: { compact: true, customAttribution: "Inventarisatie: stichting Dodenakkers" },
  });
  map.addControl(new maplibregl.NavigationControl({ visualizePitch: false }), "top-right");
  map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-right");
  await new Promise((r) => map.on("load", r));
  // Zoals op de hoofdkaart: op smalle schermen de bronvermelding inklappen.
  if (matchMedia("(max-width: 700px)").matches) {
    map.once("idle", () => document.querySelector(".maplibregl-ctrl-attrib")?.classList.remove("maplibregl-compact-show"));
  }

  const ringen = {
    type: "FeatureCollection",
    features: [100, 250].map((m) => ({
      type: "Feature",
      properties: { straal: m },
      geometry: { type: "LineString", coordinates: ring(p.lon, p.lat, m) },
    })),
  };
  map.addSource("ringen", { type: "geojson", data: ringen });
  map.addLayer({ id: "ringen-wit", type: "line", source: "ringen", paint: { "line-color": "#ffffff", "line-width": 4, "line-opacity": 0.8 } });
  map.addLayer({ id: "ringen", type: "line", source: "ringen", paint: { "line-color": "#212529", "line-width": 1.5, "line-dasharray": [3, 2] } });
  map.addSource("punt", { type: "geojson", data: { type: "Feature", properties: {}, geometry: { type: "Point", coordinates: [p.lon, p.lat] } } });
  map.addLayer({
    id: "punt",
    type: "circle",
    source: "punt",
    paint: { "circle-radius": 7, "circle-color": "#e64980", "circle-stroke-width": 2, "circle-stroke-color": "#ffffff" },
  });

  if (gekozen) toonKaart(map, gekozen, oud.kaarten[gekozen]);
  keuzeEl.addEventListener("change", () => toonKaart(map, keuzeEl.value, oud.kaarten[keuzeEl.value]));
  dekkingEl.addEventListener("input", () => {
    dekkingEl.setAttribute("aria-valuetext", `${dekkingEl.value} procent zichtbaar`);
    if (map.getLayer("oud")) map.setPaintProperty("oud", "raster-opacity", dekkingEl.value / 100);
  });
  document.querySelectorAll('input[name="basemap"]').forEach((r) =>
    r.addEventListener("change", () => {
      for (const id of Object.keys(ONDERGRONDEN)) map.setLayoutProperty(`base-${id}`, "visibility", r.value === id && r.checked ? "visible" : "none");
    })
  );
  statusEl.textContent = lijst.length
    ? `${lijst.length} oude ${lijst.length === 1 ? "kaart" : "kaarten"} over deze plek. Tegels kunnen een paar seconden laden.`
    : "Voor deze plek zijn (nog) geen oude kaarten gevonden.";
}

main().catch((e) => {
  statusEl.textContent = e.message;
  statusEl.classList.add("fout");
});
