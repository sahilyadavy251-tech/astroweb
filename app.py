"""Flask web app for the Jyotish Studio astrology engine."""
from __future__ import annotations

import json
import os
from datetime import datetime

from flask import Flask, jsonify, request, render_template, send_from_directory

from engine import chart as chart_engine
from engine import tarot as tarot_engine

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder="static", template_folder="templates")

with open(os.path.join(BASE, "data", "cities.json"), encoding="utf-8") as f:
    CITIES = json.load(f)

# warm the ephemeris at startup so the first chart request is fast
try:
    from engine import ephemeris as _eph
    _eph._load()
except Exception:
    pass


def sanitize(obj):
    """Recursively convert numpy scalars / arrays to plain Python types."""
    try:
        import numpy as np
    except Exception:
        np = None
    if isinstance(obj, dict):
        return {str(k): sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize(v) for v in obj]
    if np is not None:
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return [sanitize(v) for v in obj.tolist()]
    return obj


@app.route("/")
def index():
    return render_template("index.html")


def _strip_accents(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c)).lower()


def _city_brief(c):
    return {"name": c["name"], "region": c.get("region", ""),
            "lat": c["lat"], "lon": c["lon"], "tz": c["tz"]}


@app.route("/api/cities")
def api_cities():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify([_city_brief(c) for c in CITIES if c.get("pri")][:40])
    qn = _strip_accents(q)
    exact, starts, word, contains = [], [], [], []
    for c in CITIES:
        a = c.get("a") or _strip_accents(c["name"])
        if a == qn:
            exact.append(c)
        elif a.startswith(qn):
            starts.append(c)
        elif any(w.startswith(qn) for w in a.replace(",", " ").split()):
            word.append(c)
        elif qn in a:
            contains.append(c)
    def rank(lst):
        return sorted(lst, key=lambda c: (-c.get("pri", 0), c.get("a", "")))
    res = exact + rank(starts) + rank(word) + rank(contains)
    return jsonify([_city_brief(c) for c in res[:40]])


@app.route("/api/chart", methods=["POST"])
def api_chart():
    data = request.get_json(force=True, silent=True) or {}
    try:
        name = data.get("name", "")
        year = int(data["year"]); month = int(data["month"]); day = int(data["day"])
        hour = int(data.get("hour", 0)); minute = int(data.get("minute", 0))
        second = int(data.get("second", 0))
        tz = float(data.get("tz_offset", 5.5))
        lat = float(data["lat"]); lon = float(data["lon"])
        place = data.get("place", "")
        now = datetime.now()
        result = chart_engine.build_chart(
            name, year, month, day, hour, minute, second,
            tz, lat, lon, place, now=now)
        return jsonify(sanitize(result))
    except KeyError as e:
        return jsonify({"error": f"missing field: {e}"}), 400
    except Exception as e:  # noqa
        app.logger.exception("chart error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/matching", methods=["POST"])
def api_matching():
    """Ashtakoot Guna Milan between two birth charts."""
    try:
        d = request.get_json(force=True) or {}
        a, b = d.get("person1") or {}, d.get("person2") or {}
        ca = chart_engine.build_chart(a.get("name", ""), int(a["year"]), int(a["month"]), int(a["day"]),
                            int(a.get("hour", 0)), int(a.get("minute", 0)), 0,
                            float(a.get("tz_offset", 5.5)), float(a.get("lat", 0)),
                            float(a.get("lon", 0)), a.get("place", ""))
        cb = chart_engine.build_chart(b.get("name", ""), int(b["year"]), int(b["month"]), int(b["day"]),
                            int(b.get("hour", 0)), int(b.get("minute", 0)), 0,
                            float(b.get("tz_offset", 5.5)), float(b.get("lat", 0)),
                            float(b.get("lon", 0)), b.get("place", ""))
        from engine import extras as X
        res = X.gun_milan(ca, cb)
        res["name_a"] = a.get("name", "")
        res["name_b"] = b.get("name", "")
        res["details_a"] = {"date": ca["meta"].get("local_datetime"), "place": a.get("place", "")}
        res["details_b"] = {"date": cb["meta"].get("local_datetime"), "place": b.get("place", "")}
        return jsonify(res)
    except Exception as e:                       # noqa: BLE001
        return jsonify({"error": str(e)}), 400


@app.route("/matching")
def matching_page():
    return render_template("matching.html")


@app.route("/kundli")
def kundli():
    """Dedicated result page (opened after the birth details are submitted)."""
    return render_template("kundli.html")


@app.route("/nadi-bnn")
def nadi_bnn():
    """Standalone Nadi (BNN) + slow-planet progression tool."""
    return send_from_directory(os.path.join(BASE, "static"), "nadi-bnn.html")


@app.route("/api/tarot")
def api_tarot():
    spread = request.args.get("spread", "three")
    seed = request.args.get("seed")
    seed = int(seed) if seed and seed.isdigit() else None
    return jsonify(tarot_engine.draw(spread, seed))


@app.route("/api/transit", methods=["POST"])
def api_transit():
    data = request.get_json(force=True, silent=True) or {}
    try:
        from datetime import datetime as _dt
        today = _dt.now()
        year = int(data.get("year", today.year)); month = int(data.get("month", today.month))
        day = int(data.get("day", today.day))
        hour = int(data.get("hour", 12)); minute = int(data.get("minute", 0))
        tz = float(data.get("tz_offset", 5.5))
        lat = float(data.get("lat", 0)); lon = float(data.get("lon", 0))
        asc_sign = int(data.get("natal_asc_sign", 0))
        moon_sign = int(data.get("natal_moon_sign", 0))
        res = chart_engine.transit_chart(asc_sign, moon_sign, year, month, day,
                                         hour, minute, tz, lat, lon)
        return jsonify(sanitize(res))
    except Exception as e:  # noqa
        app.logger.exception("transit error")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
