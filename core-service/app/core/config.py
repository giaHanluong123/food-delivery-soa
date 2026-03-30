from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = DATA_DIR / "core.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"