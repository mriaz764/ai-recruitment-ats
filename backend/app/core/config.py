import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]

# Load .env explicitly using an absolute path
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://ats_user:local_dev_password@localhost:5433/recruitment_ats",
)

# Environment Mode
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"

# Authentication
AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "test_secret_key_change_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
CSRF_TOKEN_EXPIRE_MINUTES = int(os.getenv("CSRF_TOKEN_EXPIRE_MINUTES", "1440"))

# AI Provider API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Resume Storage
RESUME_STORAGE_DIR = Path(
    os.getenv("RESUME_STORAGE_DIR", str(BASE_DIR / "private_uploads" / "resumes"))
).resolve()
MAX_RESUME_SIZE_BYTES = int(os.getenv("MAX_RESUME_SIZE_BYTES", str(5 * 1024 * 1024)))


# Unified Settings Container to support `from app.core.config import settings`
class Settings:
    DATABASE_URL: str = DATABASE_URL
    ENVIRONMENT: str = ENVIRONMENT
    IS_PRODUCTION: bool = IS_PRODUCTION
    AUTH_SECRET_KEY: str = AUTH_SECRET_KEY
    JWT_ALGORITHM: str = JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = ACCESS_TOKEN_EXPIRE_MINUTES
    CSRF_TOKEN_EXPIRE_MINUTES: int = CSRF_TOKEN_EXPIRE_MINUTES
    PLATFORM_GEMINI_API_KEY: str = GEMINI_API_KEY
    PLATFORM_OPENAI_API_KEY: str = OPENAI_API_KEY
    RESUME_STORAGE_DIR: Path = RESUME_STORAGE_DIR
    MAX_RESUME_SIZE_BYTES: int = MAX_RESUME_SIZE_BYTES


settings = Settings()