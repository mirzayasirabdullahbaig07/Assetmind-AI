"""Shared UI kit for AssetMind inner pages: SVG icons, page header, KPI cards, panels, timeline, chart styling.

Reuse on every page:  from utils.ui_kit import inject_base_css, page_header, kpi_card, panel, style_fig
"""
import html as _html
from contextlib import contextmanager

import streamlit as st

from utils import overview_ui as _ov
from utils.ui_kit_ext import (  # noqa: F401  (re-exported for pages)
    EXT_CSS, badge, entity_header, info_grid, alert, result_count, style_status_df, stepper, quote, section, rank_list,
)

# ---- extra icons (added to the same registry the Overview page uses) ----
_ov._ICONS.update({
    "check": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "xcircle": '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    "trash": '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "pie": '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>',
    "building": '<rect width="16" height="20" x="4" y="2" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
})
icon = _ov.icon

_CSS = """
<style>
@keyframes amFadeUp { from {opacity:0; transform:translateY(14px);} to {opacity:1; transform:translateY(0);} }

/* ---------- Page header ---------- */
.am-ph{position:relative; overflow:hidden; display:flex; align-items:center; gap:18px; padding:26px 30px; border-radius:20px;
  color:#fff; background:linear-gradient(135deg,#0F172A 0%,#1E3A8A 58%,#0E7490 100%);
  box-shadow:0 18px 36px -18px rgba(30,58,138,.55); animation:amFadeUp .45s ease both; margin-bottom:22px;}
.am-ph::before{content:""; position:absolute; right:-70px; top:-90px; width:280px; height:280px; border-radius:50%;
  background:radial-gradient(circle,rgba(56,189,248,.32),transparent 70%);}
.am-ph-ico{position:relative; flex-shrink:0; width:60px; height:60px; border-radius:16px; display:flex; align-items:center;
  justify-content:center; color:#fff; background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.25);}
.am-ph-body{position:relative; min-width:0;}
.am-ph-title{font-size:1.9rem; font-weight:800; line-height:1.15; margin:0; padding:0;
  color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; text-shadow:0 2px 12px rgba(0,0,0,.25);}
.am-ph-sub{margin:4px 0 0 0; font-size:.95rem; color:#E2E8F0 !important;}
.am-ph-badge{position:absolute; right:26px; top:50%; transform:translateY(-50%); display:inline-flex; align-items:center; gap:8px;
  padding:6px 14px; border-radius:999px; font-size:.78rem; font-weight:600; background:rgba(255,255,255,.12);
  border:1px solid rgba(255,255,255,.22); color:#fff;}
.am-ph-badge .dot{width:8px; height:8px; border-radius:50%; background:#34D399; box-shadow:0 0 0 4px rgba(52,211,153,.25);}

/* ---------- KPI cards ---------- */
.am-kpi{--c:#2563EB; position:relative; overflow:hidden; background:#fff; border:1px solid #E2E8F0; border-radius:16px;
  padding:16px 16px 14px 16px; box-shadow:0 1px 2px rgba(15,23,42,.04); animation:amFadeUp .55s ease both;
  transition:transform .25s ease, box-shadow .25s ease, border-color .25s ease;}
.am-kpi::before{content:""; position:absolute; left:0; top:0; right:0; height:3px; background:var(--c);}
.am-kpi:hover{transform:translateY(-5px); box-shadow:0 16px 28px -14px color-mix(in srgb, var(--c) 55%, transparent); border-color:color-mix(in srgb, var(--c) 35%, white);}
.am-kpi-top{display:flex; align-items:center; justify-content:space-between;}
.am-kpi-ico{width:40px; height:40px; border-radius:12px; display:flex; align-items:center; justify-content:center; color:var(--c);
  background:color-mix(in srgb, var(--c) 12%, white); transition:all .3s ease;}
.am-kpi:hover .am-kpi-ico{background:var(--c); color:#fff; transform:rotate(-6deg) scale(1.08);}
.am-kpi-pct{font-size:.72rem; font-weight:700; color:var(--c); background:color-mix(in srgb, var(--c) 10%, white);
  padding:3px 8px; border-radius:999px;}
.am-kpi-val{font-size:2rem; font-weight:800; color:#0F172A; line-height:1; margin:14px 0 4px 0;}
.am-kpi-label{font-size:.82rem; font-weight:600; color:#64748B;}
.am-kpi-bar{height:5px; border-radius:99px; background:#F1F5F9; margin-top:12px; overflow:hidden;}
.am-kpi-bar span{display:block; height:100%; border-radius:99px; background:var(--c);}

/* ---------- Panels (st.container key "panel_*") ---------- */
[class*="st-key-panel_"]{background:#fff; border:1px solid #E2E8F0; border-radius:18px; padding:20px 22px 12px 22px;
  box-shadow:0 1px 2px rgba(15,23,42,.04); animation:amFadeUp .6s ease both; transition:box-shadow .25s ease, border-color .25s ease;}
[class*="st-key-panel_"]:hover{box-shadow:0 14px 28px -16px rgba(15,23,42,.25); border-color:#CBD5E1;}
.am-pt{display:flex; align-items:center; gap:10px; font-size:1.02rem; font-weight:700; color:#0F172A; margin-bottom:4px;}
.am-pt-ico{width:32px; height:32px; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#2563EB;
  background:linear-gradient(135deg,#EFF6FF,#E0F2FE); border:1px solid #DBEAFE;}

/* ---------- Activity timeline ---------- */
.am-tl{position:relative; margin:10px 0 6px 0; padding-left:6px; max-height:430px; overflow-y:auto;}
.am-tl-item{--c:#2563EB; position:relative; display:flex; gap:14px; padding:0 4px 18px 0;}
.am-tl-item::before{content:""; position:absolute; left:9px; top:22px; bottom:0; width:2px; background:#E2E8F0;}
.am-tl-item:last-child::before{display:none;}
.am-tl-dot{flex-shrink:0; width:20px; height:20px; border-radius:50%; margin-top:2px; background:color-mix(in srgb, var(--c) 18%, white);
  border:2px solid var(--c); box-shadow:0 0 0 4px color-mix(in srgb, var(--c) 10%, transparent);}
.am-tl-body{min-width:0; padding:8px 12px; border-radius:12px; flex:1; transition:background .2s ease;}
.am-tl-item:hover .am-tl-body{background:#F8FAFC;}
.am-tl-head{display:flex; flex-wrap:wrap; align-items:center; gap:8px;}
.am-chip{font-size:.74rem; font-weight:700; padding:2px 9px; border-radius:999px; color:#1E3A8A; background:#EFF6FF; border:1px solid #DBEAFE;}
.am-chip.ev{color:var(--c); background:color-mix(in srgb, var(--c) 10%, white); border-color:color-mix(in srgb, var(--c) 25%, white);}
.am-tl-desc{font-size:.87rem; color:#334155; margin:4px 0 2px 0;}
.am-tl-time{font-size:.76rem; color:#94A3B8;}

/* ---------- Empty state ---------- */
.am-empty{display:flex; flex-direction:column; align-items:center; gap:10px; padding:34px 10px; color:#64748B; font-size:.9rem; text-align:center;}
.am-empty .ic{width:52px; height:52px; border-radius:16px; display:flex; align-items:center; justify-content:center; color:#2563EB;
  background:linear-gradient(135deg,#EFF6FF,#E0F2FE); border:1px solid #DBEAFE;}
</style>
"""


def inject_base_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(EXT_CSS, unsafe_allow_html=True)


def page_header(icon_name: str, title: str, subtitle: str, badge: str | None = None) -> None:
    badge_html = f'<span class="am-ph-badge"><span class="dot"></span>{_html.escape(badge)}</span>' if badge else ""
    st.markdown(
        '<div class="am-ph">'
        f'<div class="am-ph-ico">{icon(icon_name, 30)}</div>'
        f'<div class="am-ph-body"><div class="am-ph-title">{_html.escape(title)}</div>'
        f'<p class="am-ph-sub">{_html.escape(subtitle)}</p></div>'
        f'{badge_html}</div>',
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value, icon_name: str, color: str = "#2563EB", total=None, pct=None) -> None:
    pct_html, bar_html = "", ""
    if pct is not None:
        try:
            p = max(0, min(100, round(float(pct))))
            pct_html = f'<span class="am-kpi-pct">{p}%</span>'
            bar_html = f'<div class="am-kpi-bar"><span style="width:{p}%"></span></div>'
        except (TypeError, ValueError):
            pass
    elif total:
        try:
            pct = max(0, min(100, round(float(value) / float(total) * 100)))
            pct_html = f'<span class="am-kpi-pct">{pct}%</span>'
            bar_html = f'<div class="am-kpi-bar"><span style="width:{pct}%"></span></div>'
        except (TypeError, ValueError, ZeroDivisionError):
            pass
    st.markdown(
        f'<div class="am-kpi" style="--c:{color}">'
        f'<div class="am-kpi-top"><div class="am-kpi-ico">{icon(icon_name, 20)}</div>{pct_html}</div>'
        f'<div class="am-kpi-val">{_html.escape(str(value))}</div><div class="am-kpi-label">{_html.escape(label)}</div>{bar_html}</div>',
        unsafe_allow_html=True,
    )


@contextmanager
def panel(key: str, title: str, icon_name: str):
    """White rounded card with an icon title. Use:  with panel('type', 'Assets by Type', 'layers'): ..."""
    with st.container(key=f"panel_{key}"):
        st.markdown(
            f'<div class="am-pt"><span class="am-pt-ico">{icon(icon_name, 18)}</span>{_html.escape(title)}</div>',
            unsafe_allow_html=True,
        )
        yield


def empty_state(text: str, icon_name: str = "info") -> None:
    st.markdown(f'<div class="am-empty"><div class="ic">{icon(icon_name, 24)}</div>{_html.escape(text)}</div>',
                unsafe_allow_html=True)


def style_fig(fig, height: int = 340):
    """Make any Plotly figure match the theme (transparent bg, clean fonts, no duplicate title)."""
    fig.update_layout(
        title=None,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Source Sans Pro, Inter, sans-serif", color="#334155", size=13),
        margin=dict(l=8, r=8, t=10, b=8),
        legend=dict(font=dict(size=12)),
    )
    fig.update_xaxes(gridcolor="#F1F5F9", zeroline=False)
    fig.update_yaxes(gridcolor="#F1F5F9", zeroline=False)
    return fig


_EVENT_COLORS = [
    ("repair", "#8B5CF6"), ("maint", "#F59E0B"), ("damage", "#EF4444"), ("issue", "#EF4444"),
    ("replac", "#0EA5E9"), ("retire", "#64748B"), ("creat", "#16A34A"), ("add", "#16A34A"), ("regist", "#16A34A"),
    ("inspect", "#14B8A6"),
]


def _event_color(event: str) -> str:
    e = (event or "").lower()
    for key, col in _EVENT_COLORS:
        if key in e:
            return col
    return "#2563EB"


def activity_list(items: list[dict]) -> None:
    """items: [{'asset_id':..., 'event':..., 'desc':..., 'date':...}]"""
    rows = []
    for it in items:
        col = _event_color(it.get("event", ""))
        rows.append(
            f'<div class="am-tl-item" style="--c:{col}"><div class="am-tl-dot"></div><div class="am-tl-body">'
            f'<div class="am-tl-head"><span class="am-chip">{_html.escape(str(it.get("asset_id", "")))}</span>'
            f'<span class="am-chip ev">{_html.escape(str(it.get("event", "")))}</span></div>'
            f'<div class="am-tl-desc">{_html.escape(str(it.get("desc") or ""))}</div>'
            f'<div class="am-tl-time">{_html.escape(str(it.get("date", "")))}</div></div></div>'
        )
    st.markdown(f'<div class="am-tl">{"".join(rows)}</div>', unsafe_allow_html=True)