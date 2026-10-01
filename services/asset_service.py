from datetime import date
from sqlalchemy import or_
from database.models import Asset, AssetHistory, Department, Location, Employee, Replacement
from services.history_service import log_event
from utils.helpers import generate_asset_id

ASSET_TYPE_PREFIXES = {
    "Desktop": "D", "Laptop": "L", "Monitor": "M", "Chair": "C", "Desk": "DK",
    "Keyboard": "K", "Mouse": "MS", "UPS": "U", "Printer": "P", "AC": "AC", "Projector": "PJ",
}


# ---------- Dashboard metrics ----------

def get_dashboard_metrics(session):
    total = session.query(Asset).count()
    active = session.query(Asset).filter(Asset.status == "Active").count()
    maintenance_required = session.query(Asset).filter(Asset.status == "Maintenance Required").count()
    damaged = session.query(Asset).filter(Asset.status == "Damaged").count()
    under_repair = session.query(Asset).filter(Asset.status == "Under Repair").count()
    retired = session.query(Asset).filter(Asset.status == "Retired").count()

    return {
        "total": total, "active": active, "maintenance_required": maintenance_required,
        "damaged": damaged, "under_repair": under_repair, "retired": retired,
    }


def get_type_distribution(session):
    rows = session.query(Asset.asset_type, Asset.id).all()
    counts = {}
    for asset_type, _ in rows:
        counts[asset_type] = counts.get(asset_type, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)


def get_status_distribution(session):
    metrics = get_dashboard_metrics(session)
    return [
        ("Active", metrics["active"]),
        ("Maintenance Required", metrics["maintenance_required"]),
        ("Damaged", metrics["damaged"]),
        ("Under Repair", metrics["under_repair"]),
        ("Retired", metrics["retired"]),
    ]


def get_department_distribution(session):
    departments = session.query(Department).all()
    result = []
    for dept in departments:
        count = session.query(Asset).filter(Asset.department_id == dept.id).count()
        result.append((dept.name, count))
    return sorted(result, key=lambda x: x[1], reverse=True)


def get_recent_activity(session, limit=10):
    rows = (
        session.query(AssetHistory, Asset)
        .join(Asset, AssetHistory.asset_id == Asset.id)
        .order_by(AssetHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    return rows


# ---------- Search & filter ----------

def search_and_filter_assets(
    session, search_term=None, asset_types=None, departments=None,
    statuses=None, conditions=None, warranty_status=None,
):
    query = session.query(Asset)

    if search_term:
        term = f"%{search_term.strip()}%"
        query = query.outerjoin(Employee, Asset.employee_id == Employee.id)
        query = query.filter(
            or_(Asset.asset_id.ilike(term), Asset.name.ilike(term), Employee.name.ilike(term))
        )

    if asset_types:
        query = query.filter(Asset.asset_type.in_(asset_types))

    if departments:
        dept_ids = [d.id for d in session.query(Department).filter(Department.name.in_(departments)).all()]
        query = query.filter(Asset.department_id.in_(dept_ids))

    if statuses:
        query = query.filter(Asset.status.in_(statuses))

    if conditions:
        query = query.filter(Asset.condition.in_(conditions))

    assets = query.order_by(Asset.asset_id).all()

    if warranty_status == "Expired":
        assets = [a for a in assets if a.warranty_end and a.warranty_end < date.today()]
    elif warranty_status == "Valid":
        assets = [a for a in assets if a.warranty_end and a.warranty_end >= date.today()]

    return assets


def get_asset_by_asset_id(session, asset_id_str):
    return session.query(Asset).filter(Asset.asset_id == asset_id_str).first()


def get_asset_history(session, asset_pk):
    return (
        session.query(AssetHistory)
        .filter(AssetHistory.asset_id == asset_pk)
        .order_by(AssetHistory.created_at.asc())
        .all()
    )


def get_all_asset_types(session):
    rows = session.query(Asset.asset_type).distinct().all()
    return sorted([r[0] for r in rows])


def get_all_department_names(session):
    rows = session.query(Department.name).order_by(Department.name).all()
    return [r[0] for r in rows]


def get_all_departments(session):
    return session.query(Department).order_by(Department.name).all()


def get_all_locations(session):
    return session.query(Location).order_by(Location.name).all()


def get_all_employees(session):
    return session.query(Employee).order_by(Employee.name).all()


# ---------- Asset creation ----------

def next_asset_id_for_type(session, asset_type):
    prefix = ASSET_TYPE_PREFIXES.get(asset_type, asset_type[:2].upper())
    existing = session.query(Asset).filter(Asset.asset_type == asset_type).count()
    return generate_asset_id(prefix, existing + 1)


def create_asset(session, asset_type, name, brand, model, department_id, location_id, employee_id,
                  purchase_date, purchase_cost, warranty_end, condition, status, image_path=None, notes=""):
    asset_id_str = next_asset_id_for_type(session, asset_type)
    asset = Asset(
        asset_id=asset_id_str, asset_type=asset_type, name=name, brand=brand, model=model,
        department_id=department_id, location_id=location_id, employee_id=employee_id,
        purchase_date=purchase_date, purchase_cost=purchase_cost, warranty_end=warranty_end,
        condition=condition, status=status, image_path=image_path, notes=notes,
    )
    session.add(asset)
    session.flush()
    log_event(session, asset.id, "Registered", "Asset registered.", new_status=status)
    session.commit()
    return asset


# ---------- Replacement lookups ----------

def get_replacement_links(session, asset_pk):
    """Returns (replaced_by_asset, replacement_for_asset) — either can be None."""
    replaced_by_link = session.query(Replacement).filter(Replacement.old_asset_id == asset_pk).first()
    replacement_for_link = session.query(Replacement).filter(Replacement.new_asset_id == asset_pk).first()

    replaced_by_asset = session.get(Asset, replaced_by_link.new_asset_id) if replaced_by_link else None
    replacement_for_asset = session.get(Asset, replacement_for_link.old_asset_id) if replacement_for_link else None

    return replaced_by_asset, replacement_for_asset