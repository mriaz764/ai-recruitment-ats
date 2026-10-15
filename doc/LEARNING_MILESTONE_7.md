# Milestone 7: Full-Text Candidate Keyword Search & Production Engineering

## 1. FastAPI Route Precedence & Path Resolution Mechanics
* **The Problem / Challenge:** 
  When adding the `GET /candidates/search` endpoint, FastAPI initially returned `422 Unprocessable Content` validation errors during testing. Even though the request URL was correct, FastAPI evaluated `GET /candidates/{candidate_id}` *before* `GET /candidates/search`. Because both routes have two path segments after `/candidates`, FastAPI greedily matched `"search"` as a path parameter and attempted to parse it as an integer `candidate_id`, triggering a Pydantic validation failure.
* **Under the Hood (How Starlette/FastAPI Router Works):**
  FastAPI relies on Starlette's routing mechanism, which evaluates routes sequentially in the order they are registered in the `APIRouter`. Parameterized routes (`/{candidate_id}`) act as wildcard matchers for any string segment in that position unless static literal routes (`/search`) are declared explicitly *above* them.
* **Interview Talking Point:**
  *“When designing RESTful APIs in FastAPI or Express, static path segments must always precede dynamic parameterized paths. This prevents static endpoints from being swallowed by greedy wildcards. In our ATS, we structured our router to enforce exact-match routes first, ensuring zero routing collisions and predictable O(1) route resolution.”*

---

## 2. PostgreSQL Full-Text Search (FTS) vs. Wildcard ILIKE
* **The Architecture:**
  Instead of doing expensive, unindexed `LIKE '%keyword%'` queries (which cause full table scans ($O(N)$ complexity) and cannot leverage database indexes), we utilized PostgreSQL native Full-Text Search via `to_tsvector` and `tsquery` stored against the resume's `raw_text`.
* **The SQLAlchemy Integration Pitfall & Solution:**
  * **The Challenge:** Initial implementation attempted to explicitly wrap the query with `func.plainto_tsquery("english", query)` inside SQLAlchemy's `.match(...)` method. This caused SQLAlchemy to double-wrap the expression (`plainto_tsquery(plainto_tsquery(...))`), resulting in a PostgreSQL `UndefinedFunction` programming error because `plainto_tsquery` does not accept a `tsquery` type as an argument.
  * **The Fix:** SQLAlchemy's `.match()` method natively and automatically invokes `plainto_tsquery` under the hood when passed a raw Python string. Passing the string directly `.match(query)` generates the correct, clean SQL syntax:
    ```sql
    to_tsvector('english', candidate_resumes.raw_text) @@ plainto_tsquery('english', :query)
    ```
* **Interview Talking Point:**
  *“For candidate resume search, exact substring matching with `ILIKE` fails on plurals, tense variations, and semantic stemming (e.g., searching for 'manage' wouldn't find 'managing'). By leveraging PostgreSQL native FTS (`tsvector` and `tsquery`) through SQLAlchemy, we enabled linguistic stemming (English dictionary), high-performance GIN indexing capability, and robust query sanitization with zero additional infrastructure cost.”*

---

## 3. Strict Multi-Tenant Isolation in Search Repositories
* **The Architecture:**
  In a multi-tenant SaaS application, data isolation is paramount. The search repository query explicitly enforces tenant boundaries by combining the search match clause with an organization filter:
  ```python
  statement = (
      select(Candidate)
      .join(CandidateResume, Candidate.id == CandidateResume.candidate_id)
      .where(Candidate.organization_id == organization_id)
      .where(func.to_tsvector("english", CandidateResume.raw_text).match(query))
      .distinct()
  )