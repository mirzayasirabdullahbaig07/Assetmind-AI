import streamlit as st
from database.db import init_db, get_session
from database.seed import seed_database
from services.asset_service import search_and_filter_assets, get_asset_by_asset_id
from services.qr_service import generate_qr_code, parse_qr_content
from utils.ui_kit import (
    inject_base_css, page_header, panel, empty_state, alert, entity_header, info_grid,
)
import config

init_db()
seed_database()
inject_base_css()

page_header(
    "qr", "QR Assets",
    "Generate a QR code for any asset, or look one up by scanning / typing its identifier.",
    badge=config.COMPANY_NAME,
)

tab1, tab2 = st.tabs(["Generate QR Code", "Look Up by ID / QR Content"])

# ---------------- TAB 1: Generate QR ----------------
with tab1:
    session = get_session()
    try:
        assets = search_and_filter_assets(session)
        asset_options = {f"{a.asset_id} — {a.name}": a.asset_id for a in assets}
    finally:
        session.close()

    left, right = st.columns([3, 2], gap="medium")

    with left:
        with panel("qr_pick", "Choose an Asset", "search"):
            search_box = st.text_input("Search asset", placeholder="Type a name or ID to filter the list below")
            filtered = ({k: v for k, v in asset_options.items() if search_box.lower() in k.lower()}
                        if search_box else asset_options)

            if not filtered:
                empty_state("No matching assets.", "search")
                asset_id_str = None
            else:
                chosen_label = st.selectbox("Select Asset", list(filtered.keys()))
                asset_id_str = filtered[chosen_label]

                if st.button("Generate QR Code", type="primary", icon=":material/qr_code_2:"):
                    qr_path = generate_qr_code(asset_id_str)
                    st.session_state["generated_qr_path"] = qr_path
                    st.session_state["generated_qr_asset"] = asset_id_str

    with right:
        with panel("qr_preview", "QR Code", "qr"):
            if (asset_id_str
                    and st.session_state.get("generated_qr_asset") == asset_id_str
                    and st.session_state.get("generated_qr_path")):
                qr_path = st.session_state["generated_qr_path"]
                _, mid, _ = st.columns([1, 3, 1])
                with mid:
                    st.image(qr_path, use_container_width=True)
                st.markdown(
                    f'<div style="text-align:center; margin-bottom:10px;"><span class="am-chip">{asset_id_str}</span></div>',
                    unsafe_allow_html=True,
                )
                with open(qr_path, "rb") as f:
                    st.download_button(
                        "Download QR Image",
                        data=f.read(),
                        file_name=f"{asset_id_str}_QR.png",
                        mime="image/png",
                        icon=":material/download:",
                        use_container_width=True,
                    )
            else:
                empty_state("Pick an asset and press Generate to see its QR code here.", "qr")

# ---------------- TAB 2: Lookup ----------------
with tab2:
    with panel("qr_lookup", "Look Up an Asset", "search"):
        st.caption("Type an asset ID (e.g. `C-018`) or paste scanned QR content (`ASSETMIND:C-018`).")
        lookup_input = st.text_input("Asset ID or QR content", placeholder="C-018  or  ASSETMIND:C-018")

        if st.button("Look Up Asset", type="primary", icon=":material/search:"):
            parsed = parse_qr_content(lookup_input)
            if not parsed:
                st.session_state["qr_lookup"] = None
                alert("danger", "Please enter a valid asset ID or QR content.")
            else:
                st.session_state["qr_lookup"] = parsed

    lookup_id = st.session_state.get("qr_lookup")
    if lookup_id:
        session = get_session()
        try:
            asset = get_asset_by_asset_id(session, lookup_id)
            st.write("")
            if not asset:
                alert("danger", f"No asset found with ID '{lookup_id}'.")
            else:
                entity_header(asset.asset_id, asset.name, [asset.status, asset.condition])

                c1, c2 = st.columns([1, 2], gap="medium")
                with c1:
                    with panel("qr_found_img", "Photo", "image"):
                        if asset.image_path:
                            try:
                                st.image(asset.image_path, use_container_width=True)
                            except Exception:
                                empty_state("No image available.", "image")
                        else:
                            empty_state("No image available.", "image")
                with c2:
                    with panel("qr_found_info", "Asset Summary", "assets"):
                        info_grid({
                            "Type": asset.asset_type,
                            "Department": asset.department.name if asset.department else "—",
                            "Location": asset.location.name if asset.location else "—",
                            "Status": asset.status,
                            "Condition": asset.condition,
                        }, badge_keys=("Status", "Condition"))

                        if st.button("Open Full Profile", type="primary", icon=":material/open_in_new:"):
                            st.session_state.selected_asset_id = asset.asset_id
                            st.switch_page("pages/2_Assets.py")
        finally:
            session.close()