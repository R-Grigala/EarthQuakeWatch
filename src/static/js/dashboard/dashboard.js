(() => {
  const cfg = window.DASH_CONFIG || {};
  const STATS_URL = cfg.statsUrl || "/api/stats";
  const EVENTS_URL = cfg.eventsUrl || "/api/events";
  const API_KEY = cfg.apiKey || "";

  const $ = (id) => document.getElementById(id);

  let statsChart = null;
  let magChart = null;

  function fmt(x, digits = 2) {
    if (x === null || x === undefined) return "—";
    const n = Number(x);
    if (Number.isNaN(n)) return "—";
    return n.toFixed(digits);
  }

  function toUtcLabel(isoString) {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toISOString().replace("T", " ").slice(0, 19);
  }

  function showError(msg) {
    const box = $("errBox");
    box.classList.remove("d-none");
    box.textContent = msg;
  }

  function clearError() {
    const box = $("errBox");
    box.classList.add("d-none");
    box.textContent = "";
  }

  async function fetchJSON(url) {
    const res = await fetch(url, {
      headers: {
        "Accept": "application/json",
        ...(API_KEY ? { "X-API-Key": API_KEY } : {})
      }
    });

    const text = await res.text();

    if (!res.ok) {
      throw new Error(`${url} -> ${res.status}\n${text.slice(0, 500)}`);
    }

    try {
      return JSON.parse(text);
    } catch {
      throw new Error(`${url} returned non-JSON:\n${text.slice(0, 500)}`);
    }
  }

  async function loadStats() {
    const s = await fetchJSON(STATS_URL);

    $("c24").textContent = s.count_last_24h ?? 0;
    $("avg24").textContent = fmt(s.avg_ml_last_24h);
    $("max24").textContent = fmt(s.max_ml_last_24h);

    $("c7").textContent = s.count_last_7d ?? 0;
    $("avg7").textContent = fmt(s.avg_ml_last_7d);

    $("c1y").textContent = s.count_last_1y ?? 0;
    $("avg1y").textContent = fmt(s.avg_ml_last_1y);
    $("max1y").textContent = fmt(s.max_ml_last_1y);
    $("lastUpdated").textContent = s.updated_utc ?? "—";
    $("totalEvents").textContent = s.total_events ?? "—";

    const labels = [
      "Count 24h", "Avg 24h", "Max 24h",
      "Count 7d", "Avg 7d",
      "Count 1y", "Avg 1y", "Max 1y",
    ];
    const values = [
      s.count_last_24h ?? 0,
      s.avg_ml_last_24h ?? 0,
      s.max_ml_last_24h ?? 0,
      s.count_last_7d ?? 0,
      s.avg_ml_last_7d ?? 0,
      s.count_last_1y ?? 0,
      s.avg_ml_last_1y ?? 0,
      s.max_ml_last_1y ?? 0,
    ];

    const ctx = $("statsBar");
    if (statsChart) statsChart.destroy();
    statsChart = new Chart(ctx, {
      type: "bar",
      data: { labels, datasets: [{ label: "Stats", data: values }] },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      }
    });

    $("statsText").textContent =
      `24h: count=${s.count_last_24h ?? 0}, avg=${fmt(s.avg_ml_last_24h)}, max=${fmt(s.max_ml_last_24h)} | ` +
      `7d: count=${s.count_last_7d ?? 0}, avg=${fmt(s.avg_ml_last_7d)} | ` +
      `1y: count=${s.count_last_1y ?? 0}, avg=${fmt(s.avg_ml_last_1y)}, max=${fmt(s.max_ml_last_1y)}`;
  }

  async function loadEvents() {
    const raw = await fetchJSON(EVENTS_URL);
    const events = Array.isArray(raw) ? raw : (raw.items || raw.data || raw.events || []);

    const normalized = events.map(e => ({
      time: e.origin_time || e.event_time || e.time,
      ml: e.ml,
      depth: e.depth_km ?? e.depth,
      lat: e.lat ?? e.latitude,
      lon: e.lon ?? e.longitude,
      region: e.region ?? e.place ?? ""
    })).filter(x => x.time);

    // Table: latest 50 (desc)
    const latest = [...normalized]
      .sort((a, b) => new Date(b.time) - new Date(a.time))
      .slice(0, 50);

    const tbody = $("eventsBody");
    tbody.innerHTML = "";
    for (const e of latest) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="text-nowrap">${toUtcLabel(e.time)}</td>
        <td>${e.ml ?? "—"}</td>
        <td>${e.depth ?? "—"}</td>
        <td>${e.lat ?? "—"}</td>
        <td>${e.lon ?? "—"}</td>
        <td>${e.region || "—"}</td>
      `;
      tbody.appendChild(tr);
    }

    // Line chart: last N points ascending
    const lastN = [...normalized]
      .sort((a, b) => new Date(a.time) - new Date(b.time))
      .slice(-80);

    const lineLabels = lastN.map(x => toUtcLabel(x.time).slice(0, 11));
    const lineData = lastN.map(x => (x.ml === null || x.ml === undefined) ? null : Number(x.ml));

    const ctx = $("magLine");
    if (magChart) magChart.destroy();
    magChart = new Chart(ctx, {
      type: "line",
      data: { labels: lineLabels, datasets: [{ label: "ML", data: lineData, spanGaps: true }] },
      options: {
        responsive: true,
        plugins: { legend: { display: true } },
        scales: { y: { beginAtZero: false } }
      }
    });
  }

  async function refreshAll() {
    clearError();
    await Promise.all([loadStats(), loadEvents()]);
  }

  // Labels on page
  if ($("statsUrlLabel")) $("statsUrlLabel").textContent = STATS_URL;
  if ($("eventsUrlLabel")) $("eventsUrlLabel").textContent = EVENTS_URL;

  refreshAll().catch(err => {
    console.error(err);
    showError(err.message || String(err));
  });

  setInterval(() => refreshAll().catch(console.error), 60000);
})();
