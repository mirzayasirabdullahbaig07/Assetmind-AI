import base64
import json
import re

from ai.groq_client import get_client
from ai.prompts import VISION_INSPECTION_SYSTEM_PROMPT, build_vision_user_prompt
import config

VALID_CONDITIONS = {"Good", "Fair", "Damaged", "Needs Attention"}


def _encode_image_to_data_url(image_path):
    ext = image_path.split(".")[-1].lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def _extract_json(text):
    """Attempts to pull a JSON object out of the model's response, even if wrapped in extra text."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except (json.JSONDecodeError, ValueError):
        return None


def _fallback_result(raw_text, reason):
    return {
        "object_type": "Unknown",
        "visible_issue": "Could not be structured automatically.",
        "condition": "Needs Attention",
        "confidence": 0.0,
        "manual_inspection_required": True,
        "explanation": f"{reason} Raw AI response has been preserved for manual review.",
        "raw_response": raw_text,
        "parse_failed": True,
    }


def run_visual_inspection(image_path, issue_context=None):
    """
    Sends an image to the Groq vision model and returns a structured, validated dict.
    Never raises to the caller for AI-related failures — always returns a usable dict,
    marking parse_failed=True / manual_inspection_required=True when something goes wrong.
    """
    try:
        client = get_client()
        data_url = _encode_image_to_data_url(image_path)

        response = client.chat.completions.create(
            model=config.GROQ_VISION_MODEL,
            messages=[
                {"role": "system", "content": VISION_INSPECTION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": build_vision_user_prompt(issue_context)},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            temperature=0.2,
            max_tokens=500,
        )
        raw_text = response.choices[0].message.content

    except Exception as e:
        return _fallback_result("", f"AI request failed: {str(e)}")

    parsed = _extract_json(raw_text)
    if parsed is None:
        return _fallback_result(raw_text, "AI response could not be parsed as structured data.")

    # Validate & sanitize fields — never trust the model blindly
    result = {
        "object_type": str(parsed.get("object_type", "Unknown"))[:100],
        "visible_issue": str(parsed.get("visible_issue", "Not specified")),
        "condition": parsed.get("condition") if parsed.get("condition") in VALID_CONDITIONS else "Needs Attention",
        "confidence": _safe_float(parsed.get("confidence"), default=0.5),
        "manual_inspection_required": bool(parsed.get("manual_inspection_required", True)),
        "explanation": str(parsed.get("explanation", "")),
        "raw_response": raw_text,
        "parse_failed": False,
    }

    # Safety net: low confidence always forces manual inspection, regardless of what the model said
    if result["confidence"] < 0.7:
        result["manual_inspection_required"] = True

    return result


def _safe_float(value, default=0.5):
    try:
        f = float(value)
        return max(0.0, min(1.0, f))
    except (TypeError, ValueError):
        return default