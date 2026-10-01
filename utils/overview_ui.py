"""Overview page UI helpers for AssetMind: inline SVG icons, CSS, hero, workflow, clickable cards."""
import streamlit as st

# ---------- Lucide-style inline SVG icons (no emojis, no external files) ----------
_ICONS = {
    "dashboard": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "assets": '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "maintenance": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "inspection": '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>',
    "ask": '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
    "reports": '<line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/>',
    "qr": '<rect width="5" height="5" x="3" y="3" rx="1"/><rect width="5" height="5" x="16" y="3" rx="1"/><rect width="5" height="5" x="3" y="16" rx="1"/><path d="M21 16h-3a2 2 0 0 0-2 2v3"/><path d="M21 21v.01"/><path d="M12 7v3a2 2 0 0 1-2 2H7"/><path d="M3 12h.01"/><path d="M12 3h.01"/><path d="M12 16v.01"/><path d="M16 12h1"/><path d="M21 12v.01"/><path d="M12 21v-1"/>',
    "settings": '<line x1="21" x2="14" y1="4" y2="4"/><line x1="10" x2="3" y1="4" y2="4"/><line x1="21" x2="12" y1="12" y2="12"/><line x1="8" x2="3" y1="12" y2="12"/><line x1="21" x2="16" y1="20" y2="20"/><line x1="12" x2="3" y1="20" y2="20"/><line x1="14" x2="14" y1="2" y2="6"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="16" x2="16" y1="18" y2="22"/>',
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "chevron": '<path d="m9 18 6-6-6-6"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7l10-5z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
}


def icon(name: str, size: int = 24, stroke: float = 1.9) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" '
        f'stroke-linejoin="round">{_ICONS[name]}</svg>'
    )


# ---------- CSS ----------
_CSS = """
<style>
@keyframes amFadeUp { from {opacity:0; transform:translateY(14px);} to {opacity:1; transform:translateY(0);} }
@keyframes amFloat  { 0%,100% {transform:translateY(0);} 50% {transform:translateY(-8px);} }

/* Hero */
.am-hero{
  position:relative; overflow:hidden; border-radius:20px; padding:36px 40px; color:#fff;
  background:linear-gradient(135deg,#0F172A 0%,#1E3A8A 55%,#0E7490 100%);
  box-shadow:0 20px 40px -18px rgba(30,58,138,.55); animation:amFadeUp .5s ease both;
}
.am-hero::before{content:""; position:absolute; right:-80px; top:-80px; width:320px; height:320px; border-radius:50%;
  background:radial-gradient(circle,rgba(56,189,248,.35),transparent 70%);}
.am-hero::after{content:""; position:absolute; right:120px; bottom:-120px; width:260px; height:260px; border-radius:50%;
  background:radial-gradient(circle,rgba(45,212,191,.25),transparent 70%);}
.am-hero-icon{position:absolute; right:48px; top:50%; margin-top:-56px; width:112px; height:112px; color:rgba(255,255,255,.18);
  animation:amFloat 5s ease-in-out infinite;}
.am-badge{display:inline-flex; align-items:center; gap:8px; padding:6px 14px; border-radius:999px; font-size:.78rem;
  font-weight:600; letter-spacing:.04em; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.22);}
.am-badge .dot{width:8px; height:8px; border-radius:50%; background:#34D399; box-shadow:0 0 0 4px rgba(52,211,153,.25);}
.am-hero .am-title{position:relative; font-size:2.6rem; font-weight:800; margin:16px 0 6px 0; padding:0; line-height:1.15;
  color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; text-shadow:0 2px 12px rgba(0,0,0,.25);}
.am-hero .am-sub{position:relative; margin:0; color:#E2E8F0 !important; font-size:1.02rem; max-width:640px;}

/* Workflow */
.am-flow{margin:22px 0 30px 0; padding:18px 22px; background:#fff; border:1px solid #E2E8F0; border-radius:16px;
  box-shadow:0 1px 2px rgba(15,23,42,.04); animation:amFadeUp .6s ease both;}
.am-flow-title{display:flex; align-items:center; gap:8px; font-weight:700; color:#0F172A; font-size:.95rem; margin-bottom:12px;}
.am-flow-title svg{color:#2563EB;}
.am-steps{display:flex; flex-wrap:wrap; align-items:center; gap:6px;}
.am-step{display:inline-flex; align-items:center; gap:8px; padding:7px 14px; border-radius:999px; font-size:.84rem; font-weight:600;
  color:#1E3A8A; background:#EFF6FF; border:1px solid #DBEAFE; transition:all .2s ease;}
.am-step:hover{background:#2563EB; color:#fff; border-color:#2563EB; transform:translateY(-2px);}
.am-step b{display:inline-flex; align-items:center; justify-content:center; width:20px; height:20px; border-radius:50%;
  background:#2563EB; color:#fff; font-size:.7rem;}
.am-step:hover b{background:#fff; color:#2563EB;}
.am-chev{color:#94A3B8; display:inline-flex;}

/* Section label */
.am-section{font-size:1.05rem; font-weight:700; color:#0F172A; margin:6px 0 14px 0;}

/* Clickable feature cards (st.container with key "fc_*") */
[class*="st-key-fc_"]{
  position:relative; background:#fff; border:1px solid #E2E8F0; border-radius:18px; padding:22px 22px 18px 22px;
  min-height:235px; gap:0 !important; cursor:pointer; overflow:hidden;
  box-shadow:0 1px 2px rgba(15,23,42,.04); animation:amFadeUp .6s ease both;
  transition:transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
[class*="st-key-fc_"]::before{content:""; position:absolute; left:0; top:0; right:0; height:3px;
  background:linear-gradient(90deg,#2563EB,#14B8A6); transform:scaleX(0); transform-origin:left; transition:transform .3s ease;}
[class*="st-key-fc_"]:hover{transform:translateY(-6px); border-color:#BFDBFE; box-shadow:0 18px 32px -14px rgba(37,99,235,.35);}
[class*="st-key-fc_"]:hover::before{transform:scaleX(1);}

/* Make the whole card the link: every wrapper becomes static, the <a> itself covers the card */
[class*="st-key-fc_"] [data-testid="stElementContainer"],
[class*="st-key-fc_"] [data-testid="element-container"],
[class*="st-key-fc_"] [data-testid="stLayoutWrapper"],
[class*="st-key-fc_"] [data-testid="stPageLink"]{position:static !important; margin:0 !important;}
[class*="st-key-fc_"] [data-testid="stPageLink"] a,
[class*="st-key-fc_"] a[data-testid="stPageLink-NavLink"]{
  position:absolute !important; inset:0 !important; width:100% !important; height:100% !important;
  z-index:10; opacity:0; padding:0 !important; margin:0 !important; display:block !important; cursor:pointer;}

.am-ico{width:52px; height:52px; border-radius:14px; display:flex; align-items:center; justify-content:center;
  color:#2563EB; background:linear-gradient(135deg,#EFF6FF,#E0F2FE); border:1px solid #DBEAFE; transition:all .3s ease;}
[class*="st-key-fc_"]:hover .am-ico{color:#fff; background:linear-gradient(135deg,#2563EB,#0EA5E9); border-color:transparent; transform:rotate(-6deg) scale(1.08);}
.am-card-title{font-size:1.08rem; font-weight:700; color:#0F172A; margin:16px 0 6px 0;}
.am-card-desc{font-size:.88rem; line-height:1.55; color:#64748B; margin:0 0 14px 0;}
.am-open{display:inline-flex; align-items:center; gap:6px; font-size:.82rem; font-weight:600; color:#2563EB; opacity:.0; transform:translateX(-6px);
  transition:all .25s ease;}
[class*="st-key-fc_"]:hover .am-open{opacity:1; transform:translateX(0);}

/* Tip bar */
.am-tip{display:flex; align-items:center; gap:12px; margin-top:26px; padding:14px 18px; border-radius:14px; color:#1E40AF;
  background:#EFF6FF; border:1px solid #DBEAFE; font-size:.92rem; animation:amFadeUp .8s ease both;}
.am-tip svg{flex-shrink:0; color:#2563EB;}
</style>
"""


def inject_overview_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def hero(subtitle: str, company: str) -> None:
    html = (
        '<div class="am-hero">'
        f'<div class="am-hero-icon">{icon("assets", 112, 1.2)}</div>'
        f'<span class="am-badge"><span class="dot"></span>{company}</span>'
        '<div class="am-title">Welcome to AssetMind</div>'
        f'<p class="am-sub">{subtitle}</p>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def workflow(steps: list[str]) -> None:
    parts = []
    for i, s in enumerate(steps, 1):
        parts.append(f'<span class="am-step"><b>{i}</b>{s}</span>')
        if i < len(steps):
            parts.append(f'<span class="am-chev">{icon("chevron", 16, 2.2)}</span>')
    html = (
        '<div class="am-flow">'
        f'<div class="am-flow-title">{icon("layers", 18)}A digital memory and lifecycle system for physical office assets</div>'
        f'<div class="am-steps">{"".join(parts)}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def section_title(text: str) -> None:
    st.markdown(f'<div class="am-section">{text}</div>', unsafe_allow_html=True)


def feature_card(key: str, icon_name: str, title: str, desc: str, page) -> None:
    """Clickable card: whole card navigates to `page` (an st.Page object)."""
    with st.container(key=f"fc_{key}"):
        st.markdown(
            f'<div class="am-ico">{icon(icon_name, 26)}</div>'
            f'<div class="am-card-title">{title}</div>'
            f'<p class="am-card-desc">{desc}</p>'
            f'<span class="am-open">Open {icon("arrow", 15, 2.2)}</span>',
            unsafe_allow_html=True,
        )
        st.page_link(page, label="Open")


def tip(text: str) -> None:
    st.markdown(f'<div class="am-tip">{icon("info", 20)}<span>{text}</span></div>', unsafe_allow_html=True)