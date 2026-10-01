import os
import uuid


def generate_asset_id(prefix: str, number: int) -> str:
    """e.g. generate_asset_id('C', 18) -> 'C-018'"""
    return f"{prefix}-{number:03d}"


def generate_ticket_id(number: int) -> str:
    """e.g. generate_ticket_id(104) -> 'TCK-104'"""
    return f"TCK-{number:03d}"


def save_uploaded_image(uploaded_file, folder):
    """Saves a Streamlit UploadedFile to disk with a unique name, returns the path (or None)."""
    if uploaded_file is None:
        return None
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path