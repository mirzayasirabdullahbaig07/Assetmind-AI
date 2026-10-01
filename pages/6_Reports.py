import calendar
import io
import streamlit as st
import pandas as pd
from datetime import date
from database.db import init_db, get_session
from database.seed import seed_database
from services.report_service import generate_monthly_report
from utils.pdf_export import build_monthly_report_pdf
from utils.ui_kit import (
    inject_base_css, page_header, panel, empty_state, alert, kpi_card,
    section, rank_list, style_status_df,
)
import config

init_db()
seed_database()
inject_base_css()

page_header(
    "reports", "Reports",
    "Monthly maintenance report — all figures calculated directly from the database.",
    badge=config.COMPANY_NAME,
)

# ---------------------------------------------------------------- period
today = date.today()
years = list(range(2022, today.year + 1))
with panel("rep_period", "Report Period", "search"):
    col_a, col_b = st.columns(2, gap="medium")
    month = col_a.selectbox("Month", list(range(1, 13)), index=today.month - 1,
                            format_func=lambda m: calendar.month_name[m])
    year = col_b.selectbox("Year", years, index=len(years) - 1)

session = get_session()
try:
    report = generate_monthly_report(session, month=month, year=year)
finally:
    session.close()

section(f"Report for {calendar.month_name[month]} {year}", "reports")

# ---------------------------------------------------------------- KPIs
total = report["total_tickets"]
k1, k2, k3, k4, k5 = st.columns(5, gap="small")
with k1: kpi_card("Total Tickets", total, "ticket", "#2563EB")
with k2: kpi_card("Open Tickets", report["open_tickets"], "alert", "#F59E0B", total=total)
with k3: kpi_card("Resolved Tickets", report["resolved_tickets"], "check", "#16A34A", total=total)
with k4: kpi_card("Repair Cost", f"Rs. {report['repair_costs']:,.0f}", "maintenance", "#8B5CF6")
with k5: kpi_card("Replacement Cost", f"Rs. {report['replacement_costs']:,.0f}", "recycle", "#0EA5E9")

st.write("")

# ---------------------------------------------------------------- rankings
col1, col2, col3 = st.columns(3, gap="medium")
with col1:
    with panel("rep_types", "Most Problematic Asset Types", "layers"):
        if report["most_problematic_types"]:
            rank_list(report["most_problematic_types"], "#EF4444")
        else:
            empty_state("No data for this period.", "layers")

with col2:
    with panel("rep_depts", "Departments with Most Issues", "building"):
        if report["top_departments"]:
            rank_list(report["top_departments"], "#F59E0B")
        else:
            empty_state("No data for this period.", "building")

with col3:
    with panel("rep_repaired", "Frequently Repaired Assets", "maintenance"):
        if report["frequently_repaired"]:
            rank_list(report["frequently_repaired"], "#8B5CF6")
        else:
            empty_state("No data for this period.", "maintenance")

st.write("")

# ---------------------------------------------------------------- tickets table
with panel("rep_tickets", "Tickets This Period", "ticket"):
    if report["ticket_rows"]:
        df = pd.DataFrame(report["ticket_rows"])
        st.dataframe(style_status_df(df, ["Status", "Priority"]), use_container_width=True, hide_index=True)

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            "Download CSV",
            data=csv_buffer.getvalue(),
            file_name=f"assetmind_report_{year}_{month:02d}.csv",
            mime="text/csv",
            icon=":material/download:",
        )
    else:
        empty_state("No tickets recorded for this period.", "ticket")

st.write("")

# ---------------------------------------------------------------- PDF export
pdf_key = f"pdf_{year}_{month:02d}"
with panel("rep_pdf", "Export as PDF", "note"):
    st.caption(f"A formatted PDF of the {calendar.month_name[month]} {year} report, ready to share or print.")
    b1, b2 = st.columns([1, 1], gap="small")
    with b1:
        if st.button("Generate PDF Report", icon=":material/picture_as_pdf:"):
            with st.spinner("Building PDF..."):
                pdf = build_monthly_report_pdf(report, company_name=config.COMPANY_NAME)
            st.session_state[pdf_key] = pdf.getvalue() if hasattr(pdf, "getvalue") else pdf
    with b2:
        if pdf_key in st.session_state:
            st.download_button(
                "Download PDF",
                data=st.session_state[pdf_key],
                file_name=f"assetmind_report_{year}_{month:02d}.pdf",
                mime="application/pdf",
                icon=":material/download:",
            )