# Frontend Architecture Review & Gap Analysis

**Date:** January 2026  
**Status:** 📋 **COMPREHENSIVE REVIEW COMPLETE**  
**Purpose:** Identify gaps and required changes to support revised backend vision

---

## Executive Summary

The frontend has a solid foundation but needs significant updates to align with the revised backend architecture. Key gaps:

1. **Missing Deterministic Embeddings Step** - DataMash doesn't support the new deterministic embeddings workflow
2. **Target Model Upload Location** - Currently in Insights (wrong), should be in Content Pillar
3. **Source-to-Target Matching** - No UI for three-phase matching results
4. **Export Functionality** - Missing export section in Business Outcomes pillar
5. **API Manager Gaps** - Missing methods for new backend capabilities

---

## Part 1: Content Pillar Analysis

### Current State

**Page:** `app/(protected)/pillars/content/page.tsx`

**Components:**
- ✅ `FileUploader` - File upload
- ✅ `FileDashboard` - File management
- ✅ `FileParser` - File parsing
- ✅ `ParsePreview` - Parse preview
- ✅ `DataMash` - Semantic embeddings creation

**Flow:**
1. Upload file
2. Parse file
3. View parse preview
4. Create embeddings (via DataMash)

### Required Changes

#### 1.1: DataMash Component - Add Deterministic Embeddings Step ❌ MISSING

**File:** `app/(protected)/pillars/content/components/DataMash.tsx`

**Current Flow:**
```
Step 1: Select Parsed File
Step 2: Create Embeddings (semantic embeddings)
```

**Required Flow:**
```
Step 1: Select Parsed File
Step 1.5: Create Deterministic Embeddings (NEW)
  - Select parsed file (if not already selected)
  - Click "Create Deterministic Embeddings"
  - Show progress
  - Store deterministic_embedding_id
Step 2: Create Semantic Embeddings (UPDATED)
  - Requires deterministic_embedding_id
  - Select deterministic embedding (if multiple)
  - Pass deterministic_embedding_id to extract_embeddings intent
```

**Changes Needed:**
1. Add state for `deterministic_embedding_id`
2. Add new Card between Step 1 and Step 2 for deterministic embeddings
3. Add `createDeterministicEmbeddings()` method to ContentAPIManager
4. Update `handleCreateEmbeddings()` to require and use `deterministic_embedding_id`
5. Show validation error if deterministic embeddings not created
6. Display deterministic embedding results (schema fingerprint, pattern signature)

**Estimated Time:** 2-3 hours

---

#### 1.2: Add Target Model Upload as Content Type ❌ MISSING

**File:** `shared/types/file.ts` and `app/(protected)/pillars/content/components/FileUploader.tsx`

**Current State:** Target model upload doesn't exist in Content Pillar

**Current Content Pillar Structure:**
- Card 1: "File Upload & Dashboard" (contains FileUploader + FileDashboard)
- Card 2: "File Parsing" (FileParser component)
- Card 3: "Parse Preview" (ParsePreview component)
- Card 4: "Data Mash" (DataMash component)

**Note:** The FileUploader component has a multi-step flow with content types:
- Structured Data
- Unstructured Documents
- Hybrid Content
- Workflow & SOP Documentation (special: `processingPillar: "operations_pillar"`)

**Pattern to Follow:** Just like `WORKFLOW_SOP` is a content type with special handling, we should add `DATA_MODEL` as a 5th content type option that automatically sets `parsing_type="data_model"` when selected.

**Required:**
1. Add new Card section: "Target Data Model Upload" (as Card 1.5, between File Upload and File Parsing)
2. Create new component: `TargetModelUpload.tsx` (or extend FileUploader with special mode)
3. File upload with `parsing_type="data_model"` parameter
4. Display parsed JSON Schema after parsing
5. Mark file as "Data Model" type in file list
6. Filter files by `parsing_type="data_model"` for selection in Insights pillar

**Implementation Approach:**

**Recommended: Add as 5th Content Type (Following SOP/Workflow Pattern)**

Just like `ContentType.WORKFLOW_SOP` is a content type with special handling (`processingPillar: "operations_pillar"`), we should add `ContentType.DATA_MODEL` as a 5th content type option.

**Pattern:**
- `ContentType.STRUCTURED` - Regular structured data
- `ContentType.UNSTRUCTURED` - Regular unstructured documents  
- `ContentType.HYBRID` - Hybrid content
- `ContentType.WORKFLOW_SOP` - Special: processed in Operations pillar
- `ContentType.DATA_MODEL` - **NEW:** Special: uses `parsing_type="data_model"` for target schemas

**Benefits:**
- ✅ Follows existing pattern (SOP/Workflow already does this)
- ✅ Keeps UI consistent (all uploads go through same FileUploader flow)
- ✅ Users see "Data Model" as a clear option alongside other content types
- ✅ Backend receives `parsing_type="data_model"` automatically when this content type is selected

**Changes Needed:**
1. **Add `ContentType.DATA_MODEL` enum** to `shared/types/file.ts`
2. **Add FileTypeConfig for Data Model** in `FILE_TYPE_CONFIGS`:
   ```typescript
   {
     contentType: ContentType.DATA_MODEL,
     category: FileTypeCategory.DATA_MODEL, // New category
     label: "Data Model",
     extensions: [".json", ".yaml", ".yml"],
     mimeTypes: ["application/json", "application/yaml"],
     description: "Target data model schemas (JSON Schema, YAML)",
     icon: "📊"
   }
   ```
3. **Update FileUploader** to show "Data Model" as 5th content type option
4. **Update ContentAPIManager.uploadFile()** to set `parsing_type="data_model"` when `contentType === ContentType.DATA_MODEL`
5. **Update FileParser** to handle `parsing_type="data_model"` files (already supports it)
6. **Add visual indicator** for "Data Model" files in `FileDashboard` (badge/icon)
7. **Update InsightsFileSelector** to filter by `parsing_type="data_model"` OR `content_type === ContentType.DATA_MODEL` for target model selection

**Estimated Time:** 1-2 hours

---

## Part 2: Insights Pillar Analysis

### Current State

**Page:** `app/(protected)/pillars/insights/page.tsx`

**Tabs:**
1. ✅ Data Quality - Quality assessment
2. ✅ Data Interpretation - Self-discovery and guided discovery
3. ✅ Your Data Mash - Lineage visualization
4. ✅ Business Analysis - Structured/unstructured analysis

**Components:**
- ✅ `DataQualitySection` - Quality assessment
- ✅ `DataInterpretationSection` - Interpretation
- ✅ `DataMappingSection` - Data mapping (exists but needs updates)
- ✅ `InsightsFileSelector` - File selection

### Required Changes

#### 2.1: Update Target Model Selection ❌ WRONG LOCATION

**File:** `app/(protected)/pillars/insights/components/DataInterpretationSection.tsx`

**Current State:**
- Uses `InsightsFileSelector` for guide selection
- Guide selection is placeholder (hardcoded guides)

**Required Changes:**
1. **Remove upload functionality** (if exists)
2. **Add file selector** showing only `parsing_type="data_model"` files
3. **Filter parsed files** to show only data model files
4. **Update guide selection** to use parsed data model files from Content Pillar

**Changes Needed:**
1. Update `InsightsFileSelector` to filter by `parsing_type="data_model"`
2. Update `DataInterpretationSection` to load data model files from Content realm state
3. Remove any upload UI from Insights pillar
4. Update guide selection to show parsed data models

**Estimated Time:** 2-3 hours

---

#### 2.2: Add Source-to-Target Matching UI ❌ MISSING

**File:** `app/(protected)/pillars/insights/components/DataMappingSection.tsx` (needs enhancement)

**Current State:**
- Has basic mapping UI
- Uses `InsightsFileSelector` for source/target
- Shows mapping results via `MappingResultsDisplay`

**Required Changes:**
1. **Add three-phase matching visualization**
   - Phase 1: Schema alignment results
   - Phase 2: Semantic matching results
   - Phase 3: Pattern validation results
2. **Add confidence scores display**
   - Overall confidence
   - Per-phase confidence
   - Per-mapping confidence
3. **Add mapping table** with:
   - Source column → Target column
   - Match type (exact, semantic, similarity)
   - Confidence score
   - Validation status
4. **Add gaps display**
   - Unmapped source fields
   - Unmapped target fields
   - Warnings/errors from pattern validation

**Changes Needed:**
1. Update `DataMappingSection` to call `match_source_to_target` intent
2. Create new component: `ThreePhaseMatchingDisplay.tsx`
3. Create new component: `MappingTable.tsx` (enhanced)
4. Update `MappingResultsDisplay` to show three-phase results
5. Add `matchSourceToTarget()` method to InsightsAPIManager

**Estimated Time:** 4-5 hours

---

#### 2.3: Enhance Data Quality Section ✅ MOSTLY COMPLETE

**File:** `app/(protected)/pillars/insights/components/DataQualitySection.tsx`

**Current State:**
- Has quality assessment UI
- Shows quality scores
- Shows issues

**Required Changes:**
1. **Add deterministic embedding confidence** to quality scores
2. **Display schema fingerprint match quality**
3. **Display pattern signature match quality**

**Changes Needed:**
1. Update quality report display to show embedding confidence
2. Add schema fingerprint visualization
3. Add pattern signature visualization

**Estimated Time:** 1-2 hours

---

## Part 3: Business Outcomes Pillar Analysis

### Current State

**Page:** `app/(protected)/pillars/business-outcomes/page.tsx`

**Tabs:**
1. ✅ Journey Recap
2. ✅ Data
3. ✅ Insights
4. ✅ Operations

**Sections:**
- ✅ Strategic Roadmap
- ✅ POC Proposal
- ❌ **Export Section - MISSING**

### Required Changes

#### 3.1: Add Export Section ❌ MISSING

**File:** `app/(protected)/pillars/business-outcomes/page.tsx` (new section)

**Required:**
1. **Add Export Tab** or section after POC Proposal
2. **Solution selector** - Show available solutions
3. **Format selector** - JSON, YAML, SQL, CSV
4. **Export options:**
   - Include mappings (default: true)
   - Include rules (default: true)
   - Include staged data (default: false)
5. **Export preview** - Show mapping table, rules summary
6. **Download button** - Download export file

**Changes Needed:**
1. Create new component: `ExportSection.tsx`
2. Add `exportToMigrationEngine()` method to OutcomesAPIManager
3. Add export tab/section to Business Outcomes page
4. Create export preview component
5. Handle download from artifact URL

**Estimated Time:** 4-6 hours

---

## Part 4: API Manager Gaps

### ContentAPIManager ❌ MISSING METHODS

**File:** `shared/managers/ContentAPIManager.ts`

**Missing Methods:**
1. `createDeterministicEmbeddings(parsed_file_id: string): Promise<DeterministicEmbeddingResponse>`
   - Calls `create_deterministic_embeddings` intent
   - Returns `deterministic_embedding_id`, `schema_fingerprint`, `pattern_signature`

**Required Changes:**
```typescript
async createDeterministicEmbeddings(
  parsedFileId: string
): Promise<DeterministicEmbeddingResponse> {
  // Submit create_deterministic_embeddings intent
  // Wait for execution
  // Return deterministic_embedding_id
}
```

**Estimated Time:** 1 hour

---

### InsightsAPIManager ❌ MISSING METHODS

**File:** `shared/managers/InsightsAPIManager.ts`

**Missing Methods:**
1. `matchSourceToTarget(
     sourceDeterministicEmbeddingId: string,
     targetDeterministicEmbeddingId: string,
     sourceParsedFileId: string,
     targetParsedFileId: string
   ): Promise<SourceToTargetMatchingResponse>`
   - Calls `match_source_to_target` intent (via GuidedDiscoveryService)
   - Returns three-phase matching results

**Required Changes:**
```typescript
async matchSourceToTarget(
  sourceDeterministicEmbeddingId: string,
  targetDeterministicEmbeddingId: string,
  sourceParsedFileId: string,
  targetParsedFileId: string
): Promise<SourceToTargetMatchingResponse> {
  // Submit match_source_to_target intent
  // Wait for execution
  // Return comprehensive mapping results
}
```

**Estimated Time:** 1 hour

---

### OutcomesAPIManager ❌ MISSING METHODS

**File:** `shared/managers/OutcomesAPIManager.ts`

**Missing Methods:**
1. `exportToMigrationEngine(
     solutionId: string,
     exportFormat: 'json' | 'yaml' | 'sql' | 'csv',
     options?: ExportOptions
   ): Promise<ExportResponse>`
   - Calls `export_to_migration_engine` intent
   - Returns export artifact URL

**Required Changes:**
```typescript
async exportToMigrationEngine(
  solutionId: string,
  exportFormat: 'json' | 'yaml' | 'sql' | 'csv',
  options?: {
    includeMappings?: boolean;
    includeRules?: boolean;
    includeStagedData?: boolean;
  }
): Promise<ExportResponse> {
  // Submit export_to_migration_engine intent
  // Wait for execution
  // Return download URL
}
```

**Estimated Time:** 1 hour

---

## Part 5: Component Gaps

### Missing Components

1. **`DeterministicEmbeddingsCard.tsx`** ❌ MISSING
   - Location: `app/(protected)/pillars/content/components/`
   - Purpose: Create and display deterministic embeddings
   - Props: `parsedFileId`, `onComplete(deterministicEmbeddingId)`

2. **`ThreePhaseMatchingDisplay.tsx`** ❌ MISSING
   - Location: `app/(protected)/pillars/insights/components/`
   - Purpose: Visualize three-phase matching results
   - Props: `matchingResults` (from match_source_to_target)

3. **`MappingTable.tsx`** ❌ MISSING (or needs enhancement)
   - Location: `app/(protected)/pillars/insights/components/`
   - Purpose: Display mapping table with confidence scores
   - Props: `mappings`, `confidenceScores`, `warnings`, `errors`

4. **`ExportSection.tsx`** ❌ MISSING
   - Location: `app/(protected)/pillars/business-outcomes/components/`
   - Purpose: Export solution to migration engine
   - Props: `solutionId`

5. **`TargetModelUpload.tsx`** ❌ MISSING
   - Location: `app/(protected)/pillars/content/components/`
   - Purpose: Upload target data model with `parsing_type="data_model"`
   - Props: `onUploadComplete(fileId)`

---

## Part 6: Type Definitions

### Missing Types

**File:** `shared/types/` (various files)

**Missing:**
1. `DeterministicEmbeddingResponse` - Response from create_deterministic_embeddings
2. `SourceToTargetMatchingResponse` - Response from match_source_to_target
3. `ExportResponse` - Response from export_to_migration_engine
4. `ThreePhaseMatchingResults` - Structure for three-phase matching display

---

## Part 7: State Management

### Current State

**File:** `shared/state/PlatformStateProvider.tsx`

**Realm States:**
- ✅ `content.files` - Files
- ✅ `content.parsedFiles` - Parsed files
- ✅ `insights.*` - Insights data
- ❌ **Missing:** `content.deterministicEmbeddings` - Deterministic embeddings
- ❌ **Missing:** `insights.mappings` - Source-to-target mappings
- ❌ **Missing:** `outcomes.exports` - Export artifacts

**Required Changes:**
1. Add `deterministicEmbeddings` to content realm state
2. Add `mappings` to insights realm state
3. Add `exports` to outcomes realm state

---

## Part 8: Summary of Required Changes

### High Priority (Blocks Demo)

1. **DataMash - Deterministic Embeddings Step** (2-3h)
   - Add Step 1.5 to DataMash
   - Update Step 2 to require deterministic_embedding_id
   - Add ContentAPIManager method

2. **Target Model Upload in Content Pillar** (1-2h)
   - Add upload section
   - Support `parsing_type="data_model"`
   - Display parsed JSON Schema

3. **Source-to-Target Matching UI** (4-5h)
   - Create ThreePhaseMatchingDisplay component
   - Update DataMappingSection
   - Add InsightsAPIManager method

4. **Export Section in Business Outcomes** (4-6h)
   - Create ExportSection component
   - Add OutcomesAPIManager method
   - Add export tab/section

### Medium Priority (Enhancements)

5. **Data Quality Enhancement** (1-2h)
   - Add deterministic embedding confidence
   - Add schema fingerprint visualization

6. **Target Model Selection in Insights** (2-3h)
   - Filter to data model files only
   - Remove upload functionality

### Total Estimated Time: **14-21 hours**

---

## Part 9: Architecture Alignment

### ✅ What's Already Aligned

1. **Intent-based flow** - Frontend uses Experience Plane Client and intent submission
2. **Realm state management** - PlatformStateProvider tracks realm states
3. **Component structure** - Well-organized by pillar
4. **API managers** - Clean separation of concerns

### ❌ What Needs Alignment

1. **Deterministic embeddings workflow** - Missing step in DataMash
2. **Target model location** - Should be in Content, not Insights
3. **Three-phase matching** - No UI for comprehensive matching results
4. **Export functionality** - Missing entirely
5. **State management** - Missing deterministic embeddings and mappings state

---

## Part 10: Implementation Priority

### Phase 1: Critical Path (8-12 hours)
1. ✅ Add deterministic embeddings step to DataMash
2. ✅ Add target model upload to Content Pillar
3. ✅ Update semantic embeddings to require deterministic_embedding_id

### Phase 2: Matching & Export (8-12 hours)
4. ✅ Add source-to-target matching UI
5. ✅ Add export section to Business Outcomes

### Phase 3: Enhancements (3-5 hours)
6. ✅ Enhance data quality display
7. ✅ Update target model selection in Insights

---

## Part 11: Detailed Component Specifications

### DeterministicEmbeddingsCard Component

**File:** `app/(protected)/pillars/content/components/DeterministicEmbeddingsCard.tsx`

**Props:**
```typescript
interface DeterministicEmbeddingsCardProps {
  parsedFileId: string;
  onComplete: (result: {
    deterministic_embedding_id: string;
    schema_fingerprint: any;
    pattern_signature: any;
  }) => void;
}
```

**Features:**
- Select parsed file (if not provided)
- "Create Deterministic Embeddings" button
- Progress indicator
- Display results (schema fingerprint, pattern signature)
- Store `deterministic_embedding_id` in state

---

### ThreePhaseMatchingDisplay Component

**File:** `app/(protected)/pillars/insights/components/ThreePhaseMatchingDisplay.tsx`

**Props:**
```typescript
interface ThreePhaseMatchingDisplayProps {
  matchingResults: {
    mapping_table: Array<{
      source_column: string;
      target_column: string;
      match_type: 'exact' | 'semantic' | 'similarity';
      confidence: number;
      pattern_validation_score?: number;
    }>;
    exact_matches: Array<any>;
    semantic_matches: Array<any>;
    validated_mappings: Array<any>;
    unmapped_source: string[];
    unmapped_target: string[];
    warnings: Array<any>;
    errors: Array<any>;
    confidence_scores: {
      schema_confidence: number;
      semantic_confidence: number;
      pattern_validation_confidence: number;
    };
    overall_confidence: number;
  };
}
```

**Features:**
- Three tabs for each phase
- Overall confidence score
- Mapping table with sortable columns
- Gaps display (unmapped fields)
- Warnings/errors display

---

### ExportSection Component

**File:** `app/(protected)/pillars/business-outcomes/components/ExportSection.tsx`

**Props:**
```typescript
interface ExportSectionProps {
  solutionId?: string;
  onExportComplete?: (exportUrl: string) => void;
}
```

**Features:**
- Solution selector (dropdown)
- Format selector (JSON, YAML, SQL, CSV)
- Export options (checkboxes)
- Export preview (mapping table, rules summary)
- Download button

---

## Part 12: API Integration Points

### Content Realm

**New Intent:** `create_deterministic_embeddings`
- **Input:** `parsed_file_id`
- **Output:** `deterministic_embedding_id`, `schema_fingerprint`, `pattern_signature`
- **Frontend Call:** `ContentAPIManager.createDeterministicEmbeddings()`

**Updated Intent:** `extract_embeddings`
- **Input:** `deterministic_embedding_id` (REQUIRED, not `parsed_file_id`)
- **Output:** `embedding_id`, `embeddings_count`
- **Frontend Call:** `ContentAPIManager.extractEmbeddings()` (needs update)

---

### Insights Realm

**New Intent:** `match_source_to_target`
- **Input:** 
  - `source_deterministic_embedding_id`
  - `target_deterministic_embedding_id`
  - `source_parsed_file_id`
  - `target_parsed_file_id`
- **Output:** Comprehensive mapping results (three-phase)
- **Frontend Call:** `InsightsAPIManager.matchSourceToTarget()` (NEW)

**Updated Intent:** `interpret_data`
- **Input:** `guide_id` (target model parsed_file_id)
- **Output:** Interpretation results
- **Frontend Call:** `InsightsAPIManager.interpretDataGuided()` (exists, needs update)

---

### Outcomes Realm

**New Intent:** `export_to_migration_engine`
- **Input:**
  - `solution_id` (required)
  - `export_format` (required: "json", "yaml", "sql", "csv")
  - `include_mappings` (optional, default: true)
  - `include_rules` (optional, default: true)
  - `include_staged_data` (optional, default: false)
- **Output:** Export artifact (download URL)
- **Frontend Call:** `OutcomesAPIManager.exportToMigrationEngine()` (NEW)

---

## Part 13: File Structure Changes

### New Files to Create

1. `app/(protected)/pillars/content/components/DeterministicEmbeddingsCard.tsx`
2. `app/(protected)/pillars/content/components/TargetModelUpload.tsx`
3. `app/(protected)/pillars/insights/components/ThreePhaseMatchingDisplay.tsx`
4. `app/(protected)/pillars/insights/components/MappingTable.tsx` (or enhance existing)
5. `app/(protected)/pillars/business-outcomes/components/ExportSection.tsx`
6. `shared/types/deterministic-embeddings.ts`
7. `shared/types/matching.ts`
8. `shared/types/export.ts`

### Files to Modify

1. `app/(protected)/pillars/content/components/DataMash.tsx` - Add deterministic embeddings step
2. `app/(protected)/pillars/content/page.tsx` - Add target model upload section
3. `app/(protected)/pillars/insights/components/DataMappingSection.tsx` - Add three-phase matching
4. `app/(protected)/pillars/insights/components/DataInterpretationSection.tsx` - Update target model selection
5. `app/(protected)/pillars/business-outcomes/page.tsx` - Add export section
6. `shared/managers/ContentAPIManager.ts` - Add createDeterministicEmbeddings()
7. `shared/managers/InsightsAPIManager.ts` - Add matchSourceToTarget()
8. `shared/managers/OutcomesAPIManager.ts` - Add exportToMigrationEngine()
9. `shared/state/PlatformStateProvider.tsx` - Add deterministic embeddings and mappings state

---

## Part 14: User Flow Updates

### Content Pillar Flow (Updated)

```
1. Upload File
   ↓
2. Parse File
   ↓
3. View Parse Preview
   ↓
4. [NEW] Upload Target Data Model (optional, separate section)
   ↓
5. [NEW] Create Deterministic Embeddings (Step 1.5 in DataMash)
   ↓
6. Create Semantic Embeddings (Step 2 in DataMash, now requires deterministic_embedding_id)
   ↓
7. View Semantic Layer Preview
```

### Insights Pillar Flow (Updated)

```
1. Select Source File (from Content Pillar)
   ↓
2. Assess Data Quality
   ↓
3. [UPDATED] Select Target Model (from Content Pillar, filtering parsing_type="data_model")
   ↓
4. [NEW] Match Source to Target (three-phase matching)
   - Shows mapping table
   - Shows confidence scores
   - Shows gaps and warnings
   ↓
5. Interpret Data (self-discovery or guided)
   ↓
6. Business Analysis
```

### Business Outcomes Pillar Flow (Updated)

```
1. Review Journey Recap
   ↓
2. Review Data
   ↓
3. Review Insights
   ↓
4. Review Operations
   ↓
5. Generate Strategic Roadmap & POC
   ↓
6. [NEW] Export to Migration Engine
   - Select solution
   - Select format
   - Configure options
   - Preview export
   - Download
```

---

## Part 15: Testing Considerations

### Components to Test

1. **DeterministicEmbeddingsCard**
   - Test deterministic embeddings creation
   - Test error handling
   - Test state management

2. **ThreePhaseMatchingDisplay**
   - Test three-phase results display
   - Test confidence score visualization
   - Test gaps display

3. **ExportSection**
   - Test export generation
   - Test format selection
   - Test download functionality

### Integration Tests

1. **End-to-End Flow:**
   - Upload → Parse → Deterministic Embeddings → Semantic Embeddings
   - Upload Target Model → Match Source to Target
   - Create Solution → Export

2. **Error Handling:**
   - Missing deterministic embeddings
   - Missing target model
   - Export failures

---

## Part 16: Conclusion

### Current State: **70% Complete**

**What Works:**
- ✅ File upload and parsing
- ✅ Semantic embeddings creation
- ✅ Data quality assessment
- ✅ Data interpretation
- ✅ Business outcomes synthesis

**What's Missing:**
- ❌ Deterministic embeddings step
- ❌ Target model upload in Content
- ❌ Source-to-target matching UI
- ❌ Export functionality
- ❌ Three-phase matching visualization

### Required Effort: **14-21 hours**

**Priority Order:**
1. **Critical Path** (8-12h) - Deterministic embeddings, target model upload
2. **Matching & Export** (8-12h) - Source-to-target matching, export
3. **Enhancements** (3-5h) - Quality display, target model selection

### Architecture Alignment: **Good Foundation, Needs Updates**

The frontend architecture is sound and follows good patterns. The main work is:
- Adding missing workflow steps
- Creating new components for new capabilities
- Updating API managers for new backend methods
- Enhancing state management

---

## Next Steps

1. **Review this document** with frontend team
2. **Prioritize implementation** based on demo timeline
3. **Create detailed component specs** for each new component
4. **Update API managers** first (backend APIs are ready)
5. **Implement components** following existing patterns
6. **Test end-to-end flows** with real backend

---

**Status:** Ready for implementation planning
