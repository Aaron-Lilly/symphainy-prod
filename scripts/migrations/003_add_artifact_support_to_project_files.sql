-- Artifact Support Migration for project_files table
-- Date: January 18, 2026
-- Purpose: Enable artifact storage in project_files table
-- Breaking Change: No - Adds new optional column
-- 
-- This migration adds support for storing artifacts (workflows, SOPs, blueprints, etc.)
-- in the project_files table alongside regular files. Artifacts are distinguished
-- by the artifact_type column (NULL for regular files).

-- Add artifact_type column to project_files
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS artifact_type TEXT;
-- artifact_type: 'workflow', 'sop', 'blueprint', 'solution', 'roadmap', 'poc', 'hybrid_embeddings', NULL (for files)

-- Add index for artifact queries (filtered index - only indexes non-NULL values)
CREATE INDEX IF NOT EXISTS idx_project_files_artifact_type 
ON project_files(artifact_type) 
WHERE artifact_type IS NOT NULL;

-- Add composite index for artifact queries (tenant + type) for efficient tenant-scoped artifact queries
CREATE INDEX IF NOT EXISTS idx_project_files_artifact_tenant 
ON project_files(artifact_type, tenant_id) 
WHERE artifact_type IS NOT NULL;

-- Add comment to document the column
COMMENT ON COLUMN project_files.artifact_type IS 'Type of artifact (workflow, sop, blueprint, solution, roadmap, poc, hybrid_embeddings). NULL for regular files.';
