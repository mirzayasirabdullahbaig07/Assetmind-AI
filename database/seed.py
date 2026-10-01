import random
from datetime import date, timedelta

from database.db import get_session
from database.models import Department, Location, Employee, Asset, AssetHistory
import config
from utils.helpers import generate_asset_id

EMPLOYEE_NAMES = [
    "Ali Khan", "Sara Ahmed", "Hamza Malik", "Ayesha Noor", "Usman Raza",
    "Zainab Hussain", "Bilal Aslam", "Mahnoor Fatima", "Fahad Siddiqui", "Hira Javed",
    "Omar Farooq", "Nida Iqbal", "Talha Sheikh", "Amna Qureshi", "Kashif Rehman",
    "Sana Riaz", "Danish Anwar", "Mariam Yousaf", "Waqas Ahmed", "Farah Baig",
    "Adeel Khalid", "Rabia Shah", "Junaid Latif", "Aisha Mumtaz", "Noman Aziz",
]

ASSET_TYPES = {
    "Desktop":   ("D", 35, ["Dell", "HP", "Lenovo"], (55000, 120000)),
    "Laptop":    ("L", 15, ["Dell", "HP", "Apple", "Lenovo"], (90000, 250000)),
    "Monitor":   ("M", 40, ["Dell", "LG", "Samsung"], (18000, 45000)),
    "Chair":     ("C", 45, ["Herman", "Boss", "Nexora Office"], (8000, 25000)),
    "Desk":      ("DK", 35, ["Nexora Office", "IKEA-style"], (12000, 30000)),
    "Keyboard":  ("K", 40, ["Logitech", "Dell", "HP"], (1500, 6000)),
    "Mouse":     ("MS", 40, ["Logitech", "Dell", "HP"], (800, 3500)),
    "UPS":       ("U", 20, ["APC", "Eaton"], (8000, 22000)),
    "Printer":   ("P", 3, ["HP", "Canon"], (25000, 60000)),
    "AC":        ("AC", 5, ["Haier", "Gree"], (60000, 150000)),
    "Projector": ("PJ", 2, ["Epson", "BenQ"], (45000, 90000)),
}

STATUS_WEIGHTS = [
    ("Active", 0.80),
    ("Maintenance Required", 0.08),
    ("Damaged", 0.05),
    ("Under Repair", 0.04),
    ("Retired", 0.03),
]


def _weighted_status():
    r = random.random()
    cumulative = 0
    for status, weight in STATUS_WEIGHTS:
        cumulative += weight
        if r <= cumulative:
            return status
    return "Active"


def _random_date(start_year=2022, end_year=2026):
    start = date(start_year, 1, 1)
    end = date(end_year, 9, 1)
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def seed_database(reset: bool = False):
    """
    Populates the database with Nexora Technologies demo data.
    Safe to call every time the app starts — it only seeds if the DB is empty.
    Pass reset=True to wipe and reseed (used by Settings > Reset Demo Data).
    """
    session = get_session()
    try:
        if reset:
            session.query(AssetHistory).delete()
            session.query(Asset).delete()
            session.query(Employee).delete()
            session.query(Location).delete()
            session.query(Department).delete()
            session.commit()

        if session.query(Asset).count() > 0:
            return

        departments = {}
        for name in config.DEPARTMENTS:
            dept = Department(name=name)
            session.add(dept)
            departments[name] = dept
        session.flush()

        location_dept_map = {
            "Engineering Room": "Software Engineering",
            "AI Lab": "AI/ML",
            "HR Office": "HR",
            "Marketing Room": "Marketing",
            "Meeting Room": None,
            "Management Office": "Management",
            "IT Room": "IT Support",
            "Server Room": None,
        }
        locations = {}
        for loc_name, dept_name in location_dept_map.items():
            loc = Location(
                name=loc_name,
                department_id=departments[dept_name].id if dept_name else None,
            )
            session.add(loc)
            locations[loc_name] = loc
        session.flush()

        employees = []
        dept_list = list(departments.values())
        for i, name in enumerate(EMPLOYEE_NAMES):
            dept = dept_list[i % len(dept_list)]
            emp = Employee(
                name=name,
                email=name.lower().replace(" ", ".") + "@nexora.com",
                department_id=dept.id,
            )
            session.add(emp)
            employees.append(emp)
        session.flush()

        location_list = list(locations.values())
        for asset_type, (prefix, count, brands, cost_range) in ASSET_TYPES.items():
            for i in range(1, count + 1):
                asset_id_str = generate_asset_id(prefix, i)
                dept = random.choice(dept_list)
                loc = random.choice(location_list)
                employee = random.choice(employees) if random.random() < 0.7 else None
                purchase_dt = _random_date()
                warranty_dt = purchase_dt + timedelta(days=365 * random.choice([1, 2, 3]))
                status = _weighted_status()
                condition = "Good" if status == "Active" else random.choice(
                    ["Fair", "Damaged", "Damaged", "Needs Attention"]
                )

                asset = Asset(
                    asset_id=asset_id_str,
                    asset_type=asset_type,
                    name=f"{asset_type} {asset_id_str}",
                    brand=random.choice(brands),
                    model=f"{random.choice(brands)[:2].upper()}-{random.randint(100,999)}",
                    department_id=dept.id,
                    location_id=loc.id,
                    employee_id=employee.id if employee else None,
                    purchase_date=purchase_dt,
                    purchase_cost=round(random.uniform(*cost_range), 2),
                    warranty_end=warranty_dt,
                    condition=condition,
                    status=status,
                    notes="",
                )
                session.add(asset)
                session.flush()

                session.add(AssetHistory(
                    asset_id=asset.id,
                    event_type="Registered",
                    description=f"{asset.name} registered in AssetMind.",
                    old_status=None,
                    new_status="Active",
                ))
                if employee:
                    session.add(AssetHistory(
                        asset_id=asset.id,
                        event_type="Assigned",
                        description=f"Assigned to {employee.name}.",
                        old_status=None,
                        new_status=None,
                    ))

        session.commit()
    finally:
        session.close()