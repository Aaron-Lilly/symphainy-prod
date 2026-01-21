-- Migration: Add versioning to artifacts table
-- Date: January 20, 2026
-- Purpose: Add versioning support for accepted artifacts (immutable past versions)
-- Breaking Change: No - Adds new optional columns

-- Add versioning fields to artifacts table
ALTER TABLE artifacts 
    ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1,
    ADD COLUMN IF NOT EXISTS parent_artifact_id TEXT,  -- Links to previous version
    ADD COLUMN IF NOT EXISTS is_current_version BOOLEAN DEFAULT TRUE;

-- Note: Foreign key constraint removed for MVP
-- The artifacts table primary key is just artifact_id (not composite with tenant_id)
-- For MVP, application logic will validate parent_artifact_id references
-- For production, consider adding unique constraint on (artifact_id, tenant_id) and re-adding FK
-- Or use application-level validation with tenant_id check

-- Add indexes for version queries
CREATE INDEX IF NOT EXISTS idx_artifacts_parent_artifact_id 
    ON artifacts(parent_artifact_id) 
    WHERE parent_artifact_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_artifacts_version 
    ON artifacts(version);

CREATE INDEX IF NOT EXISTS idx_artifacts_is_current_version 
    ON artifacts(is_current_version) 
    WHERE is_current_version = TRUE;

-- Composite index for version chain queries
CREATE INDEX IF NOT EXISTS idx_artifacts_version_chain 
    ON artifacts(parent_artifact_id, version, is_current_version);

-- Composite index for current version queries by tenant and type
CREATE INDEX IF NOT EXISTS idx_artifacts_current_version_tenant_type 
    ON artifacts(tenant_id, artifact_type, is_current_version) 
    WHERE is_current_version = TRUE;

-- Comments for documentation
COMMENT ON COLUMN artifacts.version IS 'Version number (starts at 1, increments for new versions)';
COMMENT ON COLUMN artifacts.parent_artifact_id IS 'Reference to previous version in version chain (NULL for original version)';
COMMENT ON COLUMN artifacts.is_current_version IS 'True if this is the current active version (only one per artifact chain should be TRUE)';
