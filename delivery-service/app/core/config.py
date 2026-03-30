from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = DATA_DIR / "delivery.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 0