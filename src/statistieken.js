// Dodenakkers Zuid-Holland - statistiekenpagina (2026-08-26, wens van Joop).
//
// Leest het vooraf berekende data/generated/statistieken.json (zie
// scripts/compute_statistics.py) en rendert het als losse secties met
// key/value-blokken en tabellen. Geen berekeningen hier -- alleen weergave,
// dezelfde scheiding tussen scripts/ (rekenen) en src/ (tonen) als de rest
// van de site.

const statusEl = document.getElementById("stats-status");

function el(tag, props = {}, children = []) {
  const node = document.createElement(tag);
  Object.entries(props).forEach(([k, v]) => {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else node.setAttribute(k, v);
  });
  children.forEach((c) => node.appendChild(c));
  return node;
}

function fmt(n) {
  if (n === null || n === undefined) return "-";
  return new Intl.NumberFormat("nl-NL").format(n);
}

function renderSection(container, title, note, bodyNodes) {
  const section = el("div", { class: "stats-section" });
  section.appendChild(el("h2", { text: title }));
  if (note) section.appendChild(el("p", { class: "hint" , text: note }));
  bodyNodes.forEach((n) => section.appendChild(n));
  container.appendChild(section);
}

function kv(pairs) {
  const dl = el("dl", { class: "stats-kv" });
  for (const [k, v] of pairs) {
    if (v === null || v === undefined) continue;
    dl.appendChild(el("dt", { text: k }));
    dl.appendChild(el("dd", { text: v }));
  }
  return dl;
}

function table(headers, rows) {
  const wrap = el("div", { class: "stats-table-wrap" });
  const t = el("table", { class: "stats-table" });
  const thead = el("tr", {}, headers.map((h) => el("th", { text: h })));
  t.appendChild(el("thead", {}, [thead]));
  const tbody = el("tbody");
  rows.forEach((row) => {
    tbody.appendChild(el("tr", {}, row.map((cell) => el("td", { text: cell }))));
  });
  t.appendChild(tbody);
  wrap.appendChild(t);
  return wrap;
}

function plaatsNaam(p) {
  return p || "(onbekend)";
}

async function main() {
  const res = await fetch("../data/generated/statistieken.json");
  if (!res.ok) throw new Error(`statistieken.json: HTTP ${res.status}`);
  const s = await res.json();

  // --- Basis ---
  renderSection(
    document.getElementById("stats-basis"),
    "Basisstatistieken",
    null,
    [
      kv([
        ["Totaal aantal begraafplaatsen", fmt(s.basis.totaal)],
        ["Totale oppervlakte", `${fmt(s.basis.totaal_ha)} ha`],
        ["Niet-geruimd", fmt(s.basis.niet_geruimd)],
        ["Geruimd", `${fmt(s.basis.geruimd)} (${s.basis.geruimd_pct}%)`],
        ["Statusconflicten", fmt(s.basis.statusconflict)],
        ["Gemiddelde oppervlakte", `${fmt(s.basis.gemiddelde_m2)} m²`],
        ["Mediaan oppervlakte", `${fmt(s.basis.mediaan_m2)} m²`],
        ["Grootste begraafplaats", `${s.basis.grootste.naam}, ${plaatsNaam(s.basis.grootste.plaats)} (${fmt(s.basis.grootste.m2)} m² / ${s.basis.grootste.ha} ha)`],
        ["Kleinste begraafplaats", `${s.basis.kleinste.naam}, ${plaatsNaam(s.basis.kleinste.plaats)} (${fmt(s.basis.kleinste.m2)} m²)`],
      ]),
    ]
  );

  // --- Per plaats / per gemeente (zelfde tabelvorm, dus 1 helper -- zie
  // scripts/compute_statistics.py voor waarom er nu 2 groeperingen zijn:
  // de bron heeft alleen "plaats", "gemeente" komt uit een aparte spatial
  // join tegen echte PDOK-gemeentegrenzen) ---
  function groupNodes(group, label) {
    const key = label === "Plaats" ? "plaats" : "gemeente";
    const naam = (v) => v || "(onbekend)";
    const nodes = [
      el("h3", { text: "Meeste begraafplaatsen" }),
      table(
        [label, "Aantal", "Waarvan geruimd", "Totale oppervlakte"],
        group.meeste_begraafplaatsen.map((r) => [naam(r[key]), fmt(r.aantal), fmt(r.geruimd), `${fmt(r.totaal_m2)} m²`])
      ),
      el("h3", { text: "Meeste geruimde begraafplaatsen" }),
      table(
        [label, "Geruimd", `Totaal in ${label.toLowerCase()}`],
        group.meeste_geruimd.map((r) => [naam(r[key]), fmt(r.geruimd), fmt(r.aantal)])
      ),
      el("h3", { text: "Grootste totale oppervlakte" }),
      table(
        [label, "Aantal", "Totale oppervlakte"],
        group.grootste_totale_oppervlakte.map((r) => [naam(r[key]), fmt(r.aantal), `${fmt(r.totaal_m2)} m²`])
      ),
    ];
    if (group.volledig_geruimd.length) {
      nodes.push(
        el("h3", { text: `${label === "Plaats" ? "Plaatsen" : "Gemeenten"} volledig geruimd (2+ begraafplaatsen)` }),
        table(
          [label, "Aantal begraafplaatsen"],
          group.volledig_geruimd.map((r) => [naam(r[key]), fmt(r.aantal)])
        )
      );
    } else {
      nodes.push(
        el("p", { class: "hint", text: `Geen enkele ${label.toLowerCase()} met 2 of meer begraafplaatsen heeft ze allemaal geruimd.` })
      );
    }
    return nodes;
  }
  renderSection(document.getElementById("stats-per-plaats"), "Per plaats", "\"Plaats\" is dorp/stad, zoals in de bron -- zie hiernaast voor de gemeente-indeling.", groupNodes(s.per_plaats, "Plaats"));
  renderSection(
    document.getElementById("stats-per-gemeente"),
    "Per gemeente",
    "Echte gemeentegrenzen (PDOK bestuurlijkegebieden), niet in de bron zelf -- via een spatial join toegevoegd.",
    groupNodes(s.per_gemeente, "Gemeente")
  );

  // --- Beschermd gezicht ---
  renderSection(
    document.getElementById("stats-gezicht"),
    "Beschermde stads- en dorpsgezichten",
    null,
    [
      kv([
        ["Begraafplaatsen binnen/overlappend een beschermd gezicht", `${fmt(s.beschermd_gezicht.totaal)} (${s.beschermd_gezicht.pct}%)`],
      ]),
      el("h3", { text: "Meeste begraafplaatsen in een beschermd gezicht (per plaats)" }),
      table(
        ["Plaats", "Aantal"],
        s.beschermd_gezicht.top_plaatsen.map((r) => [plaatsNaam(r.plaats), fmt(r.aantal)])
      ),
      el("h3", { text: "Meeste begraafplaatsen in een beschermd gezicht (per gemeente)" }),
      table(
        ["Gemeente", "Aantal"],
        s.beschermd_gezicht.top_gemeenten.map((r) => [plaatsNaam(r.gemeente), fmt(r.aantal)])
      ),
    ]
  );

  // --- Rijksmonumenten nabij ---
  renderSection(
    document.getElementById("stats-rijksmonumenten"),
    "Rijksmonumenten in de buurt",
    "Relaties tot 250m worden bewaard (zie de schuifregelaar op de kaart); hieronder steeds binnen 100m tenzij anders vermeld.",
    [
      kv([
        ["Gemiddeld aantal rijksmonumenten binnen 100m", s.rijksmonumenten.gemiddeld_binnen_100m],
        ["Begraafplaatsen zonder rijksmonument binnen 250m", fmt(s.rijksmonumenten.zonder_rijksmonument_binnen_250m)],
      ]),
      el("h3", { text: "Meeste rijksmonumenten binnen 100m" }),
      table(
        ["Begraafplaats", "Plaats", "Aantal binnen 100m"],
        s.rijksmonumenten.meeste_binnen_100m.map((r) => [r.naam, plaatsNaam(r.plaats), fmt(r.aantal_100m)])
      ),
      el("h3", { text: "Meest voorkomende functie van rijksmonumenten binnen 100m" }),
      table(
        ["Oorspronkelijke functie", "Aantal"],
        s.rijksmonumenten.top_functies_nabij_100m.map((r) => [r.functie, fmt(r.aantal)])
      ),
    ]
  );

  // --- Begraafplaats is zelf rijksmonument ---
  renderSection(
    document.getElementById("stats-zelf-rijksmonument"),
    "Begraafplaatsen die zelf een rijksmonument zijn",
    "Op het terrein of grenzend eraan staat een rijksmonument met een begraafplaats-gerelateerde functie (begraafplaats zelf, hek, aula, ...).",
    [
      kv([["Aantal", fmt(s.begraafplaats_als_rijksmonument.aantal)]]),
      table(
        ["Begraafplaats", "Plaats", "Rijksmonument-functie"],
        s.begraafplaats_als_rijksmonument.lijst.map((r) => [r.naam, plaatsNaam(r.plaats), r.functie])
      ),
    ]
  );

  // --- Molen ---
  if (s.molen) {
    renderSection(
      document.getElementById("stats-molen"),
      "Nabijheid tot een molen",
      `${fmt(s.molen.aantal_in_categorie)} rijksmonumenten in de bbox zijn een molen (molenaarswoningen niet meegeteld).`,
      [
        kv([
          ["Binnen 250m van een molen", fmt(s.molen.binnen["250"])],
          ["Binnen 500m van een molen", fmt(s.molen.binnen["500"])],
          ["Binnen 1000m van een molen", fmt(s.molen.binnen["1000"])],
          ["Verste begraafplaats van een molen", `${s.molen.verste.naam}, ${plaatsNaam(s.molen.verste.plaats)} (${fmt(s.molen.verste.distance_m)} m)`],
        ]),
        el("h3", { text: "Dichtstbij een molen" }),
        table(
          ["Begraafplaats", "Plaats", "Afstand tot molen"],
          s.molen.dichtstbij.map((r) => [r.naam, plaatsNaam(r.plaats), `${fmt(r.distance_m)} m`])
        ),
      ]
    );
  }

  // --- Kasteel ---
  if (s.kasteel) {
    renderSection(
      document.getElementById("stats-kasteel"),
      "Nabijheid tot een kasteel of buitenplaats",
      `${fmt(s.kasteel.aantal_in_categorie)} rijksmonumenten in de bbox zijn een kasteel/buitenplaats.`,
      [
        kv([
          ["Binnen 250m", fmt(s.kasteel.binnen["250"])],
          ["Binnen 500m", fmt(s.kasteel.binnen["500"])],
          ["Binnen 1000m", fmt(s.kasteel.binnen["1000"])],
        ]),
        el("h3", { text: "Dichtstbij een kasteel/buitenplaats" }),
        table(
          ["Begraafplaats", "Plaats", "Afstand"],
          s.kasteel.dichtstbij.map((r) => [r.naam, plaatsNaam(r.plaats), `${fmt(r.distance_m)} m`])
        ),
      ]
    );
  }

  // --- Archeologie ---
  renderSection(
    document.getElementById("stats-archeologie"),
    "Archeologische rijksmonumenten",
    null,
    [
      kv([["Begraafplaatsen die een archeologisch rijksmonument overlappen", fmt(s.archeologie.overlapt_aantal)]]),
      el("h3", { text: "Dichtstbij een archeologisch rijksmonument (zonder overlap)" }),
      table(
        ["Begraafplaats", "Plaats", "Afstand"],
        s.archeologie.dichtstbij.map((r) => [r.naam, plaatsNaam(r.plaats), `${fmt(r.distance_m)} m`])
      ),
    ]
  );

  // --- Ingangen ---
  renderSection(
    document.getElementById("stats-ingangen"),
    "Ingangen",
    null,
    [
      kv([
        ["Gedeelde ingang (begraafplaatsen)", fmt(s.ingangen.gedeeld_aantal)],
        ["Gemiddelde afstand ingang tot terrein", `${fmt(s.ingangen.gemiddelde_afstand_m)} m`],
        ["Verste ingang van het eigen terrein", `${s.ingangen.verste.naam}, ${plaatsNaam(s.ingangen.verste.plaats)} (${fmt(s.ingangen.verste.afstand_m)} m)`],
      ]),
    ]
  );

  statusEl.textContent = "";
}

main().catch((err) => {
  console.error(err);
  statusEl.textContent = `Fout bij laden: ${err.message}`;
  statusEl.style.color = "#e03131";
});
