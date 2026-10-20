"""Manual body composition entry for Garmin Connect.

Run:  python app.py   then open http://127.0.0.1:5000
"""

import hashlib
import json
import secrets
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, flash, redirect, render_template_string, request, url_for
from garminconnect import Garmin

TOKEN_DIR = Path.home() / ".garminconnect"
PROFILE_DIR = TOKEN_DIR / "profiles"
PROFILES_FILE = TOKEN_DIR / "profiles.json"
LB_PER_KG = 2.20462

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Local app: keep logged-in clients and any pending MFA login in memory.
state = {"apis": {}, "active": None, "mfa_api": None, "mfa_state": None}


def load_profiles():
    """Saved profiles as {id: {"name", "height", "unit"}}, in the order added."""
    try:
        return json.loads(PROFILES_FILE.read_text())
    except (OSError, ValueError):
        return {}


def save_profiles(profiles):
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_FILE.write_text(json.dumps(profiles, indent=2))


def add_profile(api):
    """Save a freshly logged-in client as a profile and make it active."""
    if not api.display_name:
        # login(return_on_mfa=True) skips loading the profile when no MFA
        # code was needed, so the name isn't known yet.
        api._load_profile_and_settings()
        api.password = None
    pid = hashlib.sha1(api.display_name.encode()).hexdigest()[:10]
    api.client.dump(str(PROFILE_DIR / pid))
    profiles = load_profiles()
    profiles.setdefault(pid, {"height": "", "unit": "kg"})
    profiles[pid]["name"] = api.full_name or api.display_name
    save_profiles(profiles)
    state["apis"][pid] = api
    state["active"] = pid


def migrate_single_login():
    """Turn the login saved by the earlier single-user version into a profile."""
    old = TOKEN_DIR / "garmin_tokens.json"
    if not old.exists() or PROFILES_FILE.exists():
        return
    try:
        api = Garmin()
        api.login(str(TOKEN_DIR))
        add_profile(api)
        old.unlink()
    except Exception:
        pass


def get_api(pid):
    """Return a logged-in client for a profile, restoring saved tokens if needed."""
    if pid not in state["apis"]:
        try:
            api = Garmin()
            api.login(str(PROFILE_DIR / pid))
            state["apis"][pid] = api
        except Exception:
            return None
    return state["apis"][pid]


def to_float(name):
    value = request.form.get(name, "").strip()
    return float(value) if value else None


PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{% if profile %}{{ profile.name }} · {% endif %}Body Metrics</title>
<style>
  :root { --bg:#f6f7f9; --card:#fff; --text:#1c1f24; --muted:#6b7280; --border:#dde1e6;
          --accent:#007cc3; --accentSoft:#e3f1fa; --ok:#e7f6ec; --okText:#1e6b3a; --err:#fdecec; --errText:#9b1c1c; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#121417; --card:#1c1f24; --text:#e8eaed; --muted:#9aa0a6; --border:#30353c;
            --accent:#3aa0e0; --accentSoft:#16293a; --ok:#183323; --okText:#8fd6a8; --err:#3a1c1c; --errText:#f2a3a3; }
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--text);
         font:15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
  main { max-width:720px; margin:0 auto; padding:24px 16px 48px; }
  h1 { font-size:22px; margin:0 0 4px; }
  .sub { color:var(--muted); margin:0 0 20px; }
  .card { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:20px; margin-bottom:20px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:14px; }
  label { display:block; font-size:13px; color:var(--muted); margin-bottom:4px; }
  input, select { width:100%; padding:9px 10px; border:1px solid var(--border); border-radius:6px;
                  background:var(--bg); color:var(--text); font:inherit; }
  button { background:var(--accent); color:#fff; border:0; border-radius:6px; padding:10px 18px;
           font:inherit; font-weight:600; cursor:pointer; margin-top:16px; }
  .link { background:none; color:var(--muted); padding:0; margin:0; font-weight:400; text-decoration:underline; }
  .msg { padding:10px 14px; border-radius:6px; margin-bottom:16px; }
  .msg.ok { background:var(--ok); color:var(--okText); }
  .msg.error { background:var(--err); color:var(--errText); }
  .row { display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; }
  h2 { font-size:16px; margin:0 0 14px; }
  .hint { font-size:12px; color:var(--muted); margin-top:4px; }
  .tablewrap { overflow-x:auto; }
  table { width:100%; border-collapse:collapse; font-size:14px; }
  th, td { text-align:right; padding:6px 8px; border-bottom:1px solid var(--border); white-space:nowrap; }
  th:first-child, td:first-child { text-align:left; }
  th { color:var(--muted); font-weight:500; }
  .tabs { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px; }
  .tabs form { margin:0; }
  .tab { margin:0; background:var(--card); color:var(--text); border:1px solid var(--border); font-weight:500; padding:8px 16px; }
  .tab.on { background:var(--accent); border-color:var(--accent); color:#fff; font-weight:600; }
  a.tab { display:inline-block; text-decoration:none; border-radius:6px; color:var(--muted); }
  .who { background:var(--accentSoft); border:2px solid var(--accent); border-radius:10px; padding:14px 20px; margin-bottom:20px; }
  .who .label { font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); }
  .who .name { font-size:24px; font-weight:700; line-height:1.2; }
</style>
</head>
<body>
<main>
  <h1>Body Metrics</h1>
  <p class="sub">Send smart-scale-style measurements to Garmin Connect.</p>

  {% if profiles %}
  <div class="tabs">
    {% for pid, p in profiles.items() %}
    <form method="post" action="{{ url_for('switch', pid=pid) }}">
      <button class="tab{% if pid == active %} on{% endif %}">{{ p.name }}</button>
    </form>
    {% endfor %}
    <a class="tab{% if page == 'login' %} on{% endif %}" href="{{ url_for('add') }}">+ Add person</a>
  </div>
  {% endif %}

  {% for cat, m in get_flashed_messages(with_categories=true) %}
    <div class="msg {{ cat }}">{{ m }}</div>
  {% endfor %}

  {% if page == "login" %}
  <div class="card">
    <h2>{% if profiles %}Add a person{% else %}Sign in to Garmin Connect{% endif %}</h2>
    <form method="post" action="{{ url_for('login') }}">
      <div class="grid">
        <div><label>Garmin email</label><input type="email" name="email" required autofocus></div>
        <div><label>Password</label><input type="password" name="password" required></div>
      </div>
      <p class="hint">Your password is sent only to Garmin. Each person's login is saved in {{ token_dir }} so you only sign in once.</p>
      <button>Sign in</button>
    </form>
  </div>

  {% elif page == "mfa" %}
  <div class="card">
    <h2>Two-factor code</h2>
    <form method="post" action="{{ url_for('mfa') }}">
      <label>Code sent by Garmin</label>
      <input name="code" inputmode="numeric" autocomplete="one-time-code" required autofocus>
      <button>Verify</button>
    </form>
  </div>

  {% else %}
  <div class="who row">
    <div>
      <div class="label">Entering measurements for</div>
      <div class="name">{{ profile.name }}</div>
    </div>
    <form method="post" action="{{ url_for('remove', pid=active) }}"
          onsubmit="return confirm('Sign {{ profile.name }} out and remove them from this app?')">
      <button class="link">Sign out {{ profile.name }}</button>
    </form>
  </div>

  <div class="card">
    <h2>New measurement</h2>
    <form method="post" action="{{ url_for('submit') }}" id="f">
      <input type="hidden" name="pid" value="{{ active }}">
      <div class="grid">
        <div><label>Date &amp; time</label><input type="datetime-local" name="timestamp" value="{{ now }}" required></div>
        <div><label>Units</label>
          <select name="unit" id="unit">
            <option value="kg" {% if profile.unit != 'lb' %}selected{% endif %}>kg</option>
            <option value="lb" {% if profile.unit == 'lb' %}selected{% endif %}>lb</option>
          </select></div>
        <div><label>Weight (<span class="u">kg</span>) *</label><input type="number" step="0.1" min="1" name="weight" id="weight" required></div>
        <div><label>Height (cm), used to work out BMI</label><input type="number" step="0.1" min="50" name="height" id="height" value="{{ profile.height }}"></div>
        <div><label>BMI</label><input type="number" step="0.1" name="bmi" id="bmi">
          <div class="hint">Fills itself in from weight and height.</div></div>
        <div><label>Body fat (%)</label><input type="number" step="0.1" min="0" max="100" name="percent_fat"></div>
        <div><label>Body water (%)</label><input type="number" step="0.1" min="0" max="100" name="percent_hydration"></div>
        <div><label>Muscle mass (<span class="u">kg</span>)</label><input type="number" step="0.1" min="0" name="muscle_mass"></div>
        <div><label>Bone mass (<span class="u">kg</span>)</label><input type="number" step="0.1" min="0" name="bone_mass"></div>
        <div><label>Visceral fat rating</label><input type="number" step="1" min="1" max="59" name="visceral_fat_rating"></div>
        <div><label>Metabolic age</label><input type="number" step="1" min="1" name="metabolic_age"></div>
        <div><label>BMR (kcal)</label><input type="number" step="1" min="0" name="basal_met"></div>
        <div><label>Physique rating (1–9)</label><input type="number" step="1" min="1" max="9" name="physique_rating"></div>
      </div>
      <p class="hint">Only weight is required. Leave anything else blank to skip it.</p>
      <button>Upload to {{ profile.name }}'s Garmin</button>
    </form>
  </div>

  <div class="card">
    <h2>{{ profile.name }}'s last 30 days in Garmin Connect</h2>
    {% if history %}
    <div class="tablewrap"><table>
      <tr><th>Date</th><th>Weight (kg)</th><th>BMI</th><th>Fat %</th><th>Water %</th><th>Muscle (kg)</th><th>Bone (kg)</th></tr>
      {% for h in history %}
      <tr><td>{{ h.date }}</td><td>{{ h.weight }}</td><td>{{ h.bmi }}</td><td>{{ h.fat }}</td>
          <td>{{ h.water }}</td><td>{{ h.muscle }}</td><td>{{ h.bone }}</td></tr>
      {% endfor %}
    </table></div>
    {% else %}
    <p class="hint">No weigh-ins found.</p>
    {% endif %}
  </div>

  <script>
    const $ = id => document.getElementById(id);
    function sync() {
      const unit = $("unit").value;
      document.querySelectorAll(".u").forEach(s => s.textContent = unit);
      const w = parseFloat($("weight").value), h = parseFloat($("height").value);
      if (w && h) {
        const kg = unit === "lb" ? w / {{ lb_per_kg }} : w;
        $("bmi").value = (kg / Math.pow(h / 100, 2)).toFixed(1);
      }
    }
    ["unit", "weight", "height"].forEach(id => $(id).addEventListener("input", sync));
    sync();
  </script>
  {% endif %}
</main>
</body>
</html>
"""


def render(page, **kw):
    profiles = load_profiles()
    active = state["active"]
    return render_template_string(
        PAGE, page=page, profiles=profiles, active=active, profile=profiles.get(active),
        token_dir=TOKEN_DIR, lb_per_kg=LB_PER_KG, **kw,
    )


def fmt(value, scale=1.0):
    return f"{value / scale:.1f}" if isinstance(value, (int, float)) else "–"


@app.get("/")
def index():
    profiles = load_profiles()
    if state["active"] not in profiles:
        state["active"] = next(iter(profiles), None)
    pid = state["active"]
    if pid is None:
        return render("login")
    api = get_api(pid)
    if api is None:
        flash(f"{profiles[pid]['name']}'s login has expired. Sign in again to keep using it.", "error")
        return render("login")
    history = []
    try:
        end = date.today()
        data = api.get_body_composition((end - timedelta(days=30)).isoformat(), end.isoformat())
        for e in reversed(data.get("dateWeightList") or []):
            ts = e.get("timestampGMT") or e.get("date")
            when = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M") if ts else e.get("calendarDate", "")
            history.append({
                "date": when,
                "weight": fmt(e.get("weight"), 1000),  # grams
                "bmi": fmt(e.get("bmi")),
                "fat": fmt(e.get("bodyFat")),
                "water": fmt(e.get("bodyWater")),
                "muscle": fmt(e.get("muscleMass"), 1000),
                "bone": fmt(e.get("boneMass"), 1000),
            })
    except Exception as e:
        flash(f"Couldn't load history: {e}", "error")
    return render("entry", history=history, now=datetime.now().strftime("%Y-%m-%dT%H:%M"))


@app.post("/switch/<pid>")
def switch(pid):
    if pid in load_profiles():
        state["active"] = pid
    return redirect(url_for("index"))


@app.get("/add")
def add():
    return render("login")


@app.post("/login")
def login():
    try:
        api = Garmin(request.form["email"], request.form["password"], return_on_mfa=True)
        status, client_state = api.login()
        if status == "needs_mfa":
            state["mfa_api"], state["mfa_state"] = api, client_state
            return render("mfa")
        add_profile(api)
    except Exception as e:
        flash(f"Login failed: {e}", "error")
        return render("login")
    return redirect(url_for("index"))


@app.post("/mfa")
def mfa():
    api = state["mfa_api"]
    if api is None:
        return redirect(url_for("index"))
    try:
        api.resume_login(state["mfa_state"], request.form["code"].strip())
    except Exception as e:
        # The pending MFA session survives a bad code, so let the user retry.
        flash(f"Verification failed: {e}", "error")
        return render("mfa")
    add_profile(api)
    state["mfa_api"] = state["mfa_state"] = None
    return redirect(url_for("index"))


@app.post("/remove/<pid>")
def remove(pid):
    profiles = load_profiles()
    profiles.pop(pid, None)
    save_profiles(profiles)
    state["apis"].pop(pid, None)
    shutil.rmtree(PROFILE_DIR / pid, ignore_errors=True)
    if state["active"] == pid:
        state["active"] = None
    return redirect(url_for("index"))


@app.post("/submit")
def submit():
    # Upload to the person shown on the page that was submitted, not whoever
    # is active now (matters if another tab switched profiles in between).
    pid = request.form.get("pid")
    profiles = load_profiles()
    api = get_api(pid) if pid in profiles else None
    if api is None:
        return redirect(url_for("index"))
    name = profiles[pid]["name"]
    try:
        unit = request.form.get("unit", "kg")
        profiles[pid].update(height=request.form.get("height", "").strip(), unit=unit)
        save_profiles(profiles)

        mass = 1 / LB_PER_KG if unit == "lb" else 1.0

        def kg(name):
            v = to_float(name)
            return round(v * mass, 2) if v is not None else None

        api.add_body_composition(
            request.form["timestamp"],
            weight=kg("weight"),
            percent_fat=to_float("percent_fat"),
            percent_hydration=to_float("percent_hydration"),
            muscle_mass=kg("muscle_mass"),
            bone_mass=kg("bone_mass"),
            visceral_fat_rating=to_float("visceral_fat_rating"),
            metabolic_age=to_float("metabolic_age"),
            basal_met=to_float("basal_met"),
            physique_rating=to_float("physique_rating"),
            bmi=to_float("bmi"),
        )
        flash(f"Uploaded to {name}'s Garmin. It can take a minute to show up in Garmin Connect.", "ok")
    except Exception as e:
        flash(f"Upload to {name}'s Garmin failed: {e}", "error")
    state["active"] = pid
    return redirect(url_for("index"))


if __name__ == "__main__":
    import socket
    import threading
    import webbrowser

    URL = "http://127.0.0.1:5000"
    # If it's already running (shortcut double-clicked twice), just open the page.
    with socket.socket() as s:
        already_running = s.connect_ex(("127.0.0.1", 5000)) == 0
    if already_running:
        webbrowser.open(URL)
    else:
        migrate_single_login()
        print(f"Body Metrics is running at {URL}. Close this window to stop it.")
        threading.Timer(1.0, webbrowser.open, [URL]).start()
        app.run(host="127.0.0.1", port=5000)
