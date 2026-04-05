import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = DATA_DIR / "notification.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

INTEGRATION_SERVICE_URL = os.getenv(
    "INTEGRATION_SERVICE_URL",
    "http://integration-service:8000",
)

REALTIME_HTTP_TIMEOUT = float(os.getenv("REALTIME_HTTP_TIMEOUT", "3"))
REALTIME_ENABLED = os.getenv("REALTIME_ENABLED", "true").lower() == "true"