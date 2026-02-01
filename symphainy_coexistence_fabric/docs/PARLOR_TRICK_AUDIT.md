# Service Analysis: E2E Verification & Anti-Pattern Audit

**Status:** Living Document (January 2026)
**Purpose:** Identify what works E2E, what has anti-patterns, and remediation paths
**Audience:** Team A (Infrastructure), Team B (Capabilities)

> **CRITICAL PRINCIPLE:** Infrastructure will ALWAYS be there. Fallbacks that fake answers are BUGS, not features.

---

## Classification Criteria (Updated)

### ✅ REAL - Works E2E, Fails Loudly
- Contains actual implementation logic
- Raises errors when infrastructure missing
- Properly propagates failures

### ⚠️ ANTI-PATTERN - Has Fallback Bug
- Returns fake/template data when infrastructure fails
- Silently succeeds when it should fail
- Has mock patterns that hide real failures

### 🚫 INFRASTRUCTURE BUG - Team A Issue
- Adapter has mock fallback pattern
- Library dependency not enforced
- Should fail loudly but doesn't

---

## Capability Services Audit (E2E Verified)

### Content Capability (11 services)

| Service | E2E Status | Fallback Pattern | Notes |
|---------|------------|------------------|-------|
| `IngestFileService` | ✅ WORKS | None - fails loudly | Proper RuntimeError if ctx.platform missing |
| `SaveMaterializationService` | ✅ WORKS | None - fails loudly | Boundary contract validation |
| `ParseContentService` | ✅ WORKS | None - fails loudly | Routes to real parsers |
| `CreateDeterministicEmbeddingsService` | ✅ WORKS | None - fails loudly | Validates ctx.platform |
| `GetParsedFileService` | ✅ WORKS | None | Delegates to library |
| `RetrieveArtifactMetadataService` | ✅ WORKS | None | Registry query |
| `ListArtifactsService` | ✅ WORKS | None | Registry listing |
| `ArchiveFileService` | ✅ WORKS | None - fails loudly | RuntimeError if state_surface missing |
| `DeleteFileService` | ✅ WORKS | Idempotent (OK) | Returns success if already deleted |
| `EchoService` | ✅ WORKS | None | Test service |
| `ExtractEmbeddingsService` (legacy) | ⚠️ ANTI-PATTERN | Returns empty on failure | Should fail loudly |

**Content Summary:** 10 WORK E2E, 1 ANTI-PATTERN (legacy)

---

### Security Capability (7 services)

| Service | E2E Status | Fallback Pattern | Notes |
|---------|------------|------------------|-------|
| `AuthenticateUserService` | ✅ WORKS | Returns error result | `{"success": False, "error": "..."}` |
| `CreateUserAccountService` | ✅ WORKS | Returns error result | Proper error handling |
| `ValidateTokenService` | ✅ WORKS | Returns error result | Proper error handling |
| `CheckEmailAvailabilityService` | ✅ WORKS | Returns error result | Proper error handling |
| `CreateSessionService` | ✅ WORKS | Returns error result | Proper error handling |
| `ValidateAuthorizationService` | ✅ WORKS | Returns error result | Proper error handling |
| `TerminateSessionService` | ✅ WORKS | Returns error result | Proper error handling |

**Security Summary:** 7 WORK E2E

**Note:** All services properly return `{"success": False, "error": "..."}` when auth_abstraction unavailable

---

### Insights Capability (7 services)

| Service | E2E Status | Fallback Pattern | Remediation |
|---------|------------|------------------|-------------|
| `AssessDataQualityService` | ✅ WORKS | None | Has real quality algorithms |
| `InterpretDataSelfDiscoveryService` | ⚠️ ANTI-PATTERN | Returns template | Change to fail/unavailable |
| `InterpretDataGuidedService` | ⚠️ ANTI-PATTERN | Returns template | Change to fail/unavailable |
| `AnalyzeStructuredDataService` | ⚠️ ANTI-PATTERN | Returns empty analysis | Change to fail/unavailable |
| `AnalyzeUnstructuredDataService` | ⚠️ ANTI-PATTERN | Returns empty analysis | Change to fail/unavailable |
| `VisualizeLineageService` | ✅ WORKS | None | Has graph traversal logic |
| `MapRelationshipsService` | ✅ WORKS | None | Has graph operations |

**Insights Summary:** 3 WORK E2E, 4 ANTI-PATTERNS

---

### Operations Capability (6 services)

| Service | E2E Status | Fallback Pattern | Remediation |
|---------|------------|------------------|-------------|
| `GenerateSOPService` | ⚠️ ANTI-PATTERN | Returns template SOP | Fail or return unavailable |
| `GenerateSOPFromChatService` | ⚠️ ANTI-PATTERN | Returns template | Fail or return unavailable |
| `SOPChatMessageService` | ⚠️ ANTI-PATTERN | Returns template | Fail or return unavailable |
| `CreateWorkflowService` | ⚠️ ANTI-PATTERN | Returns empty workflow | Fail or return unavailable |
| `OptimizeProcessService` | ⚠️ ANTI-PATTERN | Returns template | Fail or return unavailable |
| `AnalyzeCoexistenceService` | ⚠️ ANTI-PATTERN | Returns template | Fail or return unavailable |

**Operations Summary:** 0 WORK E2E, 6 ANTI-PATTERNS

**Why All Anti-Patterns:** All depend on agents. When agents unavailable, they return fake templates instead of failing.

---

### Outcomes Capability (6 services)

| Service | E2E Status | Fallback Pattern | Remediation |
|---------|------------|------------------|-------------|
| `SynthesizeOutcomeService` | ⚠️ ANTI-PATTERN | Returns template | Fail or return unavailable |
| `GenerateRoadmapService` | ⚠️ ANTI-PATTERN | Returns `{"phases": []}` | Fail or return unavailable |
| `CreatePOCService` | ⚠️ ANTI-PATTERN | Returns template | Fail or return unavailable |
| `CreateBlueprintService` | ⚠️ ANTI-PATTERN | Returns template | Fail or return unavailable |
| `ExportArtifactService` | ✅ WORKS | None | Has format handling logic |
| `CreateSolutionService` | ✅ WORKS | None | Solution composition logic |

**Outcomes Summary:** 2 WORK E2E, 4 ANTI-PATTERNS

---

### Control Tower Capability (9 services)

| Service | E2E Status | Fallback Pattern | Notes |
|---------|------------|------------------|-------|
| `GetPlatformStatisticsService` | ✅ WORKS | None | Aggregates from state_surface |
| `GetSystemHealthService` | ✅ WORKS | None | Health check aggregation |
| `GetRealmHealthService` | ✅ WORKS | None | Realm health aggregation |
| `ListSolutionsService` | ✅ WORKS | None | Solution registry listing |
| `GetSolutionStatusService` | ✅ WORKS | None | Solution status retrieval |
| `ValidateSolutionService` | ✅ WORKS | None | Validation logic |
| `GetPatternsService` | ✅ WORKS | None | Returns actual patterns |
| `GetCodeExamplesService` | ✅ WORKS | None | Returns actual examples |
| `GetDocumentationService` | ✅ WORKS | None | Returns actual docs |

**Control Tower Summary:** 9 WORK E2E, 0 ANTI-PATTERNS

---

### Coexistence Capability (7 services)

| Service | E2E Status | Fallback Pattern | Remediation |
|---------|------------|------------------|-------------|
| `InitiateGuideAgentService` | ⚠️ ANTI-PATTERN | Returns fake guidance | Remove fake guidance |
| `ProcessGuideAgentMessageService` | ⚠️ ANTI-PATTERN | Returns template | Fail or return unavailable |
| `IntroducePlatformService` | ✅ WORKS | None | Static introduction (intentional) |
| `ShowSolutionCatalogService` | ✅ WORKS | None | Solution catalog |
| `NavigateToSolutionService` | ✅ WORKS | None | Navigation routing |
| `RouteToLiaisonAgentService` | ⚠️ ANTI-PATTERN | Returns template | Fail or return unavailable |
| `ListAvailableMCPToolsService` | ✅ WORKS | None | MCP tool enumeration |

**Coexistence Summary:** 4 WORK E2E, 3 ANTI-PATTERNS

---

## Summary by E2E Status

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ WORKS E2E | 35 | 66% |
| ⚠️ ANTI-PATTERN | 18 | 34% |

**Total Services:** 53

---

## Key Findings

### What Works E2E (35 services)

1. **Entire Content Capability** (except legacy ExtractEmbeddingsService)
2. **Entire Security Capability** - proper error handling
3. **Entire Control Tower Capability** - no fallbacks needed
4. **Most of Insights** - real algorithms for data quality, lineage, relationships
5. **Parts of Outcomes/Coexistence** - non-agent services

### What Has Anti-Patterns (18 services)

All 18 anti-patterns follow the same broken pattern:
- Depend on agents
- Return fake/template data when agents fail
- Should instead fail loudly or return "unavailable" status

### The Anti-Pattern (BUG)

```python
# THIS IS A BUG, NOT A FEATURE
async def execute(self, ctx):
    if ctx.reasoning and ctx.reasoning.agents:
        try:
            result = await ctx.reasoning.agents.invoke("some_agent", ...)
            if result.get("status") == "completed":
                return result
        except Exception as e:
            self.logger.warning(f"Agent failed: {e}")
    
    # BUG: Returns fake data instead of failing
    return {"placeholder": True, "note": "Requires AI agent"}
```

### The Fix

```python
# CORRECT: Fail loudly or return unavailable status
async def execute(self, ctx):
    if not ctx.reasoning or not ctx.reasoning.agents:
        raise RuntimeError("Reasoning service not available")
    
    result = await ctx.reasoning.agents.invoke("some_agent", ...)
    if result.get("status") != "completed":
        raise RuntimeError(f"Agent failed: {result.get('error')}")
    
    return result
```

---

## What Team B Must Fix (18 Anti-Patterns)

### Priority 1: Remove Fake Fallbacks

All 18 services must be updated to either:
- **Fail loudly:** `raise RuntimeError("Agent not available")`
- **Return unavailable status:** `{"status": "unavailable", "reason": "..."}`

Services to fix:
1. `InitiateGuideAgentService` - Remove fake guidance
2. `ProcessGuideAgentMessageService` - Remove template response
3. `RouteToLiaisonAgentService` - Remove template routing
4. `InterpretDataSelfDiscoveryService` - Remove template interpretation
5. `InterpretDataGuidedService` - Remove template interpretation
6. `AnalyzeStructuredDataService` - Remove empty analysis
7. `AnalyzeUnstructuredDataService` - Remove empty analysis
8. `GenerateSOPService` - Remove template SOP
9. `GenerateSOPFromChatService` - Remove template
10. `SOPChatMessageService` - Remove template
11. `CreateWorkflowService` - Remove empty workflow
12. `OptimizeProcessService` - Remove template
13. `AnalyzeCoexistenceService` - Remove template
14. `SynthesizeOutcomeService` - Remove template
15. `GenerateRoadmapService` - Remove empty roadmap
16. `CreatePOCService` - Remove template
17. `CreateBlueprintService` - Remove template
18. `ExtractEmbeddingsService` (legacy) - Remove empty fallback

### Priority 2: Architecture Cleanup

1. **Add `intent_type` class attributes** to 47 services
2. **Standardize agent `__init__` signatures** (13 agents)
3. **Add `process/execute/run` methods** to 7 agents

---

## What Team A Must Fix (Infrastructure Bugs)

### Critical: GCS Adapter Mock Pattern

**Location:** `foundations/public_works/adapters/gcs_adapter.py` lines 18-73

**Problem:** Creates mock classes when google-cloud-storage not installed. Uploads appear to succeed but store nothing.

**Fix:** Fail at import time if library missing.

### Critical: OpenAI Adapter Mock Pattern

**Location:** `foundations/public_works/adapters/openai_adapter.py` lines 22-28

**Problem:** Creates mock when openai not installed.

**Fix:** Fail at import time if library missing.

---

## Related Documents

- `SERVICE_E2E_ANALYSIS.md` - Detailed E2E traces
- `INFRASTRUCTURE_GAP_ANALYSIS.md` - Team A infrastructure requirements
