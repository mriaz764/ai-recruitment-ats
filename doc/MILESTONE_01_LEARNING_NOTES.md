# Milestone 1 — Learning Notes

**Project:** AI Recruitment ATS
**Milestone:** Project initialization and FastAPI health endpoint
**Environment:** Conda environment `recruitment-ats`, Python 3.12
**Status:** Tests and Ruff checks passed in the user's local environment.

## 1. What we accomplished

- Created a dedicated Conda environment with Python 3.12.15.
- Configured package metadata and dependencies in `backend/pyproject.toml`.
- Created a FastAPI app and `GET /health` endpoint.
- Added an automated test and verified the endpoint in the browser and `/docs`.
- Ran pytest, Ruff linting, and Ruff formatting checks.

Latest reported results:

```text
1 passed
All checks passed!
2 files already formatted
```

## 2. Conda environments

An environment isolates a project's Python interpreter and packages so projects can use different dependency versions.

```bash
conda create -n recruitment-ats python=3.12 -y
conda activate recruitment-ats
python --version
which python
```

A correct interpreter path resembles `.../miniconda3/envs/recruitment-ats/bin/python`.

Each terminal has its own active environment. In a new terminal, run `conda activate recruitment-ats` if the prompt shows `(base)`.

Useful commands:

```bash
conda env list
conda deactivate
python -m pip list
python -m pip check
```

Prefer `python -m pip` over bare `pip` because it uses pip associated with the selected interpreter.

## 3. Understanding `pyproject.toml`

`backend/pyproject.toml` defines package metadata, supported Python versions, dependencies, and tool settings.

- `[build-system]`: how the project package is built/installed.
- `[project]`: package name, version, Python requirement, and runtime dependencies.
- `[project.optional-dependencies]`: optional groups; our `dev` group contains test and quality tools.
- `[tool.pytest.ini_options]`: pytest configuration.
- `[tool.ruff]`: Ruff configuration.

Install the project and development dependencies from the repository root:

```bash
python -m pip install -e "./backend[dev]"
```

`-e` means editable installation: Python imports the local project while you work on it. `[dev]` installs the optional development dependency group. Runtime dependencies are needed to run the application; development dependencies help test and maintain it.

## 4. FastAPI application

Current `backend/app/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(
    title="AI Recruitment ATS",
    description="AI-assisted recruitment and CV screening API",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the basic health status of the API."""
    return {"status": "ok"}
```

- `from fastapi import FastAPI` imports the framework class.
- `app = FastAPI(...)` creates the application object and sets documentation metadata.
- `@app.get("/health")` registers the function below it for HTTP GET requests to `/health`.
- `-> dict[str, str]` is a return type hint: a dictionary with string keys and string values.
- `return {"status": "ok"}` returns a Python dictionary that FastAPI serializes to JSON.
- HTTP `200 OK` is the default success status for this endpoint.

A health endpoint checks that the app can respond. This endpoint does not yet check PostgreSQL or AI-provider availability because those services are not connected.

An API defines how software components communicate. A web API commonly accepts HTTP requests and returns responses, often JSON. REST is an architectural style for APIs; later we will use HTTP methods such as GET, POST, PATCH, and DELETE for different operations.

## 5. Start and inspect the server

From the repository root, with the correct Conda environment active:

```bash
python -m uvicorn app.main:app --app-dir backend --reload
```

- `python -m uvicorn` runs Uvicorn using the active Python interpreter.
- `app.main:app` means “import the variable named `app` from module `app.main`.”
- `--app-dir backend` adds the backend directory to the import path.
- `--reload` restarts the development server when source files change; it is for local development.

Open `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/docs`. In `/docs`, expand `GET /health`, click **Try it out**, then **Execute**. Stop Uvicorn with `Ctrl+C`.

## 6. Automated testing with pytest

Current `backend/tests/test_main.py`:

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- `TestClient` sends requests to the app in-process; no separate Uvicorn server is required.
- `client.get("/health")` sends a simulated HTTP GET request.
- `response.status_code == 200` checks the HTTP status.
- `response.json()` parses the JSON response into Python data.
- `assert` makes a test fail when an expected condition is false.

Run all tests with `python -m pytest -q`. A passing test proves the behavior it checks, not every possible behavior of the app. Later tests will cover validation, permissions, database operations, file parsing, and AI outputs.

## 7. Ruff: linting and formatting

```bash
python -m ruff check backend
python -m ruff format --check backend
```

Apply formatting if needed:

```bash
python -m ruff format backend
```

Linting identifies suspicious or nonconforming code patterns. Formatting standardizes layout. They serve different purposes, and neither replaces tests.

## 8. Git basics

```bash
git status --short
git diff --check
```

- `git status --short` summarizes untracked, staged, and modified files.
- `git diff --check` detects whitespace errors in the diff Git can see. Ordinary diffs omit untracked files, so inspect new files and run tests/linting too.
- An untracked file is not yet included in a commit.

Never commit credentials, real CVs, uploaded documents, or private candidate data. Review changes and checks before committing; only commit after the milestone is complete and the user explicitly approves.

## 9. Debugging lessons

### Packages appear missing

Check the active interpreter before reinstalling packages:

```bash
conda activate recruitment-ats
python --version
which python
python -m pip show fastapi
```

A terminal may be using `(base)` instead of the project environment.

### Deprecation warning

A deprecation warning is not the same as a failed test. It means a library warns that an API may change or be removed. Inspect installed versions and compatibility before changing dependencies. After dependency changes, rerun tests and `python -m pip check`.

### Test passes but browser fails

A pytest TestClient test does not need a separate server. Browser testing does. Check that Uvicorn is running and the URL/port is correct.

## 10. Interview questions and answers

### Beginner

**1. What is Python?**
A high-level general-purpose programming language known for readable syntax and a broad ecosystem.

**2. What is a Python environment?**
An isolated interpreter/package setup for a project. Conda environments can also manage non-Python dependencies.

**3. What is FastAPI?**
A Python framework for APIs with type-hint support, request validation, and automatically generated documentation.

**4. What is Uvicorn?**
An ASGI server used to run an application such as FastAPI.

**5. What is JSON?**
A text format for structured data using objects, arrays, strings, numbers, booleans, and null.

**6. What does HTTP 200 mean?**
The request succeeded.

### Intermediate

**7. What does `@app.get("/health")` do?**
It registers the function below it as the handler for GET requests to `/health`.

**8. Why use type hints?**
They document expected types and help editors, tools, and reviewers. Frameworks can also use annotations to generate schemas and validate data.

**9. What is the difference between unit and integration tests?**
A unit test checks a small piece of behavior in isolation. An integration test checks how components work together. Our route test exercises the FastAPI app, but does not integrate a database or external service yet.

**10. What is dependency management?**
Declaring and installing compatible packages a project needs so its environment can be recreated.

**11. Linting vs formatting?**
Linting flags suspicious or nonconforming patterns; formatting standardizes code layout.

**12. Why does FastAPI provide `/docs`?**
FastAPI generates an OpenAPI schema and serves an interactive Swagger UI by default.

### Advanced

**13. What is ASGI?**
The Asynchronous Server Gateway Interface defines communication between Python web servers and applications, including asynchronous HTTP and WebSocket handling.

**14. Does a passing health endpoint prove the whole service is healthy?**
No. It proves only that the endpoint responds. Production services may have separate liveness and readiness checks for dependencies.

**15. Why constrain dependency versions?**
Constraints reduce risk from incompatible upgrades. Reproducible deployments often use a lock or pinned dependency set and deliberate upgrade testing.

**16. pytest vs TestClient?**
Pytest discovers and runs tests. TestClient is a helper for sending requests to the application without a separate network server.

**17. What risks arise from AI-assisted CV screening?**
Bias, incorrect extraction, unsupported inferences, privacy leaks, prompt injection in uploaded documents, and overreliance on scores. Mitigations include job-related criteria, access controls, evaluation, evidence-based explanations, and human review.

### Follow-up questions to practice

- How would you test a route that depends on PostgreSQL?
- How would you distinguish liveness from readiness?
- How would you handle an invalid or oversized CV upload?
- How would you prevent a candidate from accessing another candidate's application?
- How would you evaluate whether a matching score is reliable and fair?
- What should be logged when an LLM request fails, and what sensitive data should never be logged?

## 11. Practical exercises

1. Add a second string field to the health response and update the test.
2. Add a test that checks the endpoint returns JSON.
3. Explain what `app.main:app` means.
4. Run pytest from the repository root and explain its output.
5. Temporarily make an assertion incorrect, observe the failure, then restore it.
6. Run Ruff's formatter and explain why formatting does not replace testing.
7. Explain why synthetic candidate data should be used during development.

### Self-check

- [ ] I can activate the correct Conda environment.
- [ ] I can explain the purpose of `pyproject.toml`.
- [ ] I can explain what the FastAPI decorator registers.
- [ ] I can run the server and test `/health`.
- [ ] I can run pytest and interpret a failure.
- [ ] I can run Ruff checks and formatting.
- [ ] I can inspect Git status without committing prematurely.
- [ ] I understand that AI recruitment recommendations require evaluation and human review.

## 12. Next milestone

Milestone 2 will strengthen the Python foundations used throughout the ATS: modules, functions, type hints, data structures, exceptions, configuration, and testable code. We will connect each concept to a small project task rather than study concepts in isolation.
