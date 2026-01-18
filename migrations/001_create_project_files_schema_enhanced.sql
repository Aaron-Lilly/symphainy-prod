-- Migration: Create project_files table with enhanced schema
-- Date: January 2026
-- Purpose: Align Supabase schema with current platform architecture (Phases 1-4)
--          Incorporates valuable fields from existing schema
-- Breaking Change: Yes - This is a clean schema for new platform version

-- Drop old table if exists (breaking change - no legacy preservation)
DROP TABLE IF EXISTS project_files CASCADE;

-- Also drop any old columns that might exist (in case table wasn't fully dropped)
-- This ensures no old session_id column or triggers remain
DO $$
BEGIN
    -- Drop session_id column if it exists (from old schema)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'project_files' AND column_name = 'session_id'
    ) THEN
        ALTER TABLE project_files DROP COLUMN session_id;
    END IF;
END $$;

-- Create project_files table with enhanced schema
CREATE TABLE project_files (
    -- Primary Key
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity & Ownership
    user_id UUID NOT NULL,  -- Changed from TEXT to UUID
    tenant_id UUID NOT NULL,  -- Changed from TEXT to UUID
    -- session_id REMOVED - Runtime concept, tracked in State Surface, not persistent metadata
    
    -- File Information
    ui_name TEXT NOT NULL,  -- User-friendly filename (e.g., "permit_application.pdf")
    file_path TEXT NOT NULL,  -- GCS storage path (renamed from original_path)
    parsed_path TEXT,  -- Path to parsed results (KEEP from current schema)
    
    -- File Metadata
    file_type TEXT NOT NULL DEFAULT 'unstructured',  -- structured, unstructured, hybrid (parsing pathway)
    mime_type TEXT,  -- MIME type (e.g., application/pdf, text/csv) - for rendering, storage
    file_size BIGINT,  -- Size in bytes
    file_hash TEXT,  -- SHA256 hash
    file_checksum TEXT,  -- Additional checksum (KEEP from current schema)
    
    -- Status & Processing
    status TEXT NOT NULL DEFAULT 'uploaded',  -- uploaded, active, archived, purged
    processing_status TEXT DEFAULT 'pending',  -- pending, processing, completed, failed (KEEP from current)
    processing_errors JSONB,  -- Error tracking (KEEP from current)
    
    -- Ingestion
    ingestion_type TEXT DEFAULT 'upload',  -- upload, edi, api (standard MVP pathway)
    
    -- Audit Trail
    created_by TEXT,  -- Who created (KEEP from current)
    updated_by TEXT,  -- Who updated (KEEP from current)
    client_ip INET,  -- IP address (KEEP from current)
    user_agent TEXT,  -- User agent (KEEP from current)
    
    -- Security & Compliance
    access_level TEXT DEFAULT 'open',  -- open, restricted, private (KEEP from current)
    permissions JSONB,  -- Fine-grained permissions (KEEP from current)
    data_classification TEXT DEFAULT 'public',  -- public, internal, confidential (KEEP from current)
    retention_policy TEXT,  -- Retention policy (KEEP from current)
    compliance_flags JSONB,  -- Compliance tracking (KEEP from current)
    
    -- Platform Context
    pillar_origin TEXT DEFAULT 'content_pillar',  -- Which realm/pillar (KEEP from current)
    service_context JSONB,  -- Service-specific context (KEEP from current)
    processing_pipeline JSONB,  -- Processing steps (KEEP from current)
    
    -- Data Lineage (root_file_uuid and parent_file_uuid are separate concepts)
    arango_content_id UUID,  -- Link to ArangoDB (KEEP from current)
    lineage_depth INTEGER DEFAULT 0,  -- Depth in lineage (KEEP from current)
    root_file_uuid UUID,  -- Original file in lineage tree (KEEP from current)
    parent_file_uuid UUID,  -- Immediate parent file in lineage (KEEP from current)
    generation INTEGER DEFAULT 0,  -- Generation number (KEEP from current)
    lineage_path TEXT,  -- Lineage path (KEEP from current)
    
    -- Versioning & Insights
    version INTEGER DEFAULT 1,  -- File version (KEEP from current)
    insights JSONB,  -- Insights/metadata (KEEP from current)
    
    -- Lifecycle Tracking
    archived_at TIMESTAMPTZ,
    archive_reason TEXT,
    purged_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted BOOLEAN NOT NULL DEFAULT FALSE  -- Soft delete flag
);

-- Constraints
ALTER TABLE project_files ADD CONSTRAINT project_files_file_type_check 
    CHECK (file_type IN ('structured', 'unstructured', 'hybrid'));

-- Indexes for Performance
CREATE INDEX idx_project_files_tenant_id ON project_files(tenant_id);
CREATE INDEX idx_project_files_user_id ON project_files(user_id);
-- session_id index REMOVED - session_id not in schema
CREATE INDEX idx_project_files_status ON project_files(status);
CREATE INDEX idx_project_files_processing_status ON project_files(processing_status);
CREATE INDEX idx_project_files_deleted ON project_files(deleted);
CREATE INDEX idx_project_files_file_path ON project_files(file_path);
CREATE INDEX idx_project_files_created_at ON project_files(created_at DESC);
CREATE INDEX idx_project_files_pillar_origin ON project_files(pillar_origin);
CREATE INDEX idx_project_files_parent_file_uuid ON project_files(parent_file_uuid);
CREATE INDEX idx_project_files_root_file_uuid ON project_files(root_file_uuid);
CREATE INDEX idx_project_files_lineage_depth ON project_files(lineage_depth);

-- Composite indexes for common queries
CREATE INDEX idx_project_files_tenant_status ON project_files(tenant_id, status, deleted);
CREATE INDEX idx_project_files_lineage ON project_files(root_file_uuid, lineage_depth, generation);

-- RLS Policies (Row Level Security)
ALTER TABLE project_files ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see files in their tenant
CREATE POLICY "Users can view files in their tenant"
    ON project_files FOR SELECT
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Policy: Users can insert files in their tenant
CREATE POLICY "Users can insert files in their tenant"
    ON project_files FOR INSERT
    WITH CHECK (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Policy: Users can update files in their tenant
CREATE POLICY "Users can update files in their tenant"
    ON project_files FOR UPDATE
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Policy: Users can delete files in their tenant (soft delete)
CREATE POLICY "Users can delete files in their tenant"
    ON project_files FOR DELETE
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

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
COMMENT ON TABLE project_files IS 'File metadata table for platform file management (Phases 1-4) - Enhanced schema with lineage, security, and processing tracking';
COMMENT ON COLUMN project_files.uuid IS 'Primary key, file identifier (used as file_id in code)';
COMMENT ON COLUMN project_files.user_id IS 'User who uploaded/owns the file (UUID type)';
COMMENT ON COLUMN project_files.tenant_id IS 'Tenant for multi-tenancy isolation (UUID type)';
COMMENT ON COLUMN project_files.ui_name IS 'User-friendly filename (what user sees in UI)';
COMMENT ON COLUMN project_files.file_path IS 'GCS storage path (e.g., tenant_id/session_id/file_id/filename)';
COMMENT ON COLUMN project_files.parsed_path IS 'Path to parsed results in storage';
COMMENT ON COLUMN project_files.file_type IS 'Parsing pathway: structured, unstructured, hybrid (used by parsing tools)';
COMMENT ON COLUMN project_files.mime_type IS 'MIME type (e.g., application/pdf, text/csv) - for rendering, storage, file format identification';
COMMENT ON COLUMN project_files.file_size IS 'Size in bytes';
COMMENT ON COLUMN project_files.file_hash IS 'SHA256 hash for deduplication';
COMMENT ON COLUMN project_files.file_checksum IS 'Additional checksum for verification';
COMMENT ON COLUMN project_files.status IS 'Current status: uploaded, active, archived, purged';
COMMENT ON COLUMN project_files.processing_status IS 'Processing state: pending, processing, completed, failed';
COMMENT ON COLUMN project_files.processing_errors IS 'JSONB for error tracking during processing';
COMMENT ON COLUMN project_files.ingestion_type IS 'How file was ingested: upload, edi, api (default: upload for MVP)';
COMMENT ON COLUMN project_files.created_by IS 'User who created the file (audit trail)';
COMMENT ON COLUMN project_files.updated_by IS 'User who last updated (audit trail)';
COMMENT ON COLUMN project_files.client_ip IS 'IP address of uploader (security/audit)';
COMMENT ON COLUMN project_files.user_agent IS 'User agent of uploader (security/audit)';
COMMENT ON COLUMN project_files.access_level IS 'Access control: open, restricted, private';
COMMENT ON COLUMN project_files.permissions IS 'JSONB for fine-grained permissions';
COMMENT ON COLUMN project_files.data_classification IS 'Security classification: public, internal, confidential';
COMMENT ON COLUMN project_files.retention_policy IS 'Retention policy for compliance';
COMMENT ON COLUMN project_files.compliance_flags IS 'JSONB for compliance tracking';
COMMENT ON COLUMN project_files.pillar_origin IS 'Which realm/pillar: content_pillar, insights_pillar, etc.';
COMMENT ON COLUMN project_files.service_context IS 'JSONB for service-specific context';
COMMENT ON COLUMN project_files.processing_pipeline IS 'JSONB tracking processing steps';
COMMENT ON COLUMN project_files.arango_content_id IS 'Link to ArangoDB content';
COMMENT ON COLUMN project_files.lineage_depth IS 'Depth in lineage tree';
COMMENT ON COLUMN project_files.root_file_uuid IS 'Original file in lineage tree (root of lineage chain)';
COMMENT ON COLUMN project_files.parent_file_uuid IS 'Immediate parent file in lineage (direct predecessor)';
COMMENT ON COLUMN project_files.generation IS 'Generation number in lineage';
COMMENT ON COLUMN project_files.lineage_path IS 'Path in lineage tree';
COMMENT ON COLUMN project_files.version IS 'File version number';
COMMENT ON COLUMN project_files.insights IS 'JSONB for insights/metadata';
COMMENT ON COLUMN project_files.archived_at IS 'When file was archived (if archived)';
COMMENT ON COLUMN project_files.archive_reason IS 'Reason for archiving';
COMMENT ON COLUMN project_files.purged_at IS 'When file was purged (if purged)';
COMMENT ON COLUMN project_files.deleted IS 'Soft delete flag';
