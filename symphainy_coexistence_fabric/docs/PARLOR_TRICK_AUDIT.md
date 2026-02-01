# Parlor Trick Audit: What's Real vs Ceremony

**Status:** Living Document (January 2026)
**Purpose:** Identify what Team B built that is REAL vs what is CEREMONY/PLACEHOLDER
**Audience:** Team A (Infrastructure), Team B (Capabilities)

---

## Classification Criteria

### 🟢 REAL - Has actual implementation logic
- Contains algorithms, validation, data processing
- Would work if infrastructure was available
- Failures are meaningful (bad input, missing deps)

### 🟡 MIXED - Partial implementation
- Has some real logic but depends heavily on other components
- Has fallback behavior that returns static/template data
- Works partially without full infrastructure

### 🔴 PARLOR TRICK - Ceremony/Placeholder
- Mostly just calls another component
- Returns empty/template data on failure
- Has "note" fields like "requires AI agent"
- Would return useless data if infrastructure missing

---

## Capability Services Audit

### Content Capability (11 services)

| Service | Classification | Rationale |
|---------|---------------|-----------|
| `IngestFileService` | 🟢 REAL | 477 lines, validation, multi-type ingestion, artifact registration |
| `SaveMaterializationService` | 🟢 REAL | Boundary contract handling, state transitions |
| `ParseContentService` | 🟡 MIXED | Delegates to parsers, has file type routing logic |
| `CreateDeterministicEmbeddingsService` | 🟡 MIXED | Some logic, but depends on DeterministicEmbeddingService |
| `GetParsedFileService` | 🟡 MIXED | Delegation to library service |
| `RetrieveArtifactMetadataService` | 🟡 MIXED | Simple registry query |
| `ListArtifactsService` | 🟡 MIXED | Registry listing |
| `ArchiveFileService` | 🟢 REAL | State update logic, metadata handling |
| `DeleteFileService` | 🟢 REAL | State transitions, cleanup logic |
| `EchoService` | 🟢 REAL | Test service, intentionally simple |
| `ExtractEmbeddingsService` (legacy) | 🔴 PARLOR TRICK | Agent wrapper with empty fallback |

**Content Summary:** 4 REAL, 5 MIXED, 1 PARLOR TRICK, 1 test

---

### Security Capability (7 services)

| Service | Classification | Rationale |
|---------|---------------|-----------|
| `AuthenticateUserService` | 🟡 MIXED | Delegates to auth abstraction |
| `CreateUserAccountService` | 🟡 MIXED | Delegates to auth abstraction |
| `ValidateTokenService` | 🟡 MIXED | Delegates to auth abstraction |
| `CheckEmailAvailabilityService` | 🟡 MIXED | Delegates to auth abstraction |
| `CreateSessionService` | 🟡 MIXED | Session management via abstraction |
| `ValidateAuthorizationService` | 🟡 MIXED | Authorization check delegation |
| `TerminateSessionService` | 🟡 MIXED | Session cleanup delegation |

**Security Summary:** 0 REAL, 7 MIXED, 0 PARLOR TRICK

**Note:** All security services delegate to auth_abstraction which is Team A's responsibility

---

### Insights Capability (7 services)

| Service | Classification | Rationale |
|---------|---------------|-----------|
| `AssessDataQualityService` | 🟢 REAL | 359 lines, actual quality algorithms, confidence scoring |
| `InterpretDataSelfDiscoveryService` | 🔴 PARLOR TRICK | Agent wrapper, template fallback |
| `InterpretDataGuidedService` | 🔴 PARLOR TRICK | Agent wrapper, template fallback |
| `AnalyzeStructuredDataService` | 🔴 PARLOR TRICK | Agent wrapper, empty analysis fallback |
| `AnalyzeUnstructuredDataService` | 🔴 PARLOR TRICK | Agent wrapper, empty analysis fallback |
| `VisualizeLineageService` | 🟡 MIXED | Graph traversal + fallback |
| `MapRelationshipsService` | 🟡 MIXED | Graph operations + fallback |

**Insights Summary:** 1 REAL, 2 MIXED, 4 PARLOR TRICK

---

### Operations Capability (6 services)

| Service | Classification | Rationale |
|---------|---------------|-----------|
| `GenerateSOPService` | 🔴 PARLOR TRICK | Agent wrapper, returns template SOP with "note" |
| `GenerateSOPFromChatService` | 🔴 PARLOR TRICK | Agent wrapper |
| `SOPChatMessageService` | 🔴 PARLOR TRICK | Agent wrapper |
| `CreateWorkflowService` | 🔴 PARLOR TRICK | Agent wrapper, empty workflow fallback |
| `OptimizeProcessService` | 🔴 PARLOR TRICK | Agent wrapper |
| `AnalyzeCoexistenceService` | 🔴 PARLOR TRICK | Agent wrapper |

**Operations Summary:** 0 REAL, 0 MIXED, 6 PARLOR TRICK

---

### Outcomes Capability (6 services)

| Service | Classification | Rationale |
|---------|---------------|-----------|
| `SynthesizeOutcomeService` | 🔴 PARLOR TRICK | Agent wrapper |
| `GenerateRoadmapService` | 🔴 PARLOR TRICK | 61 lines, returns `{"phases": [], "note": "..."}` |
| `CreatePOCService` | 🔴 PARLOR TRICK | Agent wrapper |
| `CreateBlueprintService` | 🔴 PARLOR TRICK | Agent wrapper |
| `ExportArtifactService` | 🟡 MIXED | Has format handling logic |
| `CreateSolutionService` | 🟡 MIXED | Solution composition logic |

**Outcomes Summary:** 0 REAL, 2 MIXED, 4 PARLOR TRICK

---

### Control Tower Capability (9 services)

| Service | Classification | Rationale |
|---------|---------------|-----------|
| `GetPlatformStatisticsService` | 🟡 MIXED | Aggregates from state_surface |
| `GetSystemHealthService` | 🟡 MIXED | Health check aggregation |
| `GetRealmHealthService` | 🟡 MIXED | Realm health aggregation |
| `ListSolutionsService` | 🟢 REAL | Solution registry listing |
| `GetSolutionStatusService` | 🟡 MIXED | Solution status retrieval |
| `ValidateSolutionService` | 🟡 MIXED | Validation logic |
| `GetPatternsService` | 🟢 REAL | Returns actual pattern documentation |
| `GetCodeExamplesService` | 🟢 REAL | Returns actual code examples |
| `GetDocumentationService` | 🟢 REAL | Returns actual documentation |

**Control Tower Summary:** 4 REAL, 5 MIXED, 0 PARLOR TRICK

---

### Coexistence Capability (7 services)

| Service | Classification | Rationale |
|---------|---------------|-----------|
| `InitiateGuideAgentService` | 🟡 MIXED | Session creation + agent invocation + fallback |
| `ProcessGuideAgentMessageService` | 🔴 PARLOR TRICK | Agent wrapper |
| `IntroducePlatformService` | 🟢 REAL | Static but intentional introduction |
| `ShowSolutionCatalogService` | 🟢 REAL | Solution catalog presentation |
| `NavigateToSolutionService` | 🟡 MIXED | Navigation routing |
| `RouteToLiaisonAgentService` | 🔴 PARLOR TRICK | Agent routing wrapper |
| `ListAvailableMCPToolsService` | 🟢 REAL | MCP tool enumeration |

**Coexistence Summary:** 3 REAL, 2 MIXED, 2 PARLOR TRICK

---

## Summary by Classification

| Classification | Count | Percentage |
|---------------|-------|------------|
| 🟢 REAL | 16 | 30% |
| 🟡 MIXED | 22 | 42% |
| 🔴 PARLOR TRICK | 15 | 28% |

**Total Services:** 53 (including legacy)

---

## Key Findings

### What Team B Built That Is REAL

1. **Content ingestion pipeline** - IngestFileService, Archive, Delete
2. **Data quality assessment** - AssessDataQualityService with algorithms
3. **Control Tower infrastructure** - Stats, health, documentation services
4. **Platform navigation** - Solution catalog, MCP tools

### What Is Ceremony/Placeholder

1. **All agent-dependent services** in Operations, Outcomes
2. **AI-enhanced Insights services** (interpretation, analysis)
3. **SOP generation** - returns templates
4. **Roadmap generation** - returns empty structures

### The Pattern

Most parlor tricks follow this pattern:

```python
async def execute(self, ctx):
    if ctx.reasoning and ctx.reasoning.agents:
        try:
            result = await ctx.reasoning.agents.invoke("some_agent", ...)
            if result.get("status") == "completed":
                return result
        except Exception as e:
            self.logger.warning(f"Agent failed: {e}")
    
    # PARLOR TRICK: Return empty/template data
    return {"placeholder": True, "note": "Requires AI agent"}
```

---

## What Team B Can Fix

### Immediate Actions (No Team A dependency)

1. **Add `intent_type` class attributes** to all 47 services missing them
2. **Standardize agent `__init__` signatures** (13 agents need fixing)
3. **Add `process/execute/run` methods** to 7 agents missing them
4. **Remove misleading "uses_real_llm": True** from fallback paths

### Document Honestly

Change comments like:
```python
# Uses REAL AI via ctx.reasoning
```

To:
```python
# Attempts AI via ctx.reasoning, falls back to template if unavailable
```

---

## What Team A Needs to Implement

See: `INFRASTRUCTURE_GAP_ANALYSIS.md` (companion document)
