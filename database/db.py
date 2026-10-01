import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import config

Base = declarative_base()

engine = create_engine(
    f"sqlite:///{config.DB_PATH}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session():
    """Returns a new database session. Caller must close it when done."""
    return SessionLocal()


def ensure_upload_folders():
    for folder in [config.UPLOADS_ASSETS, config.UPLOADS_INSPECTIONS, config.UPLOADS_REPAIRS, config.UPLOADS_QRCODES]:
        os.makedirs(folder, exist_ok=True)


def init_db():
    """Creates all tables if they don't already exist. Safe to call on every app start."""
    from database import models  # registers all table classes onto Base before create_all
    ensure_upload_folders()
    Base.metadata.create_all(bind=engine)