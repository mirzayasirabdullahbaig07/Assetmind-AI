import streamlit as st


def apply_global_theme():
    """Injects the shared AssetMind SaaS theme. Call right after st.set_page_config() on every page."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ---------- Hide default Streamlit chrome ---------- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] { background: transparent; }
    div[data-testid="stToolbar"] {visibility: hidden; height: 0;}
    div[data-testid="stDecoration"] {display: none;}

    /* Hide Streamlit's AUTO-GENERATED page nav — we render our own below */
    section[data-testid="stSidebarNav"] { display: none; }

    /* ---------- Page background ---------- */
    .stApp { background-color: #F8FAFC; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }

    /* ---------- Typography ---------- */
    h1 { font-weight: 800 !important; color: #0F172A !important; letter-spacing: -0.02em; }
    h2, h3 { font-weight: 700 !important; color: #0F172A !important; letter-spacing: -0.01em; }
    p, label, .stMarkdown { color: #334155; }

    /* ---------- Sidebar shell ---------- */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    section[data-testid="stSidebar"] > div { padding-top: 1.2rem; }

    /* ---------- Custom nav (st.page_link) styling ---------- */
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] {
        margin: 2px 8px;
        border-radius: 8px;
        transition: all 0.15s ease;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] a {
        padding: 9px 12px !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        color: #475569 !important;
        border-radius: 8px;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] a:hover {
        background-color: #EFF6FF !important;
        color: #2563EB !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] a[aria-current="page"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] a[aria-current="page"] span,
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] a[aria-current="page"] p {
        color: #FFFFFF !important;
    }

    /* ---------- Buttons ---------- */
    div.stButton > button, div.stDownloadButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.15s ease;
        border: 1px solid #E2E8F0 !important;
    }
    div.stButton > button[kind="primary"], div.stDownloadButton > button[kind="primary"] {
        background-color: #2563EB !important;
        border: none !important;
        color: #FFFFFF !important;
        box-shadow: 0 1px 2px rgba(37, 99, 235, 0.3);
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
        transform: translateY(-1px);
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #2563EB !important;
        color: #2563EB !important;
    }

    /* ---------- Metrics ---------- */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600 !important; color: #64748B !important; font-size: 0.8rem !important;
        text-transform: uppercase; letter-spacing: 0.03em;
    }
    div[data-testid="stMetricValue"] { font-weight: 800 !important; color: #0F172A !important; }

    /* ---------- Tabs ---------- */
    button[data-baseweb="tab"] { font-weight: 600; color: #64748B; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #2563EB !important; }
    div[data-baseweb="tab-highlight"] { background-color: #2563EB !important; }

    /* ---------- Alerts / Expander / Tables / Inputs ---------- */
    div[data-testid="stAlert"] { border-radius: 10px; border: 1px solid transparent; }
    details { border-radius: 10px !important; border: 1px solid #E2E8F0 !important; }
    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #E2E8F0; }
    div[data-baseweb="select"] > div, input, textarea { border-radius: 8px !important; }
    hr { margin: 1.5rem 0 !important; border-color: #E2E8F0 !important; }
    
        /* ---------- Bigger sidebar logo ---------- */
    section[data-testid="stSidebar"] img {
        max-height: 42px !important;
        width: auto !important;
    }

    /* ---------- Bigger nav icons ---------- */
    section[data-testid="stSidebar"] div[data-testid="stPageLink"] a {
        padding: 11px 14px !important;
        font-size: 0.95rem !important;
    }
    section[data-testid="stSidebar"] [data-testid="stIconMaterial"] {
        font-size: 1.4rem !important;
    }
    section[data-testid="stSidebar"] span[class*="material"] {
        font-size: 1.4rem !important;
    }
    
    </style>
    """, unsafe_allow_html=True)