"""Sidebar styling + footer card for AssetMind. Call render_sidebar() in app.py after st.navigation()."""
import html
import streamlit as st
from utils.overview_ui import icon

HACKATHON_NAME = "Global Innovation Build Challenge V2"
TEAM_MEMBERS = ["Hamna Munir", "Mirza Yasir Abdullah Baig"]

_CSS = """
<style>
/* Sidebar shell */
[data-testid="stSidebar"]{background:#FFFFFF; border-right:1px solid #E2E8F0;}

/* Nav links */
[data-testid="stSidebarNavLink"]{border-radius:12px; margin:3px 0; padding:.6rem .8rem; font-weight:600; color:#475569;
  transition:background .2s ease, transform .2s ease, color .2s ease;}
[data-testid="stSidebarNavLink"]:hover{background:#F1F5F9; color:#0F172A; transform:translateX(4px);}
[data-testid="stSidebarNavLink"][aria-current="page"]{
  background:linear-gradient(135deg,#EFF6FF,#E0F2FE); color:#1E3A8A; box-shadow:inset 3px 0 0 #2563EB;}
[data-testid="stSidebarNavLink"][aria-current="page"] span{color:#1E3A8A;}

/* Footer card */
.am-sb{position:relative; overflow:hidden; margin-top:22px; padding:16px 16px 14px 16px; border-radius:16px; color:#fff;
  background:linear-gradient(135deg,#0F172A 0%,#1E3A8A 60%,#0E7490 100%); box-shadow:0 14px 28px -16px rgba(30,58,138,.6);}
.am-sb::before{content:""; position:absolute; right:-40px; top:-50px; width:150px; height:150px; border-radius:50%;
  background:radial-gradient(circle,rgba(56,189,248,.35),transparent 70%);}
.am-sb *{position:relative;}
.am-sb-top{display:flex; align-items:center; gap:10px;}
.am-sb-ico{width:34px; height:34px; border-radius:10px; display:flex; align-items:center; justify-content:center;
  background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.25); color:#fff;}
.am-sb-l{font-size:.64rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#BAE6FD !important;}
.am-sb-t{font-size:.84rem; font-weight:800; line-height:1.25; color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;}
.am-sb-div{height:1px; background:rgba(255,255,255,.16); margin:12px 0 10px 0;}
.am-sb-m{display:flex; align-items:center; gap:8px; font-size:.78rem; color:#E2E8F0 !important; margin-top:6px;}
.am-sb-av{flex-shrink:0; width:22px; height:22px; border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-size:.6rem; font-weight:800; color:#fff; background:linear-gradient(135deg,#2563EB,#14B8A6);}
.am-sb-note{margin:12px 2px 0 2px; font-size:.7rem; line-height:1.45; color:#94A3B8;}
</style>
"""


def _initials(name: str) -> str:
    p = name.split()
    return (p[0][0] + p[-1][0]).upper() if len(p) > 1 else name[:2].upper()


def render_sidebar() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    members = "".join(
        f'<div class="am-sb-m"><span class="am-sb-av">{html.escape(_initials(n))}</span>{html.escape(n)}</div>'
        for n in TEAM_MEMBERS
    )
    with st.sidebar:
        st.markdown(
            '<div class="am-sb"><div class="am-sb-top">'
            f'<div class="am-sb-ico">{icon("layers", 18)}</div>'
            '<div><div class="am-sb-l">Hackathon</div>'
            f'<div class="am-sb-t">{html.escape(HACKATHON_NAME)}</div></div></div>'
            f'<div class="am-sb-div"></div>{members}</div>'
            '<div class="am-sb-note">AI-assisted decision support. A technician makes the final call.</div>',
            unsafe_allow_html=True,
        )