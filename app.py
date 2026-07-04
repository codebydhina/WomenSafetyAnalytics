"""
ShesSafe - Women Safety Analytics App
Backend (Flask) - serves API data only, no database required.

Run with:  python app.py
Then open index.html in your browser (or use the "Live Server" VS Code extension).
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)  # allow index.html (opened as a file / on a different port) to call this API

# ---------------------------------------------------------------------------
# In-memory "database" (mini project -> no real DB needed)
# ---------------------------------------------------------------------------

# username -> { "name": str, "password_hash": str }
USERS = {}

ZONES = [
    {"id": 1, "name": "MG Road",        "lat": 12.9762, "lng": 77.6033, "score": 78},
    {"id": 2, "name": "Koramangala",    "lat": 12.9352, "lng": 77.6245, "score": 85},
    {"id": 3, "name": "Whitefield",     "lat": 12.9698, "lng": 77.7500, "score": 62},
    {"id": 4, "name": "Indiranagar",    "lat": 12.9719, "lng": 77.6412, "score": 74},
    {"id": 5, "name": "Electronic City","lat": 12.8452, "lng": 77.6602, "score": 55},
    {"id": 6, "name": "Jayanagar",      "lat": 12.9308, "lng": 77.5838, "score": 88},
]

INCIDENT_TYPES = ["Harassment", "Stalking", "Unsafe Lighting", "Theft", "Suspicious Activity"]

INCIDENTS = [
    {"id": 1, "type": "Harassment",         "zone": "Whitefield",      "severity": "High",
     "description": "Reported near bus stop late evening.", "time": (datetime.now() - timedelta(days=1)).isoformat()},
    {"id": 2, "type": "Unsafe Lighting",    "zone": "Electronic City", "severity": "Medium",
     "description": "Street lights not working on main road.", "time": (datetime.now() - timedelta(days=2)).isoformat()},
    {"id": 3, "type": "Suspicious Activity","zone": "MG Road",         "severity": "Low",
     "description": "Unknown person following at a distance.", "time": (datetime.now() - timedelta(hours=10)).isoformat()},
]

# a fixed simulated path (lat, lng points) used for the "Live Location" demo
LIVE_PATH = [
    {"lat": 12.9716, "lng": 77.5946},
    {"lat": 12.9726, "lng": 77.5978},
    {"lat": 12.9740, "lng": 77.6010},
    {"lat": 12.9755, "lng": 77.6050},
    {"lat": 12.9770, "lng": 77.6090},
    {"lat": 12.9790, "lng": 77.6130},
]
_live_index = {"step": 0}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "message": "ShesSafe backend running"})


# ---------------------------------------------------------------------------
# Auth (mini project version — in-memory users, hashed passwords, no sessions/JWT)
# ---------------------------------------------------------------------------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True) or {}
    username = (data.get("username") or "").strip().lower()
    name = (data.get("name") or "").strip()
    password = data.get("password") or ""

    if not username or not name or not password:
        return jsonify({"error": "Name, username and password are all required."}), 400
    if username in USERS:
        return jsonify({"error": "That username is already taken."}), 409
    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters."}), 400

    USERS[username] = {"name": name, "password_hash": generate_password_hash(password)}
    return jsonify({"username": username, "name": name}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    user = USERS.get(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password."}), 401

    return jsonify({"username": username, "name": user["name"]})


@app.route("/api/zones")
def get_zones():
    """Safety score per area, used to color the map."""
    return jsonify(ZONES)


@app.route("/api/incidents", methods=["GET", "POST"])
def incidents():
    if request.method == "POST":
        data = request.get_json(force=True) or {}
        new_incident = {
            "id": len(INCIDENTS) + 1,
            "type": data.get("type", "Other"),
            "zone": data.get("zone", "Unknown"),
            "severity": data.get("severity", "Low"),
            "description": data.get("description", ""),
            "time": datetime.now().isoformat(),
        }
        INCIDENTS.insert(0, new_incident)

        # nudge the affected zone's safety score down a little when a report comes in
        for z in ZONES:
            if z["name"] == new_incident["zone"]:
                drop = {"High": 6, "Medium": 3, "Low": 1}.get(new_incident["severity"], 1)
                z["score"] = max(10, z["score"] - drop)

        return jsonify(new_incident), 201

    return jsonify(INCIDENTS)


@app.route("/api/analytics")
def analytics():
    """Aggregated stats computed on the fly from current data."""
    total = len(INCIDENTS)

    by_type = {}
    for inc in INCIDENTS:
        by_type[inc["type"]] = by_type.get(inc["type"], 0) + 1

    safest = max(ZONES, key=lambda z: z["score"])
    riskiest = min(ZONES, key=lambda z: z["score"])

    # simulated 7-day safety trend (kept stable per run using a seeded random)
    rnd = random.Random(42)
    trend = []
    base = sum(z["score"] for z in ZONES) / len(ZONES)
    for i in range(7):
        day = (datetime.now() - timedelta(days=6 - i)).strftime("%a")
        trend.append({"day": day, "score": round(base + rnd.uniform(-6, 6), 1)})

    return jsonify({
        "total_incidents": total,
        "by_type": by_type,
        "safest_zone": safest["name"],
        "safest_score": safest["score"],
        "riskiest_zone": riskiest["name"],
        "riskiest_score": riskiest["score"],
        "avg_score": round(base, 1),
        "trend": trend,
    })


@app.route("/api/location/simulate")
def simulate_location():
    """Returns the next point along a fixed demo path, looping.
    The frontend polls this to fake 'live' location sharing."""
    step = _live_index["step"] % len(LIVE_PATH)
    point = LIVE_PATH[step]
    _live_index["step"] += 1
    return jsonify({"lat": point["lat"], "lng": point["lng"], "step": step, "timestamp": datetime.now().isoformat()})


@app.route("/api/location/reset", methods=["POST"])
def reset_location():
    _live_index["step"] = 0
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    print("ShesSafe backend running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
