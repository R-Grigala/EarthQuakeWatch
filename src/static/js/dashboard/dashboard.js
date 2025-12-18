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

  function showError(msg) {
    const box = $("errBox");
    if (!box) return;
    box.classList.remove("d-none");
    box.textContent = msg;
  }

  function clearError() {
    const box = $("errBox");
    if (!box) return;
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

    // 1 month
    if ($("c1m")) $("c1m").textContent = s.count_last_1m ?? 0;
    if ($("avg1m")) $("avg1m").textContent = fmt(s.avg_ml_last_1m);
    if ($("max1m")) $("max1m").textContent = fmt(s.max_ml_last_1m);

    // 6 months
    if ($("c6m")) $("c6m").textContent = s.count_last_6m ?? 0;
    if ($("avg6m")) $("avg6m").textContent = fmt(s.avg_ml_last_6m);
    if ($("max6m")) $("max6m").textContent = fmt(s.max_ml_last_6m);

    // 1 year
    if ($("c1y")) $("c1y").textContent = s.count_last_1y ?? 0;
    if ($("avg1y")) $("avg1y").textContent = fmt(s.avg_ml_last_1y);
    if ($("max1y")) $("max1y").textContent = fmt(s.max_ml_last_1y);

    if ($("lastUpdated")) $("lastUpdated").textContent = s.updated_utc ?? "—";
    if ($("totalEvents")) $("totalEvents").textContent = s.total_events ?? "—";

    const labels = [
      "Count 1m", "Avg 1m", "Max 1m",
      "Count 6m", "Avg 6m", "Max 6m",
      "Count 1y", "Avg 1y", "Max 1y",
    ];

    const values = [
      s.count_last_1m ?? 0,
      s.avg_ml_last_1m ?? 0,
      s.max_ml_last_1m ?? 0,

      s.count_last_6m ?? 0,
      s.avg_ml_last_6m ?? 0,
      s.max_ml_last_6m ?? 0,

      s.count_last_1y ?? 0,
      s.avg_ml_last_1y ?? 0,
      s.max_ml_last_1y ?? 0,
    ];

    const ctx = $("statsBar");
    if (ctx) {
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
    }

    if ($("statsText")) {
      $("statsText").textContent =
        `1m: count=${s.count_last_1m ?? 0}, avg=${fmt(s.avg_ml_last_1m)}, max=${fmt(s.max_ml_last_1m)} | ` +
        `6m: count=${s.count_last_6m ?? 0}, avg=${fmt(s.avg_ml_last_6m)}, max=${fmt(s.max_ml_last_6m)} | ` +
        `1y: count=${s.count_last_1y ?? 0}, avg=${fmt(s.avg_ml_last_1y)}, max=${fmt(s.max_ml_last_1y)}`;
    }
  }

  async function loadEvents() {
    const raw = await fetchJSON(EVENTS_URL);
    const events = Array.isArray(raw) ? raw : (raw.items || raw.data || raw.events || []);

    const normalized = events.map(e => ({
      time: e.origin_time || e.event_time || e.time,
      ml: e.ml,
      depth: e.depth_km ?? e.depth,
      lat: e.lat ?? e.latitude,
      lon: e.lon ?? e.longitude
    })).filter(x => x.time);

    const latest = [...normalized]
      .sort((a, b) => new Date(b.time) - new Date(a.time))
      .slice(0, 50);

    const tbody = $("eventsBody");
    if (tbody) {
      tbody.innerHTML = "";
      for (const e of latest) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="text-nowrap">${e.time ?? "—"}</td>
          <td>${e.ml ?? "—"}</td>
          <td>${e.depth ?? "—"}</td>
          <td>${e.lat ?? "—"}</td>
          <td>${e.lon ?? "—"}</td>
        `;
        tbody.appendChild(tr);
      }
    }

    const lastN = [...normalized]
      .sort((a, b) => new Date(a.time) - new Date(b.time))
      .slice(-80);

    const lineLabels = lastN.map(x => (x.time).slice(0, 10));
    const lineData = lastN.map(x => (x.ml === null || x.ml === undefined) ? null : Number(x.ml));

    const ctx = $("magLine");
    if (ctx) {
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
  }

  async function refreshAll() {
    clearError();
    await Promise.all([loadStats(), loadEvents()]);
  }

  if ($("statsUrlLabel")) $("statsUrlLabel").textContent = STATS_URL;
  if ($("eventsUrlLabel")) $("eventsUrlLabel").textContent = EVENTS_URL;

  refreshAll().catch(err => {
    console.error(err);
    showError(err.message || String(err));
  });

  setInterval(() => refreshAll().catch(console.error), 60000);
})();
