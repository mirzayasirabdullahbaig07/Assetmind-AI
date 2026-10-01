import html
import streamlit as st
import pandas as pd
from datetime import date
from database.db import init_db, get_session
from database.seed import seed_database
from services.asset_service import (
    search_and_filter_assets, get_asset_by_asset_id, get_asset_history,
    get_all_asset_types, get_all_department_names,
    get_all_departments, get_all_locations, get_all_employees,
    create_asset, get_replacement_links,
)
from services.maintenance_service import get_tickets_for_asset
from components.timeline import render_timeline
from utils.validators import validate_new_asset_form
from utils.ui_kit import (
    inject_base_css, page_header, panel, empty_state, entity_header, info_grid,
    alert, result_count, style_status_df,
)
import config

init_db()
seed_database()
inject_base_css()

page_header(
    "assets", "Assets", "Search, filter, and manage every tracked asset",
    badge=config.COMPANY_NAME,
)

if "selected_asset_id" not in st.session_state:
    st.session_state.selected_asset_id = None


# ---------------------------------------------------------------- profile
def show_profile(asset_id_str):
    session = get_session()
    try:
        asset = get_asset_by_asset_id(session, asset_id_str)
        if not asset:
            alert("danger", "Asset not found.")
            return

        if st.button("Back to Assets", icon=":material/arrow_back:"):
            st.session_state.selected_asset_id = None
            st.rerun()

        entity_header(asset.asset_id, asset.name, [asset.status, asset.condition])

        col1, col2 = st.columns([1, 2], gap="medium")
        with col1:
            with panel("photo", "Asset Photo", "image"):
                if asset.image_path:
                    try:
                        st.image(asset.image_path, use_container_width=True)
                    except Exception:
                        empty_state("Image not available.", "image")
                else:
                    empty_state("No image uploaded yet.", "image")

        with col2:
            with panel("details", "Asset Details", "assets"):
                info = {
                    "Type": asset.asset_type, "Brand": asset.brand, "Model": asset.model,
                    "Department": asset.department.name if asset.department else "—",
                    "Location": asset.location.name if asset.location else "—",
                    "Assigned Employee": asset.employee.name if asset.employee else "Unassigned",
                    "Purchase Date": asset.purchase_date.strftime("%d %b %Y") if asset.purchase_date else "—",
                    "Purchase Cost": f"Rs. {asset.purchase_cost:,.0f}" if asset.purchase_cost else "—",
                    "Warranty End": asset.warranty_end.strftime("%d %b %Y") if asset.warranty_end else "—",
                    "Condition": asset.condition, "Status": asset.status,
                }
                info_grid(info, badge_keys=("Status", "Condition"))

                if asset.warranty_end and asset.warranty_end < date.today():
                    alert("warning", "Warranty Expired")
                if asset.status == "Retired":
                    alert("danger", "This asset is retired and cannot be assigned or reused.")
                if asset.notes:
                    alert("info", f"Notes: {asset.notes}", icon_name="note")

        replaced_by_asset, replacement_for_asset = get_replacement_links(session, asset.id)
        if replaced_by_asset:
            alert("info", f"This asset was replaced by <b>{html.escape(replaced_by_asset.asset_id)}</b>.",
                  icon_name="recycle", html=True)
        if replacement_for_asset:
            alert("info", f"This asset is a replacement for <b>{html.escape(replacement_for_asset.asset_id)}</b>.",
                  icon_name="recycle", html=True)

        st.write("")
        with panel("tickets", "Maintenance Tickets", "ticket"):
            tickets = get_tickets_for_asset(session, asset.id)
            if not tickets:
                empty_state("No tickets for this asset yet.", "ticket")
            else:
                ticket_rows = [{
                    "Ticket": t.ticket_id, "Status": t.status, "Priority": t.priority,
                    "Issue": t.issue_description, "Repair Cost": t.repair_cost or "—",
                } for t in tickets]
                df = pd.DataFrame(ticket_rows)
                st.dataframe(style_status_df(df, ["Status", "Priority"]),
                             use_container_width=True, hide_index=True)

        st.write("")
        with panel("history", "History Timeline", "history"):
            history = get_asset_history(session, asset.id)
            render_timeline(history)

    finally:
        session.close()


# ----------------------------------------------------------------- browse
def show_browse():
    session = get_session()
    try:
        asset_types = get_all_asset_types(session)
        dept_names = get_all_department_names(session)
    finally:
        session.close()

    with panel("filters", "Search & Filters", "search"):
        search_term = st.text_input("Search by Asset ID, name, or employee",
                                    placeholder="e.g. LAP-0012, Dell, Ayesha ...")
        c1, c2, c3, c4 = st.columns(4)
        sel_types = c1.multiselect("Asset Type", asset_types)
        sel_depts = c2.multiselect("Department", dept_names)
        sel_status = c3.multiselect("Status", ["Active", "Maintenance Required", "Damaged", "Under Repair", "Retired"])
        sel_condition = c4.multiselect("Condition", ["Good", "Fair", "Damaged", "Needs Attention"])
        warranty_filter = st.radio("Warranty", ["All", "Valid", "Expired"], horizontal=True)

    session = get_session()
    try:
        assets = search_and_filter_assets(
            session, search_term=search_term or None, asset_types=sel_types or None,
            departments=sel_depts or None, statuses=sel_status or None,
            conditions=sel_condition or None,
            warranty_status=None if warranty_filter == "All" else warranty_filter,
        )

        result_count(len(assets))

        if not assets:
            with panel("empty", "Asset Register", "assets"):
                empty_state("No assets match your search/filters.", "search")
            return

        table_data = [{
            "Asset ID": a.asset_id, "Name": a.name, "Type": a.asset_type,
            "Department": a.department.name if a.department else "—",
            "Location": a.location.name if a.location else "—",
            "Employee": a.employee.name if a.employee else "Unassigned",
            "Status": a.status, "Condition": a.condition,
        } for a in assets]
        df = pd.DataFrame(table_data)

        with panel("table", "Asset Register", "assets"):
            st.caption("Click a row to open that asset's full profile.")
            event = st.dataframe(
                style_status_df(df, ["Status", "Condition"]),
                use_container_width=True, hide_index=True, height=460,
                on_select="rerun", selection_mode="single-row", key="assets_table",
            )
            rows = event.selection.rows if event and event.selection else []
            if rows and rows[0] < len(assets):
                st.session_state.selected_asset_id = assets[rows[0]].asset_id
                st.rerun()

            st.write("")
            c_sel, c_btn = st.columns([3, 1], vertical_alignment="bottom")
            chosen = c_sel.selectbox("Or pick an Asset ID", [a.asset_id for a in assets])
            if c_btn.button("View Profile", type="primary", use_container_width=True):
                st.session_state.selected_asset_id = chosen
                st.rerun()

    finally:
        session.close()


# -------------------------------------------------------------------- add
def show_add_asset():
    session = get_session()
    try:
        departments = get_all_departments(session)
        locations = get_all_locations(session)
        employees = get_all_employees(session)
    finally:
        session.close()

    with panel("add_basic", "Basic Details", "assets"):
        asset_type = st.selectbox("Asset Type", ["Desktop", "Laptop", "Monitor", "Chair", "Desk",
                                                  "Keyboard", "Mouse", "UPS", "Printer", "AC", "Projector"])
        name = st.text_input("Asset Name", value=f"New {asset_type}")
        b1, b2 = st.columns(2)
        brand = b1.text_input("Brand")
        model = b2.text_input("Model")

    st.write("")
    with panel("add_loc", "Location & Assignment", "mappin"):
        c1, c2, c3 = st.columns(3)
        dept_choice = c1.selectbox("Department", [d.name for d in departments])
        loc_choice = c2.selectbox("Location", [l.name for l in locations])
        emp_choice = c3.selectbox("Assign to Employee (optional)", ["Unassigned"] + [e.name for e in employees])

    st.write("")
    with panel("add_buy", "Purchase & Warranty", "wallet"):
        c4, c5, c6 = st.columns(3)
        purchase_date_val = c4.date_input("Purchase Date", value=date.today())
        purchase_cost = c5.number_input("Purchase Cost (Rs.)", min_value=0.0, step=500.0)
        warranty_end_val = c6.date_input("Warranty End", value=date.today())

    st.write("")
    with panel("add_state", "Condition & Status", "shield"):
        s1, s2 = st.columns(2)
        condition = s1.selectbox("Condition", ["Good", "Fair", "Damaged", "Needs Attention"])
        status = s2.selectbox("Status", ["Active", "Maintenance Required", "Damaged", "Under Repair"])
        notes = st.text_area("Notes (optional)")

    st.write("")
    if st.button("Save Asset", type="primary", icon=":material/save:"):
        is_valid, err = validate_new_asset_form(asset_type, name, dept_choice, loc_choice)
        if not is_valid:
            alert("danger", err)
        else:
            session = get_session()
            try:
                dept_obj = next((d for d in departments if d.name == dept_choice), None)
                loc_obj = next((l for l in locations if l.name == loc_choice), None)
                emp_obj = next((e for e in employees if e.name == emp_choice), None)

                asset = create_asset(
                    session, asset_type=asset_type, name=name.strip(), brand=brand, model=model,
                    department_id=dept_obj.id if dept_obj else None,
                    location_id=loc_obj.id if loc_obj else None,
                    employee_id=emp_obj.id if emp_obj else None,
                    purchase_date=purchase_date_val, purchase_cost=purchase_cost,
                    warranty_end=warranty_end_val, condition=condition, status=status, notes=notes,
                )
                alert("success", f"Asset <b>{html.escape(asset.asset_id)}</b> registered successfully.", html=True)
            finally:
                session.close()


# ------------------------------------------------------------------ router
if st.session_state.selected_asset_id:
    show_profile(st.session_state.selected_asset_id)
else:
    tab1, tab2 = st.tabs(["Browse Assets", "Add New Asset"])
    with tab1:
        show_browse()
    with tab2:
        show_add_asset()