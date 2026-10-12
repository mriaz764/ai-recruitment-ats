import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://ats_user:local_dev_password@localhost:5433/recruitment_ats",
)

AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
