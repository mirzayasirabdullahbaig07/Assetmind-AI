import os
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default: str = None):
    """
    Reads a secret from Streamlit Cloud secrets first (for deployment),
    falling back to a local .env variable (for development).
    """
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


GROQ_API_KEY = get_secret("GROQ_API_KEY")

# --- Groq model configuration ---
# Change models ONLY here, nowhere else in the codebase.
GROQ_TEXT_MODEL = "openai/gpt-oss-120b"
GROQ_VISION_MODEL = "qwen/qwen3.8-27b"

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "assetmind.db")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
UPLOADS_ASSETS = os.path.join(UPLOADS_DIR, "assets")
UPLOADS_INSPECTIONS = os.path.join(UPLOADS_DIR, "inspections")
UPLOADS_REPAIRS = os.path.join(UPLOADS_DIR, "repairs")
UPLOADS_QRCODES = os.path.join(UPLOADS_DIR, "qrcodes")

COMPANY_NAME = "Nexora Technologies"

DEPARTMENTS = ["Software Engineering", "AI/ML", "HR", "Marketing", "Management", "IT Support"]
LOCATIONS = ["Engineering Room", "AI Lab", "HR Office", "Marketing Room",
             "Meeting Room", "Management Office", "IT Room", "Server Room"]