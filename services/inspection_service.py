from database.models import Inspection
from services.history_service import log_event


def save_inspection(session, asset, image_path, ai_result):
    inspection = Inspection(
        asset_id=asset.id,
        image_path=image_path,
        detected_object=ai_result.get("object_type"),
        visible_issue=ai_result.get("visible_issue"),
        confidence=ai_result.get("confidence"),
        manual_inspection_required=ai_result.get("manual_inspection_required", True),
        ai_notes=ai_result.get("explanation"),
    )
    session.add(inspection)
    session.flush()

    summary = f"AI Inspection: {ai_result.get('visible_issue', 'No issue specified')} (confidence: {ai_result.get('confidence', 0):.2f})"
    log_event(session, asset.id, "AI Inspection", summary)

    session.commit()
    return inspection


def get_inspections_for_asset(session, asset_pk):
    return session.query(Inspection).filter(
        Inspection.asset_id == asset_pk
    ).order_by(Inspection.created_at.desc()).all()