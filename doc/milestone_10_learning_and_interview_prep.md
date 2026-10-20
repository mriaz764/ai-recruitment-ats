# Milestone 10: Learning & Interview Preparation

## Architectural & Technical Decisions

### 1. RFC-5545 iCalendar (`.ics`) Protocol & Organizer Attribution
* **The Decision:** We implemented a native `.ics` generator utility (`app/core/calendar.py`) that formats event start/end times in UTC (`YYYYMMDDTHHMMSSZ`) and injects `ORGANIZER:mailto:<recruiter_email>` dynamically from `AuthContext`.
* **The "Why":** Calendar clients (Google Calendar, Outlook, Apple Calendar) require strict RFC-5545 compliance to render event invites inline inside emails. Setting the recruiter's authenticated email as the `ORGANIZER` ensures that calendar clients grant the recruiter host rights to update or reschedule the event later.

### 2. Asynchronous Non-Blocking Dispatch with `BackgroundTasks`
* **The Decision:** Email and `.ics` generation run in a background execution queue via FastAPI's `BackgroundTasks`, added directly inside `service.create_interview`.
* **The "Why":** Network calls to SMTP servers or email APIs (SendGrid/Resend) add latency (200ms–1500ms). Executing the email task in the background allows the API endpoint to return an HTTP `201 Created` response immediately after the DB transaction commits, keeping UI latency under 50ms.

### 3. Provider Strategy Pattern for Future Scalability
* **The Decision:** The interview scheduling core relies on an abstract dispatch function rather than binding hard dependencies to Google Calendar or Outlook APIs directly.
* **The "Why":** This allows seamless upgrading from basic `.ics` email invites to direct 2-way Google Calendar / Microsoft Graph OAuth API synchronization without modifying the core domain logic in `app/modules/interviews/service.py`.

---

## Senior Engineering Interview Q&A

**Q: How do you handle sending calendar invites without introducing latency in your HTTP API responses?**
**A:** "I offload invitation generation and email dispatch to asynchronous background execution using FastAPI's `BackgroundTasks`. The database transaction commits first, ensuring data integrity. Once committed, the email task is queued to run outside the main request/response cycle, allowing the client to receive an immediate HTTP 201 response while the email dispatch runs concurrently."

**Q: Why is it important to set the `ORGANIZER` header dynamically in generated `.ics` files?**
**A:** "In the RFC-5545 iCalendar specification, calendar clients like Outlook and Google Calendar use the `ORGANIZER` property to establish ownership of an event. If you hardcode a generic system address, recipient calendar apps won't treat the recruiter as the event host. By dynamically pulling the authenticated recruiter's email from `AuthContext` and setting it as `ORGANIZER:mailto:`, the host can manage and update the calendar event directly from their primary inbox calendar."

## Architectural & Technical Decisions

**1. Domain Exceptions vs. Framework Exceptions**
*   **The Decision:** We removed all `fastapi.HTTPException` calls from the Service layer and replaced them with custom, domain-specific exceptions (e.g., `UnauthorizedError`, `ForbiddenError`) inheriting from a base `AppError`.
*   **The "Why":** The Service layer contains pure business logic. It should not know that it is connected to a web framework (FastAPI). If we ever migrate to a GraphQL API, gRPC, or an event-driven queue (like Celery/Kafka), the Service layer remains completely unchanged. A global exception handler at the FastAPI Router layer translates these domain errors into HTTP status codes.

**2. Tenant Context on Authentication**
*   **The Decision:** The `login` and `register` endpoints return `organization_id` and `organization_name` inside the `AuthResponse` alongside the JWT.
*   **The "Why":** In a multi-tenant SaaS, the frontend needs to know the user's active tenant boundary immediately to load the correct UI layout and state. Returning this in the auth payload eliminates a redundant `GET /me` or `GET /organizations` round-trip request on every single login.

**3. Safe Schema Evolution (Alembic Intervention)**
*   **The Decision:** When refactoring `User.name` to `full_name`, we manually edited the Alembic migration script to use `op.alter_column` instead of accepting the auto-generated `op.drop_column` and `op.add_column`.
*   **The "Why":** Auto-generators cannot reliably distinguish between a renamed column and a deleted/recreated column. Relying on the auto-generator for a rename in a production database will result in catastrophic data loss (dropping the column deletes all existing user data).

**4. Black-Box Integration Testing**
*   **The Decision:** In `test_interviews.py`, tests must authenticate via the `/auth/register` API to acquire a real JWT, rather than directly mocking the FastAPI dependency or creating `User` database models manually.
*   **The "Why":** This guarantees that our authentication middleware (`get_current_context`) works in reality, not just in theory. It also explicitly proves our cross-tenant data isolation: we can programmatically create "User A in Org A" and "User B in Org B" via the API and verify that User A receives a 404 when attempting to access User B's resources.

---

## Senior Engineering Interview Q&A

**Q: In your ATS project, how did you handle database schema migrations that involved renaming columns or changing data types?**
**A:** "I used Alembic for database migrations, but I never blindly trusted the `--autogenerate` flag. For example, when refactoring the User model to use `full_name`, the auto-generator attempted to drop the old column and add a new one, which would wipe production data. I manually intervened in the generated Python migration script and used `op.alter_column` to safely rename the attribute at the PostgreSQL level, preserving all existing records."

**Q: Why did you pass complete Pydantic schema objects (like `RegisterRequest`) into your Service layer instead of unpacking the arguments in the Controller?**
**A:** "Passing the schema object directly prevents the 'Long Parameter List' code smell. As the registration requirements grew to include full names, organizations, and passwords, passing individual strings made the function signatures brittle and error-prone. By passing the Pydantic schema, the Service layer has guaranteed, validated data structures, and adding new fields only requires updating the schema and the specific Service logic, without touching the intermediary Controller signatures."

**Q: If I look at your Service layer, I won't see any HTTP status codes like 404 or 401. How does your API return the right errors?**
**A:** "I enforce strict Layered Architecture. The Service layer is decoupled from the web transport layer. It raises domain exceptions like `ConflictError` or `ForbiddenError`. At the top level (the FastAPI application instance), I have global exception handlers that catch these custom `AppErrors` and map them to the appropriate HTTP status codes (409, 403, etc.). This makes the Service layer highly testable and framework-agnostic."