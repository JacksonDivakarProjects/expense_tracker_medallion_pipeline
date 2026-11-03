import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --- DIRECTORIES ---
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "01_raw"
DB_DIR = BASE_DIR / "data" / "02_db"
MAPPING_DIR = BASE_DIR / "data" / "03_mapping"

# Auto-create directories if they don't exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)
MAPPING_DIR.mkdir(parents=True, exist_ok=True)

# --- FILE PATHS ---
DB_PATH = str(DB_DIR / "personal_finance.duckdb")
CATEGORY_MAPPING_CSV = str(MAPPING_DIR / "category_mapping.csv")

# --- GCP CREDENTIALS ---
GCP_CLIENT_ID = os.getenv("GCP_CLIENT_ID")
GCP_CLIENT_SECRET = os.getenv("GCP_CLIENT_SECRET")
GCP_REFRESH_TOKEN = os.getenv("GCP_REFRESH_TOKEN")