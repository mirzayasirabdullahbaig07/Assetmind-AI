from datetime import date, datetime, timedelta
from sqlalchemy import func
from database.models import Asset, MaintenanceTicket, AssetHistory, Department, Replacement


def get_assets_by_status(session, status):
    assets = session.query(Asset).filter(Asset.status == status).all()
    return [{"asset_id": a.asset_id, "name": a.name, "type": a.asset_type,
             "department": a.department.name if a.department else None} for a in assets]


def get_assets_by_department(session, department_name):
    dept = session.query(Department).filter(Department.name.ilike(f"%{department_name}%")).first()
    if not dept:
        return []
    assets = session.query(Asset).filter(Asset.department_id == dept.id).all()
    return [{"asset_id": a.asset_id, "name": a.name, "status": a.status} for a in assets]


def get_assets_needing_attention(session):
    """Assets with status Maintenance Required, Damaged, or Under Repair."""
    assets = session.query(Asset).filter(
        Asset.status.in_(["Maintenance Required", "Damaged", "Under Repair"])
    ).all()
    by_type = {}
    for a in assets:
        by_type[a.asset_type] = by_type.get(a.asset_type, 0) + 1
    return {
        "total": len(assets),
        "by_type": by_type,
        "assets": [{"asset_id": a.asset_id, "type": a.asset_type, "status": a.status} for a in assets],
    }


def get_maintenance_cost(session, month=None, year=None):
    """Total repair cost of resolved tickets, optionally filtered by month/year."""
    query = session.query(MaintenanceTicket).filter(MaintenanceTicket.repair_cost.isnot(None))
    tickets = query.all()
    if month and year:
        tickets = [t for t in tickets if t.resolved_at and t.resolved_at.month == month and t.resolved_at.year == year]
    elif year:
        tickets = [t for t in tickets if t.resolved_at and t.resolved_at.year == year]

    total = sum(t.repair_cost or 0 for t in tickets)
    return {"total_cost": total, "ticket_count": len(tickets)}


def get_repeated_repairs(session, min_count=2):
    """Assets with more than min_count resolved tickets."""
    tickets = session.query(MaintenanceTicket).filter(
        MaintenanceTicket.status.in_(["Resolved", "Replaced", "Closed"])
    ).all()
    counts = {}
    for t in tickets:
        counts[t.asset_id] = counts.get(t.asset_id, 0) + 1

    result = []
    for asset_pk, count in counts.items():
        if count > min_count:
            asset = session.get(Asset, asset_pk)
            if asset:
                result.append({"asset_id": asset.asset_id, "name": asset.name, "repair_count": count})
    return sorted(result, key=lambda x: x["repair_count"], reverse=True)


def get_assets_under_warranty(session, asset_type=None):
    query = session.query(Asset).filter(Asset.warranty_end >= date.today())
    if asset_type:
        query = query.filter(Asset.asset_type.ilike(f"%{asset_type}%"))
    assets = query.all()
    return [{"asset_id": a.asset_id, "type": a.asset_type,
             "warranty_end": a.warranty_end.isoformat() if a.warranty_end else None} for a in assets]


def get_recent_tickets(session, limit=10):
    tickets = session.query(MaintenanceTicket).order_by(MaintenanceTicket.created_at.desc()).limit(limit).all()
    return [{"ticket_id": t.ticket_id, "asset_id": t.asset.asset_id if t.asset else None,
             "issue": t.issue_description, "status": t.status, "priority": t.priority} for t in tickets]


def get_replacements_this_year(session):
    year = date.today().year
    replacements = session.query(Replacement).filter(
        func.strftime("%Y", Replacement.created_at) == str(year)
    ).all()
    result = []
    for r in replacements:
        old = session.get(Asset, r.old_asset_id)
        new = session.get(Asset, r.new_asset_id)
        result.append({
            "old_asset": old.asset_id if old else None,
            "new_asset": new.asset_id if new else None,
            "reason": r.reason,
            "cost": r.replacement_cost,
        })
    return result


def get_assets_under_repair_count(session):
    return session.query(Asset).filter(Asset.status == "Under Repair").count()


def get_department_with_most_issues(session):
    tickets = session.query(MaintenanceTicket).all()
    dept_counts = {}
    for t in tickets:
        if t.asset and t.asset.department:
            name = t.asset.department.name
            dept_counts[name] = dept_counts.get(name, 0) + 1
    if not dept_counts:
        return None
    top = max(dept_counts.items(), key=lambda x: x[1])
    return {"department": top[0], "ticket_count": top[1], "breakdown": dept_counts}


def get_damaged_assets_by_type(session, asset_type):
    assets = session.query(Asset).filter(
        Asset.asset_type.ilike(f"%{asset_type}%"),
        Asset.status.in_(["Damaged", "Maintenance Required"])
    ).all()
    return [{"asset_id": a.asset_id, "name": a.name, "condition": a.condition, "status": a.status} for a in assets]

def generate_monthly_report(session, month=None, year=None):
    """
    Builds a complete maintenance report. If month/year not given, uses the current month.
    Returns a dict of stats plus a list of ticket rows for CSV/PDF export.
    """
    today = date.today()
    month = month or today.month
    year = year or today.year

    all_tickets = session.query(MaintenanceTicket).all()
    month_tickets = [
        t for t in all_tickets
        if t.created_at and t.created_at.month == month and t.created_at.year == year
    ]

    total_tickets = len(month_tickets)
    open_tickets = len([t for t in month_tickets if t.status not in ("Resolved", "Replaced", "Closed")])
    resolved_tickets = len([t for t in month_tickets if t.status in ("Resolved", "Replaced", "Closed")])

    repair_costs = sum(t.repair_cost or 0 for t in month_tickets if t.status == "Resolved")

    replacements = session.query(Replacement).filter(
        func.strftime("%Y", Replacement.created_at) == str(year),
        func.strftime("%m", Replacement.created_at) == f"{month:02d}",
    ).all()
    replacement_costs = sum(r.replacement_cost or 0 for r in replacements)

    type_issue_counts = {}
    dept_issue_counts = {}
    asset_repair_counts = {}
    for t in month_tickets:
        if t.asset:
            type_issue_counts[t.asset.asset_type] = type_issue_counts.get(t.asset.asset_type, 0) + 1
            if t.asset.department:
                dept_name = t.asset.department.name
                dept_issue_counts[dept_name] = dept_issue_counts.get(dept_name, 0) + 1
            asset_repair_counts[t.asset.asset_id] = asset_repair_counts.get(t.asset.asset_id, 0) + 1

    most_problematic_types = sorted(type_issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_departments = sorted(dept_issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    frequently_repaired = sorted(asset_repair_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    ticket_rows = [{
        "Ticket ID": t.ticket_id,
        "Asset": t.asset.asset_id if t.asset else "—",
        "Issue": t.issue_description,
        "Status": t.status,
        "Priority": t.priority,
        "Repair Cost": t.repair_cost or 0,
        "Created": t.created_at.strftime("%d %b %Y") if t.created_at else "—",
    } for t in month_tickets]

    return {
        "month": month, "year": year,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "repair_costs": repair_costs,
        "replacement_costs": replacement_costs,
        "most_problematic_types": most_problematic_types,
        "top_departments": top_departments,
        "frequently_repaired": frequently_repaired,
        "ticket_rows": ticket_rows,
    }