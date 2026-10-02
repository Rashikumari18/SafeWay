# SafeWay — Smart Safety & Journey Analysis

SafeWay is a Flask + SQLite web application for planning journeys using area-level incident signals. It combines route comparison, an interactive map, safety recommendations, incident reporting, dashboard insights, saved locations, trusted contacts and a journey check-in workflow.

## Current Features

- Interactive OpenStreetMap / Leaflet safety map
- Map-based area selection for Route A and Route B
- Optional browser geolocation to center the map (not stored by SafeWay)
- Route A/B safety comparison
- Rule-based safety score, incident count and night-report signal
- Context-aware safety recommendations
- Incident reporting with date, time, type and description
- Dashboard with area signals, incident mix and report activity
- Login / signup with password hashing
- Profile management
- Trusted contacts
- Saved locations
- Journey check-in with start / finish status and a local share code
- SOS workflow button clearly marked as a prototype workflow; it does not place calls or send messages
- Responsive dark modern UI

## Tech Stack

- **Python** — programming language
- **Flask** — web framework
- **SQLite** — database
- **HTML / CSS / JavaScript** — frontend
- **Leaflet + OpenStreetMap** — interactive map

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Project Structure

```text
SafeWay/
├── app.py
├── requirements.txt
├── sample_incidents.csv
├── README.md
├── .gitignore
├── templates/
└── static/
```

## Safety / Prototype Note

Safety scores are calculated from the available reported incident dataset and a rule-based scoring system. They are informational indicators, not guarantees of real-world safety. The map area coordinates are illustrative. Browser geolocation is used only to center the map and is not stored by the app. The journey check-in and SOS workflows are demonstrations and do not automatically contact emergency services or trusted contacts.

## Project By

Rashi Kumari
