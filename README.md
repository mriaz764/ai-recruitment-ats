# AI Recruitment ATS --- AI-Powered CV Screening Platform

An educational, portfolio-quality Applicant Tracking System (ATS) that
helps HR teams publish jobs, collect applications, analyze CVs, retrieve
relevant evidence, and review job-related candidate matches.

> **Product principle:** AI assists recruiters; it does not make final
> hiring decisions. Scores are decision-support signals, not objective
> measures of a person's worth or guaranteed predictors of job
> performance.

## 1. Project Goals

Build a web application where:

1.  HR users can register, sign in, and manage their organization.
2.  Recruiters can create and publish job descriptions with clear,
    job-related criteria.
3.  Candidates can submit applications and upload PDF or DOCX CVs.
4.  The backend securely extracts text and converts CVs into structured
    candidate profiles.
5.  An AI-assisted matching pipeline compares evidence in a CV with a
    job's requirements.
6.  Recruiters can review ranked applications, score breakdowns,
    evidence, and information gaps.
7.  Recruiters---not the AI---make shortlist and hiring decisions.
8.  The project teaches Python, FastAPI, PostgreSQL, LLM integration,
    embeddings, RAG, and agentic workflows through incremental
    implementation.

## 2. MVP Scope

### Included in the first usable version

-   Authentication and organization-level access control
-   Create, edit, publish, close, and view jobs
-   Public job details and candidate application form
-   PDF/DOCX CV upload with file validation
-   CV text extraction and structured profile parsing
-   Configurable job-related criteria and transparent scoring
-   Applicant list sorted by match score
-   Candidate detail page with evidence, strengths, gaps, and source CV
-   Manual review statuses: New, In Review, Shortlisted, Interview,
    Rejected, Hired
-   Basic audit trail for recruiter review actions
-   Tests, Docker-based local development, and deployment documentation

### Later enhancements

-   Semantic search and pgvector
-   Retrieval-Augmented Generation (RAG)
-   Controlled agentic workflow with LangGraph
-   Background processing for large batches of CVs
-   Email notifications and interview scheduling
-   Recruiter analytics and CSV export
-   OCR for scanned documents
-   Billing and multi-plan SaaS subscriptions
-   Multilingual CV support

Do not start with billing, multi-agent systems, Kubernetes, or a
separate vector database. Add complexity only when a real requirement
justifies it.

## 3. Technology Stack

  -----------------------------------------------------------------------
  Area                    Initial choice          Why
  ----------------------- ----------------------- -----------------------
  Frontend                Next.js + TypeScript    HR dashboard and
                                                  candidate-facing pages

  UI                      Tailwind CSS and a      Responsive,
                          consistent component    maintainable interface
                          library

  Backend                 Python + FastAPI        Typed REST APIs and AI
                                                  workflows

  Validation              Pydantic                Validate requests and
                                                  structured model output

  Relational database     PostgreSQL              Users, organizations,
                                                  jobs, applications, and
                                                  review data

  ORM and migrations      SQLAlchemy + Alembic    Database access and
                                                  schema evolution

  PDF parsing             PyMuPDF                 Extract text from
                                                  text-based PDFs

  DOCX parsing            python-docx             Extract text from Word
                                                  documents

  LLM integration         OpenAI or Gemini API    Structured CV parsing
                          behind a provider       and evidence-based
                          interface               explanations

  Embeddings              Hosted embedding API or Semantic representation
                          Sentence Transformers   of CV chunks and job
                                                  requirements

  Vector search           pgvector extension for  Store embeddings and
                          PostgreSQL              perform similarity
                                                  search

  RAG orchestration       Start with plain        Understand retrieval
                          Python; optionally add  before relying on a
                          LangChain               framework

  Agentic workflow        LangGraph in a later    Explicit state, tool
                          phase                   calls, retries, and
                                                  human review

  Testing                 pytest + HTTPX;         Validate logic and API
                          frontend tests as       behavior
                          needed

  Containers              Docker + Docker Compose Reproducible local
                                                  development

  Version control         Git + GitHub            Incremental development
                                                  and reviewable changes
  -----------------------------------------------------------------------

**Model-provider design:** Keep provider-specific calls behind a small
interface so the application can switch providers without rewriting the
matching engine. Never put API keys in frontend code or commit them to
Git.

## 4. High-Level Architecture

``` text
                       ┌────────────────────────────┐
                       │ Next.js Web Application    │
                       │ HR Dashboard + Apply Page  │
                       └──────────────┬─────────────┘
                                      │ HTTPS / REST
                       ┌──────────────▼─────────────┐
                       │ FastAPI Backend            │
                       │ Auth, Jobs, Applications   │
                       └──────┬──────────────┬──────┘
                              │              │
                    ┌─────────▼──────┐  ┌────▼────────────────┐
                    │ PostgreSQL     │  │ Private File Storage│
                    │ + pgvector     │  │ CV documents        │
                    └────────────────┘  └─────────────────────┘
                              │
                       ┌──────▼─────────────────────────┐
                       │ CV Processing Pipeline         │
                       │ Validate → Extract → Parse     │
                       │ → Embed/Retrieve → Match       │
                       └──────────────┬─────────────────┘
                                      │
                       ┌──────────────▼─────────────────┐
                       │ LLM / Embedding Provider       │
                       │ Structured output + embeddings │
                       └────────────────────────────────┘
```

Keep the first release as a **modular monolith**: one frontend, one
Python backend, and one PostgreSQL database. The logical modules should
have clear boundaries, but they do not need to be separate services.

## 5. Proposed Repository Structure

The structure below is the target structure. Create directories when the
relevant phase begins; do not create empty modules just to match the
tree.

``` text
ai-recruitment-ats/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Makefile
├── docs/
│   ├── architecture.md
│   ├── development-roadmap.md
│   ├── api-conventions.md
│   ├── ai-screening-and-evaluation.md
│   ├── privacy-and-security.md
│   └── decisions/
│       ├── 0001-modular-monolith.md
│       └── 0002-transparent-matching.md
├── frontend/
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── public/
│   └── src/
│       ├── app/
│       │   ├── (auth)/
│       │   │   ├── login/
│       │   │   └── register/
│       │   ├── (dashboard)/
│       │   │   ├── dashboard/
│       │   │   ├── jobs/
│       │   │   ├── applicants/
│       │   │   └── settings/
│       │   ├── jobs/[jobId]/
│       │   └── apply/[jobId]/
│       ├── components/
│       │   ├── ui/
│       │   ├── layout/
│       │   ├── jobs/
│       │   └── applicants/
│       ├── lib/
│       │   ├── api-client.ts
│       │   ├── auth.ts
│       │   └── validation.ts
│       └── types/
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   └── exceptions.py
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       └── endpoints/
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── modules/
│   │   │   ├── auth/
│   │   │   ├── organizations/
│   │   │   ├── jobs/
│   │   │   ├── applications/
│   │   │   ├── cv_processing/
│   │   │   ├── matching/
│   │   │   ├── retrieval/
│   │   │   └── screening_workflow/
│   │   └── workers/
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── fixtures/
├── scripts/
│   ├── seed_demo_data.py
│   └── evaluate_matching.py
└── infra/
    └── deployment/
```

### Backend module responsibilities

-   `auth/`: registration, login, identity, and access control.
-   `organizations/`: tenant/company boundaries and recruiter
    membership.
-   `jobs/`: job descriptions, requirements, and publishing status.
-   `applications/`: application submission, status, and CV file
    metadata.
-   `cv_processing/`: file validation, text extraction, normalization,
    and structured parsing.
-   `matching/`: deterministic scoring, score breakdown, and evaluation.
-   `retrieval/`: chunking, embeddings, vector search, and retrieval
    evaluation.
-   `screening_workflow/`: later LangGraph workflow, state, tool
    permissions, and human-review checkpoints.
-   `repositories/`: database query logic.
-   `schemas/`: Pydantic request/response contracts.
-   `models/`: SQLAlchemy persistence models.

Avoid putting all code in one file. Also avoid creating a generic
abstraction for every small function; introduce layers when they make
responsibilities clearer or testing easier.

## 6. Core Data Model

The initial relational model should include:

  -----------------------------------------------------------------------
  Entity                              Important fields / relationships
  ----------------------------------- -----------------------------------
  Organization                        id, name, created_at

  User                                id, email, password_hash or
                                      identity-provider ID

  OrganizationMember                  organization_id, user_id, role

  Job                                 id, organization_id, title,
                                      description, status, criteria_json

  Application                         id, job_id, candidate contact
                                      fields, status, submitted_at

  CVDocument                          id, application_id, storage_key,
                                      mime_type, checksum,
                                      processing_status

  CandidateProfile                    application_id,
                                      structured_profile_json,
                                      parser_version

  ScreeningResult                     application_id, job_id, score,
                                      score_breakdown_json,
                                      evidence_json, model_version,
                                      created_at

  ReviewEvent                         application_id, reviewer_id,
                                      action, notes, created_at

  CVChunk (later)                     document_id, chunk_index, text,
                                      metadata_json, embedding
  -----------------------------------------------------------------------

Use UUIDs or another consistent non-guessable identifier strategy. Store
CV files in private object storage or a private local development
volume---not in a publicly served directory. Store file metadata and
storage keys in PostgreSQL, rather than large file contents, unless
there is a specific reason to do otherwise.

Define tenant isolation from the beginning: every recruiter-facing query
must verify that the authenticated user belongs to the organization that
owns the requested job or application.

## 7. API Plan

Prefix API routes with `/api/v1`.

### Authentication and organizations

-   `POST /api/v1/auth/register`
-   `POST /api/v1/auth/login`
-   `GET /api/v1/auth/me`
-   `GET /api/v1/organizations/current`

Use a proven password-hashing library and established session or token
practices. Add rate limiting and secure cookie/session settings before
production.

### Jobs

-   `POST /api/v1/jobs`
-   `GET /api/v1/jobs`
-   `GET /api/v1/jobs/{job_id}`
-   `PATCH /api/v1/jobs/{job_id}`
-   `POST /api/v1/jobs/{job_id}/publish`
-   `POST /api/v1/jobs/{job_id}/close`

### Applications and CVs

-   `POST /api/v1/jobs/{job_id}/applications`
-   `GET /api/v1/jobs/{job_id}/applications`
-   `GET /api/v1/applications/{application_id}`
-   `GET /api/v1/applications/{application_id}/cv`
-   `PATCH /api/v1/applications/{application_id}/status`

The CV download endpoint must check authorization and return a secure
download or short-lived signed URL. Public applicants should only access
their own submission flow and must not gain access to other candidates'
information.

### Screening and retrieval

-   `POST /api/v1/jobs/{job_id}/screening-runs`
-   `GET /api/v1/jobs/{job_id}/screening-runs/{run_id}`
-   `GET /api/v1/applications/{application_id}/screening-result`
-   `POST /api/v1/jobs/{job_id}/search-candidates` (later semantic
    search)

For batch processing, a screening-run endpoint should eventually return
a run ID and status instead of waiting for every CV and model call to
finish synchronously.

## 8. Development Roadmap

Build in small milestones. Each milestone should have working code,
tests where appropriate, and a Git commit after reviewing the diff.

### Phase 0 --- Project setup and Python foundation

**Learn:** Git, virtual environments, Python modules, type hints,
configuration, and basic testing.

Tasks:

1.  Create the repository and add this README.
2.  Create `backend/` and a Python virtual environment.
3.  Configure dependencies and formatting/linting tools.
4.  Create a minimal FastAPI app with a health endpoint.
5.  Add `.env.example`, `.gitignore`, and safe configuration loading.
6.  Add an initial pytest test.

Acceptance criteria:

-   The API starts locally.
-   `GET /health` returns a successful response.
-   Tests run with one documented command.
-   Secrets and local `.env` files are not committed.

### Phase 1 --- Build a command-line CV reader

**Learn:** pathlib, file handling, exceptions, text normalization,
PDF/DOCX libraries, and unit tests.

Tasks:

1.  Prepare fictional sample CVs with no real candidate personal data.
2.  Extract text from text-based PDF and DOCX files.
3.  Handle empty files, invalid formats, and files with no extractable
    text.
4.  Normalize whitespace and preserve useful section boundaries.
5.  Define a Pydantic schema for candidate profile data.
6.  Write tests using small, non-sensitive fixture documents.

Acceptance criteria:

-   A command can read a sample CV and produce clean text.
-   Unsupported or unreadable documents return a useful error.
-   Unit tests cover normal and failure cases.

Scanned PDFs require OCR and should be treated as a later enhancement.

### Phase 2 --- Structured CV parsing with an LLM

**Learn:** API clients, prompts, structured output, Pydantic validation,
timeouts, retries, and model costs.

Tasks:

1.  Define a schema for skills, roles, dates, projects, education, and
    certifications.
2.  Create an LLM provider interface.
3.  Ask the model to extract only information supported by the CV.
4.  Represent missing or ambiguous details as unknown instead of
    inventing them.
5.  Validate model responses before saving.
6.  Store parser and model versions.
7.  Add mocked tests so normal tests do not require paid API calls.

Acceptance criteria:

-   A sample CV becomes a validated structured profile.
-   Invalid model output is handled safely.
-   The system does not treat an LLM's unsupported inference as verified
    fact.

### Phase 3 --- Job requirements and transparent matching

**Learn:** business rules, scoring algorithms, normalization, ranking,
and evaluation metrics.

Tasks:

1.  Define structured job criteria and their weights.
2.  Implement a deterministic scoring function in plain Python.
3.  Calculate separate scores for required skills, relevant experience,
    projects, and other job-related criteria.
4.  Return a score breakdown and supporting CV evidence for each
    criterion.
5.  Treat missing data as unknown and expose uncertainty.
6.  Create a fictional evaluation dataset with expected outcomes.
7.  Evaluate ranking quality and inspect false positives and false
    negatives.

Acceptance criteria:

-   Identical input produces the same score.
-   Weights are validated and total 100% (or are normalized
    consistently).
-   Every score has an understandable breakdown.
-   Scores do not use protected traits or proxies unrelated to the job.
-   The output is presented as assistance for human review, not an
    automatic employment decision.

The initial matching algorithm does not need embeddings or RAG to be
useful.

### Phase 4 --- FastAPI and PostgreSQL

**Learn:** REST APIs, dependency injection, SQL, relationships,
transactions, migrations, and integration tests.

Tasks:

1.  Configure PostgreSQL and SQLAlchemy.
2.  Create Alembic migrations for core tables.
3.  Implement job CRUD endpoints.
4.  Implement application and CV metadata endpoints.
5.  Add authentication and organization-level authorization.
6.  Validate request and response schemas.
7.  Add integration tests using a test database.

Acceptance criteria:

-   HR can create and manage jobs through the API.
-   Applications are associated with the correct job and organization.
-   Unauthorized users cannot read another organization's records.
-   Database changes are tracked through migrations.

### Phase 5 --- CV upload and application processing

**Learn:** multipart uploads, file security, storage abstraction, and
application workflows.

Tasks:

1.  Build the public job application form.
2.  Validate file size, extension, and actual file content.
3.  Generate safe storage keys; never trust an uploaded filename as a
    filesystem path.
4.  Store CVs privately.
5.  Track processing status and failures.
6.  Connect extraction and parsing to application submission.
7.  Add idempotency and safe retry behavior where appropriate.

Acceptance criteria:

-   A candidate can submit a fictional application and CV.
-   HR can view the application and authorized CV.
-   Invalid files are rejected safely.
-   Failed processing can be retried without creating duplicate
    applications.

### Phase 6 --- Next.js HR dashboard

**Learn:** frontend routing, forms, API integration, table states, error
handling, and access-aware UI.

Tasks:

1.  Build login and dashboard pages.
2.  Build job creation and editing forms.
3.  Build job applicant tables with filters and sorting.
4.  Build candidate detail pages with score breakdown and evidence.
5.  Add manual review actions and notes.
6.  Show processing, empty, loading, and error states.
7.  Ensure keyboard accessibility and responsive layouts.

Acceptance criteria:

-   HR can create a job and inspect applications end to end.
-   Recruiters can see why a candidate matched the listed criteria.
-   HR remains responsible for shortlist decisions.

### Phase 7 --- Embeddings and semantic search

**Learn:** vectors, embedding models, cosine similarity, chunking,
metadata filters, and retrieval evaluation.

Tasks:

1.  Split extracted CV text into meaningful chunks, preserving section
    information.
2.  Generate embeddings for each chunk.
3.  Enable pgvector in PostgreSQL and create a vector column and index
    when justified by dataset size.
4.  Store embedding model and version metadata.
5.  Embed job requirements or recruiter search queries.
6.  Retrieve relevant chunks using vector similarity.
7.  Filter by organization, job/application permissions, and document
    status.
8.  Compare semantic retrieval against keyword-based search on a small
    test set.

Acceptance criteria:

-   A recruiter can search for related experience using natural
    language.
-   Returned passages are relevant and traceable to their source
    document.
-   Cross-organization data is never included in retrieval.
-   Embedding model changes trigger a planned re-embedding process.

Embeddings find semantic similarity; they do not prove that a
requirement is satisfied.

### Phase 8 --- RAG for evidence-based screening explanations

**Learn:** retrieval-augmented generation, context construction,
grounded answers, citations to source passages, and RAG evaluation.

Tasks:

1.  Retrieve relevant CV chunks for each job criterion.
2.  Build a context containing only authorized, relevant evidence.
3.  Ask the LLM to assess the evidence against the criterion.
4.  Return a structured response with evidence references, conclusions,
    and unknowns.
5.  Link each evidence item to a page, section, or chunk where possible.
6.  Keep scoring logic separate from the text-generation step.
7.  Test unsupported claims, irrelevant retrieval, and prompt-injection
    attempts inside CVs.

Acceptance criteria:

-   Explanations are grounded in retrieved CV passages.
-   The model can say "insufficient evidence."
-   The system does not follow instructions embedded in uploaded CVs.
-   Generated explanations are validated and treated as untrusted until
    checked.

RAG is especially useful for questions such as "Which CV passages
support this candidate's payment-integration experience?" It should not
be used merely to add complexity to every API call.

### Phase 9 --- Controlled agentic workflow with LangGraph

**Learn:** stateful workflows, tool calling, conditional edges, retries,
checkpoints, and human-in-the-loop design.

Tasks:

1.  Define a typed workflow state containing job ID, application IDs,
    processing statuses, evidence, and errors.
2.  Add narrowly scoped tools for loading job criteria, retrieving CV
    evidence, parsing a profile, and generating a report.
3.  Use explicit graph nodes and conditional transitions.
4.  Add retry limits, timeouts, and cost limits.
5.  Record workflow events and tool outputs.
6.  Add a human-review checkpoint before any consequential action.
7.  Test failed tools, malformed outputs, duplicated tasks, and
    malicious document content.

Acceptance criteria:

-   The workflow can process a batch and report partial failures.
-   Each tool checks authorization and validates its arguments.
-   The agent cannot execute arbitrary SQL, arbitrary shell commands, or
    unrestricted external actions.
-   It cannot automatically reject applicants or send external
    communications without an explicitly approved process.

Use a workflow graph rather than an unconstrained autonomous agent. Many
steps should remain ordinary deterministic Python functions.

### Phase 10 --- Background processing, security, and deployment

**Learn:** queues, observability, secrets, production configuration,
backups, and deployment.

Tasks:

1.  Add a background worker and queue when batch processing requires it.
2.  Add structured logs, request IDs, and model usage/cost tracking.
3.  Configure rate limits and API timeouts.
4.  Use private object storage and encrypted transport.
5.  Add data-retention and deletion workflows.
6.  Run security checks and dependency updates.
7.  Deploy the frontend, backend, database, and worker.
8.  Document migrations, backups, restore procedures, and rollback
    steps.

Acceptance criteria:

-   A failed CV job does not break other applications.
-   Secrets are stored in a deployment secret manager.
-   Health checks and logs support troubleshooting.
-   Production access is restricted and sensitive CV data is not written
    into ordinary logs.

## 9. AI Screening Design Principles

Recruitment decisions can materially affect people's lives. Build
safeguards into the architecture rather than adding them at the end.

-   Use job-related, documented criteria.
-   Exclude names, photos, gender, age, ethnicity, religion, disability,
    and other protected characteristics from scoring.
-   Be alert to indirect proxies that can reproduce bias.
-   Do not infer personality, honesty, health, or other sensitive
    attributes from a CV.
-   Do not use an LLM score as ground truth.
-   Show the evidence, score breakdown, uncertainty, and missing
    information.
-   Allow recruiters to inspect all applicants and override the
    suggested ordering.
-   Evaluate the system on representative, appropriately authorized data
    before real use.
-   Keep an audit trail of model/version, criteria, result, and human
    review.
-   Define consent, access, retention, and deletion practices for
    candidate information.
-   Do not use real CVs in development fixtures or send personal data to
    a model provider without appropriate authorization and privacy
    review.

## 10. Testing Strategy

### Unit tests

-   PDF/DOCX extraction
-   Text normalization
-   Pydantic schema validation
-   Scoring and weight normalization
-   Chunking and metadata
-   Retrieval filters
-   Workflow transitions

### Integration tests

-   FastAPI endpoints
-   Database repositories and migrations
-   Authentication and tenant isolation
-   File upload and storage
-   Mocked LLM and embedding provider calls

### AI evaluation

Maintain a small, fictional or properly authorized evaluation dataset.
Measure:

-   Extraction accuracy for important fields
-   Retrieval precision at k and recall at k
-   Whether generated claims are supported by retrieved evidence
-   Ranking quality using appropriate labeled test examples
-   Failure rates, latency, and cost per CV
-   Performance across relevant candidate groups, where lawful and
    appropriate to evaluate

Never rely on a few hand-picked examples as proof that the system is
fair or reliable.

## 11. Local Development Setup

### Prerequisites

Install:

-   Python version supported by the selected dependencies
-   Node.js LTS and npm
-   Docker Desktop and Docker Compose
-   Git
-   An editor such as VS Code

### Initial setup

``` bash
# 1. Create and enter the repository
mkdir ai-recruitment-ats
cd ai-recruitment-ats
git init

# 2. Create backend environment
mkdir backend
python3 -m venv .venv

# macOS / Linux
source .venv/bin/activate

# 3. Install the backend dependencies after creating backend/pyproject.toml
# pip install -e "backend/.[dev]"
```

Create the Next.js frontend when Phase 6 begins, or earlier if you
prefer to build the UI in parallel:

``` bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir
```

Create `.env.example` with variable names and safe placeholders, for
example:

``` dotenv
APP_ENV=development
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/recruitment_ats
LLM_PROVIDER=
LLM_API_KEY=
EMBEDDING_MODEL=
CV_STORAGE_PATH=./.local/cv-storage
```

Copy the example to `.env` for local development and fill in only the
credentials you need. Ensure `.env`, uploaded CVs, database volumes, and
generated secrets are excluded from Git. Never commit actual API keys.

The exact dependency versions and database startup commands should be
added when the project is initialized, then locked and tested. Do not
assume the example environment values are production-ready.

## 12. Definition of Done for Each Milestone

Before moving to the next milestone:

1.  The feature works on a clean local setup.
2.  Relevant unit and integration tests pass.
3.  Input validation and failure cases are covered.
4.  Secrets and personal data are not exposed.
5.  The README or related docs are updated.
6.  The diff is reviewed for unrelated changes.
7.  A small, meaningful Git commit records the completed milestone.

Suggested commit sequence:

``` text
chore: initialize project structure and tooling
feat: add FastAPI health endpoint
feat: extract text from PDF and DOCX CVs
feat: parse CVs into validated candidate profiles
feat: implement transparent candidate matching
feat: add PostgreSQL models and migrations
feat: add job and application APIs
feat: add secure CV upload processing
feat: build HR applicant dashboard
feat: add CV embeddings and semantic retrieval
feat: add evidence-grounded RAG explanations
feat: add controlled screening workflow with LangGraph
test: add AI screening evaluation dataset
chore: add Docker deployment and security documentation
```

These are examples, not commits to make in advance. Commit only after
each corresponding implementation is completed and reviewed.

## 13. First Milestone: What We Build Now

Do not build the entire SaaS in the first session.

Start with this small deliverable:

1.  Initialize the repository and Python environment.
2.  Create a minimal FastAPI app with `GET /health`.
3.  Create a `cv_processing` module.
4.  Read one fictional PDF CV and extract its text.
5.  Add one unit test for successful extraction and one for an invalid
    file.
6.  Commit the working result.

Then proceed to structured parsing, matching, persistence, frontend,
embeddings, RAG, and agentic workflows in that order.

## 14. Learning Outcomes

By completing the project, you should have practical experience with:

-   Python fundamentals and maintainable application structure
-   REST APIs and FastAPI
-   PostgreSQL, SQLAlchemy, and migrations
-   Document parsing and structured LLM output
-   Embeddings, vector similarity, and semantic search
-   RAG pipelines and evidence-grounded generation
-   Agentic workflows, tool calling, and human approval
-   Testing, Docker, deployment, and operational monitoring
-   AI evaluation, privacy, and responsible design

## 15. Final Product Vision

The completed product will allow an HR team to publish a job, receive
applications, inspect structured CV profiles, search for relevant
evidence, review explainable job-match scores, and manage a
human-reviewed shortlist.

Build it as a learning project first. Use fictional data during
development, measure the quality of the AI features, and only consider
real recruitment use after privacy, security, reliability, and fairness
have been properly evaluated.
