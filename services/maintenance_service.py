from datetime import datetime
from database.models import MaintenanceTicket, Asset, Replacement
from services.history_service import log_event, change_asset_status
from services.asset_service import create_asset
from utils.helpers import generate_ticket_id


def _next_ticket_number(session):
    return session.query(MaintenanceTicket).count() + 1


def create_ticket(session, asset, issue_description, image_path=None, priority="Medium", reported_by="Employee"):
    ticket_id = generate_ticket_id(_next_ticket_number(session))
    ticket = MaintenanceTicket(
        ticket_id=ticket_id, asset_id=asset.id, issue_description=issue_description,
        image_path=image_path, priority=priority, status="Open", reported_by=reported_by,
    )
    session.add(ticket)
    session.flush()

    if asset.status == "Active":
        change_asset_status(session, asset, "Maintenance Required",
                             description=f"Issue reported: {issue_description}",
                             related_ticket_id=ticket.id)
    else:
        log_event(session, asset.id, "Ticket Created",
                   f"Ticket {ticket_id} opened: {issue_description}",
                   related_ticket_id=ticket.id)

    session.commit()
    return ticket


def update_ticket_status(session, ticket, new_status, note=None):
    old_status = ticket.status
    ticket.status = new_status
    log_event(session, ticket.asset_id, "Ticket Status Changed",
               note or f"Ticket {ticket.ticket_id} moved from {old_status} to {new_status}.",
               old_status=old_status, new_status=new_status, related_ticket_id=ticket.id)
    session.commit()


def start_repair(session, ticket):
    asset = session.get(Asset, ticket.asset_id)
    update_ticket_status(session, ticket, "Under Repair", note=f"Repair started on ticket {ticket.ticket_id}.")
    if asset:
        change_asset_status(session, asset, "Under Repair",
                             description=f"Repair started (ticket {ticket.ticket_id}).",
                             related_ticket_id=ticket.id)
    session.commit()


def resolve_ticket(session, ticket, repair_cost, resolution):
    asset = session.get(Asset, ticket.asset_id)
    ticket.repair_cost = repair_cost
    ticket.resolution = resolution
    ticket.resolved_at = datetime.utcnow()
    update_ticket_status(session, ticket, "Resolved",
                          note=f"Resolved: {resolution} (Cost: Rs. {repair_cost:,.0f})")
    if asset:
        change_asset_status(session, asset, "Active",
                             description=f"Repair completed: {resolution}",
                             related_ticket_id=ticket.id)
        asset.condition = "Good"
    session.commit()


def mark_beyond_repair(session, ticket, note=None):
    asset = session.get(Asset, ticket.asset_id)
    if asset:
        asset.condition = "Damaged"
    log_event(session, ticket.asset_id, "Beyond Repair",
              note or f"Ticket {ticket.ticket_id} marked beyond economical repair.",
              related_ticket_id=ticket.id)
    session.commit()


def retire_asset(session, asset, reason):
    old_status = asset.status
    asset.status = "Retired"
    log_event(session, asset.id, "Retired", f"Asset retired. Reason: {reason}",
              old_status=old_status, new_status="Retired")
    session.commit()


def create_replacement(session, old_asset, new_asset_kwargs, reason, replacement_cost):
    if old_asset.status != "Retired":
        retire_asset(session, old_asset, reason)

    new_asset = create_asset(session, **new_asset_kwargs)

    replacement = Replacement(
        old_asset_id=old_asset.id, new_asset_id=new_asset.id,
        reason=reason, replacement_cost=replacement_cost,
    )
    session.add(replacement)

    log_event(session, new_asset.id, "Replacement", f"Registered as replacement for {old_asset.asset_id}.")
    log_event(session, old_asset.id, "Replaced", f"Replaced by {new_asset.asset_id}.")

    session.commit()
    return new_asset, replacement


def get_open_tickets(session):
    return session.query(MaintenanceTicket).filter(
        MaintenanceTicket.status.notin_(["Resolved", "Replaced", "Closed"])
    ).order_by(MaintenanceTicket.created_at.desc()).all()


def get_all_tickets(session):
    return session.query(MaintenanceTicket).order_by(MaintenanceTicket.created_at.desc()).all()


def get_ticket_by_ticket_id(session, ticket_id_str):
    return session.query(MaintenanceTicket).filter(MaintenanceTicket.ticket_id == ticket_id_str).first()


def get_tickets_for_asset(session, asset_pk):
    return session.query(MaintenanceTicket).filter(
        MaintenanceTicket.asset_id == asset_pk
    ).order_by(MaintenanceTicket.created_at.desc()).all()


def count_resolved_tickets_for_asset(session, asset_pk):
    return session.query(MaintenanceTicket).filter(
        MaintenanceTicket.asset_id == asset_pk,
        MaintenanceTicket.status.in_(["Resolved", "Replaced", "Closed"])
    ).count()