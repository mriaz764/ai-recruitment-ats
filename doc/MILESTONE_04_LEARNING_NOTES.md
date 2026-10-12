# Milestone 4 — Authentication and Organizations

## AI Recruitment ATS — Learning Notes

**Project:** AI Recruitment ATS  
**Milestone:** 4  
**Focus:** Authentication, authorization, organizations, and organization-scoped job APIs  
**Backend:** Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, PyJWT, pwdlib  
**Architecture:** Modular monolith with feature-based modules

---

## 1. Milestone Overview

In Milestone 4, we added authentication and organization management to our AI Recruitment ATS.

Previously, our job APIs allowed requests without verifying the identity of the user. We have now introduced authentication so that users must log in and provide a valid access token to access protected endpoints.

We also introduced organizations so that different companies can use the same ATS without accessing one another's job data.

### What we implemented

- User registration.
- Organization creation during registration.
- Secure password hashing and password verification.
- Login with email and password.
- Signed, expiring JWT access tokens.
- Authentication dependencies in FastAPI.
- Organization membership and role validation.
- Organization-scoped job creation and retrieval.
- Protection against accessing another organization's jobs.
- Database migration for users, organizations, and memberships.
- Automated tests for authentication and organization isolation.
- Updated test fixtures for authenticated API requests.

## 2. Architecture

Our backend follows a modular monolith architecture. The application is deployed as one backend application, but its code is organized into feature-based modules.

We use the following request flow:

`Route → Controller → Service → Repository → Database`

### Responsibilities of each layer

**Routes**

Define API endpoints, HTTP methods, request schemas, and dependencies. They also protect endpoints by requiring authentication or authorization.

**Controllers**

Coordinate the HTTP request and response. They call the relevant service functions.

**Services**

Contain business logic, such as registration, login, password verification, token generation, and organization-related operations.

**Repositories**

Encapsulate database queries, such as finding a user by email or retrieving an organization's membership.

**Models**

Represent database tables using SQLAlchemy ORM.

**Schemas**

Validate incoming request data and define structured API responses using Pydantic.

**Dependencies**

Provide shared resources and security checks, such as database sessions and authenticated-user context.

### Why this architecture?

Separating responsibilities makes the code easier to maintain, test, and extend. For example, authentication rules can be changed in the service layer without placing all the logic inside an API route.

---

## 3. Database Design

We introduced three new database tables and updated the existing jobs table.

### 3.1 Users

The `users` table stores account information.

Important fields:

- `id`: Unique user identifier.
- `email`: User's email address; unique and indexed.
- `password_hash`: Hashed password, not the original password.
- `is_active`: Indicates whether the account is active.
- `created_at`: Account creation timestamp.

**Important:** We never store a user's original password in the database.

### 3.2 Organizations

The `organizations` table represents companies or teams using the ATS.

Important fields:

- `id`: Unique organization identifier.
- `name`: Organization name.
- `created_at`: Organization creation timestamp.

For example, a recruitment company can create an organization and manage its job listings within that organization.

### 3.3 Memberships

The `memberships` table connects users with organizations.

Important fields:

- `id`: Unique membership identifier.
- `user_id`: Reference to a user.
- `organization_id`: Reference to an organization.
- `role`: User's role within the organization.
- `created_at`: Membership creation timestamp.

A unique constraint on `user_id` and `organization_id` prevents the same user from having duplicate memberships in the same organization.

This design allows one user to belong to multiple organizations.

### 3.4 Jobs

We added an `organization_id` column to the existing `jobs` table.

It is a nullable foreign key referencing the organizations table.

Why is it nullable?

Existing jobs were created before organizations existed. Making this column nullable allows the migration to preserve those records without assigning them to an arbitrary organization.

New organization-scoped job records receive the authenticated user's organization ID.

### Database relationship overview

- One user can have multiple organization memberships.
- One organization can have multiple members.
- One organization can have multiple jobs.
- Each membership connects one user to one organization.
- A job created under the new organization-scoped workflow belongs to its associated organization.

---

## 4. User Registration

Registration is implemented through the authentication service.

The registration process follows these steps:

1. Validate the incoming registration request.
2. Normalize the email address by trimming whitespace and converting it to lowercase.
3. Validate the email format.
4. Check whether the email address is already registered.
5. Hash the password.
6. Create the user record.
7. Create the organization.
8. Create an organization membership with the `owner` role.
9. Generate a JWT access token.
10. Commit the database transaction.
11. Return the authentication response.

### Why create an organization during registration?

Our current registration workflow creates an organization for the new user. The first user becomes the organization's owner.

This provides a straightforward onboarding experience for a company setting up its ATS account.

### Why use a database transaction?

Creating a user, organization, and membership involves several related database operations.

A transaction ensures these changes are committed together. If a database operation fails, the service rolls back the transaction rather than leaving a partially created account.

### Duplicate email handling

If an email address is already registered, the API returns a conflict response instead of creating another account.

The application also uses a database uniqueness constraint, providing protection against duplicate records even when concurrent requests occur.

---

## 5. Password Hashing

We use `pwdlib` with its recommended password-hashing configuration, which is configured with Argon2 support.

Password hashing converts a password into a stored hash that can later be verified without saving the original password.

For example:

- Original password: provided by the user during registration.
- Stored value: a password hash generated by the password-hashing library.

We use two main functions:

- `hash_password(password)`: Creates the password hash.
- `verify_password(password, password_hash)`: Checks whether a submitted password matches the stored hash.

### Why not store plain-text passwords?

If the database were exposed, storing original passwords would directly reveal users' credentials. Password hashing reduces that risk.

We also avoid returning password hashes in API responses.

**Learning point:** Password hashing and encryption are different. Password hashing is designed for verification, not for recovering the original password.

---

## 6. Login

The login endpoint accepts an email address and password.

The service performs these operations:

1. Validate and normalize the email address.
2. Find the user by email.
3. Verify that the account exists and is active.
4. Verify the submitted password against the stored password hash.
5. Retrieve the user's organization membership.
6. Generate an access token for the selected organization.
7. Return the token and relevant account and organization information.

If the email or password is incorrect, the API returns `401 Unauthorized` with a generic error message.

This avoids unnecessarily revealing whether a particular email address is registered.

If a valid user has no organization membership, the service returns a `403 Forbidden` response.

### Current organization selection

Our current login implementation selects the user's first membership, ordered by membership ID.

This is sufficient for the current milestone, but it is not a complete organization-switching workflow.

A future enhancement can allow users who belong to multiple organizations to select the organization they want to access.

---

## 7. JWT Access Tokens

JWT stands for JSON Web Token.

A JWT allows the server to identify the user and the organization context associated with an authenticated request.

We use PyJWT to create and validate signed access tokens.

### Token payload

Our token contains:

- `sub`: The user ID, represented as a string.
- `org_id`: The organization ID.
- `iat`: The time the token was issued.
- `exp`: The token expiration time.

The token uses the HS256 signing algorithm.

### Token expiration

The access-token lifetime is configurable through:

`ACCESS_TOKEN_EXPIRE_MINUTES`

The default configured value is 30 minutes.

After expiration, the token is no longer accepted and the user must authenticate again using the current authentication workflow.

### Secret key configuration

The application reads its signing key from the `AUTH_SECRET_KEY` environment variable.

The key must be configured before the application starts.

For local development, you generated a random key using:

```bash
export AUTH_SECRET_KEY="$(openssl rand -hex 32)"
```

This exports the key into the current terminal session. If you open another terminal or restart your shell, you may need to configure it again.

For production, use a secure environment configuration or secrets manager. Never commit the actual secret key to Git or expose it in logs.

### Important JWT security concept

A signed JWT is not automatically encrypted. Its payload can generally be decoded by anyone who obtains the token.

Therefore, do not put passwords, password hashes, or other secrets inside the token.

Our token is signed so the application can detect tampering and validate the token's authenticity and expiration.

---

## 8. Authentication in FastAPI

We implemented shared authentication dependencies in:

`app/modules/auth/dependencies.py`

### HTTP Bearer authentication

Protected endpoints expect an HTTP Authorization header in this format:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

The bearer authentication dependency extracts the token from the request.

### `get_current_context`

The `get_current_context` dependency performs the following checks:

1. Confirms that a bearer token was supplied.
2. Confirms that the authentication secret is configured.
3. Validates the JWT signature and expiration.
4. Reads the user ID and organization ID from the token.
5. Checks that the user exists and is active.
6. Checks that the user still belongs to the organization in the token.
7. Validates the membership role.
8. Returns the authenticated context.

The context includes the user's ID, email, organization ID, organization name, and role.

This means endpoint functions do not need to repeat the same token-validation logic.

### Why verify membership on each request?

A token can remain unexpired after a user is removed from an organization.

Checking the current membership allows the application to reject requests when that membership no longer exists.

This approach does not, by itself, provide immediate revocation of every possible token scenario. Future token-revocation requirements may need additional mechanisms.

### Authentication errors

The authentication dependency returns `401 Unauthorized` when the token is missing or invalid, or when the account is no longer eligible to authenticate.

The response includes a `WWW-Authenticate: Bearer` header for authentication failures where appropriate.

---

## 9. Authorization and Roles

Authentication answers:

**Who is making the request?**

Authorization answers:

**What is that user allowed to do?**

Our organization roles are:

| Role | Intended meaning |
|---|---|
| `owner` | Owns and manages the organization |
| `admin` | Manages organization operations |
| `recruiter` | Performs recruitment work |

The first user created through registration receives the `owner` role.

### Role dependencies

The authentication module includes `require_roles`, which allows endpoints to declare which roles are permitted.

For example, an endpoint could require an owner or administrator role for an organization-management operation.

The current job-manager dependency permits the three defined roles: owner, admin, and recruiter.

**Important:** Defining role names does not automatically implement every possible permission rule. Fine-grained permissions for organization settings, invitations, billing, and user management can be added as those features are implemented.

---

## 10. Organization-Scoped Job APIs

Before this milestone, job endpoints were not scoped to an authenticated organization.

We updated the job API workflow so that the authenticated organization context determines which jobs a user can access.

### Read operations

Listing jobs and retrieving an individual job require authentication.

The organization ID comes from the validated authentication context, not from a client-supplied query parameter or request body.

### Write operations

Creating a job associates it with the authenticated organization.

Updating a job or changing its status also uses the authenticated organization context.

### Why should the client not choose an arbitrary organization ID?

If a server trusts an organization ID supplied by the client without checking membership, a user could attempt to access another organization's data.

Using the validated authentication context helps prevent this class of cross-organization access.

### Organization isolation

The job repository and service apply organization scoping to relevant job queries.

If a user requests a job belonging to another organization, the API returns `404 Not Found` rather than exposing the other organization's job.

This behavior also applies to the tested update and status-update workflows.

For listing jobs, the API returns only jobs belonging to the authenticated organization.

**Learning point:** Authentication alone is not enough for a multi-tenant application. Every data-access path must enforce the correct tenant or organization boundary.

---

## 11. Database Migrations

We added an Alembic migration:

`backend/alembic/versions/4eaa16f7c6c1_add_organizations_and_users.py`

The migration creates:

- `users`
- `organizations`
- `memberships`

It also adds the nullable `organization_id` foreign key and index to `jobs`.

### Why use Alembic?

Alembic manages database schema changes through versioned migration files.

Instead of manually recreating the database whenever a model changes, we can apply migrations in a controlled and repeatable way.

The migration was applied using:

```bash
alembic -c ../alembic.ini upgrade head
```

The database revision was checked using:

```bash
alembic -c ../alembic.ini current
```

The applied revision was:

`4eaa16f7c6c1 (head)`

### Existing job records

The migration preserves existing jobs. Their `organization_id` remains `NULL` unless explicitly assigned through a separate migration or data-management operation.

The new organization-scoped job APIs do not automatically assign these legacy records to the first registered user.

This is intentional: assigning old jobs to an arbitrary organization could expose data to the wrong company.

A future production rollout must include an explicit plan to identify and assign legacy records where appropriate.

---

## 12. Testing

We updated the test infrastructure to support authenticated requests.

### Database fixture

The shared database fixture provides a database session for tests and rolls back test transactions after use.

### Identity fixture

The test identity setup creates an organization, an owner user, and a membership.

The shared test client receives an access token so protected job endpoints can be tested as an authenticated user.

### Authentication tests

The authentication tests cover:

- Successful registration.
- Duplicate-email registration.
- Successful login.
- Invalid login credentials.
- Missing access token.
- Invalid access token.
- Expired access token.

### Organization isolation tests

These tests verify that:

- A user cannot retrieve another organization's job.
- A user cannot update another organization's job.
- A user cannot change another organization's job status.
- Job listings contain only the authenticated organization's jobs.

### Error-handling tests

The existing centralized error-handling tests remain part of the suite.

They help ensure application errors, request validation errors, and database-related failures are handled consistently.

### Verification commands

Run these commands from the backend directory:

```bash
ruff format app tests
ruff check app tests
python -m compileall -q app
pytest -v
git diff --check
```

At the end of the current implementation and before the documentation update, the results were:

- **32 tests passed**
- Ruff checks passed.
- Python compilation check passed.
- `git diff --check` was clean after removing the extra blank line at the end of `pyproject.toml`.

These results describe the code checks performed before the learning document was finalized. Run the checks again after any further code changes.

---

## 13. Important Files Added or Updated

| File or directory | Responsibility |
|---|---|
| `app/core/config.py` | Database and authentication configuration |
| `app/modules/auth/schemas.py` | Registration, login, and authentication response schemas |
| `app/modules/auth/security.py` | Password hashing, password verification, and JWT creation |
| `app/modules/auth/repository.py` | User and membership database queries |
| `app/modules/auth/service.py` | Registration and login business logic |
| `app/modules/auth/controller.py` | Authentication request handling |
| `app/modules/auth/router.py` | Authentication endpoints |
| `app/modules/auth/dependencies.py` | Token validation, authenticated context, and role dependencies |
| `app/modules/organizations/models.py` | User, organization, and membership models |
| `app/modules/jobs/` | Organization-scoped job API workflow |
| `app/db/session.py` | SQLAlchemy engine, base, and session factory |
| `app/db/dependencies.py` | Database-session dependency |
| `alembic/env.py` | Alembic metadata imports |
| `alembic/versions/4eaa16f7c6c1_add_organizations_and_users.py` | Database migration |
| `tests/conftest.py` | Shared database, identity, and authenticated-client fixtures |
| `tests/test_auth.py` | Authentication tests |
| `tests/test_organization_isolation.py` | Cross-organization access tests |
| `tests/test_jobs.py` | Job API tests |
| `tests/test_database_error_handling.py` | Database error-handling tests |
| `tests/test_exception_handlers.py` | Centralized exception-handler tests |

---

## 14. Environment and Dependencies

The backend uses Python 3.12 in the `recruitment-ats` Conda environment.

Activate it with:

```bash
conda activate recruitment-ats
```

The new authentication dependencies include:

```toml
"pwdlib[argon2]>=0.2,<1.0",
"PyJWT>=2.10,<3.0",
```

The backend also uses FastAPI, SQLAlchemy, PostgreSQL, Alembic, Pydantic, and the existing project dependencies.

Keep environment-specific settings outside source code. Do not commit real credentials, database passwords, or signing keys.

---

## 15. Key Lessons Learned

After this milestone, you should understand these concepts:

1. **Password hashing:** Passwords should be stored as hashes, not plain text.
2. **JWT authentication:** A signed token can carry identity and expiration claims.
3. **Authentication dependencies:** FastAPI dependencies allow shared security checks.
4. **Authorization:** A logged-in user may still lack permission to perform an operation.
5. **Multi-tenancy:** An ATS serving multiple companies must isolate each organization's data.
6. **Database relationships:** Foreign keys connect users, organizations, memberships, and jobs.
7. **Transactions:** Related database operations should succeed or fail together.
8. **Database migrations:** Alembic tracks and applies schema changes.
9. **Automated testing:** Authentication and tenant-isolation tests protect important security boundaries.
10. **Layered architecture:** Routes, controllers, services, and repositories have separate responsibilities.

---

## 16. Current Limitations and Future Improvements

The following are future enhancements, not claims that the current milestone has implemented them.

- Organization switching for users who belong to multiple organizations.
- Invitation workflows for adding team members.
- Organization and membership management APIs.
- More granular permissions for owner, admin, and recruiter roles.
- Access-token refresh and revocation workflows.
- Password reset and email verification.
- Login rate limiting and additional abuse protection.
- A deliberate migration plan for legacy jobs without an organization.
- Additional production security and deployment checks.

The current login workflow chooses the first membership. The current registration workflow creates a new organization for the registering user. These behaviors should be considered when designing the next milestone.

---

## 17. Milestone 4 Summary

Milestone 4 adds the foundation for a multi-tenant recruitment ATS.

Users can register, create an organization, log in, and receive a signed access token. Protected job endpoints validate that token and use the user's current organization membership to scope access to job data.

The implementation uses a modular architecture, centralized dependencies, database migrations, and automated tests to keep the codebase maintainable as the product grows.

**Completion status:** Authentication and organization-scoped job API implementation passed the reported checks. Final milestone completion remains subject to saving this document, updating the README checklist, and reviewing the final Git changes.
