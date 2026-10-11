# Milestone 2 — PostgreSQL, SQLAlchemy, and the Jobs API

## Milestone status

**Implemented and locally verified**

- PostgreSQL 17 runs through Docker Compose.
- FastAPI connects to PostgreSQL through SQLAlchemy.
- The Jobs feature uses a feature-first module structure.
- Jobs can be created and listed through the API.
- Alembic tracks database schema revisions.
- Automated tests cover job creation, listing, request validation, and the health endpoint.
- Ruff linting, Ruff formatting checks, and the test suite pass.

Last reported verification:

```text
ruff check app tests
All checks passed!

ruff format --check app tests
20 files already formatted

pytest -v
4 passed
```

Run these commands from the `backend/` directory to verify the current local state again.

## 1. What we built

The backend currently exposes:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Basic API health check |
| POST | `/jobs` | Create a job |
| GET | `/jobs` | List jobs |

The Jobs endpoints have been tested through Swagger at `http://127.0.0.1:8000/docs`.

A successful `POST /jobs` request returns `201 Created`. A successful `GET /jobs` request returns `200 OK`.

Example request body:

```json
{
  "title": "Senior Flutter Developer",
  "department": "Engineering",
  "description": "Develop and maintain cross-platform mobile applications using Flutter and Dart.",
  "location": "Remote"
}
```

The response includes id, created_at, and is_active. PostgreSQL generates the ID and creation timestamp, while SQLAlchemy supplies the default value for is_active when creating a job.

## 2. Current Jobs module structure

```text
backend/
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   ├── main.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── dependencies.py
│   │   └── session.py
│   ├── api/
│   │   └── routes/
│   │       └── health.py
│   └── modules/
│       └── jobs/
│           ├── controller.py
│           ├── models.py
│           ├── repository.py
│           ├── router.py
│           ├── schemas.py
│           └── service.py
└── tests/
    ├── test_jobs.py
    └── test_main.py
```

The project uses a **modular monolith**: one FastAPI backend and one PostgreSQL database, with clear boundaries between features and layers. These modules are not separate microservices.

## 3. Request flow: route → controller → service → repository

### Router — `app/modules/jobs/router.py`

The router defines HTTP endpoints, declares response models and status codes, and uses FastAPI dependency injection to receive a database session.

`Depends(get_db)` is the standard FastAPI way to request a dependency. Ruff's `B008` rule is intentionally ignored for this router file only because this pattern is expected in FastAPI route declarations.

### Controller — `app/modules/jobs/controller.py`

The controller coordinates the endpoint and delegates work to the service. It should not contain SQL queries or transaction details.

### Service — `app/modules/jobs/service.py`

The service implements application/business operations. Creating a job includes the transaction workflow: ask the repository to persist the object, commit the transaction, refresh the object, and roll back if a SQLAlchemy database error occurs.

### Repository — `app/modules/jobs/repository.py`

The repository encapsulates database operations. It adds and flushes a new `Job` object and queries jobs ordered by creation time.

### SQLAlchemy model — `app/modules/jobs/models.py`

The `Job` model describes the database table and its columns using SQLAlchemy's typed ORM mapping.

Current columns:

- `id`
- `title`
- `department`
- `description`
- `location`
- `is_active`
- `created_at`

The `id` is a primary key. PostgreSQL automatically maintains its sequence. We removed the extra `ix_jobs_id` index because the primary-key index already indexes `id`.

### Pydantic schemas — `app/modules/jobs/schemas.py`

- `JobCreate` validates incoming request data and field length constraints.
- `JobRead` describes the response shape.
- `ConfigDict(from_attributes=True)` allows Pydantic to build a response from SQLAlchemy model attributes.

Database models and API schemas serve different purposes: the model represents persistence, while the schema defines the API contract.

## 4. Database session and dependency injection

### Configuration — `app/core/config.py`

`DATABASE_URL` is read from the environment and has a local development fallback. Do not use the local fallback credentials in production.

### Engine and session factory — `app/db/session.py`

- The SQLAlchemy engine manages connectivity and connection pooling.
- `SessionLocal` creates database sessions.
- `Base` is the declarative base used by ORM models.

### Request-scoped dependency — `app/db/dependencies.py`

`get_db()` creates a session, yields it to the request, and closes it in a `finally` block. This makes session cleanup reliable even when request processing raises an exception.

The service owns the transaction for job creation; closing a session and committing a transaction are different operations.

## 5. PostgreSQL with Docker Compose

The root `docker-compose.yml` runs PostgreSQL 17. The local host port is `5433`, mapped to PostgreSQL's container port `5432`, because port `5432` was already occupied on the development machine.

The configured development database is:

- Database: `recruitment_ats`
- User: `ats_user`
- Host port: `5433`

The compose file contains a development password. Keep this configuration local and replace it with secure secret management before deployment. Never commit real production credentials.

Useful commands from the repository root:

```bash
docker compose up -d
docker compose ps
docker compose logs db
docker compose exec db psql -U ats_user -d recruitment_ats
```

To inspect the Jobs table:

```sql
\d jobs
```

Exit the `psql` prompt with `\q`.

## 6. Alembic migrations

Alembic tracks database schema versions. The repository has two revisions:

1. `b5ad1ab80cd0` — baseline for the existing `jobs` table.
2. `9c82c7273610` — removes the redundant `ix_jobs_id` index.

The existing table was already present before Alembic was introduced. We used `alembic stamp head` to record the baseline revision without executing the baseline migration's `upgrade()` function. We then generated and applied a new migration that removed only the redundant index.

This distinction matters:

- `alembic stamp head` records a revision; it does not apply the migration operations.
- `alembic upgrade head` applies outstanding migration operations and advances the database revision.
- `alembic current` reports the revision recorded for the connected database.
- `alembic history` shows the migration history.

Run Alembic commands from the `backend/` directory, where `alembic.ini` is located:

```bash
alembic current
alembic history
alembic upgrade head
```

When changing a model in the future:

1. Update the SQLAlchemy model.
2. Generate a migration with `alembic revision --autogenerate -m "describe change"`.
3. Inspect the generated migration manually.
4. Apply it with `alembic upgrade head`.
5. Verify the database and run the tests.

Never assume an autogenerated migration is correct without reviewing it.

## 7. Automated tests

The test suite currently contains four tests:

- `test_create_job_returns_created_job`
- `test_list_jobs_returns_saved_job`
- `test_create_job_rejects_invalid_input`
- `test_health_check_returns_ok`

The Jobs tests use a database connection and transaction, then roll the transaction back during cleanup. This is intended to keep test records from being permanently committed.

These tests use the configured PostgreSQL database. Make sure Docker is running before running them. For larger future test suites, consider a dedicated test database so tests never risk interacting with development data.

Run tests from `backend/`:

```bash
pytest -v
```

## 8. Code quality checks

Run these commands from `backend/`:

```bash
ruff check app tests
ruff format --check app tests
pytest -v
```

What they do:

- `ruff check` reports lint and code-quality issues.
- `ruff format --check` verifies consistent formatting without modifying files.
- `pytest -v` runs the automated tests.

To apply formatting when necessary:

```bash
ruff format app tests
```

The `B008` Ruff rule is configured as a per-file ignore for `app/modules/jobs/router.py`, because FastAPI route parameters commonly use `Depends(...)` in defaults. Keep this exception scoped to the router instead of disabling the rule globally.

## 9. Local development workflow

Activate the Conda environment from the repository root:

```bash
conda activate recruitment-ats
```

Start the database from the repository root:

```bash
docker compose up -d
```

Start the API from the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

Open Swagger:

- `http://127.0.0.1:8000/docs`

Stop the development API with `Ctrl+C`.

Before considering a change complete:

1. Run relevant tests.
2. Run Ruff lint checks.
3. Run Ruff formatting checks.
4. Inspect the Git diff, including untracked files.
5. Update documentation when behavior or setup changes.
6. Commit only after reviewing the changes and receiving explicit approval.

## 10. Known limitations and next steps

This milestone implements basic job creation and listing. It is not yet a complete recruitment ATS.

Not implemented yet:

- Authentication and organization/tenant authorization
- Job detail, update, publish, and close endpoints
- Applications and CV upload
- CV extraction and parsing
- Matching, embeddings, RAG, and AI workflows
- Pagination and search/filtering for job listings
- A dedicated test database configuration
- Production secret management and deployment hardening

Next, we should finish the documentation and Git review, then choose the next feature milestone. Do not add extra abstractions unless a real requirement justifies them.

## 11. Responsible recruitment design

AI-assisted screening must support human review rather than make final hiring decisions. Use job-related criteria, expose evidence and uncertainty, protect candidate data, and do not score candidates on protected traits or unrelated proxies. Development tests should use fictional data rather than real CVs.
