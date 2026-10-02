from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "safeway.db"

app = Flask(__name__)
app.secret_key = "safeway-demo-secret-change-before-deployment"

AREAS = {
    "Central Market": (22.5726, 88.3639),
    "Lake Road": (22.5448, 88.3426),
    "College Road": (22.5800, 88.4000),
    "Station Road": (22.5697, 88.3697),
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS trusted_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        name TEXT NOT NULL, phone TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS saved_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        name TEXT NOT NULL, address TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT, area TEXT NOT NULL,
        incident_type TEXT NOT NULL, incident_date TEXT NOT NULL,
        incident_time TEXT NOT NULL, description TEXT, user_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS journey_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        route_name TEXT NOT NULL,
        contact_id INTEGER,
        share_code TEXT UNIQUE NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        started_at TEXT NOT NULL,
        finished_at TEXT
    );
    """)
    if conn.execute("SELECT COUNT(*) AS c FROM incidents").fetchone()["c"] == 0:
        demo = [
            ("Central Market", "Poor lighting", "2026-09-18", "21:10", "Low lighting reported near the main road."),
            ("Central Market", "Harassment", "2026-09-20", "22:00", "Reported incident used for safety analysis."),
            ("Lake Road", "Poor lighting", "2026-09-15", "20:30", "Reported low-light area."),
            ("Lake Road", "Suspicious activity", "2026-09-21", "23:15", "Reported suspicious activity."),
            ("College Road", "Traffic", "2026-09-17", "18:20", "Heavy traffic reported."),
            ("Station Road", "Theft", "2026-09-12", "19:45", "Reported theft incident."),
        ]
        conn.executemany("""INSERT INTO incidents
            (area,incident_type,incident_date,incident_time,description)
            VALUES (?,?,?,?,?)""", demo)
    conn.commit()
    conn.close()


def current_user():
    if "user_id" not in session:
        return None
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    conn.close()
    return user


def area_stats(area):
    conn = get_db()
    rows = conn.execute(
        "SELECT incident_type,incident_time FROM incidents WHERE LOWER(area)=LOWER(?)",
        (area.strip(),),
    ).fetchall()
    conn.close()
    if not rows:
        return {"score": 90, "status": "No reported incidents", "level": "low", "count": 0, "night": 0}
    risk = 0
    night = 0
    for r in rows:
        typ = r["incident_type"].lower()
        risk += 10
        if "harassment" in typ or "theft" in typ:
            risk += 8
        elif "suspicious" in typ:
            risk += 6
        elif "poor lighting" in typ:
            risk += 5
        hour = int(r["incident_time"].split(":")[0]) if r["incident_time"] else 0
        if hour >= 20:
            risk += 4
            night += 1
    score = max(35, min(95, 100 - risk))
    if score >= 75:
        status, level = "Relatively safer", "low"
    elif score >= 55:
        status, level = "Moderate risk", "medium"
    else:
        status, level = "Higher reported risk", "high"
    return {"score": score, "status": status, "level": level, "count": len(rows), "night": night}


def recommendation(score):
    if score >= 75:
        return "Lower reported risk in the available dataset. Stay aware and use normal safety practices."
    if score >= 55:
        return "Review reported incidents and consider a better-lit route, especially after dark."
    return "Higher reported risk is recorded. Consider another route and avoid isolated areas where possible."


def journey_tip(a, b):
    if a["score"] == b["score"]:
        return "Both areas have the same current score. Check distance, lighting and your travel conditions before deciding."
    return "Use the score as one signal only; also consider route length, time of travel, lighting and current conditions."


def active_journey(user_id):
    conn = get_db()
    row = conn.execute("""SELECT j.*, c.name AS contact_name FROM journey_sessions j
                          LEFT JOIN trusted_contacts c ON c.id=j.contact_id
                          WHERE j.user_id=? AND j.status='active' ORDER BY j.id DESC LIMIT 1""", (user_id,)).fetchone()
    conn.close()
    return row


@app.route("/")
def index():
    return render_template("index.html", user=current_user())


@app.route("/routes", methods=["GET", "POST"])
def routes():
    result = None
    user = current_user()
    saved_locations = []
    contacts = []
    active = None
    if user:
        conn = get_db()
        saved_locations = conn.execute("SELECT * FROM saved_locations WHERE user_id=? ORDER BY id DESC", (user["id"],)).fetchall()
        contacts = conn.execute("SELECT * FROM trusted_contacts WHERE user_id=? ORDER BY id DESC", (user["id"],)).fetchall()
        conn.close()
        active = active_journey(user["id"])
    if request.method == "POST":
        a = request.form.get("area_a", "").strip()
        b = request.form.get("area_b", "").strip()
        if not a or not b:
            flash("Please enter both areas.", "error")
        else:
            sa, sb = area_stats(a), area_stats(b)
            result = {
                "a": {**sa, "area": a, "recommendation": recommendation(sa["score"])},
                "b": {**sb, "area": b, "recommendation": recommendation(sb["score"])},
            }
            result["tip"] = journey_tip(sa, sb)
    return render_template("routes.html", result=result, user=user, saved_locations=saved_locations, contacts=contacts, active=active)


@app.route("/journey/start", methods=["POST"])
def start_journey():
    user = current_user()
    if not user:
        flash("Log in to start a journey check-in.", "error")
        return redirect(url_for("login"))
    route_name = request.form.get("route_name", "SafeWay journey").strip() or "SafeWay journey"
    contact_id = request.form.get("contact_id") or None
    conn = get_db()
    old = conn.execute("SELECT id FROM journey_sessions WHERE user_id=? AND status='active'", (user["id"],)).fetchone()
    if old:
        flash("You already have an active journey check-in.", "error")
    else:
        code = secrets.token_urlsafe(6).upper()
        conn.execute("""INSERT INTO journey_sessions(user_id,route_name,contact_id,share_code,status,started_at)
                        VALUES(?,?,?,?,?,?)""", (user["id"], route_name, contact_id, code, "active", datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        flash("Journey check-in started. The share code is shown on this page; no message is sent automatically.", "success")
    conn.close()
    return redirect(url_for("routes"))


@app.route("/journey/finish", methods=["POST"])
def finish_journey():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    conn = get_db()
    conn.execute("""UPDATE journey_sessions SET status='completed', finished_at=?
                    WHERE user_id=? AND status='active'""", (datetime.now().strftime("%Y-%m-%d %H:%M"), user["id"]))
    conn.commit()
    conn.close()
    flash("Journey check-in completed.", "success")
    return redirect(url_for("routes"))


@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        fields = [request.form.get(x, "").strip() for x in ["area", "incident_type", "incident_date", "incident_time"]]
        desc = request.form.get("description", "").strip()
        if not all(fields):
            flash("Please fill all required fields.", "error")
        else:
            conn = get_db()
            conn.execute("""INSERT INTO incidents(area,incident_type,incident_date,incident_time,description,user_id)
                            VALUES(?,?,?,?,?,?)""", (*fields, desc, session.get("user_id")))
            conn.commit()
            conn.close()
            flash("Incident report added successfully.", "success")
            return redirect(url_for("report"))
    return render_template("report.html", user=current_user())


@app.route("/dashboard")
def dashboard():
    conn = get_db()
    areas = conn.execute("SELECT area,COUNT(*) count FROM incidents GROUP BY area ORDER BY count DESC").fetchall()
    types = conn.execute("SELECT incident_type,COUNT(*) count FROM incidents GROUP BY incident_type ORDER BY count DESC").fetchall()
    total = conn.execute("SELECT COUNT(*) c FROM incidents").fetchone()["c"]
    night = conn.execute("SELECT COUNT(*) c FROM incidents WHERE CAST(substr(incident_time,1,2) AS INTEGER)>=20").fetchone()["c"]
    recent = conn.execute("SELECT * FROM incidents ORDER BY id DESC LIMIT 6").fetchall()
    trend_rows = conn.execute("""SELECT incident_date, COUNT(*) count FROM incidents
                               GROUP BY incident_date ORDER BY incident_date ASC""").fetchall()
    conn.close()
    area_data = [{"area": a["area"], **area_stats(a["area"])} for a in areas]
    avg = round(sum(x["score"] for x in area_data) / len(area_data), 1) if area_data else 90
    max_type = max([t["count"] for t in types], default=1)
    type_data = [{"incident_type": t["incident_type"], "count": t["count"], "percent": round(t["count"] * 100 / max_type)} for t in types]
    trend = [{"date": r["incident_date"], "count": r["count"]} for r in trend_rows]
    return render_template("dashboard.html", user=current_user(), total=total, night=night, day=total-night,
                           areas=area_data, types=type_data, recent=recent, average=avg, trend=trend)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    conn = get_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            conn.execute("UPDATE users SET name=? WHERE id=?", (name, user["id"]))
            conn.commit()
            flash("Profile updated.", "success")
            user = conn.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
    contacts = conn.execute("SELECT * FROM trusted_contacts WHERE user_id=? ORDER BY id DESC", (user["id"],)).fetchall()
    locations = conn.execute("SELECT * FROM saved_locations WHERE user_id=? ORDER BY id DESC", (user["id"],)).fetchall()
    conn.close()
    return render_template("profile.html", user=user, contacts=contacts, locations=locations)


@app.route("/profile/contact", methods=["POST"])
def add_contact():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    if name and phone:
        conn = get_db()
        conn.execute("INSERT INTO trusted_contacts(user_id,name,phone) VALUES(?,?,?)", (user["id"], name, phone))
        conn.commit()
        conn.close()
        flash("Trusted contact added.", "success")
    return redirect(url_for("profile"))


@app.route("/profile/location", methods=["POST"])
def add_location():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    name = request.form.get("name", "").strip()
    address = request.form.get("address", "").strip()
    if name and address:
        conn = get_db()
        conn.execute("INSERT INTO saved_locations(user_id,name,address) VALUES(?,?,?)", (user["id"], name, address))
        conn.commit()
        conn.close()
        flash("Location saved.", "success")
    return redirect(url_for("profile"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            flash("Welcome back!", "success")
            return redirect(url_for("index"))
        flash("Invalid email or password.", "error")
    return render_template("login.html", mode="login", user=current_user())


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter a name, email and password of at least 6 characters.", "error")
        else:
            conn = get_db()
            try:
                cur = conn.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)", (name, email, generate_password_hash(password)))
                conn.commit()
                session["user_id"] = cur.lastrowid
                flash("Account created successfully.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                flash("An account with this email already exists.", "error")
            finally:
                conn.close()
    return render_template("login.html", mode="signup", user=current_user())


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("index"))


@app.route("/sos")
def sos():
    flash("SOS workflow opened. No real emergency call or message is sent by this prototype.", "success")
    return redirect(url_for("index"))


@app.route("/api/area/<path:area>")
def api_area(area):
    s = area_stats(area)
    return jsonify({"area": area, **s, "recommendation": recommendation(s["score"])})


@app.route("/api/areas")
def api_areas():
    return jsonify([{"area": name, "lat": coords[0], "lng": coords[1], **area_stats(name)} for name, coords in AREAS.items()])


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
