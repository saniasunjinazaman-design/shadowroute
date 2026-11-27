#!/usr/bin/env python3
"""Read-only live BGP route dashboard for Project Shadow Route (redesigned UI)."""
import base64, csv, datetime as dt, hashlib, hmac, html, json, os, re, statistics, subprocess
from pathlib import Path
import streamlit as st
from streamlit_autorefresh import st_autorefresh

ROOT = Path(os.environ.get("SHADOW_ROUTE_ROOT", Path(__file__).resolve().parents[1])).expanduser().resolve()
PREFIX = "10.150.0.0/24"
EXPECTED = 150
OBSERVER = "as152brd-router0-10.152.0.254"
ROUTERS = {
    "AS2": "as2brd-router0-10.2.0.254",
    "AS3": "as3brd-router0-10.3.0.254",
    "AS150": "as150brd-router0-10.150.0.254",
    "AS151": "as151brd-router0-10.151.0.254",
    "AS152": OBSERVER,
}

st.set_page_config(page_title="Shadow Route | BGP Monitor", page_icon="🛡️", layout="wide")

# ----------------------------------------------------------------- styling
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
:root{--bg:#0d1524;--panel:#141f33;--panel2:#18253c;--line:#233350;--text:#e8eef9;--muted:#8fa3c2;
--ok:#2dd4a0;--bad:#ff5470;--warn:#f5b942;--accent:#5b9dff}
html,body,[class*="css"],.stApp{font-family:'Manrope',system-ui,-apple-system,'Segoe UI',sans-serif}
.stApp{background:radial-gradient(1200px 600px at 80% -10%,#16264a 0%,var(--bg) 55%)}
#MainMenu,footer,header[data-testid="stHeader"]{visibility:hidden;height:0}
.block-container{padding-top:1.4rem;padding-bottom:2rem;max-width:1400px}
h1,h2,h3,h4,p,span,div,label{color:var(--text)}
section[data-testid="stSidebar"]{background:#0a111e;border-right:1px solid var(--line)}
.topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}
.brand{display:flex;align-items:center;gap:12px}
.brand-logo{width:40px;height:40px;border-radius:11px;background:linear-gradient(135deg,#3b82f6,#7c5cff);
display:flex;align-items:center;justify-content:center;font-size:20px}
.brand-title{font-size:20px;font-weight:800;letter-spacing:.2px;line-height:1.1}
.brand-sub{font-size:12.5px;color:var(--muted);margin-top:2px}
.chip{display:inline-flex;align-items:center;gap:8px;padding:7px 13px;border:1px solid var(--line);
border-radius:999px;background:var(--panel);font-size:12.5px;color:var(--muted)}
.dot{width:9px;height:9px;border-radius:50%;background:var(--ok);display:inline-block}
.dot.live{animation:pulse 1.6s ease-out infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(45,212,160,.6)}100%{box-shadow:0 0 0 10px rgba(45,212,160,0)}}
@media (prefers-reduced-motion:reduce){.dot.live{animation:none}}
.hero{border-radius:18px;padding:26px 30px;border:1px solid var(--tone);
background:linear-gradient(100deg,color-mix(in srgb,var(--tone) 18%,var(--panel)) 0%,var(--panel) 70%);
display:flex;justify-content:space-between;align-items:center;gap:24px;margin-bottom:16px}
.hero-state{font-size:13px;color:var(--tone);font-weight:700;display:flex;align-items:center;gap:8px}
.hero-title{font-size:34px;font-weight:800;margin:6px 0 6px;letter-spacing:-.4px}
.hero-desc{font-size:14.5px;color:var(--muted);max-width:620px;line-height:1.55}
.hero-right{text-align:right;min-width:190px}
.hero-big{font-size:56px;font-weight:800;color:var(--tone);line-height:1;letter-spacing:-1px}
.hero-cap{font-size:12.5px;color:var(--muted);margin-top:6px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:16px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.kpi-l{font-size:12.5px;color:var(--muted);font-weight:600}
.kpi-v{font-size:24px;font-weight:800;margin-top:6px}
.kpi-s{font-size:12px;color:var(--muted);margin-top:4px}
.good{color:var(--ok)}.bad{color:var(--bad)}.warn{color:var(--warn)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px 20px;margin-bottom:14px}
.panel-h{font-size:15px;font-weight:700;margin-bottom:2px}
.panel-s{font-size:12.5px;color:var(--muted);margin-bottom:12px}
.pathrow{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:6px 0 14px}
.hop{padding:6px 12px;border-radius:9px;border:1px solid var(--line);background:var(--panel2);
font-weight:700;font-size:13.5px}
.hop.origin{border-color:var(--tone);color:var(--tone)}
.arrow{color:var(--muted)}
.kv{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid var(--line);font-size:13.5px}
.kv:last-child{border-bottom:none}.kv span:first-child{color:var(--muted)}
.mono,code,pre{font-family:'JetBrains Mono',ui-monospace,monospace!important}
.codebox{background:#0a111e;border:1px solid var(--line);border-radius:10px;padding:11px 13px;
font-size:12px;color:#b9c8e2;overflow-x:auto;white-space:pre}
.strip{display:flex;gap:3px;flex-wrap:nowrap;overflow:hidden}
.tick{flex:1;height:26px;border-radius:4px;min-width:4px}
.tick.n{background:var(--ok)}.tick.h{background:var(--bad)}.tick.o{background:var(--warn)}
.tick.empty{background:var(--line)}
.stTabs [data-baseweb="tab-list"]{gap:6px;border-bottom:1px solid var(--line)}
.stTabs [data-baseweb="tab"]{height:42px;padding:0 16px;color:var(--muted);font-weight:600}
.stTabs [aria-selected="true"]{color:var(--text)!important}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:12px;overflow:hidden}
[data-testid="stForm"]{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px}
.login-head{text-align:center;margin:8vh 0 18px}
.login-head .brand-logo{margin:0 auto 14px;width:56px;height:56px;font-size:28px}
.login-title{font-size:26px;font-weight:800}.login-sub{font-size:13.5px;color:var(--muted);margin-top:4px}
.brand-logo img{width:100%;height:100%;object-fit:cover;border-radius:11px}
.login-img{width:100%;border-radius:14px;border:1px solid var(--line);margin-bottom:14px}
@media (max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}.hero{flex-direction:column;align-items:flex-start}
.hero-right{text-align:left}.hero-title{font-size:26px}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------------- images
ASSETS = ROOT / "assets"
EXTS = (".png", ".jpg", ".jpeg", ".webp", ".svg")

def find_img(stem):
    for e in EXTS:
        f = ASSETS / (stem + e)
        if f.exists(): return f
    return None

def img_uri(f):
    if f is None: return None
    mime = "image/svg+xml" if f.suffix == ".svg" else "image/" + f.suffix.lstrip(".").replace("jpg", "jpeg")
    return "data:" + mime + ";base64," + base64.b64encode(f.read_bytes()).decode()

LOGO = img_uri(find_img("logo"))
LOGO_HTML = '<img src="' + LOGO + '" alt="logo"/>' if LOGO else "🛡️"

# ----------------------------------------------------------------- login
# Accounts are saved in users.json next to app.py (salted PBKDF2 hashes, never plain text).
# Optional administrator credentials can be supplied with SHADOW_USER and SHADOW_PASS.
# No default administrator password is included in this repository.
USERS_FILE = ROOT / "users.json"
ADMIN_USER = os.environ.get("SHADOW_USER", "")
ADMIN_PASS = os.environ.get("SHADOW_PASS", "")

def _pbkdf2(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 120000).hex()

def load_users():
    try: return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return {}

def save_users(d):
    USERS_FILE.write_text(json.dumps(d, indent=2), encoding="utf-8")
    try: os.chmod(USERS_FILE, 0o600)
    except OSError: pass

def register(user, pw, pw2):
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,24}", user):
        return False, "Username must be 3 to 24 characters: letters, numbers, dot, dash or underscore."
    if len(pw) < 6: return False, "Password must be at least 6 characters."
    if pw != pw2: return False, "The two passwords do not match."
    users = load_users()
    if user.lower() in {k.lower() for k in users} or user.lower() == ADMIN_USER.lower():
        return False, "That username is taken. Choose another one."
    salt = os.urandom(16).hex()
    users[user] = {"salt": salt, "hash": _pbkdf2(pw, salt),
                   "created": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    try: save_users(users)
    except OSError as e: return False, "Could not save the account: " + str(e)
    return True, "Account created. Open the Sign in tab and log in."

def check_login(user, pw):
    if ADMIN_USER and ADMIN_PASS and user == ADMIN_USER and hmac.compare_digest(pw, ADMIN_PASS): return True
    rec = load_users().get(user)
    return bool(rec) and hmac.compare_digest(rec["hash"], _pbkdf2(pw, rec["salt"]))

if not st.session_state.get("auth"):
    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        login_img = img_uri(find_img("login"))
        st.markdown('<div class="login-head"><div class="brand-logo">' + LOGO_HTML + '</div>'
                    '<div class="login-title">Shadow Route</div>'
                    '<div class="login-sub">Sign in or create an account to open the BGP monitor</div></div>',
                    unsafe_allow_html=True)
        if login_img:
            st.markdown('<img class="login-img" src="' + login_img + '" alt=""/>', unsafe_allow_html=True)
        tab_in, tab_up = st.tabs(["Sign in", "Create account"])
        with tab_in:
            with st.form("login"):
                u = st.text_input("Username")
                pw = st.text_input("Password", type="password")
                go = st.form_submit_button("Sign in", use_container_width=True)
            if go:
                if check_login(u.strip(), pw):
                    st.session_state["auth"] = u.strip(); st.rerun()
                else:
                    st.error("Username or password is wrong. If you are new, create an account first.")
        with tab_up:
            with st.form("signup"):
                nu = st.text_input("Choose a username")
                p1 = st.text_input("Choose a password", type="password")
                p2 = st.text_input("Repeat the password", type="password")
                su = st.form_submit_button("Create account", use_container_width=True)
            if su:
                ok, msg = register(nu.strip(), p1, p2)
                (st.success if ok else st.error)(msg)
    st.stop()

st_autorefresh(interval=2000, key="shadow-refresh")

# ------------------------------------------------------------ data helpers
def docker(container, *args):
    try:
        p = subprocess.run(["docker", "exec", container, *args], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)
    return (True, p.stdout.strip()) if p.returncode == 0 else (False, (p.stderr or p.stdout).strip())

def selected_route(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not re.match(r"^\s*" + re.escape(PREFIX) + r"\s+", line): continue
        if not re.search(r"\]\s+\*\s*\(", line): continue
        path = None
        for d in lines[i:i + 16]:
            m = re.search(r"BGP\.as_path:\s*(.+)", d)
            if m:
                raw = m.group(1).strip()
                path = [int(x) for x in raw.split()] if re.fullmatch(r"\d+(?:\s+\d+)*", raw) else raw
                break
        return {"header": line.strip(), "path": path}
    return None

def current():
    ok, text = docker(OBSERVER, "birdc", "show", "route", "all")
    if not ok: return {"status": "ROUTER_OFFLINE", "error": text}
    route = selected_route(text)
    if route is None: return {"status": "ROUTE_MISSING"}
    path = route["path"]
    if not isinstance(path, list) or not path: return {"status": "ROUTE_UNPARSED", "route": route}
    origin = path[-1]
    return {"status": "NORMAL" if origin == EXPECTED else "HIJACK_ALERT", "origin": origin, "route": route}

def filter_state():
    ok, text = docker("as3brd-router0-10.3.0.254", "cat", "/etc/bird/bird.conf")
    if not ok: return "UNKNOWN"
    m = re.search(r"protocol\s+bgp\s+c_as151\s*\{(.*?)(?=\nprotocol\s+bgp|\Z)", text, re.S)
    return "ENABLED" if m and re.search(r"if\s+net\s*=\s*10\.150\.0\.0/24\s+then\s+reject", m.group(1)) else "NOT DETECTED"

def peers():
    out = []
    for asn, container in ROUTERS.items():
        ok, text = docker(container, "birdc", "show", "protocols")
        if not ok:
            out.append({"AS": asn, "BGP peers": "unavailable", "Detail": text[:100]}); continue
        states = []
        for line in text.splitlines():
            c = line.split()
            if len(c) >= 5 and c[1] == "BGP": states.append(c[0] + ": " + c[-1])
        out.append({"AS": asn, "BGP peers": "; ".join(states) or "none", "Detail": "up"})
    return out

def events():
    p = ROOT / "logs/alerts.jsonl"
    if not p.exists(): return []
    out = []
    for line in p.read_text(errors="replace").splitlines()[-300:]:
        try:
            e = json.loads(line)
            if e.get("prefix") == PREFIX: out.append(e)
        except json.JSONDecodeError: pass
    return out

def timing_rows():
    p = ROOT / "evidence/evaluation/detection_times.csv"
    if not p.exists(): return []
    try:
        with p.open(newline="", encoding="utf-8") as f: return list(csv.DictReader(f))
    except (OSError, csv.Error): return []

# ------------------------------------------------------------- UI helpers
THEME = {
    "NORMAL": ("#2dd4a0", "Route is normal", "The prefix is reachable through its trusted origin. No action needed."),
    "HIJACK_ALERT": ("#ff5470", "Hijack detected", "Another AS is now announcing this prefix and its route was selected. Traffic may be diverted."),
    "ROUTER_OFFLINE": ("#f5b942", "Router unreachable", "The observer router did not answer. Check that the containers are running and Docker access is allowed."),
    "ROUTE_MISSING": ("#f5b942", "Route not found", "The observer has no selected route for this prefix yet."),
    "ROUTE_UNPARSED": ("#f5b942", "Route could not be read", "A route exists but its AS path could not be parsed."),
}

def esc(x): return html.escape(str(x))

def kpi(label, value, sub="", cls=""):
    return ('<div class="kpi"><div class="kpi-l">' + esc(label) + '</div><div class="kpi-v ' + cls + '">'
            + esc(value) + '</div><div class="kpi-s">' + esc(sub) + '</div></div>')

def topology_svg(path, status):
    pos = {150: (90, 150), 2: (270, 150), 3: (450, 150), 152: (630, 150), 151: (450, 42)}
    role = {150: "Victim", 2: "Transit", 3: "Transit + filter", 152: "Observer", 151: "Attacker"}
    links = [(150, 2), (2, 3), (3, 152), (151, 3)]
    tone = "#2dd4a0" if status == "NORMAL" else "#ff5470"
    active = set()
    if isinstance(path, list):
        chain = [152] + path
        for a, b in zip(chain, chain[1:]):
            active.add(frozenset((a, b)))
    s = ['<svg viewBox="0 0 720 230" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Network topology">']
    for a, b in links:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        on = frozenset((a, b)) in active
        col = tone if on else "#2b3c5c"
        w = 4 if on else 2
        dash = "" if on else ' stroke-dasharray="5 5"'
        s.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="%d"%s/>' % (x1, y1, x2, y2, col, w, dash))
    for asn, (x, y) in pos.items():
        in_path = isinstance(path, list) and (asn in path or asn == 152)
        if asn == 151: ring = "#ff5470" if (isinstance(path, list) and 151 in path) else "#5a3a4a"
        else: ring = tone if in_path else "#2b3c5c"
        fill = "#2a1620" if asn == 151 else "#18253c"
        s.append('<circle cx="%d" cy="%d" r="34" fill="%s" stroke="%s" stroke-width="3"/>' % (x, y, fill, ring))
        s.append('<text x="%d" y="%d" fill="#e8eef9" font-size="15" font-weight="800" text-anchor="middle" '
                 'font-family="Manrope,sans-serif">AS%d</text>' % (x, y + 5, asn))
        ty = y - 46 if asn == 151 else y + 56
        if asn == 151: ty = y + 56 if False else y - 44
        s.append('<text x="%d" y="%d" fill="#8fa3c2" font-size="12" text-anchor="middle" '
                 'font-family="Manrope,sans-serif">%s</text>' % (x, ty if asn != 151 else y - 42, role[asn]))
    s.append('</svg>')
    return "".join(s)

# ------------------------------------------------------------------- poll
r = current(); filt = filter_state(); status = r["status"]; origin = r.get("origin")
tone, title, desc = THEME.get(status, THEME["ROUTE_MISSING"])
now = dt.datetime.now().astimezone()
path = r.get("route", {}).get("path") if r.get("route") else None

hist = st.session_state.setdefault("hist", [])
hist.append((now.strftime("%H:%M:%S"), status)); del hist[:-60]

# ----------------------------------------------------------------- header
st.markdown(
    '<div class="topbar"><div class="brand"><div class="brand-logo">' + LOGO_HTML + '</div><div>'
    '<div class="brand-title">Shadow Route</div>'
    '<div class="brand-sub">Live BGP prefix-origin monitor · SEED Emulator · read-only</div></div></div>'
    '<div class="chip"><span class="dot live"></span>Live · updated ' + now.strftime("%H:%M:%S") + ' · every 2 s</div></div>',
    unsafe_allow_html=True)

# ------------------------------------------------------------------- hero
big = ("AS" + str(origin)) if origin is not None else "—"
st.markdown(
    '<div class="hero" style="--tone:' + tone + '"><div><div class="hero-state">'
    '<span class="dot" style="background:' + tone + '"></span>' + esc(status.replace("_", " ").title()) + '</div>'
    '<div class="hero-title">' + esc(title) + '</div><div class="hero-desc">'
    + esc(desc if status != "ROUTER_OFFLINE" else desc + " " + str(r.get("error", ""))[:120]) + '</div></div>'
    '<div class="hero-right"><div class="hero-big">' + esc(big) + '</div>'
    '<div class="hero-cap">Origin AS of ' + PREFIX + '</div></div></div>',
    unsafe_allow_html=True)

# ------------------------------------------------------------------- KPIs
filt_cls = "good" if filt == "ENABLED" else ("warn" if filt == "UNKNOWN" else "bad")
origin_cls = "good" if status == "NORMAL" else ("bad" if status == "HIJACK_ALERT" else "warn")
hops = str(len(path)) if isinstance(path, list) else "—"
st.markdown('<div class="kpis">'
            + kpi("Trusted origin", "AS" + str(EXPECTED), "Expected owner of the prefix", "good")
            + kpi("Observed origin", big, "Seen from AS152", origin_cls)
            + kpi("AS3 prefix filter", filt, "Blocks the prefix from AS151", filt_cls)
            + kpi("AS path length", hops, "Hops from observer to origin")
            + '</div>', unsafe_allow_html=True)

# --------------------------------------------------------- topology + route
left, right = st.columns([1.35, 1])
with left:
    st.markdown('<div class="panel"><div class="panel-h">Network topology</div>'
                '<div class="panel-s">The highlighted links are the path AS152 is using right now.</div>'
                + topology_svg(path, status) + '</div>', unsafe_allow_html=True)
with right:
    if isinstance(path, list):
        hop_html = '<span class="hop">AS152</span>'
        for i, a in enumerate(path):
            last = i == len(path) - 1
            hop_html += '<span class="arrow">→</span><span class="hop' + (' origin' if last else '') + '" style="--tone:' + tone + '">AS' + str(a) + '</span>'
    else:
        hop_html = '<span class="hop">AS path unavailable</span>'
    hdr = r.get("route", {}).get("header", r.get("error", "No selected route")) if r.get("route") or r.get("error") else "No selected route"
    st.markdown(
        '<div class="panel"><div class="panel-h">Selected route</div>'
        '<div class="panel-s">Best route chosen by the observer router.</div>'
        '<div class="pathrow">' + hop_html + '</div>'
        '<div class="kv"><span>Prefix</span><span class="mono">' + PREFIX + '</span></div>'
        '<div class="kv"><span>Observer</span><span>AS152</span></div>'
        '<div class="kv"><span>Normal path</span><span>AS150 → AS2 → AS3 → AS152</span></div>'
        '<div class="kv"><span>Attacker peering</span><span>AS151 → AS3</span></div>'
        '<div style="height:10px"></div><div class="codebox">' + esc(hdr) + '</div></div>',
        unsafe_allow_html=True)

# ---------------------------------------------------------- recent polls
ticks = ""
for ts, stt in hist:
    c = "n" if stt == "NORMAL" else ("h" if stt == "HIJACK_ALERT" else "o")
    ticks += '<div class="tick ' + c + '" title="' + ts + ' · ' + stt + '"></div>'
ticks += '<div class="tick empty"></div>' * (60 - len(hist))
st.markdown('<div class="panel"><div class="panel-h">Recent checks</div>'
            '<div class="panel-s">Last 60 polls in this browser session. Green is normal, red is a hijack, amber is an error.</div>'
            '<div class="strip">' + ticks + '</div></div>', unsafe_allow_html=True)

# ------------------------------------------------------------------- tabs
t1, t2, t3, t4, t5 = st.tabs(["Policy", "BGP peers", "Alert history", "Evaluation", "Gallery"])
with t1:
    st.markdown(
        '<div class="panel"><div class="panel-h">Protection policy</div>'
        '<div class="panel-s">Exact-prefix configuration check on AS3. This is not full RPKI validation.</div>'
        '<div class="kv"><span>Protected prefix</span><span class="mono">' + PREFIX + '</span></div>'
        '<div class="kv"><span>Expected origin</span><span>AS' + str(EXPECTED) + '</span></div>'
        '<div class="kv"><span>Filter on AS3 (neighbor AS151)</span><span class="' + filt_cls + '">' + esc(filt) + '</span></div></div>',
        unsafe_allow_html=True)
with t2:
    st.dataframe(peers(), use_container_width=True, hide_index=True)
with t3:
    es = events()
    if es:
        view = [{k: e.get(k) for k in ("timestamp_utc", "prefix", "expected_origin", "observed_origin", "as_path", "status")}
                for e in es[-25:][::-1]]
        st.dataframe(view, use_container_width=True, hide_index=True)
    else:
        st.info("No alerts yet. Events appear here when logs/alerts.jsonl records a change for " + PREFIX + ".")
with t4:
    good = []
    for row in timing_rows():
        try: good.append({"Run": int(row["run"]), "Detection time (s)": float(row["detection_seconds"])})
        except (KeyError, ValueError): pass
    if good:
        vals = [x["Detection time (s)"] for x in good]
        st.markdown('<div class="kpis" style="grid-template-columns:repeat(4,1fr)">'
                    + kpi("Runs", str(len(good)))
                    + kpi("Mean", "%.3f s" % statistics.mean(vals))
                    + kpi("Median", "%.3f s" % statistics.median(vals))
                    + kpi("Fastest / slowest", "%.2f / %.2f s" % (min(vals), max(vals)))
                    + '</div>', unsafe_allow_html=True)
        st.bar_chart(good, x="Run", y="Detection time (s)", color="#5b9dff")
        st.dataframe(good, use_container_width=True, hide_index=True)
    else:
        st.info("No evaluation data found at evidence/evaluation/detection_times.csv.")

with t5:
    gdir = ASSETS / "gallery"
    pics = sorted([f for f in gdir.iterdir() if f.suffix.lower() in EXTS]) if gdir.exists() else []
    if pics:
        cols = st.columns(3)
        for i, f in enumerate(pics):
            cols[i % 3].image(str(f), caption=f.stem.replace("_", " ").replace("-", " "), use_container_width=True)
    else:
        st.info("No pictures yet. Copy images into " + str(gdir) + " and they will show up here.")

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    side_logo = find_img("sidebar") or find_img("logo")
    if side_logo: st.image(str(side_logo), use_container_width=True)
    st.markdown("Signed in as **" + esc(st.session_state.get("auth", "")) + "**", unsafe_allow_html=True)
    if st.button("Sign out", use_container_width=True):
        st.session_state.clear(); st.rerun()
    st.markdown("### Lab setup")
    st.markdown('<div class="kv"><span>Victim</span><span>AS150</span></div>'
                '<div class="kv"><span>Attacker</span><span>AS151</span></div>'
                '<div class="kv"><span>Observer</span><span>AS152</span></div>'
                '<div class="kv"><span>Exchange</span><span>IX100</span></div>', unsafe_allow_html=True)
    st.info("Read-only monitor. It never changes BIRD routes or configuration.")
    st.caption("Set SHADOW_USER and SHADOW_PASS to enable an administrator login. For a local lab, create an account using the sign-up tab.")