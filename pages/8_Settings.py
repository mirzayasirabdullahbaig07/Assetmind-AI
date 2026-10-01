import html
import streamlit as st
from database.db import init_db, get_session
from database.seed import seed_database
from database.models import Asset
from utils.ui_kit import (
    inject_base_css, page_header, panel, alert, kpi_card, info_grid, icon,
)
import config

# ---- Hackathon details (edit here) ----
HACKATHON_NAME = "Global Innovation Build Challenge V2"
TEAM_MEMBERS = ["Hamna Munir", "Mirza Yasir Abdullah Baig"]

init_db()
seed_database()
inject_base_css()

st.markdown("""
<style>
/* Danger zone panel */
.st-key-panel_danger{border-color:#FECACA !important; background:linear-gradient(180deg,#FFF5F5,#FFFFFF) !important;}
.st-key-panel_danger .am-pt-ico{color:#DC2626; background:#FEE2E2; border-color:#FECACA;}

/* Hackathon banner */
.am-hack{position:relative; overflow:hidden; display:flex; align-items:center; gap:16px; padding:20px 24px; border-radius:16px; margin:6px 0 16px 0;
  background:linear-gradient(135deg,#0F172A 0%,#1E3A8A 60%,#0E7490 100%); color:#fff;}
.am-hack::before{content:""; position:absolute; right:-60px; top:-70px; width:220px; height:220px; border-radius:50%;
  background:radial-gradient(circle,rgba(56,189,248,.32),transparent 70%);}
.am-hack-ico{position:relative; flex-shrink:0; width:52px; height:52px; border-radius:14px; display:flex; align-items:center; justify-content:center;
  background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.25); color:#fff;}
.am-hack-l{position:relative; font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#BAE6FD !important;}
.am-hack-t{position:relative; font-size:1.35rem; font-weight:800; line-height:1.25; margin-top:2px; color:#FFFFFF !important;
  -webkit-text-fill-color:#FFFFFF !important;}

/* Team cards */
.am-team{display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:12px; margin:8px 0 14px 0;}
.am-tm{display:flex; align-items:center; gap:14px; padding:14px 16px; border-radius:14px; background:#F8FAFC; border:1px solid #EEF2F7;
  transition:all .25s ease;}
.am-tm:hover{background:#EFF6FF; border-color:#BFDBFE; transform:translateY(-3px); box-shadow:0 14px 24px -16px rgba(37,99,235,.5);}
.am-tm-av{flex-shrink:0; width:46px; height:46px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800;
  color:#fff; background:linear-gradient(135deg,#2563EB,#14B8A6);}
.am-tm-n{font-weight:700; color:#0F172A; line-height:1.25;}
.am-tm-r{font-size:.78rem; color:#94A3B8; margin-top:2px;}

.am-lbl{font-size:.72rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:#94A3B8; margin:14px 0 4px 0;}
.am-about{color:#334155; font-size:.93rem; line-height:1.7;}
</style>
""", unsafe_allow_html=True)

page_header(
    "settings", "Settings",
    "API status, database info, and demo data management.",
    badge=config.COMPANY_NAME,
)

# ---------------------------------------------------------------- API status
with panel("set_api", "Groq API Status", "activity"):
    if config.GROQ_API_KEY:
        masked = (config.GROQ_API_KEY[:6] + "..." + config.GROQ_API_KEY[-4:]
                  if len(config.GROQ_API_KEY) > 12 else "configured")
        alert("success", f"<b>GROQ_API_KEY is configured</b> ({html.escape(masked)})", html=True)
    else:
        alert("danger", "<b>GROQ_API_KEY is not set.</b> Add it to your <code>.env</code> file (local) "
                        "or Streamlit Secrets (deployment).", html=True)

    info_grid({
        "Text Model": config.GROQ_TEXT_MODEL,
        "Vision Model": config.GROQ_VISION_MODEL,
    })

st.write("")

# ---------------------------------------------------------------- database
session = get_session()
try:
    total_assets = session.query(Asset).count()
finally:
    session.close()

with panel("set_db", "Database Info", "layers"):
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        kpi_card("Database File", "assetmind.db", "layers", "#2563EB")
    with c2:
        kpi_card("Total Assets", total_assets, "assets", "#0D9488")

st.write("")

# ---------------------------------------------------------------- reset
if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False

with panel("danger", "Reset Demo Data", "trash"):
    alert(
        "warning",
        "This will <b>permanently delete</b> all assets, employees, tickets, inspections, and history, then "
        "regenerate fresh Nexora Technologies demo data. <b>This cannot be undone.</b>",
        html=True,
    )

    if not st.session_state.confirm_reset:
        if st.button("Reset Demo Data", icon=":material/delete:"):
            st.session_state.confirm_reset = True
            st.rerun()
    else:
        alert("danger", "Are you sure? Type <b>RESET</b> below to confirm.", html=True)
        confirm_text = st.text_input("Confirmation", placeholder="RESET")
        col_a, col_b = st.columns(2, gap="small")
        with col_a:
            if st.button("Confirm Reset", type="primary", icon=":material/check_circle:",
                         disabled=(confirm_text != "RESET"), use_container_width=True):
                session = get_session()
                try:
                    seed_database(reset=True)
                    st.toast("Demo data has been reset and regenerated.", icon="✅")
                except Exception as e:
                    alert("danger", f"Reset failed: {html.escape(str(e))}", html=True)
                finally:
                    session.close()
                st.session_state.confirm_reset = False
                st.rerun()
        with col_b:
            if st.button("Cancel", use_container_width=True):
                st.session_state.confirm_reset = False
                st.rerun()

st.write("")

# ---------------------------------------------------------------- about
def _initials(name: str) -> str:
    parts = name.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else name[:2].upper()


with panel("set_about", "About AssetMind", "info"):
    st.markdown(
        f'<div class="am-hack"><div class="am-hack-ico">{icon("layers", 26)}</div><div>'
        '<div class="am-hack-l">Hackathon Project</div>'
        f'<div class="am-hack-t">{html.escape(HACKATHON_NAME)}</div></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="am-about"><b>AssetMind</b> is a digital memory and lifecycle system for physical office assets, '
        f'built for <b>{html.escape(config.COMPANY_NAME)}</b>.<br><br>'
        'It connects: Physical object → Digital identity → Visual evidence → Condition → Maintenance → Repair → '
        'Replacement → Historical memory.<br><br>'
        'AI features in this app are <b>AI-assisted decision support</b> — visual inspection and natural-language '
        'database queries. The system never claims perfect damage detection, automatic hardware diagnosis, or fully '
        'autonomous repair decisions. A technician or manager always makes the final call.</div>',
        unsafe_allow_html=True,
    )

    cards = "".join(
        f'<div class="am-tm"><div class="am-tm-av">{html.escape(_initials(n))}</div>'
        f'<div><div class="am-tm-n">{html.escape(n)}</div><div class="am-tm-r">Team Member</div></div></div>'
        for n in TEAM_MEMBERS
    )
    st.markdown(f'<div class="am-lbl">Team</div><div class="am-team">{cards}</div>', unsafe_allow_html=True)