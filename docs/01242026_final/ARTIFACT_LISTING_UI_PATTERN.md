# Artifact Listing UI Pattern: Eligibility-Based Dropdowns

**Date:** January 26, 2026  
**Context:** CTO guidance on UI dropdowns and artifact-centric thinking  
**Status:** ✅ **CRITICAL PATTERN - Lock This In**

---

## Executive Summary

**The Key Insight:**
> **UI dropdowns should not list "files." They should list *artifacts filtered by type + lifecycle + eligibility*.**

This pattern transforms UI from file-centric to artifact-centric, making dropdowns capability-based rather than storage-based.

---

## 1. The Mental Shift

### Old Thinking (File-Centric)
```
"What files exist?"
→ Query storage/index
→ Return file objects
→ UI displays files
```

### New Thinking (Artifact-Centric)
```
"What artifacts are valid inputs to the next intent in this journey?"
→ Query artifact index by eligibility
→ Return artifact metadata
→ UI displays eligible artifacts
```

**The Question Changes:**
- ❌ "What files exist?"
- ✅ "What artifacts are eligible for `parse_content`?"

---

## 2. The Canonical Pattern

### General Query Shape

```typescript
listArtifacts({
  tenant_id: string,
  artifact_type: string,
  lifecycle_state?: "READY" | "ARCHIVED",  // Default: READY
  eligible_for?: string  // Next intent: "parse_content", "extract_embeddings", etc.
}): Promise<ArtifactListItem[]>
```

**That's it. That's the pattern.**

---

## 3. Concrete Examples

### Example 1: "Select ingested files available for parsing"

**Old Pattern:**
```typescript
// Query files where status = "uploaded"
const files = await listFiles();
const uploadableFiles = files.filter(f => f.status === "uploaded");
```

**New Pattern:**
```typescript
// Query artifacts eligible for parse_content
const artifacts = await listArtifacts({
  artifact_type: "file",
  lifecycle_state: "READY",
  eligible_for: "parse_content"
});
```

**Eligibility Logic:**
- Artifact type = "file"
- Lifecycle state = READY
- No existing child artifact of type "parsed_content" (optional, policy-dependent)
- File type ∈ {unstructured, hybrid} (optional)

---

### Example 2: "Select parsed files available for deterministic embedding"

**Old Pattern:**
```typescript
// Query parsed_data_files table
const parsedFiles = await listParsedFiles();
```

**New Pattern:**
```typescript
// Query artifacts eligible for extract_deterministic_embeddings
const artifacts = await listArtifacts({
  artifact_type: "parsed_content",
  lifecycle_state: "READY",
  eligible_for: "extract_deterministic_embeddings"
});
```

**Eligibility Logic:**
- Artifact type = "parsed_content"
- Lifecycle state = READY
- Parser type supported (optional)
- Record count > 0 (optional)
- Not already embedded deterministically (optional)

---

### Example 3: "Select deterministic embeddings available for semantic interpretation"

**New Pattern:**
```typescript
const artifacts = await listArtifacts({
  artifact_type: "deterministic_embedding",
  lifecycle_state: "READY",
  eligible_for: "semantic_interpretation"
});
```

**What UI Doesn't Care About:**
- ❌ Where it's stored
- ❌ How it was produced
- ❌ What service ran

**What UI Does Care About:**
- ✅ What it is (artifact_type)
- ✅ Whether it's usable (lifecycle_state, eligibility)

---

## 4. Artifact List Item Structure

### Dropdown Item Schema

```typescript
interface ArtifactListItem {
  artifact_id: string,
  artifact_type: string,
  display_name: string,  // From semantic_payload, NOT filename
  created_at: string,
  lineage_hint?: string,  // "From: Customer Policy PDF"
  summary?: string,  // "12,431 rows", "Policy Sections", etc.
  eligible_for: string[]  // Intents this artifact is eligible for
}
```

### Display Examples

**File Artifact:**
```
"Customer Policy PDF (Uploaded Jan 12)"
```

**Parsed Content Artifact:**
```
"Parsed Policy Table (12,431 rows)"
```

**Deterministic Embedding Artifact:**
```
"Deterministic Embedding v1 (Policy Sections)"
```

**Key Point:**
- `display_name` comes from `semantic_payload`
- NOT from filename
- NOT from storage path

---

## 5. System Roles

### Supabase: Discovery/Index (For Dropdowns)

**Perfect for:**
- `listArtifactsByType()`
- `listArtifactsByTenant()`
- `listArtifactsByLineage()`
- `listArtifactsEligibleForIntent()`

**Returns:**
- Metadata
- Identity
- Eligibility signals

**Never:**
- ❌ Resolves artifacts
- ❌ Retrieves content
- ❌ Validates access (that's Runtime)

---

### Runtime: Resolution (For Actions)

**When user selects artifact:**
```
User clicks artifact in dropdown
→ Pass artifact_id to action
→ Runtime.resolveArtifact(artifact_id)
→ Runtime validates access, lifecycle, state
→ Runtime retrieves content via materialization
→ Return content
```

**Dropdowns never hit Runtime resolution APIs.**
**They only hit index APIs (Supabase).**

---

## 6. Simplification Win

### Old Pattern (Multiple Methods)

```typescript
class ContentAPIManager {
  async listFiles(): Promise<ContentFile[]>
  async listParsedFiles(): Promise<ParsedFile[]>
  async listEmbeddings(): Promise<Embedding[]>
  // ... many more
}
```

### New Pattern (Single Method)

```typescript
class ContentAPIManager {
  async listArtifacts(filters: ArtifactListFilters): Promise<ArtifactListItem[]>
  // That's it. Everything else is just filters.
}
```

**Everything else is just sugar (convenience methods that call `listArtifacts` with specific filters).**

---

## 7. Mapping to Existing Tables

### Source of Truth for Lists

**Primary:**
- `project_files` (artifact index) - main source

**Filters:**
- `artifact_type` (file, parsed_content, embeddings, etc.)
- `tenant_id`
- `lifecycle_state` (READY, ARCHIVED, etc.)
- `deleted = false`
- Lineage fields (parent/root)
- `representation_type` (optional)

### What You Stop Using for UI Lists

**These can still exist for lineage/audit, but:**
- ❌ `parsed_data_files` - never drives UI selection
- ❌ `embedding_files` - never drives UI selection
- ❌ `parsed_results` - never drives UI selection

**Remember:**
> **They never drive UI selection.**

---

## 8. Why This Solves the "Recency" Problem

**Original Concern:**
> "State Surface would have the most recent artifact, not the old one I want"

**Solution:**
- **State Surface = resolution** (when user selects)
- **Supabase = selection** (when user browses)

**Flow:**
1. Dropdown queries Supabase → lists **all eligible artifacts** (not just recent)
2. User selects artifact_id
3. Action resolves via State Surface → gets **that specific artifact**

**No ambiguity. No recency bias. No magic fallbacks.**

---

## 9. Implementation Pattern

### Backend: Artifact Index API

```python
# In Supabase/Index service
async def list_artifacts(
    tenant_id: str,
    artifact_type: str,
    lifecycle_state: str = "READY",
    eligible_for: Optional[str] = None
) -> List[ArtifactListItem]:
    """
    List artifacts from index (Supabase).
    
    This is discovery/index only - not resolution.
    """
    # Query artifact index
    # Apply filters
    # Return artifact metadata (not content)
    pass
```

### Frontend: Artifact Listing

```typescript
// ContentAPIManager.ts
async listArtifacts(filters: {
  artifact_type: string,
  lifecycle_state?: string,
  eligible_for?: string
}): Promise<ArtifactListItem[]> {
  // Query Supabase artifact index
  // Returns artifact metadata for dropdowns
  // NOT content retrieval
}
```

### Frontend: Artifact Resolution

```typescript
// When user selects artifact from dropdown
async resolveArtifact(artifact_id: string, artifact_type: string) {
  // Call Runtime artifact resolution API
  // Runtime validates, resolves, returns content
}
```

---

## 10. The One-Liner (For Team)

> **UI dropdowns enumerate artifacts by eligibility; actions resolve artifacts by ID.**

If they remember only that, you're safe.

---

## 11. Migration Path

### Step 1: Add `listArtifacts()` alongside existing methods

**Backward Compatible:**
```typescript
// Keep existing for now
async listFiles(): Promise<ContentFile[]> { ... }

// Add new
async listArtifacts(filters): Promise<ArtifactListItem[]> { ... }
```

### Step 2: Migrate one dropdown at a time

**Example:**
```typescript
// OLD
const files = await contentManager.listFiles();
const uploadableFiles = files.filter(f => f.status === "uploaded");

// NEW
const artifacts = await contentManager.listArtifacts({
  artifact_type: "file",
  eligible_for: "parse_content"
});
```

### Step 3: Deprecate old methods

Once all dropdowns migrated, deprecate:
- `listFiles()`
- `listParsedFiles()`
- etc.

---

## 12. Success Criteria

### Functional

- ✅ Dropdowns show eligible artifacts (not all files)
- ✅ Artifact selection resolves correctly
- ✅ No storage queries from UI
- ✅ Eligibility logic works correctly

### Architectural

- ✅ UI asks "what artifacts are eligible?" not "what files exist?"
- ✅ Supabase used for discovery, Runtime for resolution
- ✅ Single `listArtifacts()` method, not multiple file methods
- ✅ Artifact-centric mental model throughout UI

---

## 13. Conclusion

**The Fix:**
The fix is not changing the UI flow — it's changing **what backs the dropdowns**.

**Same UX.**
**Radically cleaner architecture.**

**Key Principle:**
> **UI dropdowns enumerate artifacts by eligibility; actions resolve artifacts by ID.**

This pattern transforms UI from file-centric to artifact-centric, making the platform's artifact model visible and consistent throughout the user experience.
