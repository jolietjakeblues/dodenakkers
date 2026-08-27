// Dodenakkers Zuid-Holland - kandidaat-begraafplaatsen (2026-08-27,
// EXPERIMENTEEL, wens van Joop). Toont data/generated/kandidaat_begraafplaatsen.json
// (zie scripts/compute_kandidaat_begraafplaatsen.py) als tabel. Geen
// berekeningen hier, alleen weergave -- zelfde scheiding als statistieken.js.

const statusEl = document.getElementById("stats-status");

function el(tag, props = {}, children = []) {
  const node = document.createElement(tag);
  Object.entries(props).forEach(([k, v]) => {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k === "html") node.innerHTML = v;
    else node.setAttribute(k, v);
  });
  children.forEach((c) => node.appendChild(c));
  return node;
}

function fmt(n) {
  if (n === null || n === undefined) return "-";
  return new Intl.NumberFormat("nl-NL").format(n);
}

// Permalink naar de hoofdkaart, gecentreerd op de kandidaat, met de
// archeologische-onderzoeksgebieden-laag alvast aangevinkt (zie
// LAYER_TOGGLE_CODES in app.js -- "arch" is dezelfde code).
function mapLink(kandidaat) {
  const params = new URLSearchParams({
    lon: kandidaat.lon.toFixed(5),
    lat: kandidaat.lat.toFixed(5),
    z: "16.00",
    lyr: "terrein,ingang,gezicht,arch",
  });
  return `index.html?${params.toString()}`;
}

// Compacte weergave van bebouwing_bij_punt() uit
// scripts/compute_kandidaat_begraafplaatsen.py: aantal BAG-gebouwen binnen
// 30m van de kandidaat, plus bouwjaar-range. Geen check gedraaid (bv. lokaal
// met --no-kadaster-check) -> "-"; check mislukt (endpoint niet bereikbaar)
// -> "?".
function fmtBebouwing(b) {
  if (!b) return "-";
  if (b.fout) return "? (kadaster-check mislukt)";
  const n = b.aantal_gebouwen_binnen_30m;
  if (n === 0) return "0 (open terrein)";
  const oud = b.oudste_bouwjaar_nabij;
  const nieuw = b.nieuwste_bouwjaar_nabij;
  if (oud == null) return `${fmt(n)}`;
  return oud === nieuw ? `${fmt(n)} (${oud})` : `${fmt(n)} (${oud}-${nieuw})`;
}

// Zelfde idee, maar voor een rijksmonument (klooster/synagoge) i.p.v. een
// archeologisch onderzoeksgebied: rijksmonumentenlaag aan i.p.v. "arch", en
// "monalle" erbij zodat het punt zichtbaar is ongeacht de rm-afstandsslider
// op de hoofdkaart (deze kandidaten liggen vaak juist ver van een bekende
// begraafplaats, dus zouden anders weggefilterd worden).
function mapLinkRijksmonument(kandidaat) {
  const params = new URLSearchParams({
    lon: kandidaat.lon.toFixed(5),
    lat: kandidaat.lat.toFixed(5),
    z: "16.00",
    lyr: "terrein,ingang,gezicht,mon,monalle",
  });
  return `index.html?${params.toString()}`;
}

function renderRijksmonumentSectie(containerId, titel, data, bebouwingCheck) {
  const container = document.getElementById(containerId);
  const section = el("div", { class: "stats-section" });
  section.appendChild(el("h2", { text: `${titel} (${data.kandidaten.length})` }));
  section.appendChild(
    el("div", { class: "warning-box" }, [
      el("p", { text: data.waarschuwing }),
    ])
  );
  if (data.aantal_buiten_zuid_holland_bbox_rand) {
    section.appendChild(
      el("p", {
        class: "hint",
        text: `${fmt(data.aantal_buiten_zuid_holland_bbox_rand)} rijksmonument(en) genegeerd (bbox-rand-effect, buiten Zuid-Holland).`,
      })
    );
  }
  if (bebouwingCheck && data.kandidaten.some((k) => k.bebouwing)) {
    section.appendChild(el("p", { class: "hint", text: bebouwingCheck.waarschuwing }));
  }

  const wrap = el("div", { class: "stats-table-wrap" });
  const t = el("table", { class: "stats-table kandidaten-table" });
  t.appendChild(
    el("thead", {}, [
      el("tr", {}, [
        el("th", { text: "Naam" }),
        el("th", { text: "Type" }),
        el("th", { text: "Gemeente" }),
        el("th", { text: "Afstand" }),
        el("th", { text: "Dichtstbijzijnde bekende bp" }),
        el("th", { text: "Rijksmonumenten in cluster" }),
        el("th", { text: bebouwingCheck ? `Gebouwen binnen ${bebouwingCheck.radius_m}m` : "Bebouwing" }),
        el("th", { text: "Links" }),
      ]),
    ])
  );
  const tbody = el("tbody");
  for (const k of data.kandidaten) {
    const links = el("td", {}, [
      el("a", { href: k.monumentenregister_url, target: "_blank", rel: "noopener", text: "bron" }),
      el("span", { text: " · " }),
      el("a", { href: mapLinkRijksmonument(k), text: "kaart" }),
    ]);
    tbody.appendChild(
      el("tr", {}, [
        el("td", { text: k.naam || "(geen naam)" }),
        el("td", { text: k.functie }),
        el("td", { text: k.gemeente }),
        el("td", { text: `${fmt(k.afstand_tot_bekende_bp_m)} m` }),
        el("td", { text: k.dichtstbijzijnde_bp }),
        el("td", { text: fmt(k.aantal_rijksmonumenten_in_cluster) }),
        el("td", { text: fmtBebouwing(k.bebouwing) }),
        links,
      ])
    );
  }
  t.appendChild(tbody);
  wrap.appendChild(t);
  section.appendChild(wrap);
  container.appendChild(section);
}

async function main() {
  const res = await fetch("../data/generated/kandidaat_begraafplaatsen.json");
  if (!res.ok) throw new Error(`kandidaat_begraafplaatsen.json: HTTP ${res.status}`);
  const d = await res.json();

  const concreet = d.kandidaten.filter((c) => c.zekerheid === "concreet genoemd").length;
  const ver = d.kandidaten.filter((c) => c.afstand_tot_bekende_bp_m > 250).length;

  const samenvatting = document.getElementById("kandidaten-samenvatting");
  samenvatting.appendChild(
    el("div", { class: "stats-section" }, [
      el("h2", { text: "Samenvatting" }),
      el("dl", { class: "stats-kv" }, [
        el("dt", { text: "Onderzoeksgebieden doorzocht" }), el("dd", { text: fmt(d.aantal_onderzoeksgebieden_doorzocht) }),
        el("dt", { text: "Tekstuele treffers (grafterm gevonden)" }), el("dd", { text: fmt(d.aantal_treffers) }),
        el("dt", { text: "...waarvan buiten Zuid-Holland (bbox-rand-effect, genegeerd)" }), el("dd", { text: fmt(d.aantal_buiten_zuid_holland_bbox_rand) }),
        el("dt", { text: "Kandidaten in Zuid-Holland" }), el("dd", { text: fmt(d.kandidaten.length) }),
        el("dt", { text: "...concreet genoemd (geen hedge-taal)" }), el("dd", { text: fmt(concreet) }),
        el("dt", { text: "...verder dan 250m van een bekende begraafplaats" }), el("dd", { text: fmt(ver) }),
      ]),
    ])
  );

  const tableContainer = document.getElementById("kandidaten-tabel");
  const section = el("div", { class: "stats-section" });
  section.appendChild(el("h2", { text: `Alle ${d.kandidaten.length} kandidaten` }));
  section.appendChild(
    el("p", { class: "hint", text: "Gesorteerd: concreet genoemd eerst, dan verste afstand tot een bekende begraafplaats eerst." })
  );

  const wrap = el("div", { class: "stats-table-wrap" });
  const t = el("table", { class: "stats-table kandidaten-table" });
  t.appendChild(
    el("thead", {}, [
      el("tr", {}, [
        el("th", { text: "Zekerheid" }),
        el("th", { text: "Afstand" }),
        el("th", { text: "Gemeente" }),
        el("th", { text: "Term" }),
        el("th", { text: "Fragment" }),
        el("th", { text: "Dichtstbijzijnde bekende bp" }),
        el("th", { text: "Links" }),
      ]),
    ])
  );
  const tbody = el("tbody");
  for (const c of d.kandidaten) {
    const zekerheidBadge = el("span", {
      class: c.zekerheid === "concreet genoemd" ? "badge badge-concreet" : "badge badge-onzeker",
      text: c.zekerheid,
    });
    const links = el("td", {}, [
      el("a", { href: c.cho_uri, target: "_blank", rel: "noopener", text: "bron" }),
      el("span", { text: " · " }),
      el("a", { href: mapLink(c), text: "kaart" }),
    ]);
    tbody.appendChild(
      el("tr", {}, [
        el("td", {}, [zekerheidBadge]),
        el("td", { text: `${fmt(c.afstand_tot_bekende_bp_m)} m` }),
        el("td", { text: c.gemeente }),
        el("td", { text: c.gevonden_term }),
        el("td", { class: "fragment-cell", text: c.fragment }),
        el("td", { text: c.dichtstbijzijnde_bp }),
        links,
      ])
    );
  }
  t.appendChild(tbody);
  wrap.appendChild(t);
  section.appendChild(wrap);
  tableContainer.appendChild(section);

  renderRijksmonumentSectie("kandidaten-kloosters", "Kloosters", d.kloosters, d.bebouwing_check);
  renderRijksmonumentSectie("kandidaten-synagoges", "Synagoges", d.synagoges, d.bebouwing_check);
  renderRijksmonumentSectie("kandidaten-kapellen", "Kapellen", d.kapellen, d.bebouwing_check);

  statusEl.textContent = "";
}

main().catch((err) => {
  console.error(err);
  statusEl.textContent = `Fout bij laden: ${err.message}`;
  statusEl.style.color = "#e03131";
});
