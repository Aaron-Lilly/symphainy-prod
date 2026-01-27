-- ============================================================================
-- Project Files → Artifact-Centric Migration
-- ============================================================================
-- Purpose: Evolve project_files table to artifact-centric schema
--          Keep table name for backward compatibility (hardcoded in codebase)
--          Add artifact registry fields while maintaining file-specific fields
-- Date: January 26, 2026
-- Status: Phase 2b - In-Place Schema Evolution
-- ============================================================================

-- ============================================================================
-- Strategy: Add artifact-centric columns to existing project_files table
-- ============================================================================
-- We keep project_files as the table name (hardcoded in SupabaseFileAdapter)
-- But evolve it to support artifact-centric operations
-- ============================================================================

-- ============================================================================
-- 1. Add artifact-centric columns (if not exist)
-- ============================================================================

-- Lifecycle state (artifact-centric)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'project_files' 
        AND column_name = 'artifact_lifecycle_state'
    ) THEN
        ALTER TABLE public.project_files 
        ADD COLUMN artifact_lifecycle_state TEXT DEFAULT 'PENDING'
        CONSTRAINT project_files_artifact_lifecycle_state_check 
        CHECK (artifact_lifecycle_state IN ('PENDING', 'READY', 'FAILED', 'ARCHIVED', 'DELETED'));
    END IF;
END $$;

-- Semantic descriptor (what it means - independent of storage)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'project_files' 
        AND column_name = 'semantic_descriptor'
    ) THEN
        ALTER TABLE public.project_files 
        ADD COLUMN semantic_descriptor JSONB DEFAULT '{}';
    END IF;
END $$;

-- Produced by (provenance)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'project_files' 
        AND column_name = 'produced_by'
    ) THEN
        ALTER TABLE public.project_files 
        ADD COLUMN produced_by JSONB;
    END IF;
END $$;

-- Parent artifacts (lineage - array)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'project_files' 
        AND column_name = 'parent_artifacts'
    ) THEN
        ALTER TABLE public.project_files 
        ADD COLUMN parent_artifacts JSONB DEFAULT '[]';
    END IF;
END $$;

-- ============================================================================
-- 2. Ensure artifact_type is NOT NULL for artifact-centric records
-- ============================================================================

-- Make artifact_type required for new records (existing can be nullable during migration)
-- We'll set defaults for existing records
DO $$
BEGIN
    -- Set default artifact_type for existing records that don't have it
    UPDATE public.project_files 
    SET artifact_type = 'file' 
    WHERE artifact_type IS NULL;
    
    -- For now, keep it nullable to avoid breaking existing code
    -- We'll enforce NOT NULL in a later migration after all code is updated
END $$;

-- ============================================================================
-- 3. Create indexes for artifact-centric queries
-- ============================================================================

-- Primary query pattern: tenant + artifact_type + lifecycle (for UI dropdowns)
CREATE INDEX IF NOT EXISTS idx_project_files_tenant_artifact_lifecycle 
    ON public.project_files (tenant_id, artifact_type, artifact_lifecycle_state)
    WHERE artifact_lifecycle_state IN ('READY', 'ARCHIVED') 
    AND artifact_type IS NOT NULL;

-- Tenant + artifact_type queries
CREATE INDEX IF NOT EXISTS idx_project_files_tenant_artifact_type 
    ON public.project_files (tenant_id, artifact_type)
    WHERE artifact_type IS NOT NULL;

-- Lifecycle state queries
CREATE INDEX IF NOT EXISTS idx_project_files_artifact_lifecycle_state 
    ON public.project_files (artifact_lifecycle_state)
    WHERE artifact_lifecycle_state IS NOT NULL;

-- Lineage queries (parent_artifacts is JSONB array)
CREATE INDEX IF NOT EXISTS idx_project_files_parent_artifacts 
    ON public.project_files USING GIN (parent_artifacts)
    WHERE parent_artifacts IS NOT NULL AND jsonb_array_length(parent_artifacts) > 0;

-- Semantic descriptor queries
CREATE INDEX IF NOT EXISTS idx_project_files_semantic_descriptor 
    ON public.project_files USING GIN (semantic_descriptor)
    WHERE semantic_descriptor IS NOT NULL;

-- Produced by queries
CREATE INDEX IF NOT EXISTS idx_project_files_produced_by 
    ON public.project_files USING GIN (produced_by)
    WHERE produced_by IS NOT NULL;

-- ============================================================================
-- 4. Migrate existing data to artifact-centric fields
-- ============================================================================

-- Set artifact_lifecycle_state based on existing status
UPDATE public.project_files
SET artifact_lifecycle_state = CASE
    WHEN status = 'uploaded' AND processing_status = 'pending' THEN 'PENDING'
    WHEN status = 'uploaded' AND processing_status = 'complete' THEN 'READY'
    WHEN status = 'uploaded' AND processing_status = 'failed' THEN 'FAILED'
    WHEN archived_at IS NOT NULL THEN 'ARCHIVED'
    WHEN deleted = true THEN 'DELETED'
    ELSE 'READY'
END
WHERE artifact_lifecycle_state IS NULL OR artifact_lifecycle_state = 'PENDING';

-- Set semantic_descriptor from existing metadata
UPDATE public.project_files
SET semantic_descriptor = jsonb_build_object(
    'schema', 'file_v1',
    'file_type', file_type,
    'mime_type', mime_type,
    'parser_type', NULL,
    'embedding_model', NULL
)
WHERE semantic_descriptor IS NULL OR semantic_descriptor = '{}';

-- Set produced_by from existing metadata (if available)
-- For existing records, we may not have execution_id, so leave NULL
-- New records will have this populated

-- ============================================================================
-- 5. Add comments for documentation
-- ============================================================================

COMMENT ON COLUMN public.project_files.artifact_lifecycle_state IS 
    'Artifact lifecycle state: PENDING, READY, FAILED, ARCHIVED, DELETED (artifact-centric)';

COMMENT ON COLUMN public.project_files.semantic_descriptor IS 
    'What the artifact means (schema, record_count, parser_type, embedding_model) - independent of storage';

COMMENT ON COLUMN public.project_files.produced_by IS 
    'Provenance: which intent execution produced this artifact (intent, execution_id)';

COMMENT ON COLUMN public.project_files.parent_artifacts IS 
    'Lineage: array of parent artifact IDs';

COMMENT ON COLUMN public.project_files.artifact_type IS 
    'Type of artifact: file, parsed_content, embeddings, etc. (required for artifact-centric records)';

-- ============================================================================
-- 6. Migration Notes
-- ============================================================================
-- 
-- This migration:
-- 1. Adds artifact-centric columns to existing project_files table
-- 2. Keeps all existing columns for backward compatibility
-- 3. Migrates existing data to new artifact-centric fields
-- 4. Creates indexes for artifact-centric queries
-- 
-- After this migration:
-- - project_files serves as both file metadata AND artifact index
-- - Code can query using artifact-centric fields
-- - Existing file-specific queries continue to work
-- 
-- Next Steps:
-- 1. Update ContentOrchestrator to populate artifact-centric fields
-- 2. Update RegistryAbstraction to query project_files with artifact filters
-- 3. Gradually migrate queries from file-centric to artifact-centric
-- ============================================================================
