# streamlit_app.py -- place this at project root (next to the src/ folder)
# --- THEME: Neon Sunset (eye-catching, high-contrast, glassmorphism + motion)
# --- UPDATED: Improved font visibility and enhanced select/multiselect styling
import sys
from pathlib import Path
import importlib
import traceback
import os
import json
import time
import random

# -------------------------
# Client-side animation HTML (complete document)
# New theme: Neon Sunset — bold gradients, soft blur, animated glow
# Fonts: Poppins + Inter (improved weights and fallbacks) — increased legibility
# -------------------------
ANIM_HTML = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&family=Inter:wght@300;400;600&display=swap');
    :root{
      --bg-1: #0f1724; /* deep navy */
      --bg-2: #ff6b6b; /* coral */
      --bg-3: #f6d365; /* warm yellow */
      --glass: rgba(255,255,255,0.06);
      --accent: #ff6b6b; /* coral */
      --accent-2: #ffa800; /* amber */
      --muted: rgba(255,255,255,0.78);
      --text: #f8fbff;
    }
    *{ box-sizing: border-box; }
    body { margin:0; font-family: Poppins, Inter, system-ui, -apple-system; background: radial-gradient(1200px 600px at 10% 20%, rgba(255,107,107,0.09), transparent), radial-gradient(1000px 500px at 90% 80%, rgba(255,168,0,0.06), transparent), linear-gradient(180deg,var(--bg-1), #071426); color: var(--text); font-size:15px; }
    .wrap { max-width:1200px; margin:22px auto; padding:20px; }
    .panel { background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02)); border-radius:14px; padding:18px; box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.04); backdrop-filter: blur(6px) saturate(120%); }
    .title { display:flex; align-items:center; gap:14px; }
    .brand { font-weight:800; color:var(--accent); font-size:18px; letter-spacing:0.6px; text-shadow: 0 6px 18px rgba(255,107,107,0.12); }
    .subtitle { color:var(--muted); font-size:12px; margin-left:auto; }

    /* Monospace ASCII — larger, high contrast */
    .ascii { white-space:pre; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, 'Roboto Mono', monospace; font-size:13px; color:var(--text); filter: drop-shadow(0 6px 24px rgba(255,107,107,0.06)); }
    .typing { color:#fff3e6; font-weight:700; font-size:14px; }

    .progress { height:12px; background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border-radius:999px; overflow:hidden; border: 1px solid rgba(255,255,255,0.03); }
    .progress > i { display:block; height:100%; width:0%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); border-radius:999px; transition: width 160ms linear; box-shadow: 0 8px 30px rgba(255,107,107,0.14); }

    .controls { display:flex; gap:10px; }
    .btn { padding:10px 14px; border-radius:12px; background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02)); color:var(--accent); font-weight:800; cursor:pointer; border:1px solid rgba(255,255,255,0.04); box-shadow: 0 8px 20px rgba(11,24,40,0.45); }
    .btn.ghost { background:transparent; color:var(--muted); border:1px dashed rgba(255,255,255,0.03); }
    .log { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:12px; border-radius:10px; font-family: ui-monospace, monospace; color:#f8fbff; max-height:260px; overflow:auto; border:1px solid rgba(255,255,255,0.03); }

    .glow { position:relative; }
    .glow:before { content:''; position:absolute; inset:-40px -40px; background: radial-gradient(ellipse at center, rgba(255,107,107,0.06), transparent 20%); filter: blur(30px); pointer-events:none; }

    /* Make buttons and controls more tappable on mobile */
    @media (max-width:780px){ .wrap { padding:12px; } .title { flex-direction:column; align-items:flex-start; gap:8px; } .btn{ padding:12px 16px; font-size:15px; } }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="panel glow">
      <div class="title">
        <div class="brand">PAYBUDDY • Neon Toolkit</div>
        <div class="subtitle">Neon Sunset • Session: DEV</div>
      </div>

      <div style="margin-top:14px; display:flex; gap:18px; align-items:flex-start;">
        <div style="flex:2">
          <div class="ascii" id="ascii">PAYBUDDY</div>
          <div style="margin-top:8px;" class="typing" id="boot"></div>
          <div style="margin-top:12px;" class="progress"><i id="bar"></i></div>
        </div>
        <div style="flex:1">
          <div style="display:flex; flex-direction:column; gap:10px;">
            <button class="btn" id="play">Start</button>
            <button class="btn" id="stop">Stop</button>
            <button class="btn ghost" id="clear">Clear</button>
            <div style="font-size:12px; color:var(--muted);">Demo controls</div>
          </div>
        </div>
      </div>

      <div style="margin-top:12px;" class="log" id="log">[idle] — hit Start to see live demo output</div>
    </div>
  </div>

<script>
(function(){
  const ascii = [' ██████╗  █████╗ ██╗   ██╗██╗   ██╗██████╗ ██╗   ██╗', '██╔════╝ ██╔══██╗██║   ██║██║   ██║██╔══██╗██║   ██║', '██║  ███╗███████║██║   ██║██║   ██║██████╔╝██║   ██║', '██║   ██║██╔══██║╚██╗ ██╔╝╚██╗ ██╔╝██╔═══╝ ██║   ██║', '╚██████╔╝██║  ██║ ╚████╔╝  ╚████╔╝ ██║     ╚██████╔╝', ' ╚═════╝ ╚═╝  ╚═╝  ╚═══╝    ╚═══╝  ╚═╝      ╚═════╝'].join('\n');
  document.getElementById('ascii').textContent = ascii;

  const bootLines = [
    'Igniting neon rails...',
    'Applying runtime shaders...',
    'Syncing telemetry...',
    'Systems nominal — enjoy the glow.'
  ];

  const bootEl = document.getElementById('boot');
  const bar = document.getElementById('bar');
  const log = document.getElementById('log');
  const play = document.getElementById('play');
  const stop = document.getElementById('stop');
  const clear = document.getElementById('clear');

  let timer = null; let progress = 0;

  function tick(){
    const now = new Date().toLocaleTimeString();
    const msg = ['NEON','DBG','OK','WARN'][Math.floor(Math.random()*4)];
    const samples = ['Cache primed','Shader warmed','Artifact stored','Probe queued','UI frame rendered'];
    const line = `${now} [${msg}] — ${samples[Math.floor(Math.random()*samples.length)]}`;
    log.innerHTML = line + '<br>' + log.innerHTML;
    if (log.childNodes.length>140) log.removeChild(log.lastChild);
    progress = Math.min(100, progress + (Math.random()*12));
    bar.style.width = progress + '%';
    if (progress>=100) { clearInterval(timer); timer=null; }
  }

  play.addEventListener('click', ()=>{ if (timer) return; progress=0; bar.style.width='0%'; bootEl.textContent = bootLines.join(' '); timer = setInterval(tick, 320); });
  stop.addEventListener('click', ()=>{ if (timer) clearInterval(timer); timer=null; });
  clear.addEventListener('click', ()=>{ log.innerHTML='[cleared]'; progress=0; bar.style.width='0%'; });
})();
</script>
</body>
</html>
"""

# -------------------------
# Ensure src/ is importable
# -------------------------
ROOT = Path(__file__).parent.resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# -------------------------
# Safe import helper
# -------------------------
def safe_import(module_name):
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        class _M:
            pass
        m = _M()
        m.__error__ = e
        return m

scanner = safe_import("scanner")
auth_test = safe_import("auth_test")
stress_mod = safe_import("stress")
footprint = safe_import("footprint")
pcap_mod = safe_import("pcap")
reporting = safe_import("reporting")
logger_mod = safe_import("logger")

# -------------------------
# Map expected function names
# -------------------------
def get_callable(mod, *names, fallback=None):
    for n in names:
        if hasattr(mod, n):
            return getattr(mod, n)
    return fallback

run_scan = get_callable(scanner, "run_scan", "sync_port_scan",
                        fallback=lambda *a, **k: {"error":"scanner module missing"})

sync_port_scan = get_callable(scanner, "sync_port_scan", fallback=run_scan)

check_password_strength = get_callable(auth_test, "check_password_strength", "policy_check",
                                       fallback=lambda pw: {"error":"auth module missing"})
simulate_hash_check = get_callable(auth_test, "simulate_hash_check", "offline_hash_check",
                                   fallback=lambda lst: {"error":"auth module missing"})

run_stress_test = get_callable(stress_mod, "run_stress_test", "stress_test",
                              fallback=lambda url, clients, duration: ({"error":"stress module missing"}, None))

run_directory_finder = get_callable(footprint, "run_directory_finder", "check_paths",
                                    fallback=lambda url: {"error":"footprint missing"})
run_subdomain_finder = get_callable(
    footprint, "run_subdomain_finder", "probe_subdomains",
    fallback=lambda domain: {"error": "footprint missing"}
)

capture_packets = get_callable(
    pcap_mod, "capture_packets", "capture_scapy",
    fallback=lambda *a, **k: (None, {"error": "pcap missing"})
)

analyze_pcap = get_callable(
    pcap_mod, "analyze_pcap_file",
    fallback=lambda *a, **k: {"error": "pcap missing"}
)

generate_json_summary = get_callable(
    reporting, "generate_json_summary", "generate_manifest",
    fallback=lambda: {"error": "reporting missing"}
)

generate_docx_report = get_callable(
    reporting, "generate_docx_report",
    fallback=lambda: {"error": "reporting missing"}
)

read_log_tail = get_callable(
    logger_mod, "read_log_tail", "tail_logs",
    fallback=lambda n=200: "No logs available (logger module missing)"
)

# -------------------------
# Streamlit UI
# -------------------------
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PayBuddy Toolkit — Neon", layout="wide")

# -------------------------
# GLOBAL Theme CSS (Neon Sunset)
# -------------------------
st.markdown(
    """
<style>
:root{ --bg: #071426; --muted: rgba(255,255,255,0.85); --accent: #ff6b6b; --accent-2:#ffa800; }
[data-testid="stAppViewContainer"] { background: linear-gradient(180deg, rgba(11,18,36,0.8), rgba(7,20,38,1)); color: #e9f7ff; font-family: Poppins, Inter, system-ui, -apple-system; font-size:15px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border-right: 1px solid rgba(255,255,255,0.03); }
h1,h2,h3{ color: #ffffff !important; }
.stButton>button{ background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); color: var(--accent); border:1px solid rgba(255,255,255,0.04); box-shadow: 0 8px 28px rgba(0,0,0,0.6); border-radius:12px; padding:0.6em 1em; font-weight:800; }
.stButton>button:hover{ transform: translateY(-2px); }
input, textarea, [role="textbox"]{ background: rgba(255,255,255,0.02); color: #fff !important; border: 1px solid rgba(255,255,255,0.03) !important; font-family: Poppins, Inter, system-ui; font-weight:600; }
.stCodeBlock pre, code{ background: rgba(255,255,255,0.02) !important; color: #f9fafb !important; border-left: 6px solid var(--accent); padding:12px; border-radius:8px; }
.panel{ background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(10,18,30,0.25)); padding:16px; border-radius:14px; box-shadow: 0 12px 40px rgba(0,0,0,0.6); }
.badge{ display:inline-block; background: linear-gradient(90deg, rgba(255,107,107,0.08), rgba(255,168,0,0.06)); border:1px solid rgba(255,255,255,0.03); color:var(--accent); padding:8px 14px; border-radius:999px; font-weight:800; }

/* Improve legibility for select/multiselect and option boxes */
/* Streamlit uses different DOM across versions; target common elements */
div[role="listbox"], select, .stSelectbox, .stMultiSelect, .css-1v3fvcr, .css-1szy77t { 
  background: rgba(255,255,255,0.02) !important;
  color: #ffffff !important;
  font-family: Poppins, Inter, system-ui, -apple-system !important;
  font-weight:700 !important;
  font-size:14px !important;
  border-radius:10px !important;
  padding:8px 10px !important;
  border: 1px solid rgba(255,255,255,0.04) !important;
}

/* Dropdown caret and focus improvements */
[role="listbox"]:focus, select:focus, .stSelectbox:focus { outline: 2px solid rgba(255,107,107,0.18) !important; box-shadow: 0 6px 24px rgba(255,107,107,0.06) !important; }

/* Increase spacing for multi-select chips */
.css-1n76uvr, .stMultiSelect { gap:8px !important; }

/* Make sidebar select labels clearer */
[data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] select { font-size:14px !important; font-weight:700 !important; }

/* Accessibility: ensure contrast and larger hit targets */
button, select, input, textarea { min-height:40px; }

</style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Render animation
# -------------------------
components.html(ANIM_HTML, height=420, scrolling=True)

# -------------------------
# Evidence directories
# -------------------------
EVIDENCE_DIR = ROOT / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = EVIDENCE_DIR / "outputs"; OUTPUT_DIR.mkdir(exist_ok=True)
PCAP_DIR = EVIDENCE_DIR / "pcaps"; PCAP_DIR.mkdir(exist_ok=True)
SS_DIR = EVIDENCE_DIR / "screenshots"; SS_DIR.mkdir(exist_ok=True)

# -------------------------
# Sidebar Legal Training Targets
# -------------------------
st.sidebar.markdown("## 🧪 Legal Training Targets")

DEMO_URL = "https://local-demo.paybuddy.test"

legal_targets = {
    "Local Demo": DEMO_URL,
    "OWASP Juice Shop": "https://juice-shop.herokuapp.com",
    "WebGoat": "https://webgoat.herokuapp.com/WebGoat",
    "bWAPP": "http://www.itsecgames.com/",
    "DVWA (local)": "http://localhost/dvwa",
    "Metasploitable 2 (local VM)": "http://192.168.56.101",
}

selected_label = st.sidebar.selectbox("Choose a legal test target", list(legal_targets.keys()))
selected_url = legal_targets[selected_label]

st.sidebar.markdown("---")
st.sidebar.warning("⚠ Use this toolkit only on systems you own or have explicit permission to test.")
st.sidebar.markdown("---")

# -------------------------
# Diagnostics
# -------------------------
with st.expander("Diagnostics (backend import errors)"):
    for name, mod in [
        ("scanner", scanner), ("auth_test", auth_test), ("stress", stress_mod),
        ("footprint", footprint), ("pcap", pcap_mod), ("reporting", reporting),
        ("logger", logger_mod)
    ]:
        if hasattr(mod, "__error__"):
            st.warning(f"Module '{name}' import failed: {mod.__error__}")
            tb = "".join(traceback.format_exception_only(type(mod.__error__), mod.__error__))
            st.code(tb)
        else:
            st.success(f"Module '{name}' loaded")

menu = st.sidebar.selectbox(
    "Module",
    [
        "Dashboard", "Port Scanner", "Password Assessment", "Stress Tester",
        "Footprint", "Packet Capture", "Reporting", "Evidence", "Toolkit Logs"
    ],
)

# -------------------------
# Dashboard
# -------------------------
if menu == "Dashboard":
    st.header("Toolkit Overview")
    st.markdown("### 🔧 Features (based on loaded backend modules)")
    st.markdown(
        """
- Port scanner (**run_scan / sync_port_scan**)  
- Password assessment (**check_password_strength / policy_check**)  
- Stress tester (**run_stress_test / stress_test**)  
- Footprint (**check_paths / probe_subdomains**)  
- Packet capture (**capture_scapy / pyshark**)  
- Reporting (**generate_json_summary / generate_docx_report**)  
        """
    )
    st.info("If a module is missing you will see a warning in Diagnostics above.")
    st.success("Console online — choose a module from the left panel.")

    st.markdown("### Live Console (Python-updated preview)")
    if st.button("Emit sample log"):
        t = time.strftime("%H:%M:%S", time.gmtime(time.time()))
        st.write(f"{t} [INFO] -- Sample log emitted from Python backend")

# -------------------------
# Port Scanner
# -------------------------
elif menu == "Port Scanner":
    st.header("Port Scanner")
    target = st.text_input("Target (IP or hostname)", selected_url)
    ports = st.text_input("Ports (comma separated)", "22,80,443")
    max_workers = st.slider("Max workers", 1, 200, 50)

    if st.button("Start Scan"):
        try:
            ports_list = [int(p.strip()) for p in ports.split(",") if p.strip()]
        except Exception:
            st.error("Invalid ports list")
            ports_list = []
        if ports_list:
            with st.spinner("Scanning..."):
                res = run_scan(target, ports_list, max_workers=max_workers)
            st.json(res)

            safe_target = target.replace(":", "_").replace("/", "_")
            out = OUTPUT_DIR / f"scan_{int(time.time())}_{safe_target}.json"
            with open(out, "w") as f:
                json.dump(res, f, indent=2)
            st.success(f"Saved result to {out}")

# -------------------------
# Password Assessment
# -------------------------
elif menu == "Password Assessment":
    st.header("Password assessment")
    pw = st.text_input("Password", type="password")
    if st.button("Check strength"):
        res = check_password_strength(pw)
        st.json(res)

    st.markdown("---")
    st.subheader("Offline hash simulation")
    file = st.file_uploader("Upload hash list (.txt)", type=["txt"])
    if file and st.button("Simulate hash check"):
        hashes = file.getvalue().decode("utf-8").splitlines()
        out = simulate_hash_check(hashes)
        st.json(out)
        outpath = OUTPUT_DIR / f"hashsim_{int(time.time())}.json"
        with open(outpath, "w") as fp:
            json.dump(out, fp, indent=2)
        st.success(f"Saved to {outpath}")

# -------------------------
# Stress Tester
# -------------------------
elif menu == "Stress Tester":
    st.header("Stress Tester (lab only)")
    url = st.text_input("Target URL", selected_url)
    clients = st.number_input("Clients", 1, 200, 20)
    duration = st.number_input("Duration (s)", 1, 120, 5)

    if st.button("Run test"):
        with st.spinner("Running..."):
            try:
                out = run_stress_test(url, clients, duration)
                if isinstance(out, tuple):
                    summary, fig = out
                else:
                    summary, fig = out, None
            except Exception as e:
                summary, fig = {"error": str(e)}, None

        st.json(summary)
        if fig:
            try:
                st.image(fig)
            except Exception:
                st.text(f"Plot saved at: {fig}")

# -------------------------
# Footprint
# -------------------------
elif menu == "Footprint":
    st.header("Footprint")
    base = st.text_input("Base URL", selected_url)
    domain = st.text_input("Domain", selected_url)

    if st.button("Run path check"):
        with st.spinner("Running path checks..."):
            res = run_directory_finder(base)
        st.json(res)

    if st.button("Probe subs"):
        with st.spinner("Probing subs..."):
            res = run_subdomain_finder(domain)
        st.json(res)

# -------------------------
# Packet Capture
# -------------------------
elif menu == "Packet Capture":
    st.header("Packet capture")
    secs = st.slider("Duration (s)", 1, 60, 5)

    if st.button("Capture"):
        with st.spinner("Capturing..."):
            pcap_file, summary = capture_packets(secs)
        st.success(f"PCAP saved: {pcap_file}")
        st.json(summary)

# -------------------------
# Reporting
# -------------------------
elif menu == "Reporting":
    st.header("Reporting")
    if st.button("Generate manifest (JSON)"):

        out = generate_json_summary()
        st.success(f"Generated: {out}")

    if st.button("Generate DOCX"):
        out = generate_docx_report()
        st.success(f"Generated: {out}")

# -------------------------
# Evidence
# -------------------------
elif menu == "Evidence":
    st.header("Evidence files")
    files = []
    for p in EVIDENCE_DIR.glob("**/*"):
        if p.is_file():
            files.append(str(p.relative_to(ROOT)))
    st.write(files)

# -------------------------
# Toolkit Logs
# -------------------------
elif menu == "Toolkit Logs":
    st.header("Toolkit logs (tail)")
    tail = read_log_tail()
    if isinstance(tail, (dict, list)):
        st.json(tail)
    else:
        st.code(str(tail))
