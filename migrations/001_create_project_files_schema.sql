-- Migration: Create project_files table with clean schema
-- Date: January 2026
-- Purpose: Align Supabase schema with current platform architecture (Phases 1-4)
-- Breaking Change: Yes - This is a clean schema for new platform version

-- Drop old table if exists (breaking change - no legacy preservation)
DROP TABLE IF EXISTS project_files CASCADE;

-- Create project_files table
CREATE TABLE project_files (
    -- Primary Key
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity & Ownership
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    session_id UUID,  -- Optional: for session-scoped files
    
    -- File Information
    ui_name TEXT NOT NULL,  -- User-friendly filename (e.g., "permit_application.pdf")
    file_path TEXT NOT NULL,  -- GCS storage path (e.g., "tenant_id/session_id/file_id/filename")
    storage_location TEXT NOT NULL,  -- Full GCS path (alias for file_path, for clarity)
    
    -- File Metadata
    file_type TEXT NOT NULL DEFAULT 'unstructured',  -- structured, unstructured, hybrid
    content_type TEXT NOT NULL DEFAULT 'application/octet-stream',  -- MIME type
    file_size BIGINT NOT NULL,  -- Size in bytes
    file_hash TEXT,  -- SHA256 hash for deduplication
    
    -- Lifecycle & Status
    status TEXT NOT NULL DEFAULT 'active',  -- active, archived, purged
    ingestion_type TEXT,  -- upload, edi, api
    archived_at TIMESTAMPTZ,
    archive_reason TEXT,
    purged_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted BOOLEAN NOT NULL DEFAULT FALSE  -- Soft delete flag
);

-- Indexes for Performance
CREATE INDEX idx_project_files_tenant_id ON project_files(tenant_id);
CREATE INDEX idx_project_files_user_id ON project_files(user_id);
CREATE INDEX idx_project_files_session_id ON project_files(session_id);
CREATE INDEX idx_project_files_status ON project_files(status);
CREATE INDEX idx_project_files_deleted ON project_files(deleted);
CREATE INDEX idx_project_files_file_path ON project_files(file_path);
CREATE INDEX idx_project_files_created_at ON project_files(created_at DESC);

-- Composite index for common queries
CREATE INDEX idx_project_files_tenant_status ON project_files(tenant_id, status, deleted);

-- RLS Policies (Row Level Security)
ALTER TABLE project_files ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see files in their tenant
CREATE POLICY "Users can view files in their tenant"
    ON project_files FOR SELECT
    USING (tenant_id = auth.jwt() ->> 'tenant_id');

-- Policy: Users can insert files in their tenant
CREATE POLICY "Users can insert files in their tenant"
    ON project_files FOR INSERT
    WITH CHECK (tenant_id = auth.jwt() ->> 'tenant_id');

-- Policy: Users can update files in their tenant
CREATE POLICY "Users can update files in their tenant"
    ON project_files FOR UPDATE
    USING (tenant_id = auth.jwt() ->> 'tenant_id');

-- Policy: Users can delete files in their tenant (soft delete)
CREATE POLICY "Users can delete files in their tenant"
    ON project_files FOR DELETE
    USING (tenant_id = auth.jwt() ->> 'tenant_id');

-- Trigger: Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_project_files_updated_at
    BEFORE UPDATE ON project_files
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE project_files IS 'File metadata table for platform file management (Phases 1-4)';
COMMENT ON COLUMN project_files.uuid IS 'Primary key, file identifier (used as file_id in code)';
COMMENT ON COLUMN project_files.user_id IS 'User who uploaded/owns the file';
COMMENT ON COLUMN project_files.tenant_id IS 'Tenant for multi-tenancy isolation';
COMMENT ON COLUMN project_files.session_id IS 'Optional session identifier for session-scoped files';
COMMENT ON COLUMN project_files.ui_name IS 'User-friendly filename (what user sees in UI)';
COMMENT ON COLUMN project_files.file_path IS 'GCS storage path (e.g., tenant_id/session_id/file_id/filename)';
COMMENT ON COLUMN project_files.storage_location IS 'Full storage location (can be same as file_path)';
COMMENT ON COLUMN project_files.file_type IS 'Type: structured, unstructured, hybrid';
COMMENT ON COLUMN project_files.content_type IS 'MIME type (e.g., application/pdf, text/csv)';
COMMENT ON COLUMN project_files.file_size IS 'Size in bytes';
COMMENT ON COLUMN project_files.file_hash IS 'SHA256 hash for deduplication';
COMMENT ON COLUMN project_files.status IS 'Current status: active, archived, purged';
COMMENT ON COLUMN project_files.ingestion_type IS 'How file was ingested: upload, edi, api';
COMMENT ON COLUMN project_files.archived_at IS 'When file was archived (if archived)';
COMMENT ON COLUMN project_files.archive_reason IS 'Reason for archiving';
COMMENT ON COLUMN project_files.purged_at IS 'When file was purged (if purged)';
COMMENT ON COLUMN project_files.deleted IS 'Soft delete flag';
