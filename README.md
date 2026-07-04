# ShesSafe — Women Safety Analytics App

A mini project with:
- **Frontend:** one single file, `index.html` (HTML + CSS + JavaScript). Uses Leaflet for the map and Chart.js for the analytics charts (loaded from CDN, so you need an internet connection in the browser).
- **Backend:** `app.py`, a small Flask API. No database — all data lives in memory while the server runs, which resets each time you restart it.

## Features
1. **Login / Register** — create an account or log in before accessing the app
2. **Safety Map** — zones colored by a live safety score (0–100)
3. **Report an Incident** — submitting a report updates the affected zone's score
4. **Analytics Dashboard** — totals, safest/riskiest zone, incident-type chart, 7-day trend
5. **Live Location (simulated)** — toggle "sharing" to watch a marker move along a demo path

### About the login system
- Accounts are stored **in memory** on the backend (a Python dict) — simple on purpose for a mini project. They reset whenever you restart `app.py`.
- Passwords are hashed with Werkzeug's `generate_password_hash` / `check_password_hash` (never stored in plain text).
- There's no session/token system — once logged in, the browser just remembers your name via `localStorage` until you click the logout (⏻) button. This is fine for a demo but not meant for production use.

## How to run this in VS Code

### 1. Open the folder
Open the `shesafe` folder in VS Code (`File → Open Folder…`).

### 2. Install Python dependencies
Open a terminal in VS Code (`` Ctrl+` `` / `` Cmd+` ``) and run:

```bash
pip install -r requirements.txt
```

> If you have multiple Python versions, you may need `pip3` instead of `pip`.

### 3. Start the backend
In the same terminal:

```bash
python app.py
```

You should see:
```
ShesSafe backend running on http://127.0.0.1:5000
```

Leave this terminal running — it needs to stay open while you use the app.

### 4. Open the frontend
Right-click `index.html` in VS Code's file explorer and choose **"Open with Live Server"** (if you have the Live Server extension), or simply double-click `index.html` in your file explorer to open it directly in your browser.

Either way works — the page calls the backend at `http://127.0.0.1:5000`, which is already running from step 3.

## Project structure
```
shesafe/
├── index.html        # entire frontend (HTML + CSS + JS)
├── app.py             # Flask backend / API
├── requirements.txt   # Python dependencies
└── README.md
```

## API endpoints (for reference)
| Method | Endpoint                 | Purpose                              |
|--------|---------------------------|---------------------------------------|
| POST   | `/api/register`            | Create a new account                 |
| POST   | `/api/login`               | Log in with username + password      |
| GET    | `/api/zones`               | List zones with safety scores        |
| GET    | `/api/incidents`           | List incident reports                |
| POST   | `/api/incidents`           | Submit a new incident report         |
| GET    | `/api/analytics`           | Aggregated stats + trend data        |
| GET    | `/api/location/simulate`   | Next point on the demo location path |
| POST   | `/api/location/reset`      | Reset the simulated path to start    |

## Notes for your project write-up
- No database is used — data is stored in Python lists in memory (resets on restart). This keeps the mini project simple; swapping in SQLite later would only require changing the functions in `app.py`.
- The map uses OpenStreetMap tiles via Leaflet (free, no API key needed).
- "Live location" is simulated with a fixed path for demo purposes — a real version would use the browser's Geolocation API.
