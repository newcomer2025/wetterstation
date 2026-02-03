#!/usr/bin/env python3
import csv
import os
from datetime import datetime
from flask import Flask, render_template_string, send_file

app = Flask(__name__)

@app.after_request
def add_no_cache_headers(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

CSV_FILE = "/home/genie/wetterstation/wetterdaten.csv"

HTML = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="60">
  <title>Wetterstation</title>
</head>
<body>
<h1>Wetterstation</h1>
<p>Stand: {{ t }}</p>

{% if latest %}
<ul>
  <li>Temperatur: {{ latest[2] }} °C</li>
  <li>Feuchte: {{ latest[3] }} %</li>
  <li>Druck: {{ latest[4] }} hPa</li>
</ul>
{% else %}
<p>Keine Daten vorhanden.</p>
{% endif %}

<p><a href="/download">CSV herunterladen</a></p>
</body>
</html>
"""

@app.route("/")
def index():
    latest = None
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, "r") as f:
                rows = list(csv.reader(f))
                if len(rows) > 1:
                    latest = rows[-1]  # letzte Zeile = neueste Messung
        except Exception:
            latest = None

    return render_template_string(
        HTML,
        latest=latest,
        t=datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
    )

@app.route("/download")
def download():
    path = os.path.abspath(CSV_FILE)
    if not os.path.exists(path):
        return ("Keine Daten verfügbar", 404)
    return send_file(path, mimetype="text/csv", as_attachment=True, download_name="wetterdaten.csv")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

