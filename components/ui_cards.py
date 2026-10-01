import streamlit as st


def feature_card(icon, title, description):
    """One feature tile — icon badge, title, description — SaaS-style grid card."""
    st.markdown(f"""
    <div style="
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px;
        padding: 20px; height: 100%; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    ">
        <div style="
            width: 44px; height: 44px; border-radius: 10px;
            background: linear-gradient(135deg, #EFF6FF, #ECFEFF);
            display: flex; align-items: center; justify-content: center;
            font-size: 22px; margin-bottom: 12px;
        ">{icon}</div>
        <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 6px;">{title}</div>
        <div style="font-size: 0.88rem; color: #64748B; line-height: 1.5;">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def metric_tile(label, value, icon=None, accent="#2563EB"):
    """A styled metric card — replaces st.metric for a sharper dashboard look."""
    icon_html = f'<span style="margin-right:6px;">{icon}</span>' if icon else ""
    st.markdown(f"""
    <div style="
        background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px;
        padding:16px 18px; box-shadow:0 1px 3px rgba(15,23,42,0.04);
        border-top: 3px solid {accent};
    ">
        <div style="font-size:0.78rem; font-weight:600; color:#64748B; text-transform:uppercase; letter-spacing:0.03em;">
            {icon_html}{label}
        </div>
        <div style="font-size:1.8rem; font-weight:800; color:#0F172A; margin-top:4px;">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def page_header(icon, title, subtitle=None):
    """Consistent icon-badge header block used at the top of every page."""
    subtitle_html = f'<div style="color:#64748B; font-size:0.95rem; margin-top:3px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom: 24px;">
        <div style="
            width:48px; height:48px; border-radius:12px;
            background:linear-gradient(135deg,#EFF6FF,#ECFEFF);
            border:1px solid #DBEAFE;
            display:flex; align-items:center; justify-content:center;
            font-size:23px; flex-shrink:0;
            box-shadow:0 1px 3px rgba(15,23,42,0.06);
        ">{icon}</div>
        <div>
            <div style="font-size:1.65rem; font-weight:800; color:#0F172A; line-height:1.2;">{title}</div>
            {subtitle_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(icon, title, subtitle=None):
    """Smaller icon-badge header for sub-sections within a page (below the main page_header)."""
    subtitle_html = f'<div style="color:#94A3B8; font-size:0.82rem; margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; margin: 22px 0 14px 0;">
        <div style="
            width:34px; height:34px; border-radius:9px;
            background:#F1F5F9; border:1px solid #E2E8F0;
            display:flex; align-items:center; justify-content:center;
            font-size:16px; flex-shrink:0;
        ">{icon}</div>
        <div>
            <div style="font-size:1.1rem; font-weight:700; color:#0F172A;">{title}</div>
            {subtitle_html}
        </div>
    </div>
    """, unsafe_allow_html=True)