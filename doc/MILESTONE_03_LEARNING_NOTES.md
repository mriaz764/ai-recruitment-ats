# Milestone 3 — Complete Job Management

## Goal

Implement complete job-management APIs while preserving the existing
FastAPI architecture.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /jobs | Create a job |
| GET | /jobs | List all jobs |
| GET | /jobs/{job_id} | Retrieve one job |
| PUT | /jobs/{job_id} | Replace a job's editable fields |
| PATCH | /jobs/{job_id}/status | Activate or deactivate a job |

## Architecture

The existing feature-first architecture is preserved:

Router -> Controller -> Service -> Repository -> PostgreSQL

- Router: Defines HTTP endpoints, dependencies, and response schemas.
- Controller: Delegates incoming requests to the service.
- Service: Applies business rules and coordinates database transactions.
- Repository: Encapsulates SQLAlchemy database queries and updates.
- Model: Represents the jobs database table.
- Pydantic schemas: Validate requests and serialize API responses.

## Retrieving a Job

The repository queries a job by its ID and returns the matching model
or None when the record does not exist.

The service raises NotFoundError when the job is missing. The centralized
exception handler returns HTTP 404 with the JOB_NOT_FOUND error code.

## Updating a Job

PUT /jobs/{job_id} requires all editable job fields:
title, department, description, and location.

The request is validated using JobUpdate. Invalid data returns HTTP 422.

## Activating and Deactivating Jobs

PATCH /jobs/{job_id}/status accepts an is_active boolean.

- true activates the job.
- false deactivates the job.

The job remains in the database; changing its status does not delete it.

## Database Transaction Safety

Write operations commit when successful. If a SQLAlchemy error occurs,
the service rolls back the transaction and re-raises the exception for
centralized error handling.

## Automated Tests

Tests cover:
- Job creation and listing.
- Retrieving existing and missing jobs.
- Updating existing and missing jobs.
- Invalid update input.
- Activating and deactivating jobs.
- Missing jobs during status updates.
- Existing centralized error handling and health checks.

## Verification Results

At the end of implementation:
- 21 tests passed.
- Ruff checks passed.
- All 24 files passed the formatting check.

## Status

Implementation and automated tests completed. Final Git review and
commit approval remain separate steps.
