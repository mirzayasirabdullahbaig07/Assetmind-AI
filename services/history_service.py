from database.models import AssetHistory


def log_event(session, asset_pk, event_type, description, old_status=None, new_status=None, related_ticket_id=None):
    """Creates an asset_history row. Caller is responsible for session.commit()."""
    event = AssetHistory(
        asset_id=asset_pk,
        event_type=event_type,
        description=description,
        old_status=old_status,
        new_status=new_status,
        related_ticket_id=related_ticket_id,
    )
    session.add(event)
    return event


def change_asset_status(session, asset, new_status, description=None, related_ticket_id=None):
    """Updates asset.status and logs a matching history event in one call."""
    old_status = asset.status
    if old_status == new_status:
        return None
    asset.status = new_status
    return log_event(
        session,
        asset_pk=asset.id,
        event_type="Status Changed",
        description=description or f"Status changed from {old_status} to {new_status}.",
        old_status=old_status,
        new_status=new_status,
        related_ticket_id=related_ticket_id,
    )