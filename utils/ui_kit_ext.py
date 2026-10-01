"""Extra UI pieces for list/detail/form pages (Assets, Maintenance, ...). Imported via utils.ui_kit."""
import html as _html

from utils import overview_ui as _ov

_ov._ICONS.update({
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "plus": '<path d="M5 12h14"/><path d="M12 5v14"/>',
    "ticket": '<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v2"/><path d="M13 17v2"/><path d="M13 11v2"/>',
    "history": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
    "recycle": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    "mappin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    "image": '<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
    "note": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
})
icon = _ov.icon

EXT_CSS = """
<style>
/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"]{gap:6px; background:#F1F5F9; padding:5px; border-radius:14px; border-bottom:none;}
.stTabs [data-baseweb="tab"]{height:42px; padding:0 22px; border-radius:10px; font-weight:600; color:#64748B; background:transparent;}
.stTabs [data-baseweb="tab"][aria-selected="true"]{background:#fff; color:#1E3A8A; box-shadow:0 1px 3px rgba(15,23,42,.14);}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"]{display:none;}

/* ---------- Buttons ---------- */
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,#2563EB,#0EA5E9); border:none; color:#fff; border-radius:10px; font-weight:600;
  padding:.5rem 1.3rem; transition:transform .2s ease, box-shadow .2s ease;}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover{
  transform:translateY(-2px); box-shadow:0 10px 20px -8px rgba(37,99,235,.6); color:#fff;}
.stButton > button[kind="secondary"], .stButton > button[data-testid="stBaseButton-secondary"]{
  border-radius:10px; font-weight:600; border:1px solid #CBD5E1; transition:all .2s ease;}
.stButton > button[kind="secondary"]:hover, .stButton > button[data-testid="stBaseButton-secondary"]:hover{
  border-color:#2563EB; color:#2563EB; transform:translateY(-1px);}

/* ---------- Inputs ---------- */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"]{border-radius:10px !important;}

/* ---------- Badges ---------- */
.am-pill{--c:#64748B; display:inline-flex; align-items:center; gap:6px; padding:3px 11px; border-radius:999px; font-size:.76rem;
  font-weight:700; color:var(--c); background:color-mix(in srgb, var(--c) 12%, white); border:1px solid color-mix(in srgb, var(--c) 28%, white);}
.am-pill::before{content:""; width:6px; height:6px; border-radius:50%; background:var(--c);}

/* ---------- Entity header ---------- */
.am-eh{display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; background:#fff;
  border:1px solid #E2E8F0; border-radius:18px; padding:18px 22px; margin:6px 0 16px 0; box-shadow:0 1px 2px rgba(15,23,42,.04);
  animation:amFadeUp .5s ease both;}
.am-eh-title{font-size:1.45rem; font-weight:800; color:#0F172A; margin:8px 0 0 0; line-height:1.2;}
.am-eh-badges{display:flex; gap:8px; flex-wrap:wrap;}

/* ---------- Info grid ---------- */
.am-ig{display:grid; grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:12px; margin:8px 0 6px 0;}
.am-it{padding:12px 14px; border-radius:12px; background:#F8FAFC; border:1px solid #EEF2F7; transition:all .2s ease;}
.am-it:hover{background:#EFF6FF; border-color:#DBEAFE; transform:translateY(-2px);}
.am-it-l{font-size:.7rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase; color:#94A3B8;}
.am-it-v{font-size:.95rem; font-weight:600; color:#0F172A; margin-top:4px; word-break:break-word;}

/* ---------- Alerts ---------- */
.am-al{--c:#2563EB; display:flex; gap:12px; align-items:flex-start; padding:12px 16px; border-radius:12px; margin:10px 0;
  font-size:.9rem; color:#1E293B; background:color-mix(in srgb, var(--c) 8%, white); border:1px solid color-mix(in srgb, var(--c) 25%, white);}
.am-al svg{color:var(--c); flex-shrink:0; margin-top:1px;}

/* ---------- Result count ---------- */
.am-count{font-size:.9rem; color:#64748B; margin:16px 2px 8px 2px;}
.am-count b{color:#0F172A; font-size:1.05rem;}

/* ---------- Stepper ---------- */
.am-stp{display:flex; margin:10px 0 8px 0;}
.am-stp-i{flex:1; position:relative; text-align:center; min-width:0;}
.am-stp-i:not(:first-child)::before{content:""; position:absolute; top:17px; left:-50%; width:100%; height:3px; background:#E2E8F0; z-index:0;}
.am-stp-i.done:not(:first-child)::before, .am-stp-i.active:not(:first-child)::before{background:linear-gradient(90deg,#2563EB,#0EA5E9);}
.am-stp-c{position:relative; z-index:1; width:36px; height:36px; margin:0 auto; border-radius:50%; display:flex; align-items:center;
  justify-content:center; font-weight:700; font-size:.85rem; background:#F1F5F9; color:#94A3B8; border:3px solid #F1F5F9; transition:all .25s ease;}
.am-stp-i.done .am-stp-c{background:linear-gradient(135deg,#2563EB,#0EA5E9); border-color:transparent; color:#fff;}
.am-stp-i.active .am-stp-c{background:#fff; border-color:#2563EB; color:#2563EB; box-shadow:0 0 0 6px rgba(37,99,235,.14);}
.am-stp-l{margin-top:8px; font-size:.8rem; font-weight:600; color:#94A3B8; padding:0 4px;}
.am-stp-i.done .am-stp-l{color:#334155;}
.am-stp-i.active .am-stp-l{color:#1E3A8A; font-weight:800;}

/* ---------- Quote ---------- */
.am-q{border-left:4px solid #2563EB; background:#F8FAFC; padding:14px 18px; border-radius:0 12px 12px 0; color:#1E293B;
  font-size:.95rem; line-height:1.6; margin:10px 0 6px 0;}
.am-q-l{font-size:.7rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase; color:#94A3B8; margin-bottom:4px;}

/* ---------- Expander ---------- */
[data-testid="stExpander"]{border:1px solid #E2E8F0 !important; border-radius:14px !important; background:#fff; margin-bottom:10px; overflow:hidden;
  transition:box-shadow .2s ease, border-color .2s ease;}
[data-testid="stExpander"]:hover{border-color:#BFDBFE !important; box-shadow:0 8px 20px -14px rgba(37,99,235,.45);}
[data-testid="stExpander"] summary{font-weight:600;}

/* ---------- Section heading (no box) ---------- */
.am-sec{display:flex; align-items:center; gap:10px; font-size:1.1rem; font-weight:700; color:#0F172A; margin:24px 0 12px 0;}

/* ---------- Before/after ---------- */
.am-arrow{width:48px; height:48px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:110px auto 0 auto;
  color:#fff; background:linear-gradient(135deg,#2563EB,#0EA5E9); box-shadow:0 8px 18px -6px rgba(37,99,235,.55);}

/* ---------- Ranking list ---------- */
.am-rk{--c:#2563EB; display:flex; flex-direction:column; gap:14px; margin:12px 0 6px 0;}
.am-rk-i{display:flex; align-items:center; gap:12px;}
.am-rk-n{flex-shrink:0; width:28px; height:28px; border-radius:9px; display:flex; align-items:center; justify-content:center; font-size:.78rem;
  font-weight:800; color:var(--c); background:color-mix(in srgb, var(--c) 12%, white);}
.am-rk-i:first-child .am-rk-n{background:var(--c); color:#fff;}
.am-rk-b{flex:1; min-width:0;}
.am-rk-h{display:flex; justify-content:space-between; gap:8px; font-size:.86rem; margin-bottom:5px;}
.am-rk-l{font-weight:600; color:#1E293B; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}
.am-rk-v{font-weight:800; color:#0F172A;}
.am-rk-t{height:7px; border-radius:99px; background:#F1F5F9; overflow:hidden;}
.am-rk-t span{display:block; height:100%; border-radius:99px; background:linear-gradient(90deg,var(--c),color-mix(in srgb, var(--c) 55%, white));}

/* ---------- Download buttons ---------- */
[data-testid="stDownloadButton"] button{background:linear-gradient(135deg,#2563EB,#0EA5E9); color:#fff; border:none; border-radius:10px; font-weight:600;
  padding:.5rem 1.3rem; transition:transform .2s ease, box-shadow .2s ease;}
[data-testid="stDownloadButton"] button:hover{transform:translateY(-2px); box-shadow:0 10px 20px -8px rgba(37,99,235,.6); color:#fff;}
</style>
"""

_BADGE_COLORS = {
    "active": "#16A34A", "good": "#16A34A", "resolved": "#16A34A", "closed": "#16A34A", "completed": "#16A34A", "low": "#16A34A",
    "maintenance required": "#F59E0B", "needs attention": "#F59E0B", "medium": "#F59E0B", "open": "#F59E0B", "pending": "#F59E0B",
    "damaged": "#EF4444", "high": "#EF4444", "critical": "#DC2626",
    "under repair": "#8B5CF6", "in progress": "#8B5CF6",
    "retired": "#64748B", "fair": "#0EA5E9",
    "reviewing": "#0EA5E9", "repair approved": "#14B8A6", "replacement requested": "#F97316", "replaced": "#0EA5E9",
}
_ALERT = {
    "info": ("#2563EB", "info"), "warning": ("#F59E0B", "alert"),
    "danger": ("#EF4444", "xcircle"), "success": ("#16A34A", "check"),
}


def badge_color(text) -> str:
    return _BADGE_COLORS.get(str(text or "").strip().lower(), "#64748B")


def badge(text) -> str:
    return f'<span class="am-pill" style="--c:{badge_color(text)}">{_html.escape(str(text or "—"))}</span>'


def entity_header(chip: str, title: str, badges: list) -> None:
    """Detail-page header: ID chip + big title on the left, status badges on the right."""
    import streamlit as st
    pills = "".join(badge(b) for b in badges if b)
    st.markdown(
        '<div class="am-eh"><div>'
        f'<span class="am-chip">{_html.escape(str(chip))}</span>'
        f'<div class="am-eh-title">{_html.escape(str(title))}</div></div>'
        f'<div class="am-eh-badges">{pills}</div></div>',
        unsafe_allow_html=True,
    )


def info_grid(items: dict, badge_keys=()) -> None:
    import streamlit as st
    tiles = []
    for label, value in items.items():
        val = badge(value) if label in badge_keys else _html.escape(str(value if value not in (None, "") else "—"))
        tiles.append(f'<div class="am-it"><div class="am-it-l">{_html.escape(str(label))}</div><div class="am-it-v">{val}</div></div>')
    st.markdown(f'<div class="am-ig">{"".join(tiles)}</div>', unsafe_allow_html=True)


def alert(kind: str, text: str, icon_name: str | None = None, html: bool = False) -> None:
    import streamlit as st
    color, default_icon = _ALERT.get(kind, _ALERT["info"])
    body = text if html else _html.escape(text)
    st.markdown(
        f'<div class="am-al" style="--c:{color}">{icon(icon_name or default_icon, 20)}<div>{body}</div></div>',
        unsafe_allow_html=True,
    )


def result_count(n: int, noun: str = "asset(s)") -> None:
    import streamlit as st
    st.markdown(f'<div class="am-count"><b>{n}</b> {noun} found</div>', unsafe_allow_html=True)


def style_status_df(df, cols):
    """Colour status-like columns in a dataframe (works with st.dataframe)."""
    def _fn(v):
        c = badge_color(v)
        return f"background-color:{c}22; color:{c}; font-weight:600;"
    styler = df.style
    mapper = getattr(styler, "map", None) or styler.applymap
    cols = [c for c in cols if c in df.columns]
    return mapper(_fn, subset=cols) if cols else styler


def stepper(steps: list, current: int, finished: bool = False) -> None:
    """Horizontal progress stepper. current = index of active step; finished=True marks every step done."""
    import streamlit as st
    items = []
    for i, label in enumerate(steps):
        if finished or i < current:
            state, inner = "done", icon("check", 18, 2.6)
        elif i == current:
            state, inner = "active", str(i + 1)
        else:
            state, inner = "todo", str(i + 1)
        items.append(
            f'<div class="am-stp-i {state}"><div class="am-stp-c">{inner}</div>'
            f'<div class="am-stp-l">{_html.escape(label)}</div></div>'
        )
    st.markdown(f'<div class="am-stp">{"".join(items)}</div>', unsafe_allow_html=True)


def quote(text: str, label: str = "Issue") -> None:
    import streamlit as st
    st.markdown(
        f'<div class="am-q"><div class="am-q-l">{_html.escape(label)}</div>{_html.escape(str(text or "—"))}</div>',
        unsafe_allow_html=True,
    )


def section(title: str, icon_name: str = "info") -> None:
    """Unboxed section heading with an icon tile."""
    import streamlit as st
    st.markdown(
        f'<div class="am-sec"><span class="am-pt-ico">{icon(icon_name, 18)}</span>{_html.escape(title)}</div>',
        unsafe_allow_html=True,
    )


def rank_list(rows, color: str = "#2563EB") -> None:
    """Ranked horizontal-bar list. rows: [(label, value), ...] already sorted high -> low."""
    import streamlit as st
    rows = [(r[0], r[1]) for r in rows]
    try:
        top = max(float(v) for _, v in rows) or 1.0
    except (TypeError, ValueError):
        top = 1.0
    items = []
    for i, (label, value) in enumerate(rows, 1):
        try:
            width = max(4, round(float(value) / top * 100))
        except (TypeError, ValueError):
            width = 4
        items.append(
            f'<div class="am-rk-i"><div class="am-rk-n">{i}</div><div class="am-rk-b">'
            f'<div class="am-rk-h"><span class="am-rk-l">{_html.escape(str(label))}</span>'
            f'<span class="am-rk-v">{_html.escape(str(value))}</span></div>'
            f'<div class="am-rk-t"><span style="width:{width}%"></span></div></div></div>'
        )
    st.markdown(f'<div class="am-rk" style="--c:{color}">{"".join(items)}</div>', unsafe_allow_html=True)