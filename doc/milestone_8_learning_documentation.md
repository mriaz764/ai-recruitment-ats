# Milestone 8 — Transparent Job Matching & Evidence-Based Scoring

## 1. Executive Summary & Core Objective
In modern recruitment platforms, traditional AI candidate matching relies on opaque "black-box" vector embeddings (e.g., LLM cosine similarity). While powerful, these models lack auditability and explainability—making it difficult for recruiters to justify *why* a candidate matched a role. 

**Milestone 8** introduces a **transparent, deterministic, and explainable job matching engine** into our FastAPI ATS. Instead of black-box scores, it evaluates candidates against recruiter-defined weighted criteria, performs keyword matching, and extracts exact sentence-level evidence snippets from candidate resumes (`raw_text`).

---

## 2. Architectural Design & Layered Pattern
The module follows our strict clean architecture pattern across 4 distinct layers:
1. **Router (`router.py`)**: Exposes REST endpoints under `/jobs/{job_id}/criteria` and `/jobs/{job_id}/matches`, handling request validation and dependency injection.
2. **Controller (`controller.py`)**: Manages request orchestration, HTTP status code translation, and response serialization.
3. **Service (`service.py`)**: Contains core domain business logic, including sentence tokenization, keyword overlap calculation, evidence extraction, and weighted score aggregation.
4. **Repository (`repository.py`)**: Encapsulates all SQLAlchemy database queries, ensuring multi-tenant data isolation.

---

## 3. Database Modeling & Multi-Tenant Isolation (`JobMatchCriteria`)
* **Table**: `job_match_criteria`
* **Core Columns**:
  * `id` (Primary Key)
  * `job_id` (ForeignKey to `jobs.id` with `ondelete="CASCADE"`)
  * `organization_id` (Foreign key / tenant identifier for security)
  * `criterion_name` (String, e.g., "FastAPI Experience")
  * `weight` (Float, relative importance weight, e.g., `2.0`)
  * `keywords` (Text, comma-separated keywords like `fastapi, python, postgresql`)

### Multi-Tenancy & Security
* Every query filters strictly by `organization_id` alongside `job_id`, preventing cross-tenant data leaks.
* Foreign keys ensure referential integrity, where deleting a job automatically cascades and cleans up its associated match criteria.

---

## 4. Core Algorithm & Evidence Extraction Logic
When evaluating candidates (`GET /jobs/{job_id}/matches`), the service layer executes the following deterministic pipeline:

1. **Criteria Fetching**: Retrieves all match criteria configured for the given job.
2. **Candidate Resume Retrieval**: Fetches the latest candidate resume `raw_text`.
3. **Sentence Tokenization & Normalization**:
   * Splits the resume `raw_text` into individual sentences (using punctuation regex or delimiter splitting).
   * Normalizes text to lowercase for robust matching.
4. **Keyword Matching & Evidence Extraction**:
   * For each criterion, splits the comma-separated `keywords` list.
   * Checks if any keyword is present in the resume text.
   * Scans sentences sequentially to find the **first sentence containing a matching keyword**, saving it as the `evidence_snippet`.
5. **Weighted Percentage Score Calculation**:
   * Formula: 
     $$\text{Match Score} = \left( \frac{\sum (\text{matched}_i \times \text{weight}_i)}{\sum \text{weight}_i} \right) \times 100$$
   * Returns a normalized score between `0.0` and `100.0` with a granular criterion breakdown.

---

## 5. Key Interview Talking Points & Deep-Dive Questions

If an interviewer asks about this implementation during a system design or code review, you can highlight these engineering decisions:

* **Why deterministic matching over pure LLM embeddings?**
  * *Answer*: Deterministic keyword scoring combined with sentence extraction provides 100% explainability and auditability. Recruiters can instantly verify *why* a candidate scored 85% by looking at the highlighted evidence snippets directly from their resume.
* **How do you handle performance at scale?**
  * *Answer*: By indexing `job_id` and `organization_id` on the `job_match_criteria` table and leveraging SQLAlchemy 2.0 compiled statements, criteria lookups are $O(1)$ indexed. Text processing is performed efficiently in-memory per candidate during evaluation.
* **How is database schema versioning managed?**
  * *Answer*: Handled via Alembic migrations (`alembic/versions/...`), ensuring reproducible upgrades and downgrades across development, staging, and production environments.