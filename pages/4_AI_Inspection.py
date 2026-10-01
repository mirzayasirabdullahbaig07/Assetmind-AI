import html
import streamlit as st
from database.db import init_db, get_session
from database.seed import seed_database
from services.asset_service import search_and_filter_assets, get_asset_by_asset_id
from services.inspection_service import save_inspection, get_inspections_for_asset
from ai.vision import run_visual_inspection
from utils.validators import validate_image_file
from utils.helpers import save_uploaded_image
from utils.ui_kit import (
    inject_base_css, page_header, panel, empty_state, alert, kpi_card, quote,
    section, icon,
)
from utils.ui_kit_ext import badge_color
import config

init_db()
seed_database()
inject_base_css()

page_header(
    "inspection", "AI Visual Inspection",
    "AI-assisted visual condition analysis — decision support, not diagnosis.",
    badge=config.COMPANY_NAME,
)
alert("info", "A technician always makes the final call. The AI only highlights what is visible in the photo.")

if not config.GROQ_API_KEY:
    alert("warning", "<b>GROQ_API_KEY is not configured.</b> Add it to your <code>.env</code> file to enable AI inspection.",
          html=True)

session = get_session()
try:
    assets = search_and_filter_assets(session)
    asset_options = {f"{a.asset_id} — {a.name}": a.asset_id for a in assets}
finally:
    session.close()

# ---------------------------------------------------------------- new inspection
left, right = st.columns([3, 2], gap="medium")
with left:
    with panel("insp_form", "Inspect an Asset", "inspection"):
        chosen_label = st.selectbox("Select Asset to Inspect", list(asset_options.keys()) if asset_options else [])
        issue_context = st.text_input("Reported issue (optional context for the AI)",
                                      placeholder="e.g. Chair leg appears broken.")
        uploaded_image = st.file_uploader("Upload a current photo", type=["png", "jpg", "jpeg", "webp"])

with right:
    with panel("insp_preview", "Image Preview", "image"):
        if uploaded_image:
            st.image(uploaded_image, use_container_width=True, caption="Image to be analyzed")
        else:
            empty_state("Upload a photo to preview it here.", "image")

st.write("")
run_clicked = st.button("Run AI Inspection", type="primary", icon=":material/search:", disabled=not uploaded_image)

if run_clicked:
    img_valid, img_err = validate_image_file(uploaded_image)
    if not img_valid:
        alert("danger", img_err)
    else:
        asset_id_str = asset_options.get(chosen_label)
        session = get_session()
        try:
            asset = get_asset_by_asset_id(session, asset_id_str)
            image_path = save_uploaded_image(uploaded_image, config.UPLOADS_INSPECTIONS)

            with st.spinner("Analyzing image with Groq vision model..."):
                result = run_visual_inspection(image_path, issue_context=issue_context or None)

            inspection = save_inspection(session, asset, image_path, result)

            section("Inspection Result", "note")

            if result.get("parse_failed"):
                alert("warning", "<b>Manual review required</b> — the AI response could not be fully structured.", html=True)
                with st.expander("Raw AI response"):
                    st.text(result.get("raw_response", ""))
            else:
                c1, c2, c3 = st.columns(3, gap="medium")
                confidence = result["confidence"]
                with c1:
                    kpi_card("Detected Object", result["object_type"], "search", "#2563EB")
                with c2:
                    kpi_card("Condition", result["condition"], "shield", badge_color(result["condition"]))
                with c3:
                    kpi_card("Confidence", f"{confidence:.0%}", "activity", "#0D9488", pct=confidence * 100)

                st.write("")
                with panel("insp_detail", "Findings", "note"):
                    quote(result["visible_issue"], "Visible Issue")
                    quote(result["explanation"], "Explanation")
                    if result["manual_inspection_required"]:
                        alert("warning", "<b>Manual inspection required</b> — visual evidence alone is not conclusive.",
                              html=True)
                    else:
                        alert("success", "No further manual inspection flagged based on visible evidence.")

            st.caption(f"Saved to {asset.asset_id}'s inspection history.")

        finally:
            session.close()

# ---------------------------------------------------------------- history
with panel("insp_hist", "Past Inspections for an Asset", "history"):
    review_label = st.selectbox(
        "View inspection history for",
        list(asset_options.keys()) if asset_options else [],
        key="review_asset",
    )

    if review_label:
        session = get_session()
        try:
            asset = get_asset_by_asset_id(session, asset_options[review_label])
            inspections = get_inspections_for_asset(session, asset.id)  # newest-first

            if not inspections:
                empty_state("No inspections recorded for this asset yet.", "inspection")
            else:
                for insp in inspections:
                    date_str = insp.created_at.strftime("%d %b %Y, %I:%M %p") if insp.created_at else "—"
                    label = (
                        f"{date_str} — {insp.detected_object or 'Unknown'} ({insp.confidence:.0%} confidence)"
                        if insp.confidence else date_str
                    )
                    with st.expander(label):
                        col1, col2 = st.columns([1, 2], gap="medium")
                        with col1:
                            if insp.image_path:
                                try:
                                    st.image(insp.image_path, use_container_width=True)
                                except Exception:
                                    st.caption("Image not available.")
                        with col2:
                            quote(insp.visible_issue, "Visible Issue")
                            quote(insp.ai_notes, "AI Notes")
                            if insp.manual_inspection_required:
                                alert("warning", "Manual inspection was flagged.")
        finally:
            session.close()

# ---------------------------------------------------------------- old vs new
with panel("insp_cmp", "Visual Timeline — Old vs New", "recycle"):
    st.caption("Compares the two most recent inspections for the selected asset above.")

    if review_label:
        session = get_session()
        try:
            asset = get_asset_by_asset_id(session, asset_options[review_label])
            inspections = get_inspections_for_asset(session, asset.id)  # newest-first

            if len(inspections) < 2:
                empty_state("Need at least two inspections on this asset to show a before/after comparison.", "recycle")
            else:
                newest, previous = inspections[0], inspections[1]
                col_old, col_arrow, col_new = st.columns([5, 1, 5], gap="small")

                def _side(col, insp, tag, color):
                    with col:
                        d = insp.created_at.strftime("%d %b %Y") if insp.created_at else "—"
                        st.markdown(f'<span class="am-pill" style="--c:{color}">{tag} · {html.escape(d)}</span>',
                                    unsafe_allow_html=True)
                        if insp.image_path:
                            try:
                                st.image(insp.image_path, use_container_width=True)
                            except Exception:
                                st.caption("Image not available.")
                        st.markdown(f"Detected: **{html.escape(str(insp.detected_object or '—'))}**")
                        st.caption(insp.visible_issue or "No issue noted")

                _side(col_old, previous, "Previous", "#64748B")
                with col_arrow:
                    st.markdown(f'<div class="am-arrow">{icon("arrow", 24, 2.4)}</div>', unsafe_allow_html=True)
                _side(col_new, newest, "Current", "#2563EB")

                st.write("")
                if newest.confidence and newest.confidence < 0.7:
                    alert("info", "Confidence on the latest inspection is low — object identity across the two images "
                                  "is not being asserted with certainty.")
                else:
                    alert("info", "<b>Detected change:</b> " +
                          html.escape(newest.visible_issue or "No visible issue detected in the current inspection."),
                          icon_name="activity", html=True)
        finally:
            session.close()