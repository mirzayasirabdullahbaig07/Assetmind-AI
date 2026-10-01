import html
import streamlit as st
from datetime import date
from database.db import init_db, get_session
from database.seed import seed_database
from services.asset_service import (
    search_and_filter_assets, get_asset_by_asset_id,
    get_all_departments, get_all_locations, get_all_employees,
)
from services.maintenance_service import (
    create_ticket, get_all_tickets, get_ticket_by_ticket_id,
    update_ticket_status, start_repair, resolve_ticket, mark_beyond_repair,
    retire_asset, create_replacement, count_resolved_tickets_for_asset,
)
from utils.validators import validate_image_file, validate_issue_report, validate_repair_entry
from utils.helpers import save_uploaded_image
from utils.ui_kit import (
    inject_base_css, page_header, panel, empty_state, info_grid, alert,
    entity_header, stepper, quote, kpi_card,
)
import config

init_db()
seed_database()
inject_base_css()

page_header(
    "maintenance", "Maintenance",
    "Report issues and manage repair / replacement workflows",
    badge=config.COMPANY_NAME,
)

# Workflow paths shown in the progress stepper
REPAIR_PATH = ["Open", "Reviewing", "Repair Approved", "Under Repair", "Resolved"]
REPLACE_PATH = ["Open", "Reviewing", "Replacement Requested", "Replaced", "Closed"]


def workflow_position(ticket):
    """Return (steps, current_index, finished) for the stepper."""
    status = ticket.status
    on_replace_path = status in ("Replacement Requested", "Replaced") or (
        status == "Closed" and not getattr(ticket, "resolution", None)
    )
    steps = REPLACE_PATH if on_replace_path else REPAIR_PATH
    if status in steps:
        idx = steps.index(status)
    elif status == "Closed":
        idx = len(steps) - 1
    else:
        idx = 0
    finished = status in ("Resolved", "Closed")
    return steps, idx, finished


tab1, tab2 = st.tabs(["Report New Issue", "Manage Tickets"])

# ---------------- TAB 1: Report New Issue ----------------
with tab1:
    session = get_session()
    try:
        assets = search_and_filter_assets(session)
        asset_options = {f"{a.asset_id} — {a.name}": a.asset_id for a in assets if a.status != "Retired"}
    finally:
        session.close()

    with panel("report_issue", "Report an Issue", "alert"):
        chosen_label = st.selectbox("Select Asset", list(asset_options.keys()) if asset_options else [])
        issue_text = st.text_area("Describe the issue", placeholder="e.g. Chair leg appears broken.", height=130)
        priority = st.select_slider("Priority", options=["Low", "Medium", "High"], value="Medium")

    st.write("")
    with panel("report_extra", "Attachment & Reporter", "image"):
        c1, c2 = st.columns([3, 2], gap="medium")
        uploaded_image = c1.file_uploader("Upload a photo (optional)", type=["png", "jpg", "jpeg", "webp"])
        reported_by = c2.text_input("Reported by", value="Employee")

    st.write("")
    if st.button("Submit Ticket", type="primary", icon=":material/send:"):
        asset_id_str = asset_options.get(chosen_label)
        is_valid, err = validate_issue_report(asset_id_str, issue_text)
        if not is_valid:
            alert("danger", err)
        else:
            img_valid, img_err = validate_image_file(uploaded_image)
            if not img_valid:
                alert("danger", img_err)
            else:
                session = get_session()
                try:
                    asset = get_asset_by_asset_id(session, asset_id_str)
                    image_path = save_uploaded_image(uploaded_image, config.UPLOADS_REPAIRS) if uploaded_image else None
                    ticket = create_ticket(
                        session, asset, issue_text.strip(),
                        image_path=image_path, priority=priority, reported_by=reported_by or "Employee",
                    )
                    alert(
                        "success",
                        f"Ticket <b>{html.escape(ticket.ticket_id)}</b> created for "
                        f"<b>{html.escape(asset.asset_id)}</b>. Status: Open.",
                        html=True,
                    )
                finally:
                    session.close()

# ---------------- TAB 2: Manage Tickets ----------------
with tab2:
    session = get_session()
    try:
        tickets = get_all_tickets(session)
        ticket_map = {f"{t.ticket_id} — {t.asset.asset_id} ({t.status})": t.ticket_id for t in tickets}
        statuses = [t.status for t in tickets]
    finally:
        session.close()

    if not ticket_map:
        with panel("no_tickets", "Tickets", "ticket"):
            empty_state("No tickets yet. Report an issue in the first tab.", "ticket")
    else:
        # --- summary row ---
        total = len(statuses)
        n_open = statuses.count("Open")
        n_done = sum(1 for s in statuses if s in ("Resolved", "Replaced", "Closed"))
        n_prog = total - n_open - n_done
        k1, k2, k3, k4 = st.columns(4, gap="small")
        with k1: kpi_card("Total Tickets", total, "ticket", "#2563EB")
        with k2: kpi_card("Open", n_open, "alert", "#F59E0B", total=total)
        with k3: kpi_card("In Progress", n_prog, "maintenance", "#8B5CF6", total=total)
        with k4: kpi_card("Completed", n_done, "check", "#16A34A", total=total)

        st.write("")
        with panel("pick_ticket", "Select Ticket", "search"):
            chosen = st.selectbox("Select a ticket", list(ticket_map.keys()), label_visibility="collapsed")
        ticket_id_str = ticket_map[chosen]

        session = get_session()
        try:
            ticket = get_ticket_by_ticket_id(session, ticket_id_str)
            asset = ticket.asset

            entity_header(ticket.ticket_id, f"{asset.asset_id} — {asset.name}", [ticket.status, ticket.priority])

            # --- progress stepper ---
            steps, idx, finished = workflow_position(ticket)
            with panel("progress", "Workflow Progress", "activity"):
                stepper(steps, idx, finished)

            st.write("")
            left, right = st.columns([2, 3], gap="medium")

            # --- left: ticket details ---
            with left:
                with panel("t_details", "Ticket Details", "note"):
                    info_grid(
                        {"Status": ticket.status, "Priority": ticket.priority, "Asset Condition": asset.condition},
                        badge_keys=("Status", "Priority", "Asset Condition"),
                    )
                    quote(ticket.issue_description, "Issue")
                    if ticket.image_path:
                        try:
                            st.image(ticket.image_path, width=300)
                        except Exception:
                            st.caption("Image not available.")

                    resolved_count = count_resolved_tickets_for_asset(session, asset.id)
                    if resolved_count >= 2:
                        alert(
                            "warning",
                            f"<b>Repeated Maintenance</b> — this asset has {resolved_count} resolved tickets in its history.",
                            html=True,
                        )

            # --- right: next step / workflow actions ---
            with right:
                with panel("t_actions", "Next Step", "maintenance"):
                    if ticket.status == "Open":
                        st.caption("A new ticket. Start the review to continue.")
                        if st.button("Move to Reviewing", type="primary", icon=":material/visibility:"):
                            update_ticket_status(session, ticket, "Reviewing")
                            st.rerun()

                    elif ticket.status == "Reviewing":
                        st.caption("Decide whether this asset can be repaired or needs replacement.")
                        colA, colB = st.columns(2)
                        with colA:
                            if st.button("Approve Repair", type="primary", icon=":material/check_circle:",
                                         use_container_width=True):
                                update_ticket_status(session, ticket, "Repair Approved")
                                st.rerun()
                        with colB:
                            if st.button("Request Replacement", icon=":material/autorenew:",
                                         use_container_width=True, help="Beyond repair"):
                                mark_beyond_repair(session, ticket)
                                update_ticket_status(session, ticket, "Replacement Requested")
                                st.rerun()

                    elif ticket.status == "Repair Approved":
                        st.caption("Repair is approved. Start the repair work.")
                        if st.button("Start Repair", type="primary", icon=":material/build:"):
                            start_repair(session, ticket)
                            st.rerun()

                    elif ticket.status == "Under Repair":
                        st.markdown("**Complete the repair**")
                        repair_cost = st.number_input("Repair cost (Rs.)", min_value=0.0, step=100.0)
                        resolution = st.text_area("Resolution", placeholder="e.g. Chair leg replaced.")
                        if st.button("Mark Resolved", type="primary", icon=":material/task_alt:"):
                            is_valid, err = validate_repair_entry(repair_cost, resolution)
                            if not is_valid:
                                alert("danger", err)
                            else:
                                resolve_ticket(session, ticket, repair_cost, resolution.strip())
                                st.toast("Ticket resolved and asset marked Active again.", icon="✅")
                                st.rerun()

                    elif ticket.status == "Replacement Requested":
                        if asset.status != "Retired":
                            st.markdown("**Step 1: Retire this asset**")
                            reason = st.text_input("Retirement reason", value="Beyond economical repair")
                            if st.button("Retire Asset", icon=":material/delete:"):
                                retire_asset(session, asset, reason)
                                st.rerun()
                        else:
                            alert("success", f"<b>{html.escape(asset.asset_id)}</b> is retired. "
                                             "Now create its replacement below.", html=True)
                            st.markdown("**Step 2: Create Replacement Asset**")

                            departments = get_all_departments(session)
                            locations = get_all_locations(session)
                            employees = get_all_employees(session)

                            r1, r2, r3 = st.columns(3)
                            dept_choice = r1.selectbox("Department", [d.name for d in departments])
                            loc_choice = r2.selectbox("Location", [l.name for l in locations])
                            emp_choice = r3.selectbox("Assign to Employee (optional)",
                                                      ["Unassigned"] + [e.name for e in employees])
                            new_name = st.text_input("New Asset Name", value=f"{asset.asset_type} (Replacement)")
                            b1, b2 = st.columns(2)
                            new_brand = b1.text_input("Brand", value=asset.brand or "")
                            new_model = b2.text_input("Model", value="")
                            p1, p2, p3 = st.columns(3)
                            new_cost = p1.number_input("Purchase Cost (Rs.)", min_value=0.0, step=1000.0)
                            new_warranty = p2.date_input("Warranty End", value=date.today())
                            replacement_cost = p3.number_input("Replacement Cost (Rs., for reporting)",
                                                               min_value=0.0, step=1000.0, value=new_cost)

                            if st.button("Create Replacement", type="primary", icon=":material/recycling:"):
                                dept_obj = next((d for d in departments if d.name == dept_choice), None)
                                loc_obj = next((l for l in locations if l.name == loc_choice), None)
                                emp_obj = next((e for e in employees if e.name == emp_choice), None)

                                new_asset_kwargs = dict(
                                    asset_type=asset.asset_type,
                                    name=new_name.strip() or f"{asset.asset_type} (Replacement)",
                                    brand=new_brand, model=new_model,
                                    department_id=dept_obj.id if dept_obj else None,
                                    location_id=loc_obj.id if loc_obj else None,
                                    employee_id=emp_obj.id if emp_obj else None,
                                    purchase_date=date.today(), purchase_cost=new_cost,
                                    warranty_end=new_warranty, condition="Good", status="Active",
                                    notes=f"Replacement for {asset.asset_id}.",
                                )
                                new_asset, replacement = create_replacement(
                                    session, asset, new_asset_kwargs,
                                    reason=f"Replacement for {asset.asset_id}",
                                    replacement_cost=replacement_cost,
                                )
                                update_ticket_status(session, ticket, "Replaced")
                                st.toast(f"{new_asset.asset_id} created as replacement for {asset.asset_id}.", icon="♻️")
                                st.rerun()

                    elif ticket.status == "Replaced":
                        st.caption("Replacement is in place. Close the ticket to finish.")
                        if st.button("Close Ticket", type="primary", icon=":material/lock:"):
                            update_ticket_status(session, ticket, "Closed")
                            st.rerun()

                    elif ticket.status in ("Resolved", "Closed"):
                        alert("success", f"This ticket is <b>{html.escape(ticket.status)}</b>.", html=True)
                        details = {}
                        if ticket.resolution:
                            details["Resolution"] = ticket.resolution
                        if ticket.repair_cost:
                            details["Repair Cost"] = f"Rs. {ticket.repair_cost:,.0f}"
                        if details:
                            info_grid(details)

        finally:
            session.close()