import streamlit as st


def render_timeline(history_rows):
    """
    history_rows: list of AssetHistory objects, ordered oldest -> newest.
    """
    if not history_rows:
        st.info("No history recorded yet for this asset.")
        return

    for event in history_rows:
        date_str = event.created_at.strftime("%d %b %Y") if event.created_at else "—"
        st.markdown(
            f"""
            <div style="border-left: 3px solid #2563EB; background:#F8FAFC; padding: 10px 14px; margin-bottom: 12px; border-radius: 0 8px 8px 0;">
                <div style="color:#64748B; font-size: 0.8rem;">{date_str}</div>
                <div style="font-weight: 600; color:#0F172A;">{event.event_type}</div>
                <div style="color:#334155; font-size: 0.9rem;">{event.description or ''}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )