from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    locations = relationship("Location", back_populates="department")
    employees = relationship("Employee", back_populates="department")
    assets = relationship("Asset", back_populates="department")


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    department = relationship("Department", back_populates="locations")
    assets = relationship("Asset", back_populates="location")


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    department = relationship("Department", back_populates="employees")
    assets = relationship("Asset", back_populates="employee")


class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    asset_id = Column(String(20), unique=True, nullable=False)
    asset_type = Column(String(50), nullable=False)
    name = Column(String(150), nullable=False)
    brand = Column(String(100))
    model = Column(String(100))

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    purchase_date = Column(Date)
    purchase_cost = Column(Float)
    warranty_end = Column(Date)

    condition = Column(String(30), default="Good")
    status = Column(String(30), default="Active")
    image_path = Column(String(255))
    notes = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    department = relationship("Department", back_populates="assets")
    location = relationship("Location", back_populates="assets")
    employee = relationship("Employee", back_populates="assets")
    tickets = relationship("MaintenanceTicket", back_populates="asset")
    history = relationship("AssetHistory", back_populates="asset")
    inspections = relationship("Inspection", back_populates="asset")


class MaintenanceTicket(Base):
    __tablename__ = "maintenance_tickets"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(String(20), unique=True, nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    issue_description = Column(Text)
    image_path = Column(String(255))
    ai_findings = Column(Text)
    ai_confidence = Column(Float)

    priority = Column(String(20), default="Medium")
    status = Column(String(30), default="Open")

    reported_by = Column(String(100))
    assigned_to = Column(String(100))
    repair_cost = Column(Float)
    resolution = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime)

    asset = relationship("Asset", back_populates="tickets")


class AssetHistory(Base):
    __tablename__ = "asset_history"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    event_type = Column(String(50), nullable=False)
    description = Column(Text)
    old_status = Column(String(30))
    new_status = Column(String(30))
    related_ticket_id = Column(Integer, ForeignKey("maintenance_tickets.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    asset = relationship("Asset", back_populates="history")


class Inspection(Base):
    __tablename__ = "inspections"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    image_path = Column(String(255))
    detected_object = Column(String(100))
    visible_issue = Column(Text)
    confidence = Column(Float)
    manual_inspection_required = Column(Boolean, default=True)
    ai_notes = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

    asset = relationship("Asset", back_populates="inspections")


class Replacement(Base):
    __tablename__ = "replacements"
    id = Column(Integer, primary_key=True)
    old_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    new_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    reason = Column(Text)
    replacement_cost = Column(Float)
    created_at = Column(DateTime, server_default=func.now())