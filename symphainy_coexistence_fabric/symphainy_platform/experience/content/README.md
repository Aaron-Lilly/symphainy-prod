# Content Experience Surface

**What it is:** User interface for content management — the "Content Pillar."

**What it provides:**
- File upload interface
- Content browsing and search
- File metadata management
- Content visualization

**Capability lens:** `capabilities/content`

**Current implementation:** `solutions/content_solution/`

**SDK operations used:**
- `invoke_intent("ingest_file", ...)` — Upload a file
- `invoke_intent("parse_content", ...)` — Parse content
- `query_state(...)` — Get file/content status

**Layer:** Solutions Plane (above SDK boundary) — must use Experience SDK only.
