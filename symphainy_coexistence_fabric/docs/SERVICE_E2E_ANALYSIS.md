# Service E2E Analysis: What Actually Works

**Status:** Living Document (January 2026)
**Purpose:** Trace actual execution paths and identify what works vs what doesn't
**Audience:** Team A (Infrastructure), Team B (Capabilities)

---

## Foundational Principle

> **Infrastructure will ALWAYS be there. That's what Team A guarantees.**
> 
> Any "fallback" pattern that fakes an answer when infrastructure is unavailable is an **ANTI-PATTERN**.
> Services should FAIL LOUDLY, not return fake data.

---

## Fallback Pattern Classification

### ✅ SAFE PATTERNS - Fail Loudly

These patterns are correct - they raise errors when infrastructure is missing:

```python
# CORRECT: Fail loudly when infrastructure missing
if not ctx.platform:
    raise RuntimeError("Platform service not available")

if not ctx.state_surface:
    raise RuntimeError("State Surface not available")

if not self._ingestion:
    raise RuntimeError("IngestionAbstraction not available.")
```

### ❌ ANTI-PATTERNS - Fake Data on Failure

These patterns are BUGS - they return fake/empty data instead of failing:

```python
# BUG: Fake fallback guidance
except Exception as e:
    self.logger.warning(f"Could not get guidance: {e}")
    initial_guidance = {
        "recommended_pillar": "content",
        "reasoning": "Start by uploading your files"  # FAKE DATA
    }

# BUG: Mock classes when library not installed
except ImportError:
    class MockBlob:
        def download_as_bytes(self):
            return b"mock data"  # GARBAGE DATA
```

---

## E2E Path Traces

### 1. File Upload (IngestFileService)

**Path:** Intent → IngestFileService → PlatformService → IngestionAbstraction → UploadAdapter → FileStorageAbstraction → GCSAdapter

```
Step 1: IngestFileService.execute(ctx)
        ✅ Validates boundary_contract_id (FAILS if missing)
        ✅ Validates ctx.platform exists (FAILS if missing)
        
Step 2: ctx.platform.ingest_file(file_data, ...)
        ✅ Checks self._ingestion exists (FAILS if missing)
        
Step 3: IngestionAbstraction.ingest_data(request)
        ✅ Checks upload_adapter exists (returns error result)
        
Step 4: UploadAdapter.ingest(request)
        ✅ Calls file_storage.upload_file()
        
Step 5: FileStorageAbstraction.upload_file(path, data, ...)
        ✅ Calls gcs.upload_file()
        ✅ Calls supabase.create_file() for metadata
        
Step 6: GCSAdapter.upload_file(blob_name, data, ...)
        ⚠️ PROBLEM: If google.cloud not installed → MockBlob
        ⚠️ MockBlob.upload_from_string() does nothing but returns success
```

**VERDICT:** Works E2E **IF** google.cloud is installed. **SILENTLY FAILS** if not.

**ISSUE FOR TEAM A:** `GCSAdapter` has mock fallback (lines 18-73). This should be removed - if google.cloud isn't installed, initialization should fail loudly.

---

### 2. File Parsing (ParseContentService)

**Path:** Intent → ParseContentService → PlatformService.parse() → Parser Abstraction → Parser Adapter

```
Step 1: ParseContentService.execute(ctx)
        ✅ Gets file_id from parameters (FAILS if missing)
        ✅ Gets file metadata from state_surface
        
Step 2: ctx.platform.parse(file_reference, file_type)
        ✅ Gets parser for file_type (FAILS if no parser)
        ✅ Gets file data from state_surface
        
Step 3: Parser.parse(request) or Parser.process(file_ref, data, opts)
        For PDF: PdfProcessingAbstraction → PdfAdapter
        For CSV: CsvProcessingAbstraction → CsvAdapter
        etc.
```

**VERDICT:** Works E2E **IF** parsers are initialized and file exists in state_surface.

**ISSUES FOUND:**
1. `PdfAdapter` (lines 37-46) has fallback from pdfplumber to PyPDF2 - this is **SAFE** (both produce real results)
2. If neither library installed, initialization fails - this is **CORRECT**

---

### 3. File Delete (DeleteFileService)

**Path:** Intent → DeleteFileService → StateSurface → FileStorageAbstraction → GCSAdapter

```
Step 1: DeleteFileService.execute(ctx)
        ✅ Validates file_id or file_reference (FAILS if missing)
        ✅ Checks ctx.state_surface exists (FAILS if missing)
        
Step 2: ctx.state_surface.get_file_metadata(file_reference)
        ⚠️ Returns None if not found (idempotent - OK)
        
Step 3: file_storage.delete_file(storage_location)
        ⚠️ Catches exception, logs warning (OK - file may already be gone)
        
Step 4: ctx.state_surface.delete_file_reference(...)
        ✅ If this fails, exception propagates
```

**VERDICT:** Works E2E. Deletion is idempotent.

---

### 4. User Authentication (AuthenticateUserService)

**Path:** Intent → AuthenticateUserService → SecurityGuardSDK → AuthAbstraction → SupabaseAdapter

```
Step 1: AuthenticateUserService.execute(ctx)
        ✅ Validates email and password (FAILS if missing)
        
Step 2: _authenticate(ctx, email, password)
        ✅ Tries SecurityGuardSDK
        ✅ Falls back to auth_abstraction
        ✅ Returns {"success": False, "error": "..."} if neither works
```

**VERDICT:** Works E2E **IF** Supabase is configured. Returns clear error if not.

---

### 5. Guide Agent Initialization (InitiateGuideAgentService)

**Path:** Intent → InitiateGuideAgentService → ReasoningService.agents.invoke()

```
Step 1: InitiateGuideAgentService.execute(ctx)
        ✅ Creates guide session
        
Step 2: ctx.reasoning.agents.invoke("guide_agent", ...)
        ❌ ANTI-PATTERN: On failure, returns FAKE guidance:
        
        initial_guidance = {
            "recommended_pillar": "content",
            "recommended_action": "upload_files",
            "reasoning": "Start by uploading your files"  # FAKE
        }
```

**VERDICT:** ANTI-PATTERN. Returns fake data when agent unavailable.

**FIX:** Should return clear indicator that AI guidance is unavailable, not fake guidance.

---

### 6. SOP Generation (GenerateSOPService)

**Path:** Intent → GenerateSOPService → ReasoningService.agents.invoke("sop_generation_agent")

```
Step 1: GenerateSOPService.execute(ctx)
        ✅ Validates process_description
        
Step 2: _generate_via_agent(ctx, ...)
        ❌ ANTI-PATTERN: On failure, returns template SOP:
        
        return {
            "title": "SOP: ...",
            "sections": [
                {"title": "Purpose", "content": "[PLACEHOLDER]"},
                ...
            ],
            "note": "TEMPLATE ONLY"
        }
```

**VERDICT:** ANTI-PATTERN. Returns template instead of failing.

**FIX:** Should return `{"success": False, "error": "SOP agent unavailable"}` or raise exception.

---

## Critical Infrastructure Issues for Team A

### Issue 1: GCS Adapter Mock Pattern (CRITICAL)

**Location:** `foundations/public_works/adapters/gcs_adapter.py` lines 18-73

**Problem:** When `google.cloud` library isn't installed, the adapter creates mock classes that pretend to work but actually do nothing.

```python
# CURRENT (ANTI-PATTERN):
except ImportError:
    class MockBlob:
        def upload_from_string(self, data, content_type=None):
            pass  # Does nothing!
        def download_as_bytes(self):
            return b"mock data"  # Returns garbage!
```

**Impact:** File uploads appear to succeed but store nothing. File downloads return `b"mock data"`.

**FIX:**
```python
# CORRECT:
try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound, GoogleCloudError
except ImportError:
    raise ImportError(
        "google-cloud-storage is required for GCSAdapter. "
        "Install with: pip install google-cloud-storage"
    )
```

---

### Issue 2: OpenAI Adapter Mock Pattern

**Location:** `foundations/public_works/adapters/openai_adapter.py` lines 22-28

**Problem:** Similar to GCS - creates mock when openai library not installed.

**FIX:** Fail at initialization if openai not installed.

---

### Issue 3: Word Adapter ImportError Fallback

**Location:** `foundations/public_works/adapters/word_adapter.py` line 36

**Problem:** Catches ImportError for python-docx but unclear what happens.

**Assessment Needed:** Trace what happens if python-docx not installed.

---

## Parlor Trick Remediation Plan

### Pattern A: Agent-Dependent Services

**Services Affected:**
- GenerateSOPService
- GenerateRoadmapService  
- CreateWorkflowService
- CreatePOCService
- CreateBlueprintService
- SynthesizeOutcomeService
- InterpretDataSelfDiscoveryService
- InterpretDataGuidedService
- AnalyzeStructuredDataService
- AnalyzeUnstructuredDataService
- ProcessGuideAgentMessageService
- RouteToLiaisonAgentService

**Current Pattern:**
```python
if ctx.reasoning and ctx.reasoning.agents:
    try:
        result = await ctx.reasoning.agents.invoke("agent_name", ...)
        if result.get("status") == "completed":
            return result
    except Exception:
        pass
return {"placeholder": True, "note": "Requires AI"}  # ANTI-PATTERN
```

**Remediation:**
```python
# OPTION 1: Fail loudly
if not ctx.reasoning or not ctx.reasoning.agents:
    raise RuntimeError("Reasoning service not available")

result = await ctx.reasoning.agents.invoke("agent_name", ...)
if result.get("status") != "completed":
    raise RuntimeError(f"Agent failed: {result.get('error')}")
return result

# OPTION 2: Return clear unavailable status (for non-critical features)
if not ctx.reasoning or not ctx.reasoning.agents:
    return {
        "artifacts": {
            "status": "unavailable",
            "reason": "AI reasoning service not configured"
        },
        "events": [{"type": "agent_unavailable", "agent": "sop_generation_agent"}]
    }
```

---

### Pattern B: Fallback Guidance

**Services Affected:**
- InitiateGuideAgentService

**Current Pattern:**
```python
except Exception:
    initial_guidance = {
        "recommended_pillar": "content",
        "reasoning": "Start by uploading..."  # FAKE
    }
```

**Remediation:**
```python
except Exception as e:
    self.logger.error(f"Guide agent unavailable: {e}")
    session["guidance_status"] = "unavailable"
    session["guidance_error"] = str(e)
    # NO fake guidance - let UI show "AI guidance unavailable"
```

---

## Service Classification (Updated)

| Service | E2E Status | Issues |
|---------|------------|--------|
| IngestFileService | ✅ Works | GCS mock pattern upstream |
| ParseContentService | ✅ Works | Depends on parser libraries |
| DeleteFileService | ✅ Works | Clean implementation |
| ArchiveFileService | ✅ Works | Clean implementation |
| AuthenticateUserService | ✅ Works | Returns clear errors |
| AssessDataQualityService | ✅ Works | Has real algorithms |
| InitiateGuideAgentService | ⚠️ ANTI-PATTERN | Fake fallback guidance |
| GenerateSOPService | ⚠️ ANTI-PATTERN | Returns template |
| GenerateRoadmapService | ⚠️ ANTI-PATTERN | Returns empty structure |
| CreateWorkflowService | ⚠️ ANTI-PATTERN | Returns template |
| All Interpret* services | ⚠️ ANTI-PATTERN | Agent wrappers |
| All Analyze* services | ⚠️ ANTI-PATTERN | Agent wrappers |

---

## Action Items

### For Team A (Infrastructure)

1. **CRITICAL:** Remove GCS mock pattern - fail loudly if google-cloud-storage not installed
2. **CRITICAL:** Remove OpenAI mock pattern - fail loudly if openai not installed
3. **HIGH:** Verify all adapters fail loudly when dependencies missing
4. **MEDIUM:** Add infrastructure health checks to startup

### For Team B (Capabilities)

1. **CRITICAL:** Remove fake fallback patterns from all agent-dependent services
2. **HIGH:** Update services to return clear "unavailable" status instead of fake data
3. **MEDIUM:** Add `intent_type` class attribute to all 47 services missing it
4. **LOW:** Standardize agent `__init__` signatures

---

## Testing Strategy

### E2E Verification Tests

```python
@pytest.mark.integration
async def test_ingest_file_actually_stores_data():
    """Verify file is actually stored, not mocked."""
    # Upload file
    result = await service.execute(ctx)
    assert result["artifacts"]["artifact"]["semantic_payload"]["artifact_id"]
    
    # Verify file exists in GCS
    file_exists = await gcs_adapter.file_exists(storage_location)
    assert file_exists, "File was not actually stored!"
    
    # Verify content matches
    content = await gcs_adapter.download_file(storage_location)
    assert content == original_data, "Stored content doesn't match!"
```

### Anti-Pattern Detection Tests

```python
def test_no_mock_patterns_in_adapters():
    """Ensure adapters don't have silent mock fallbacks."""
    adapter_files = glob.glob("**/adapters/*.py")
    
    for filepath in adapter_files:
        content = open(filepath).read()
        
        # Check for mock fallback pattern
        assert "except ImportError:" not in content or \
               "raise ImportError" in content, \
               f"{filepath} has silent ImportError fallback"
        
        # Check for mock class definitions
        assert "class Mock" not in content, \
               f"{filepath} contains mock class"
```

---

## Questions for Architecture Review

1. **Should agent-dependent services fail loudly or return "unavailable" status?**
   - Fail loudly = Frontend shows error
   - Unavailable status = Frontend can show graceful "feature unavailable"

2. **What's the contract for "must have" vs "nice to have" infrastructure?**
   - GCS = must have (no file storage without it)
   - OpenAI = nice to have? Or required for AI features?

3. **How should we handle partial infrastructure availability?**
   - Some parsers installed but not others
   - Some agents working but not all
