import os
import qrcode
import config

QR_PREFIX = "ASSETMIND"


def generate_qr_code(asset_id_str):
    """
    Generates (or reuses a cached) QR code image for an asset.
    QR content format: ASSETMIND:<asset_id>  e.g. ASSETMIND:C-018
    Returns the file path to the PNG.
    """
    filename = f"{asset_id_str}.png"
    path = os.path.join(config.UPLOADS_QRCODES, filename)

    if os.path.exists(path):
        return path

    qr_content = f"{QR_PREFIX}:{asset_id_str}"
    img = qrcode.make(qr_content, box_size=10, border=3)
    img.save(path)
    return path


def parse_qr_content(scanned_text):
    """
    Given raw scanned/typed text, extracts the asset_id if it matches our QR format.
    Also accepts a plain asset ID typed manually (e.g. 'C-018').
    Returns the asset_id string, or None if unrecognized.
    """
    if not scanned_text:
        return None
    text = scanned_text.strip()

    if text.upper().startswith(f"{QR_PREFIX}:"):
        return text.split(":", 1)[1].strip().upper()

    # Fallback: treat as a plain manual asset ID (e.g. "C-018" or "c-018")
    return text.upper()