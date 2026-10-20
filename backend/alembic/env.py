
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context
from app.core.config import DATABASE_URL
from app.db.session import Base
from app.modules.applications.models import JobApplication  # noqa: F401
from app.modules.candidates.models import Candidate  # noqa: F401
from app.modules.candidates.resume_models import CandidateResume  # noqa: F401
from app.modules.matching.models import JobMatchCriteria  # noqa: F401
from app.modules.jobs.models import Job  # noqa: F401
from app.modules.organizations.models import (  # noqa: F401
    Membership,
    Organization,
    User,
)
from app.modules.interviews.models import Interview, InterviewInterviewer # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
