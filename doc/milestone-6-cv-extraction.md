# Milestone 6: CV Text Extraction & Hybrid Search Foundation

## 🧠 Architectural Deep Dive
In designing our recruitment ATS, we opted for a **Hybrid SaaS Model** for resume processing:
1. **Manual Tier (Local Parsing):** Uses pure-Python libraries (`pypdf` for PDFs, `python-docx` for Word docs) to extract raw text synchronously during upload at **\$0 API cost**.
2. **Persistence & Search:** Extracted text is stored directly in a `raw_text` TEXT column in PostgreSQL, enabling instant full-text searches (`to_tsvector`) without hitting LLM rate limits or incurring token fees.
3. **AI Tier Readiness (Future Milestones):** The normalized plain text serves as a clean input buffer for future LLM parsing (OpenAI/Gemini), supporting both platform-managed API keys and Bring-Your-Own-Key (BYOK) configurations.

---

## 🛡️ Key Engineering Challenges Solved

- **Orphan File Prevention (Transactional Safety):** If resume binary upload succeeds but text extraction fails (e.g., corrupted file or password-protected PDF), our service catches the exception, deletes the orphaned file from local/cloud storage, and rolls back the database transaction.
- **Table & Multi-Paragraph Extraction:** For DOCX files, standard paragraph iteration misses structured layout data. We implemented table traversal (`doc.tables`) to capture embedded grids, skills lists, and tables.
- **Domain Exception Translation:** Low-level library errors (`PdfReadError`, `BadZipFile`) are intercepted and translated into clean, standardized `CVExtractionError` exceptions with precise error codes (`EMPTY_DOCUMENT`, `CORRUPTED_FILE`, `ENCRYPTED_FILE`, `UNSUPPORTED_FILE_EXTENSION`) mapped to HTTP 400 responses.

---

## 🎯 Backend Interview Questions & Answers

### Q1: How do you handle file uploads safely in a backend application without bloating your database or leaving orphaned files on disk?
**Answer:** 
1. **Size and Type Validation:** Validate file extensions and inspect magic bytes (e.g., checking `%PDF-` header or verifying ZIP central directory structures for DOCX) *before* writing heavy files to disk.
2. **Transactional Storage Cleanup:** Wrap file writing, extraction, and database persistence inside a robust `try...except` block. If a database commit fails or text extraction throws an error, the catch block explicitly invokes storage deletion (`storage.delete_resume()`) to purge the saved file, preventing disk space leaks.

### Q2: Why choose local Python text extraction over sending every uploaded resume directly to an LLM for parsing?
**Answer:**
- **Cost Efficiency:** At scale (e.g., 10,000+ candidate resumes), parsing text via LLM APIs incurs significant token costs and rate-limit bottlenecks. Local extraction (`pypdf`/`python-docx`) runs in milliseconds at zero cost.
- **Hybrid Search Capability:** Storing extracted text in PostgreSQL allows recruiters to perform instant keyword searches using native database full-text search indexes without depending on external AI services. LLM parsing can then be reserved as an on-demand, premium feature for deep profile analysis.

### Q3: How do you test file parsers without cluttering your Git repository with binary `.pdf` and `.docx` test files?
**Answer:**
We use programmatic **`pytest` fixtures** combined with libraries like `python-docx` to dynamically generate valid files (`tmp_path / "resume.docx"`) and malformed headers in memory during test execution. This keeps the repository clean, lightweight, and completely deterministic.