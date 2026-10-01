import streamlit as st
from database.db import init_db, get_session
from database.seed import seed_database
from services.asset_service import (
    get_dashboard_metrics,
    get_type_distribution,
    get_status_distribution,
    get_department_distribution,
    get_recent_activity,
)
from components.charts import (
    type_distribution_chart,
    status_distribution_chart,
    department_distribution_chart,
)
from utils.ui_kit import (
    inject_base_css, page_header, kpi_card, panel, style_fig, activity_list, empty_state,
)
import config

init_db()
seed_database()
inject_base_css()

page_header(
    "dashboard", "Dashboard",
    "Live overview of every asset — status, type and department at a glance.",
    badge=config.COMPANY_NAME,
)

session = get_session()
try:
    metrics = get_dashboard_metrics(session)
    type_counts = get_type_distribution(session)
    status_counts = get_status_distribution(session)
    dept_counts = get_department_distribution(session)
    recent = get_recent_activity(session, limit=8)
finally:
    session.close()

# --- KPI row ---
total = metrics["total"]
kpis = [
    ("Total Assets", metrics["total"], "assets", "#2563EB", None),
    ("Active", metrics["active"], "check", "#16A34A", total),
    ("Maintenance Req.", metrics["maintenance_required"], "alert", "#F59E0B", total),
    ("Damaged", metrics["damaged"], "xcircle", "#EF4444", total),
    ("Under Repair", metrics["under_repair"], "maintenance", "#8B5CF6", total),
    ("Retired", metrics["retired"], "trash", "#64748B", total),
]
for col, (label, value, ico, color, tot) in zip(st.columns(6, gap="small"), kpis):
    with col:
        kpi_card(label, value, ico, color, total=tot)

st.write("")

# --- Charts row ---
col1, col2 = st.columns(2, gap="medium")
with col1:
    with panel("type", "Assets by Type", "layers"):
        fig = type_distribution_chart(type_counts)
        if fig:
            st.plotly_chart(style_fig(fig), use_container_width=True)
        else:
            empty_state("No asset type data available.", "layers")

with col2:
    with panel("status", "Status Distribution", "pie"):
        fig = status_distribution_chart(status_counts)
        if fig:
            st.plotly_chart(style_fig(fig), use_container_width=True)
        else:
            empty_state("No status data available.", "pie")

st.write("")

# --- Department chart + recent activity ---
col_a, col_b = st.columns([3, 2], gap="medium")
with col_a:
    with panel("dept", "Assets by Department", "building"):
        fig = department_distribution_chart(dept_counts)
        if fig:
            st.plotly_chart(style_fig(fig, height=430), use_container_width=True)
        else:
            empty_state("No department data available.", "building")

with col_b:
    with panel("recent", "Recent Activity", "activity"):
        if not recent:
            empty_state("No activity recorded yet.", "clock")
        else:
            items = []
            for history, asset in recent:
                date_str = history.created_at.strftime("%d %b %Y, %I:%M %p") if history.created_at else "—"
                items.append({
                    "asset_id": asset.asset_id,
                    "event": history.event_type,
                    "desc": history.description,
                    "date": date_str,
                })
            activity_list(items)