-- Migration: Add boundary contract support to materializations
-- Date: January 2026
-- Purpose: Transform project_files to materializations index with boundary contract references
--          This makes Supabase a "materialization index" not a "file metadata store"
-- Breaking Change: Yes - Adds required boundary_contract_id

-- Add boundary contract reference to project_files (which becomes materializations index)
ALTER TABLE project_files 
    ADD COLUMN IF NOT EXISTS boundary_contract_id UUID REFERENCES data_boundary_contracts(contract_id),
    ADD COLUMN IF NOT EXISTS representation_type TEXT,  -- 'reference', 'partial_extraction', 'deterministic', 'semantic_embedding', 'full_artifact'
    ADD COLUMN IF NOT EXISTS materialization_policy_basis TEXT,  -- Which policy authorized this materialization
    ADD COLUMN IF NOT EXISTS materialization_ttl INTERVAL,  -- TTL for this materialization
    ADD COLUMN IF NOT EXISTS materialization_expires_at TIMESTAMPTZ,  -- When this materialization expires
    ADD COLUMN IF NOT EXISTS materialization_backing_store TEXT,  -- Where materialized: 'gcs', 'supabase', 'memory', 'none'
    ADD COLUMN IF NOT EXISTS source_external BOOLEAN DEFAULT TRUE,  -- Whether source is external (not owned by platform)
    ADD COLUMN IF NOT EXISTS source_location TEXT,  -- External source location (if external)
    ADD COLUMN IF NOT EXISTS source_type TEXT;  -- External source type: 'file', 'api', 'database', etc.

-- Add constraints
ALTER TABLE project_files 
    ADD CONSTRAINT project_files_representation_type_check 
        CHECK (representation_type IS NULL OR representation_type IN (
            'reference', 'partial_extraction', 'deterministic', 'semantic_embedding', 'full_artifact'
        )),
    ADD CONSTRAINT project_files_materialization_backing_store_check 
        CHECK (materialization_backing_store IS NULL OR materialization_backing_store IN (
            'gcs', 'supabase', 'memory', 'none'
        ));

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_project_files_boundary_contract_id ON project_files(boundary_contract_id);
CREATE INDEX IF NOT EXISTS idx_project_files_representation_type ON project_files(representation_type);
CREATE INDEX IF NOT EXISTS idx_project_files_materialization_expires_at ON project_files(materialization_expires_at) WHERE materialization_expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_project_files_source_external ON project_files(source_external);

-- Update comments to reflect new semantics
COMMENT ON TABLE project_files IS 'Materializations Index - Tracks materialized representations, not source files. Source data stays external.';
COMMENT ON COLUMN project_files.boundary_contract_id IS 'Reference to Data Boundary Contract that authorized this materialization';
COMMENT ON COLUMN project_files.representation_type IS 'Type of materialized representation: reference, partial_extraction, deterministic, semantic_embedding, full_artifact';
COMMENT ON COLUMN project_files.materialization_policy_basis IS 'Policy rule that authorized this materialization';
COMMENT ON COLUMN project_files.materialization_ttl IS 'Time to live for this materialization';
COMMENT ON COLUMN project_files.materialization_expires_at IS 'When this materialization expires (for auto-purge)';
COMMENT ON COLUMN project_files.materialization_backing_store IS 'Where materialized data is stored: gcs, supabase, memory, none';
COMMENT ON COLUMN project_files.source_external IS 'Whether source data is external (not owned by platform)';
COMMENT ON COLUMN project_files.source_location IS 'External source location (if source_external = true)';
COMMENT ON COLUMN project_files.source_type IS 'External source type: file, api, database, etc.';

-- Migration note: Existing rows will have NULL boundary_contract_id
-- These should be migrated to have default boundary contracts created
-- See migration script for creating default contracts for existing data
