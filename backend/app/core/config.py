import os
from pathlib import Path

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://ats_user:local_dev_password@localhost:5433/recruitment_ats",
)

AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# CV files are stored privately, outside the public web directory.
BASE_DIR = Path(__file__).resolve().parents[2]
RESUME_STORAGE_DIR = Path(
    os.getenv("RESUME_STORAGE_DIR", str(BASE_DIR / "private_uploads" / "resumes"))
).resolve()

MAX_RESUME_SIZE_BYTES = int(os.getenv("MAX_RESUME_SIZE_BYTES", str(5 * 1024 * 1024)))
