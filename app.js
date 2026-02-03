function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const c = lines[i].split(",");
    if (c.length < 5) continue;
    rows.push({
      date: c[0],
      time: c[1],
      t: parseFloat(c[2]),
      h: parseFloat(c[3]),
      p: parseFloat(c[4])
    });
  }
  return rows;
}
function fmt(n, unit) {
  if (Number.isFinite(n)) return n.toFixed(2) + " " + unit;
  return "–";
}

async function load() {
  try {
    const url = "wetterdaten.csv?cb=" + Date.now(); // Cache-Buster
    const r = await fetch(url, { cache: "no-store" });
    if (!r.ok) throw new Error("HTTP " + r.status);

    const text = await r.text();
    const rows = parseCSV(text);
    if (rows.length === 0) return;

    const last = rows[rows.length - 1];

    document.getElementById("temp").textContent = fmt(last.t, "°C");
    document.getElementById("hum").textContent  = fmt(last.h, "%");
    document.getElementById("pres").textContent = fmt(last.p, "hPa");
    document.getElementById("ts").textContent   = last.date + " " + last.time;
  } catch (e) {
    // optional: still bleiben oder in Konsole loggen
    console.log("Load error:", e);
  }
}

load();
setInterval(load, 60000); // alle 60s aktualisieren
