import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Load key-value pairs from .env into os.environ
#load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

# Load .env explicitly using an absolute path
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://ats_user:local_dev_password@localhost:5433/recruitment_ats",
)

# Environment Mode
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"

AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
CSRF_TOKEN_EXPIRE_MINUTES = int(os.getenv("CSRF_TOKEN_EXPIRE_MINUTES", "1440"))  # Default: 24 hours
# CV files are stored privately, outside the public web directory.
BASE_DIR = Path(__file__).resolve().parents[2]
RESUME_STORAGE_DIR = Path(
    os.getenv("RESUME_STORAGE_DIR", str(BASE_DIR / "private_uploads" / "resumes"))
).resolve()

MAX_RESUME_SIZE_BYTES = int(os.getenv("MAX_RESUME_SIZE_BYTES", str(5 * 1024 * 1024)))


