(async function () {
  "use strict";
  const SEV_COLOR = ["#B9B6AD", "#E3AE45", "#DE7A2C", "#C2352A", "#5E1020"];
  const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  const fmt = n => n.toLocaleString("en-US");
  const $ = id => document.getElementById(id);

  const res = await fetch("data/crashes.json");
  const { meta, cols, dict } = await res.json();
  const N = meta.n;

  if (meta.preview) $("preview-banner").hidden = false;

  // ---- rows ------------------------------------------------------------
  const rows = new Array(N);
  for (let i = 0; i < N; i++) {
    const d = cols.date[i];
    const siteKey = dict.site[cols.site[i]];
    const bar = siteKey.indexOf("|");
    rows[i] = {
      i, date: d, year: Math.floor(d / 10000), sev: cols.sev[i],
      lat: cols.lat[i], lon: cols.lon[i], time: cols.time[i],
      town: dict.town[cols.town[i]], site: cols.site[i],
      place: siteKey.slice(bar + 1), speed: cols.speed[i],
      control: dict.control[cols.control[i]], surface: dict.surface[cols.surface[i]],
      weather: dict.weather[cols.weather[i]], coord: dict.coord[cols.coord[i]],
    };
  }

  const first = new Date(meta.first + "T12:00:00"), last = new Date(meta.last + "T12:00:00");
  const years = [];
  for (let y = first.getFullYear(); y <= last.getFullYear(); y++) years.push(y);
  const lastYear = last.getFullYear();
  const partialLabel = last.getMonth() < 11 ? `through ${MONTHS[last.getMonth()]}` : "";

  // ---- header -------------------------------------------------------------
  const fatal = rows.filter(r => r.sev === 4).length;
  const serious = rows.filter(r => r.sev === 3).length;
  $("sign-sub").textContent =
    `Every crash reported to the state involving a bicycle, ${first.getFullYear()} to ${MONTHS[last.getMonth()]} ${lastYear}`;
  $("lede").innerHTML =
    `Police in Rhode Island reported <strong>${fmt(N)}</strong> crashes involving a bicycle from ` +
    `${MONTHS[first.getMonth()]} ${first.getFullYear()} through ${MONTHS[last.getMonth()]} ${lastYear}. ` +
    `In <strong>${fmt(fatal)}</strong> of them someone was killed, and in <strong>${fmt(serious)}</strong> more someone was seriously hurt.`;
  $("built").textContent = `Data built ${meta.built}.`;

  // ---- filters ------------------------------------------------------------
  const state = { y0: years[0], y1: lastYear, sev: new Set([0, 1, 2, 3, 4]), town: "" };
  // ?town=Providence, or <body data-town="..."> (set when folded into providenceontherecord.org)
  const askTown = new URLSearchParams(location.search).get("town") || document.body.dataset.town || "";
  for (const [id, sel] of [["y0", state.y0], ["y1", state.y1]]) {
    const el = $(id);
    for (const y of years) el.add(new Option(String(y), y, false, y === sel));
  }
  const sevCounts = [0, 0, 0, 0, 0];
  rows.forEach(r => { if (r.sev >= 0) sevCounts[r.sev]++; });
  const sevpick = $("sevpick");
  for (let s = 4; s >= 0; s--) {
    const lab = document.createElement("label");
    lab.innerHTML = `<input type="checkbox" value="${s}" checked><span class="dot" style="background:${SEV_COLOR[s]}"></span>${meta.severity_labels[s]}<span class="n">${fmt(sevCounts[s])}</span>`;
    sevpick.appendChild(lab);
  }
  const townCounts = new Map();
  rows.forEach(r => townCounts.set(r.town, (townCounts.get(r.town) || 0) + 1));
  [...townCounts].filter(([t]) => t).sort((a, b) => b[1] - a[1])
    .forEach(([t, n]) => $("town").add(new Option(`${t} (${fmt(n)})`, t)));
  if (askTown && townCounts.has(askTown)) { state.town = askTown; $("town").value = askTown; }

  $("filters").addEventListener("change", e => {
    const t = e.target;
    if (t.id === "y0") state.y0 = +t.value;
    else if (t.id === "y1") state.y1 = +t.value;
    else if (t.id === "town") state.town = t.value;
    else if (t.type === "checkbox") t.checked ? state.sev.add(+t.value) : state.sev.delete(+t.value);
    if (state.y0 > state.y1) {
      [state.y0, state.y1] = [state.y1, state.y0];
      $("y0").value = state.y0; $("y1").value = state.y1;
    }
    render(t.id === "town");
  });

  const pass = r => r.year >= state.y0 && r.year <= state.y1 &&
    (r.sev < 0 || state.sev.has(r.sev)) && (!state.town || r.town === state.town);

  // ---- map ----------------------------------------------------------------
  const map = new maplibregl.Map({
    container: "map",
    // OpenFreeMap: free OpenStreetMap vector tiles, no key (CARTO raster tiles
    // showed an "API key required" watermark in an Oct 6 2026 preview)
    style: "https://tiles.openfreemap.org/styles/positron",
    bounds: [[-71.91, 41.14], [-71.08, 42.03]],
    fitBoundsOptions: { padding: 12 },
    maxBounds: [[-72.6, 40.8], [-70.4, 42.4]],
    attributionControl: { compact: true },
    cooperativeGestures: window.matchMedia("(pointer: coarse)").matches,
  });
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-left");
  // redraw when the box changes size (the map drew in part of its box when the page laid out after it)
  new ResizeObserver(() => map.resize()).observe(document.getElementById("map"));

  const toGeo = list => ({
    type: "FeatureCollection",
    features: list.filter(r => r.lat != null).map(r => ({
      type: "Feature", id: r.i,
      geometry: { type: "Point", coordinates: [r.lon, r.lat] },
      properties: { i: r.i, sev: r.sev },
    })),
  });

  let mapReady = false;
  map.on("load", () => {
    map.addSource("crashes", { type: "geojson", data: toGeo(rows.filter(pass)) });
    map.addLayer({
      id: "crashes", type: "circle", source: "crashes",
      layout: { "circle-sort-key": ["get", "sev"] },
      paint: {
        "circle-color": ["match", ["get", "sev"], 0, SEV_COLOR[0], 1, SEV_COLOR[1], 2, SEV_COLOR[2], 3, SEV_COLOR[3], 4, SEV_COLOR[4], "#888"],
        "circle-radius": ["interpolate", ["linear"], ["zoom"],
          8, ["match", ["get", "sev"], 4, 4.5, 3, 3.5, 2.2],
          14, ["match", ["get", "sev"], 4, 10, 3, 8, 6]],
        "circle-stroke-color": "#fff",
        "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 8, 0.4, 14, 1.2],
        "circle-opacity": 0.9,
      },
    });
    mapReady = true;
    map.on("mouseenter", "crashes", () => map.getCanvas().style.cursor = "pointer");
    map.on("mouseleave", "crashes", () => map.getCanvas().style.cursor = "");
    map.on("click", "crashes", e => {
      const f = e.features.sort((a, b) => b.properties.sev - a.properties.sev)[0];
      const r = rows[f.properties.i];
      new maplibregl.Popup({ maxWidth: "300px" }).setLngLat(f.geometry.coordinates).setHTML(popup(r, e.features.length)).addTo(map);
    });
  });

  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  function when(r) {
    const y = Math.floor(r.date / 10000), m = Math.floor(r.date / 100) % 100, d = r.date % 100;
    let s = `${MONTHS[m - 1]} ${d}, ${y}`;
    if (r.time >= 0) {
      const h = Math.floor(r.time / 100), mi = r.time % 100;
      s += `, ${((h + 11) % 12) + 1}:${String(mi).padStart(2, "0")} ${h < 12 ? "a.m." : "p.m."}`;
    }
    return s;
  }
  const COORD = { ridot: "RIDOT's point", tiger: "Where the named streets meet (Census map)" };
  function popup(r, stacked) {
    const sev = r.sev >= 0 ? `<span class="pop-sev"><span class="dot" style="background:${SEV_COLOR[r.sev]}"></span>${meta.severity_labels[r.sev]}</span>` : "Injury not recorded";
    const rowsHtml = [
      ["Speed limit", r.speed ? `${r.speed} mph` : ""],
      ["Traffic control", r.control],
      ["Road surface", r.surface],
      ["Weather", r.weather],
      ["Placed by", COORD[r.coord] || r.coord],
    ].filter(([, v]) => v).map(([k, v]) => `<dt>${k}</dt><dd>${esc(v)}</dd>`).join("");
    const more = stacked > 1 ? `<p class="pop-when" style="margin:8px 0 0">${stacked - 1} more crash${stacked > 2 ? "es" : ""} at this spot. Zoom in to separate them.</p>` : "";
    return `<div class="pop"><div class="pop-when">${when(r)}</div><div class="pop-where">${esc(r.place || "Location not written")}<br><span style="font-weight:400">${esc(r.town)}</span></div>${sev}<dl>${rowsHtml}</dl>${more}</div>`;
  }

  // ---- year bars ----------------------------------------------------------
  function drawYears(list) {
    const by = new Map(years.map(y => [y, [0, 0, 0, 0, 0, 0]]));
    list.forEach(r => { const a = by.get(r.year); if (a) { a[5]++; if (r.sev >= 0) a[r.sev]++; } });
    const max = Math.max(1, ...[...by.values()].map(a => a[5]));
    const el = $("years"); el.innerHTML = "";
    for (const y of years) {
      const a = by.get(y);
      const partial = y === lastYear && partialLabel;
      el.insertAdjacentHTML("beforeend",
        `<div class="y">${y}</div><div class="bar" role="img" aria-label="${y}: ${a[5]} crashes, ${a[4]} fatal, ${a[3]} serious injury">` +
        [4, 3, 2, 1, 0].map(s => a[s] ? `<span style="width:${(a[s] / max) * 100}%;background:${SEV_COLOR[s]}"></span>` : "").join("") +
        `</div><div class="v">${fmt(a[5])}${partial ? `<span class="partial">*</span>` : ""}</div>`);
    }
    $("years-note").textContent = `Bars are split by the worst injury in each crash, fatal first.` +
      (partialLabel ? ` *${lastYear} runs ${partialLabel}.` : "");
  }

  // ---- clusters -----------------------------------------------------------
  function drawSites(list) {
    const g = new Map();
    list.forEach(r => {
      if (!r.place) return;
      let s = g.get(r.site);
      if (!s) g.set(r.site, s = { r, n: 0, bad: 0, pts: [] });
      s.n++; if (r.sev >= 3) s.bad++;
      if (r.lat != null) s.pts.push([r.lon, r.lat]);
    });
    const top = [...g.values()].filter(s => s.n > 1).sort((a, b) => b.n - a.n || b.bad - a.bad).slice(0, 10);
    const ol = $("sites"); ol.innerHTML = "";
    if (!top.length) { ol.innerHTML = `<li class="empty">No place has more than one crash within these filters.</li>`; return; }
    top.forEach((s, k) => {
      const li = document.createElement("li");
      const bad = s.bad ? `${s.bad} serious or fatal` : "none serious";
      li.innerHTML = `<button type="button"><span class="rank">${k + 1}</span><span class="where">${esc(s.r.place)}<span class="town">${esc(s.r.town)}</span></span><span class="num"><b>${s.n}</b>${bad}</span></button>`;
      li.querySelector("button").addEventListener("click", () => {
        if (!s.pts.length) return;
        const med = i => s.pts.map(p => p[i]).sort((a, b) => a - b)[Math.floor(s.pts.length / 2)];
        map.flyTo({ center: [med(0), med(1)], zoom: 16, essential: false });
        $("map").scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
      });
      ol.appendChild(li);
    });
  }

  // ---- render -------------------------------------------------------------
  function render(townChanged) {
    const list = rows.filter(pass);
    const drawn = list.filter(r => r.lat != null).length;
    $("count").innerHTML = `<strong>${fmt(list.length)}</strong>crash${list.length === 1 ? "" : "es"} shown` +
      (list.length - drawn ? `; ${fmt(list.length - drawn)} could not be placed on the map` : "");
    if (mapReady) map.getSource("crashes").setData(toGeo(list));
    // years chart ignores the year filter so the trend stays whole
    drawYears(rows.filter(r => (r.sev < 0 || state.sev.has(r.sev)) && (!state.town || r.town === state.town)));
    drawSites(list);
    if (townChanged && mapReady) {
      const pts = list.filter(r => r.lat != null);
      if (state.town && pts.length) {
        const b = new maplibregl.LngLatBounds();
        pts.forEach(r => b.extend([r.lon, r.lat]));
        map.fitBounds(b, { padding: 40, maxZoom: 14 });
      } else if (!state.town) map.fitBounds([[-71.91, 41.14], [-71.08, 42.03]], { padding: 12 });
    }
  }
  render(false);
  map.on("load", () => render(!!state.town));
})();
