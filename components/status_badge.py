import streamlit as st

STATUS_COLORS = {
    "Active": "#16A34A",
    "Maintenance Required": "#F59E0B",
    "Damaged": "#EF4444",
    "Under Repair": "#8B5CF6",
    "Retired": "#64748B",
    "Open": "#F59E0B",
    "Reviewing": "#3B82F6",
    "Repair Approved": "#8B5CF6",
    "Resolved": "#16A34A",
    "Replacement Requested": "#EF4444",
    "Replaced": "#14B8A6",
    "Closed": "#64748B",
}


def status_badge_html(status):
    color = STATUS_COLORS.get(status, "#64748B")
    return (
        f"<span style='background-color:{color}22; color:{color}; "
        f"padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:600;'>"
        f"{status}</span>"
    )


def render_status_badge(status):
    st.markdown(status_badge_html(status), unsafe_allow_html=True)