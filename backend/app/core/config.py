import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://ats_user:local_dev_password@localhost:5433/recruitment_ats",
)
