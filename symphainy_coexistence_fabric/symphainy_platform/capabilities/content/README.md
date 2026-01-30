# Content Capability

**What it does:** Content ingestion, parsing, embeddings, and content management.

**Core functions:**
- File ingestion and upload handling
- Content parsing (PDF, DOCX, text, etc.)
- Deterministic embedding generation
- Content storage and retrieval
- File metadata management

**MVP exposure:** `experience/content`

**Current implementation:** `realms/content/intent_services/`

**Intent types:**
- `ingest_file` — Upload and process a file
- `parse_content` — Extract content from files
- `create_deterministic_embeddings` — Generate semantic embeddings
- `retrieve_content` — Fetch stored content

**Layer:** Execution Plane (below SDK boundary) — may access Public Works and State Surface directly.
