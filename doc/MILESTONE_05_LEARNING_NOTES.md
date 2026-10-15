# Milestone 5 — Learning Notes

**Project:** AI Recruitment ATS  
**Focus:** Candidate management, resume storage, applications, authentication, and organization-level authorization  
**Architecture:** Modular monolith using FastAPI, SQLAlchemy, PostgreSQL, and Pydantic

## 1. What this milestone covers

This milestone extends the Jobs API with candidate and resume management,
application workflows, authentication, and organization-level access control.

The backend follows the feature-first architecture:

Router → Controller → Service → Repository → Database

Each layer has a separate responsibility:

- Router: defines HTTP endpoints, dependencies, and response models.
- Controller: delegates requests to the service layer.
- Service: implements business rules and transaction handling.
- Repository: contains database query and persistence logic.
- Model: maps Python objects to database tables.
- Schema: validates request data and defines response structures.

## 2. Authentication and access tokens

The authentication module uses JWT access tokens.

The token contains:

- `sub`: the user ID.
- `org_id`: the organization ID.
- `iat`: the issue time.
- `exp`: the expiration time.

The token is signed using the configured `AUTH_SECRET_KEY` and the HS256
algorithm.

The authentication dependency:

1. Reads the bearer token.
2. Validates and decodes the token.
3. Loads the user from the database.
4. Rejects missing or inactive users.
5. verifies the user's membership in the requested organization.
6. Checks whether the organization role is allowed to access the ATS.

Authentication failures return HTTP 401. Authenticated users without
sufficient permissions receive HTTP 403.

Access tokens must be kept private. The signing secret must be configured
securely and must not be committed to source control.

## 3. Organization-level authorization

The application obtains the organization ID from the authenticated
context rather than trusting an organization ID supplied by the client.

This is important in a multi-tenant system: a recruiter belonging to one
organization must not be able to read or modify another organization's
records simply by changing a request ID.

The service and repository layers must preserve organization scoping for
candidate and application operations.

## 4. Candidate management

The candidate module manages candidate records.

Candidate operations follow the same layered architecture as the Jobs
module. Request schemas validate incoming data, services implement
business rules, and repositories handle database operations.

Candidate data is associated with the appropriate organization so that
access can be restricted to authorized users.

## 5. Resume upload and download

Resume handling requires more than accepting a filename from a request.

The implementation validates supported resume types and enforces the
configured maximum file size. Storage keys are generated and validated
rather than trusting uploaded filenames as filesystem paths.

Resume storage responsibilities include:

- Validating supported file types and file sizes.
- Using generated storage keys.
- Keeping uploaded files outside public static-file access.
- Checking that requested resume files are authorized.
- Handling database and filesystem failures.
- Cleaning up stored files when an associated database operation fails,
  where applicable.

A database record and a file on disk are separate resources. They do not
share a single atomic transaction, so failure handling and cleanup matter.

Never expose a resume download without checking the requesting user's
authorization.

## 6. Application workflow

An application connects a candidate to a job within an organization.

The application service checks that the candidate and job belong to the
correct organization, rejects inactive jobs, and prevents duplicate
applications for the same candidate and job within an organization.

The database also enforces uniqueness for the organization, candidate,
and job combination. This protects data integrity even if concurrent
requests bypass the service's initial duplicate check.

Application status values are validated through the request schema.
Status changes are performed through the service layer, which handles
database transaction failures.

## 7. Database transactions and error handling

Database operations may fail even after request validation succeeds.

The service layer handles database errors by rolling back the session
where appropriate and re-raising unexpected errors for normal API error
handling.

Expected business conflicts, such as duplicate applications, are
translated into appropriate application errors.

Filesystem operations need their own error handling because a database
rollback cannot automatically restore a file that was deleted or written.

Tests should cover both successful operations and failure paths.

## 8. Testing and code quality

The backend uses pytest for automated tests and Ruff for linting and
formatting.

Run these commands from the `backend/` directory with the correct Conda
environment activated and PostgreSQL available:

```bash
python -m ruff check app tests
python -m ruff format --check app tests
python -m pytest -q


python -m ruff check app tests
python -m ruff format --check app tests
python -m pytest -q

```
