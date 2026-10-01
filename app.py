import streamlit as st
from database.db import init_db
from database.seed import seed_database
from utils.theme import apply_global_theme
from utils.overview_ui import (
    inject_overview_css, hero, workflow, section_title, feature_card, tip,
)
from utils.sidebar import render_sidebar
import config

st.set_page_config(
    page_title="AssetMind — Nexora Technologies",
    page_icon="assets/icon.svg",
    layout="wide",
)

apply_global_theme()
init_db()
seed_database()

st.logo("assets/logo.svg", icon_image="assets/icon.svg", size="large")


# ---- Pages are defined first so overview cards can link to them ----
def overview_page():
    inject_overview_css()

    hero(
        "Smart Office Asset Memory & Maintenance System — track every asset from first day to final replacement.",
        config.COMPANY_NAME,
    )

    workflow([
        "Physical object", "Digital identity", "Visual evidence", "Condition",
        "Maintenance", "Repair", "Replacement", "Historical memory",
    ])

    section_title("Explore modules")

    cards = [
        ("dashboard", "dashboard", "Dashboard", "Live overview of all 280 assets — status, type, and department breakdowns."),
        ("assets", "assets", "Assets", "Search, filter, and open any asset's full profile and history timeline."),
        ("maintenance", "maintenance", "Maintenance", "Report issues, manage tickets, repair and replacement workflows."),
        ("inspection", "inspection", "AI Inspection", "AI-assisted visual condition analysis — decision support, not diagnosis."),
        ("ask", "ask", "Ask AssetMind", "Natural-language questions, answered from real database results."),
        ("reports", "reports", "Reports", "Monthly maintenance reports with CSV and PDF export."),
        ("qr", "qr", "QR Assets", "Generate, download, and look up assets by QR code or manual ID."),
        ("settings", "settings", "Settings", "API status, database info, and demo data reset."),
    ]

    for start in (0, 4):
        cols = st.columns(4, gap="medium")
        for col, (key, ico, title, desc) in zip(cols, cards[start:start + 4]):
            with col:
                feature_card(key, ico, title, desc, PAGES[key])
        st.write("")

    tip("Click any card or use the sidebar to navigate between sections.")


PAGES = {
    "dashboard": st.Page("pages/1_Dashboard.py", title="Dashboard", icon=":material/space_dashboard:", url_path="dashboard"),
    "assets": st.Page("pages/2_Assets.py", title="Assets", icon=":material/inventory_2:", url_path="assets"),
    "maintenance": st.Page("pages/3_Maintenance.py", title="Maintenance", icon=":material/build:", url_path="maintenance"),
    "inspection": st.Page("pages/4_AI_Inspection.py", title="AI Inspection", icon=":material/photo_camera:", url_path="ai-inspection"),
    "ask": st.Page("pages/5_Ask_AssetMind.py", title="Ask AssetMind", icon=":material/smart_toy:", url_path="ask-assetmind"),
    "reports": st.Page("pages/6_Reports.py", title="Reports", icon=":material/bar_chart:", url_path="reports"),
    "qr": st.Page("pages/7_QR_Assets.py", title="QR Assets", icon=":material/qr_code_2:", url_path="qr-assets"),
    "settings": st.Page("pages/8_Settings.py", title="Settings", icon=":material/settings:", url_path="settings"),
}

overview = st.Page(overview_page, title="Overview", icon=":material/home:", default=True)

nav = st.navigation([overview, *PAGES.values()])
render_sidebar()
nav.run()