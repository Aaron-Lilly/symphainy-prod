-- ============================================================================
-- Artifact Index Table Migration
-- ============================================================================
-- Purpose: Create artifact_index table for discovery/exploration (Supabase)
--          This is the discovery layer - State Surface (ArangoDB) is authoritative
-- Date: January 26, 2026
-- Status: Phase 2b - Supabase Artifact Index Implementation
-- ============================================================================

-- ============================================================================
-- 1. Create artifact_index table
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.artifact_index (
    -- Identity
    artifact_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    tenant_id UUID NOT NULL,
    
    -- Lifecycle
    lifecycle_state TEXT NOT NULL DEFAULT 'PENDING',
    
    -- Semantics (what it means - independent of storage)
    semantic_descriptor JSONB NOT NULL DEFAULT '{}',
    
    -- Provenance
    produced_by JSONB NOT NULL,
    parent_artifacts JSONB NOT NULL DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Lineage (structured metadata)
    lineage JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT artifact_index_pkey PRIMARY KEY (artifact_id),
    CONSTRAINT artifact_index_lifecycle_state_check CHECK (
        lifecycle_state IN ('PENDING', 'READY', 'FAILED', 'ARCHIVED', 'DELETED')
    ),
    CONSTRAINT artifact_index_artifact_type_check CHECK (
        artifact_type IN (
            'file', 
            'parsed_content', 
            'embeddings', 
            'summary', 
            'workflow', 
            'sop', 
            'solution',
            'deterministic_embeddings',
            'semantic_profile',
            'chunk'
        )
    )
) TABLESPACE pg_default;

-- ============================================================================
-- 2. Create indexes for discovery/exploration
-- ============================================================================

-- Primary query pattern: tenant + type + lifecycle (for UI dropdowns)
CREATE INDEX IF NOT EXISTS idx_artifact_index_tenant_type_state 
    ON public.artifact_index (tenant_id, artifact_type, lifecycle_state)
    WHERE lifecycle_state IN ('READY', 'ARCHIVED');

-- Tenant + type queries (all lifecycle states)
CREATE INDEX IF NOT EXISTS idx_artifact_index_tenant_type 
    ON public.artifact_index (tenant_id, artifact_type);

-- Lifecycle state queries
CREATE INDEX IF NOT EXISTS idx_artifact_index_lifecycle_state 
    ON public.artifact_index (lifecycle_state);

-- Lineage queries (parent_artifacts is JSONB array)
CREATE INDEX IF NOT EXISTS idx_artifact_index_parent_artifacts 
    ON public.artifact_index USING GIN (parent_artifacts);

-- Time-based queries (recent artifacts)
CREATE INDEX IF NOT EXISTS idx_artifact_index_created_at 
    ON public.artifact_index (created_at DESC);

-- Semantic descriptor queries (for filtering by schema, parser_type, etc.)
CREATE INDEX IF NOT EXISTS idx_artifact_index_semantic_descriptor 
    ON public.artifact_index USING GIN (semantic_descriptor);

-- Produced by queries (intent, execution_id)
CREATE INDEX IF NOT EXISTS idx_artifact_index_produced_by 
    ON public.artifact_index USING GIN (produced_by);

-- ============================================================================
-- 2a. Add lineage column if table already exists (for existing tables)
-- ============================================================================

-- Add lineage column if it doesn't exist (for tables created before this migration)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'artifact_index' 
        AND column_name = 'lineage'
    ) THEN
        ALTER TABLE public.artifact_index 
        ADD COLUMN lineage JSONB DEFAULT '{}';
    END IF;
END $$;

-- Lineage queries (structured derivation metadata)
-- Only create index if column exists (safe for re-runs)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'artifact_index' 
        AND column_name = 'lineage'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_artifact_index_lineage 
        ON public.artifact_index USING GIN (lineage)
        WHERE lineage IS NOT NULL AND lineage != '{}'::jsonb;
    END IF;
END $$;

-- ============================================================================
-- 3. Create update trigger function (if not exists)
-- ============================================================================

-- Create or replace function (simpler than checking existence)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 4. Create update trigger
-- ============================================================================

DROP TRIGGER IF EXISTS update_artifact_index_updated_at ON public.artifact_index;

CREATE TRIGGER update_artifact_index_updated_at
    BEFORE UPDATE ON public.artifact_index
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 5. Add comments for documentation
-- ============================================================================

COMMENT ON TABLE public.artifact_index IS 
    'Artifact index for discovery and exploration. State Surface (ArangoDB) is authoritative for resolution.';

COMMENT ON COLUMN public.artifact_index.artifact_id IS 
    'Stable, global artifact identifier';

COMMENT ON COLUMN public.artifact_index.artifact_type IS 
    'Type of artifact: file, parsed_content, embeddings, summary, workflow, sop, solution, etc.';

COMMENT ON COLUMN public.artifact_index.tenant_id IS 
    'Tenant identifier for multi-tenancy';

COMMENT ON COLUMN public.artifact_index.lifecycle_state IS 
    'Artifact lifecycle state: PENDING, READY, FAILED, ARCHIVED, DELETED';

COMMENT ON COLUMN public.artifact_index.semantic_descriptor IS 
    'What the artifact means (schema, record_count, parser_type, embedding_model) - independent of storage';

COMMENT ON COLUMN public.artifact_index.produced_by IS 
    'Provenance: which intent execution produced this artifact (intent, execution_id)';

COMMENT ON COLUMN public.artifact_index.parent_artifacts IS 
    'Lineage: array of parent artifact IDs (backward compatibility)';

COMMENT ON COLUMN public.artifact_index.lineage IS 
    'Structured lineage metadata: derived_from, derivation_intent, derivation_run_id, generation, root_artifact_id';

-- ============================================================================
-- Migration Complete
-- ============================================================================
