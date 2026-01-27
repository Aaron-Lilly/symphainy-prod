# Content Realm Intent Analysis

**Date:** January 27, 2026  
**Status:** ✅ **ANALYSIS COMPLETE**

---

## Executive Summary

This document provides a cross-reference analysis of Content Realm intents across three perspectives:
1. **Journey Contracts** - What *should* happen (desired behavior)
2. **Backend Implementations** - What *actually* happens (current code)
3. **Frontend Expectations** - What the *UI needs* (client requirements)

### Key Findings

| Category | Count | Notes |
|----------|-------|-------|
| Intents in Journey Contracts | 9 | Across 4 journeys |
| Intents Actually Implemented | 27+ | Many more than contracts specify |
| Intents Used by Frontend | 10 | Via ContentAPIManager |
| **Gaps Identified** | 8 | See recommendations below |
| **Naming Conflicts** | 3 | Need resolution |

---

## 1. Journey Contract Inventory

### Journey 1: File Upload & Materialization ✅ (Contracts Exist)
| Intent | Status | Notes |
|--------|--------|-------|
| `ingest_file` | ✅ Contract exists | `intent_ingest_file.md` |
| `save_materialization` | ✅ Contract exists | `intent_save_materialization.md` |

### Journey 2: File Parsing
| Intent | Contract Status | Backend Status | Frontend Status |
|--------|-----------------|----------------|-----------------|
| `parse_content` | 📋 Needs contract | ✅ Implemented | ✅ Used |
| `save_parsed_content` | 📋 In contract | ❌ NOT implemented | ❌ Not used |

**⚠️ GAP:** Journey contract specifies `save_parsed_content` but backend doesn't have this - parsing auto-saves. **Recommendation:** Remove `save_parsed_content` from journey contract OR implement if explicit save is desired.

### Journey 3: Deterministic Embedding
| Intent | Contract Status | Backend Status | Frontend Status |
|--------|-----------------|----------------|-----------------|
| `create_deterministic_embeddings` | 📋 Needs contract | ✅ Implemented | ❌ Not directly used |
| `save_embeddings` | 📋 In contract | ❌ NOT implemented | ❌ Not used |

**⚠️ GAP:** Journey contract specifies `save_embeddings` but backend has `extract_embeddings`. Frontend uses `extract_embeddings`. **Recommendation:** Align contract to use `extract_embeddings` OR rename backend intent.

### Journey 4: File Management
| Intent | Contract Status | Backend Status | Frontend Status |
|--------|-----------------|----------------|-----------------|
| `list_artifacts` | 📋 Needs contract | ❌ Name mismatch | ⚠️ Direct API |
| `get_artifact_metadata` | 📋 Needs contract | ⚠️ Similar exists | ⚠️ Direct API |
| `archive_file` | 📋 Needs contract | ✅ Implemented | ❌ Not used |

**⚠️ NAMING CONFLICTS:**
- Contract: `list_artifacts` vs Backend: `list_files` - Frontend uses `list_files` intent
- Contract: `get_artifact_metadata` vs Backend: `retrieve_artifact_metadata` / `retrieve_file_metadata`

---

## 2. Backend Implementation Inventory

### All Implemented Intents (content_orchestrator.py)

| Intent Type | In Journey Contract? | Used by Frontend? | Category |
|-------------|---------------------|-------------------|----------|
| `ingest_file` | ✅ Yes | ✅ Yes | Ingestion |
| `bulk_ingest_files` | ❌ No | ❌ No | Bulk Ops |
| `bulk_parse_files` | ❌ No | ❌ No | Bulk Ops |
| `bulk_extract_embeddings` | ❌ No | ❌ No | Bulk Ops |
| `bulk_interpret_data` | ❌ No | ❌ No | Bulk Ops |
| `get_operation_status` | ❌ No | ❌ No | Status |
| `register_file` | ❌ No | ❌ No | Management |
| `retrieve_file_metadata` | ⚠️ Similar | ❌ No | Management |
| `retrieve_file` | ❌ No | ❌ No | Management |
| `list_files` | ⚠️ Similar | ✅ Yes | Management |
| `save_materialization` | ✅ Yes | ✅ Yes | Ingestion |
| `get_file_by_id` | ❌ No | ❌ No | Management |
| `archive_file` | ✅ Yes | ❌ No | Lifecycle |
| `purge_file` | ❌ No | ❌ No | Lifecycle |
| `restore_file` | ❌ No | ❌ No | Lifecycle |
| `validate_file` | ❌ No | ❌ No | Validation |
| `preprocess_file` | ❌ No | ❌ No | Processing |
| `search_files` | ❌ No | ❌ No | Query |
| `query_files` | ❌ No | ❌ No | Query |
| `update_file_metadata` | ❌ No | ❌ No | Management |
| `parse_content` | ✅ Yes | ✅ Yes | Parsing |
| `create_deterministic_embeddings` | ✅ Yes | ❌ No | Embeddings |
| `extract_embeddings` | ⚠️ Different name | ✅ Yes | Embeddings |
| `extract_deterministic_structure` | ❌ No | ❌ No | Embeddings |
| `hydrate_semantic_profile` | ❌ No | ❌ No | Semantic |
| `get_parsed_file` | ❌ No | ✅ Yes | Retrieval |
| `get_semantic_interpretation` | ❌ No | ✅ Yes | Semantic |

### Artifact Management Handlers (artifact_management_handlers.py)

| Intent Type | In Journey Contract? | Used by Frontend? | Category |
|-------------|---------------------|-------------------|----------|
| `register_artifact` | ❌ No | ❌ No | Management |
| `retrieve_artifact_metadata` | ⚠️ Similar | ❌ No | Management |
| `retrieve_artifact` | ❌ No | ❌ No | Management |
| `archive_artifact` | ⚠️ Similar | ❌ No | Lifecycle |
| `delete_artifact` | ❌ No | ❌ No | Lifecycle |

---

## 3. Frontend Expectations (ContentAPIManager.ts)

### Intent-Based Operations (via submitIntent)
| Method | Intent Used | Status |
|--------|-------------|--------|
| `uploadFile()` | `ingest_file` | ✅ Aligned |
| `saveMaterialization()` | `save_materialization` | ✅ Aligned |
| `listFiles()` | `list_files` | ⚠️ Name differs from contract |
| `parseFile()` | `parse_content` | ✅ Aligned |
| `extractEmbeddings()` | `extract_embeddings` | ⚠️ Name differs from contract |
| `getParsedFile()` | `get_parsed_file` | 📋 Not in contract |
| `getSemanticInterpretation()` | `get_semantic_interpretation` | 📋 Not in contract |

### Direct API Operations (not intent-based)
| Method | API Endpoint | Notes |
|--------|--------------|-------|
| `resolveArtifact()` | `/api/artifact/resolve` | State Surface resolution |
| `listArtifacts()` | `/api/artifact/list` | Artifact discovery |
| `getPendingIntents()` | `/api/intent/pending/list` | Pending intent discovery |
| `createPendingIntent()` | `/api/intent/pending/create` | Resumable workflows |

---

## 4. Recommendations

### Naming Alignment Needed

| Journey Contract Says | Backend Has | Frontend Uses | **Recommendation** |
|----------------------|-------------|---------------|-------------------|
| `list_artifacts` | `list_files` | `list_files` | **Keep `list_files`** - more specific for Content Realm |
| `get_artifact_metadata` | `retrieve_artifact_metadata` | Direct API | **Use `retrieve_artifact_metadata`** for consistency |
| `save_embeddings` | `extract_embeddings` | `extract_embeddings` | **Use `extract_embeddings`** - describes action better |
| `save_parsed_content` | (not implemented) | (not used) | **Remove from contract** - parsing auto-saves |

### Journey Contract Updates Recommended

#### File Parsing Journey
**Current:** `parse_content`, `save_parsed_content`
**Recommended:** `parse_content` only (parsing auto-saves, or add `get_parsed_file` for retrieval)

#### Deterministic Embedding Journey
**Current:** `create_deterministic_embeddings`, `save_embeddings`
**Recommended:** `create_deterministic_embeddings`, `extract_embeddings` (align with frontend)

#### File Management Journey
**Current:** `list_artifacts`, `get_artifact_metadata`, `archive_file`
**Recommended:** `list_files`, `retrieve_artifact_metadata`, `archive_file` (align with implementation)

### Intents to Add to Journey Contracts

These intents are implemented and used by frontend but not in any journey contract:

| Intent | Category | Recommendation |
|--------|----------|----------------|
| `get_parsed_file` | Retrieval | Add to File Parsing journey |
| `get_semantic_interpretation` | Semantic | Add to new Semantic journey OR Insights |
| `extract_embeddings` | Embeddings | Add to Deterministic Embedding journey |

### Intents to Document (Implemented but Not in Journey Flows)

These are implemented for specific use cases but not part of user journeys:

| Intent | Purpose | Keep/Remove |
|--------|---------|-------------|
| `bulk_ingest_files` | Batch operations | Keep - admin use |
| `bulk_parse_files` | Batch operations | Keep - admin use |
| `bulk_extract_embeddings` | Batch operations | Keep - admin use |
| `register_file` | Legacy file registration | Keep - migration use |
| `validate_file` | File validation | Keep - pre-processing |
| `preprocess_file` | File preprocessing | Keep - pipeline use |

---

## 5. Intent Contract Creation Plan

Based on this analysis, I will create intent contracts for:

### File Parsing Journey (2 intents)
1. **`parse_content`** - Parse file content
2. **`get_parsed_file`** - Retrieve parsed content (added based on frontend usage)

### Deterministic Embedding Journey (2 intents)
1. **`create_deterministic_embeddings`** - Create deterministic embeddings from parsed content
2. **`extract_embeddings`** - Extract embeddings (renamed from `save_embeddings` to match implementation)

### File Management Journey (3 intents)
1. **`list_files`** - List files (renamed from `list_artifacts` to match implementation)
2. **`retrieve_artifact_metadata`** - Get artifact metadata
3. **`archive_file`** - Archive file

### Additional Intents (not in journeys but important)
4. **`get_semantic_interpretation`** - Get semantic interpretation (used by frontend)

---

## 6. Summary of Decisions

| Decision | Rationale |
|----------|-----------|
| Use `list_files` not `list_artifacts` | Matches implementation and frontend |
| Use `extract_embeddings` not `save_embeddings` | Matches implementation and frontend |
| Remove `save_parsed_content` | Not implemented, parsing auto-saves |
| Add `get_parsed_file` to parsing journey | Used by frontend for retrieval |
| Add `get_semantic_interpretation` | Used by frontend |

---

**Last Updated:** January 27, 2026  
**Author:** Content Realm Analysis  
**Status:** ✅ **READY FOR CONTRACT CREATION**
