# AI Recruitment ATS

An educational, portfolio-quality Applicant Tracking System (ATS) built incrementally with **FastAPI, Python, PostgreSQL, and AI-assisted CV screening**.

The goal is to build a maintainable recruitment platform while learning backend engineering and AI through a real project.

> **Product principle:** AI assists recruiters; it does not make final hiring decisions. Any future matching scores must be explainable, grounded in job-related evidence, and reviewed by a human.

## Project status

The project is under active development. The backend foundation and first Jobs API are implemented.

### Implemented

- FastAPI application with a health endpoint.
- PostgreSQL 17 running through Docker Compose.
- SQLAlchemy 2.x engine, session factory, ORM base, and request-scoped database dependency.
- Feature-first Jobs module using `router → controller → service → repository`.
- Pydantic request and response schemas.
- Create and list job endpoints.
- Alembic migrations for the Jobs table baseline and a follow-up index cleanup.
- Automated tests for health, job creation, job listing, and invalid job input.
- Ruff linting and formatting checks.

### Not implemented yet

- Authentication or organization/tenant authorization.
- Job detail, update, publish, or close endpoints.
- Applications, candidate records, and CV uploads.
- CV text extraction or structured CV parsing.
- Candidate matching, embeddings, RAG, or AI agent workflows.
- Frontend dashboard.
- Production deployment and production secret management.

This is not yet production-ready recruitment software.

## Technology stack

| Area | Technology | Purpose |
|---|---|---|
| Backend API | Python 3.12, FastAPI | HTTP endpoints and API documentation |
| Validation | Pydantic | Request validation and response contracts |
| Database | PostgreSQL 17 | Persistent application data |
| ORM | SQLAlchemy 2.x | Python models and database access |
| Database migrations | Alembic | Versioned schema changes |
| PostgreSQL driver | Psycopg 3 | Connect Python to PostgreSQL |
| Testing | pytest, FastAPI TestClient | Automated API and behavior tests |
| Code quality | Ruff | Linting and formatting |
| Local database runtime | Docker Compose | Reproducible local PostgreSQL |
| Environment | Conda | Isolated Python environment |

Planned technologies include Next.js, CV parsing libraries, an LLM provider, embeddings, pgvector, and RAG. They are not part of the current implementation unless explicitly added in a later milestone.

## Architecture

The backend is a **modular monolith**: one FastAPI application and one PostgreSQL database, with code organized by feature. We are not splitting the application into microservices.

The Jobs request flow is:

```text
HTTP request
    ↓
Router
    ↓
Controller
    ↓
Service
    ↓
Repository
    ↓
SQLAlchemy model / PostgreSQL
```

### Responsibilities

- **Router** — defines HTTP endpoints, status codes, response models, and dependency injection.
- **Controller** — coordinates the endpoint and delegates work to the service.
- **Service** — implements application/business operations and transaction orchestration.
- **Repository** — encapsulates database query and persistence operations.
- **Model** — defines the SQLAlchemy database mapping.
- **Schema** — defines validated request and response data with Pydantic.
- **Database dependency** — provides a session for a request and closes it afterward.


We keep these layers because they clarify responsibilities and make the feature easier to test. We will avoid adding abstractions that do not solve a real problem.

### Error Handling

- Centralized FastAPI exception handlers for application, validation, HTTP, database, and unexpected errors.
- Consistent API error responses that avoid exposing internal exception details.
- Database transaction rollback on failed write operations.
- Automated tests for error responses and transaction safety.

See [`doc/ERROR_HANDLING_LEARNING_NOTES.md`](doc/ERROR_HANDLING_LEARNING_NOTES.md) for implementation details and learning notes.

## Repository structure

Current backend structure:

```text
ai-recruitment-ats/
├── README.md
├── .gitignore
├── docker-compose.yml
├── alembic.ini
├── doc/
│   ├── MILESTONE_01_LEARNING_NOTES.md
│   └── MILESTONE_02_LEARNING_NOTES.md
└── backend/
    ├── pyproject.toml
    ├── alembic/
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions/
    │       ├── b5ad1ab80cd0_baseline_jobs_table.py
    │       └── 9c82c7273610_remove_redundant_jobs_id_index.py
    ├── app/
    │   ├── main.py
    │   ├── __init__.py
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

Some `__init__.py` files are omitted from this overview for readability. Add future feature modules when implementation begins rather than creating empty directories just to match a target structure.

## Prerequisites

Install the following:

- Git
- Docker Desktop with Docker Compose
- Conda
- Python 3.12 in the `recruitment-ats` Conda environment

Node.js and a frontend toolchain will be needed when we begin the Next.js frontend.

## Local development setup

Commands below assume you are in the repository root unless the step says to change directories.

### 1. Activate the Python environment

```bash
conda activate recruitment-ats
```

If the environment does not exist yet:

```bash
conda create -n recruitment-ats python=3.12 -y
conda activate recruitment-ats
```

### 2. Start PostgreSQL

```bash
docker compose up -d
docker compose ps
```

The Compose configuration uses PostgreSQL 17 and maps host port `5433` to container port `5432`. Port `5433` is used because host port `5432` was already occupied on the development machine.

The local development database configuration currently uses:

- Database: `recruitment_ats`
- User: `ats_user`
- Host: `localhost`
- Port: `5433`

The Compose file contains development credentials. Do not reuse them in production. Production secrets must be supplied securely through environment configuration or a secret manager.

### 3. Install backend dependencies

```bash
cd backend
python -m pip install -e ".[dev]"
```

### 4. Check the database migration version

Run Alembic commands from `backend/`, where `alembic.ini` is located:

```bash
alembic current
alembic history
```

Apply any pending migrations:

```bash
alembic upgrade head
```

The current migration chain is:

1. `b5ad1ab80cd0` — baseline for the existing `jobs` table.
2. `9c82c7273610` — removes the redundant `ix_jobs_id` index.

**Migration note:** The original Jobs table existed before Alembic was introduced. The baseline was registered with `alembic stamp head`, which records a revision without executing its migration operations. A subsequent migration was generated and applied to remove the redundant index. For a new database, review the baseline and use the normal migration workflow from an empty database.

### 5. Start the API

From `backend/`:

```bash
uvicorn app.main:app --reload
```

Open the interactive API documentation:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Health check: <http://127.0.0.1:8000/health>

Stop the development server with `Ctrl+C`.

## Current API endpoints

| Method | Endpoint | Success response | Purpose |
|---|---|---|---|
| GET | `/health` | `200 OK` | Check that the API is responding |
| POST | `/jobs` | `201 Created` | Create a job |
| GET | `/jobs` | `200 OK` | List jobs |

### Create a job

`POST /jobs`

Example request:

```json
{
  "title": "Senior Flutter Developer",
  "department": "Engineering",
  "description": "Develop and maintain cross-platform mobile applications using Flutter and Dart.",
  "location": "Remote"
}
```

The response includes the database-generated `id`, `is_active` default, and `created_at` timestamp.

The API currently uses `/jobs`. The planned API convention is to introduce an `/api/v1` prefix when we deliberately implement API versioning; it has not been added yet.

## Database and migrations

SQLAlchemy models describe the database structure. Alembic tracks changes to that structure as versioned migrations.

Useful commands, run from `backend/`:

```bash
# Show the revision applied to the configured database
alembic current

# Show available migration history
alembic history

# Generate a migration after changing a SQLAlchemy model
alembic revision --autogenerate -m "describe the schema change"

# Apply pending migrations
alembic upgrade head
```

Always inspect autogenerated migration files before applying them. Autogeneration is a starting point, not a guarantee that the migration is correct.

Do not use `Base.metadata.create_all()` as a replacement for the migration workflow in normal application development.

## Testing and code quality

Make sure Docker's PostgreSQL container is running. Then run the following commands from `backend/`:

```bash
ruff check app tests
ruff format --check app tests
pytest -v
```

To apply formatting if needed:

```bash
ruff format app tests
```

The current test suite covers:

- Health endpoint returns a successful response.
- Job creation returns the saved job.
- Job listing returns a saved job.
- Invalid job input is rejected with HTTP `422`.

The Jobs tests use a database transaction that is rolled back during cleanup. The tests connect to the configured database, so a dedicated test database is recommended as the project grows.

Ruff's `B008` rule is intentionally ignored only for `app/modules/jobs/router.py`, where FastAPI's `Depends(...)` declaration is the expected dependency-injection pattern.

## Development workflow

For each feature:

1. Understand the requirement and decide which layer owns each responsibility.
2. Implement the smallest useful change.
3. Add or update tests.
4. Run `ruff check app tests`.
5. Run `ruff format --check app tests`.
6. Run `pytest -v`.
7. Review the complete Git diff, including new untracked files.
8. Update the README or learning notes when setup or behavior changes.
9. Commit only after the changes have been reviewed and explicitly approved.


## Roadmap
We will build the product in small, testable milestones. Check a milestone only after its work is implemented and verified.

### Milestone checklist

- [x] **Milestone 1 — Backend foundation**
  - [x] Initialize the Python project and development tools.
  - [x] Create the FastAPI application.
  - [x] Add the health endpoint and its test.

- [x] **Milestone 2 — Jobs API and PostgreSQL**
  - [x] Configure PostgreSQL with Docker Compose.
  - [x] Add SQLAlchemy session management and a Jobs model.
  - [x] Implement the feature-first Jobs module.
  - [x] Add job creation and listing endpoints.
  - [x] Introduce Alembic migrations.
  - [x] Add API tests and code-quality checks.

- [ ] **Milestone 3 — Complete job management**
  - [ ] Add job detail endpoint.
  - [ ] Add job update endpoint.
  - [ ] Add publish and close operations.
  - [ ] Add tests for successful and invalid operations.

- [ ] **Milestone 4 — Authentication and organizations**
  - [ ] Add authentication.
  - [ ] Add organization and recruiter membership models.
  - [ ] Enforce organization-level authorization before exposing recruiter data.
  - [ ] Test access-control boundaries.

- [ ] **Milestone 5 — Applications and secure CV uploads**
  - [ ] Add application data models and endpoints.
  - [ ] Add CV upload validation and size limits.
  - [ ] Store CVs privately and save file metadata.
  - [ ] Add authorization checks for CV access.

- [ ] **Milestone 6 — CV text extraction**
  - [ ] Extract text from PDF files.
  - [ ] Extract text from DOCX files.
  - [ ] Handle invalid, empty, and unreadable files.
  - [ ] Add tests using fictional sample CVs.

- [ ] **Milestone 7 — Structured CV parsing**
  - [ ] Define validated candidate-profile schemas.
  - [ ] Integrate an LLM provider behind a small provider interface.
  - [ ] Validate structured model output.
  - [ ] Handle missing or ambiguous information without inventing facts.
  - [ ] Add mocked tests that do not require paid API calls.

- [ ] **Milestone 8 — Transparent job matching**
  - [ ] Define job-related criteria and weights.
  - [ ] Implement deterministic matching and scoring.
  - [ ] Return score breakdowns and supporting CV evidence.
  - [ ] Evaluate ranking quality using fictional or properly authorized examples.
  - [ ] Keep final hiring decisions with human reviewers.

- [ ] **Milestone 9 — Next.js recruiter dashboard**
  - [ ] Initialize the Next.js frontend.
  - [ ] Build the recruiter dashboard and job management UI.
  - [ ] Display applications and candidate evidence.
  - [ ] Add loading, empty, validation, and error states.
  - [ ] Connect the frontend to the backend API.

- [ ] **Milestone 10 — Embeddings and semantic retrieval**
  - [ ] Add CV chunking and metadata.
  - [ ] Generate embeddings.
  - [ ] Evaluate PostgreSQL with pgvector for vector storage and search.
  - [ ] Enforce access filters during retrieval.
  - [ ] Compare retrieval results against a small evaluation set.

- [ ] **Milestone 11 — Evidence-grounded RAG**
  - [ ] Retrieve relevant CV passages for job criteria.
  - [ ] Generate structured explanations grounded in retrieved evidence.
  - [ ] Link evidence to source passages where possible.
  - [ ] Test unsupported claims and prompt-injection attempts.
  - [ ] Allow the system to report insufficient evidence.

- [ ] **Milestone 12 — Background workflows and production readiness**
  - [ ] Add background processing when workload justifies it.
  - [ ] Add structured logging, request IDs, and usage/cost tracking.
  - [ ] Harden secrets, access controls, data retention, and deletion.
  - [ ] Add monitoring, backups, and deployment documentation.
  - [ ] Verify failure handling and operational recovery.

Do not start with billing, Kubernetes, a separate vector database, or multi-agent systems. Add complexity only when a real requirement justifies it.

## Responsible AI and candidate privacy

Recruitment can materially affect people's lives. Future AI features must be built with safeguards from the beginning:

- Use documented, job-related criteria.
- Do not score candidates using protected characteristics or unrelated proxies.
- Do not infer personality, honesty, health, or other sensitive traits from CVs.
- Show evidence, uncertainty, missing information, and score breakdowns.
- Let recruiters inspect applications and make the final hiring decisions.
- Use fictional CVs in development and tests.
- Protect uploaded CVs with private storage and access checks.
- Do not send personal candidate data to an external model provider without appropriate authorization and privacy review.
- Keep model outputs and generated explanations subject to validation and human review.

## Learning documentation

- [`doc/MILESTONE_01_LEARNING_NOTES.md`](doc/MILESTONE_01_LEARNING_NOTES.md) — initial backend foundation.
- [`doc/MILESTONE_02_LEARNING_NOTES.md`](doc/MILESTONE_02_LEARNING_NOTES.md) — PostgreSQL, SQLAlchemy, Alembic, Jobs architecture, and tests.

## Final product vision

The completed ATS will let recruiters publish jobs, receive applications, inspect structured CV profiles, review traceable job-match evidence, and manage a human-reviewed shortlist.

Build the system as a learning project first. Use fictional data, test failure cases, evaluate AI quality, and only consider real recruitment use after privacy, security, reliability, and fairness have been properly assessed.
