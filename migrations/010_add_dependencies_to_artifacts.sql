-- Migration: Add dependencies to artifacts table
-- Date: January 20, 2026
-- Purpose: Track artifact → artifact dependencies for impact analysis and lineage
-- Breaking Change: No - Adds new optional column

-- Add dependencies field to artifacts table
ALTER TABLE artifacts 
    ADD COLUMN IF NOT EXISTS source_artifact_ids JSONB DEFAULT '[]'::jsonb;

-- Add index for dependency queries (GIN index for JSONB array searches)
CREATE INDEX IF NOT EXISTS idx_artifacts_source_artifact_ids 
    ON artifacts USING GIN (source_artifact_ids);

-- Composite index for dependency queries by tenant
CREATE INDEX IF NOT EXISTS idx_artifacts_dependencies_tenant 
    ON artifacts(tenant_id, source_artifact_ids) 
    WHERE jsonb_array_length(source_artifact_ids) > 0;

-- Comments for documentation
COMMENT ON COLUMN artifacts.source_artifact_ids IS 'JSONB array of artifact IDs that this artifact depends on (for impact analysis and lineage)';
