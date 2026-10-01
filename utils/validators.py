import os

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_IMAGE_SIZE_MB = 10


def validate_image_file(uploaded_file):
    if uploaded_file is None:
        return True, None  # image is optional

    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False, f"Unsupported image type '{ext}'. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"

    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        return False, f"Image too large ({size_mb:.1f} MB). Max allowed is {MAX_IMAGE_SIZE_MB} MB."

    return True, None


def validate_issue_report(asset_selected, issue_description):
    if not asset_selected:
        return False, "Please select an asset."
    if not issue_description or not issue_description.strip():
        return False, "Please describe the issue."
    if len(issue_description.strip()) < 5:
        return False, "Issue description is too short. Please provide more detail."
    return True, None


def validate_repair_entry(repair_cost, resolution):
    if repair_cost is None or repair_cost < 0:
        return False, "Please enter a valid repair cost."
    if not resolution or not resolution.strip():
        return False, "Please describe how the issue was resolved."
    return True, None


def validate_new_asset_form(asset_type, name, department, location):
    if not asset_type:
        return False, "Please select an asset type."
    if not name or not name.strip():
        return False, "Please enter an asset name."
    if not department:
        return False, "Please select a department."
    if not location:
        return False, "Please select a location."
    return True, None