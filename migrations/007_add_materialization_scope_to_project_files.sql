-- Migration: Add materialization_scope to project_files
-- Date: January 2026
-- Purpose: Add materialization_scope JSONB column to project_files for workspace-scoped filtering
--          This enables efficient querying of files by user_id, session_id, solution_id
-- Breaking Change: No - Adds optional column

-- Add materialization_scope column to project_files
-- This stores workspace scope (user_id, session_id, solution_id) for efficient filtering
ALTER TABLE project_files 
    ADD COLUMN IF NOT EXISTS materialization_scope JSONB;

-- Create GIN index for efficient JSONB queries
CREATE INDEX IF NOT EXISTS idx_project_files_materialization_scope ON project_files USING GIN (materialization_scope);

-- Add comment
COMMENT ON COLUMN project_files.materialization_scope IS 'Workspace scope for materialization: {"user_id": "...", "session_id": "...", "solution_id": "...", "scope_type": "workspace"}. Used for filtering files by workspace.';
