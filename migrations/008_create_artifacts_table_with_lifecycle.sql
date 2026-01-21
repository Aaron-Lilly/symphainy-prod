-- Migration: Create artifacts table with lifecycle state tracking
-- Date: January 20, 2026
-- Purpose: Create dedicated artifacts table for Artifact Plane registry with lifecycle management
-- Breaking Change: No - New table

-- Create artifacts table for Artifact Plane registry
CREATE TABLE IF NOT EXISTS artifacts (
    -- Primary Key
    artifact_id TEXT PRIMARY KEY,
    
    -- Identity & Ownership
    tenant_id UUID NOT NULL,
    session_id UUID,
    solution_id UUID,
    execution_id TEXT,
    
    -- Artifact Information
    artifact_type TEXT NOT NULL,  -- 'roadmap', 'poc', 'blueprint', 'sop', 'workflow', 'report', etc.
    realm TEXT,  -- 'outcomes', 'journey', 'insights', 'content'
    
    -- Lifecycle State (Phase 2.1)
    lifecycle_state TEXT NOT NULL DEFAULT 'draft',  -- 'draft', 'accepted', 'obsolete'
    owner TEXT NOT NULL DEFAULT 'client',  -- 'client', 'platform', 'shared'
    purpose TEXT NOT NULL DEFAULT 'delivery',  -- 'decision_support', 'delivery', 'governance', 'learning'
    
    -- Lifecycle Transitions Audit Trail
    lifecycle_transitions JSONB DEFAULT '[]'::jsonb,  -- Array of transition records
    
    -- Storage References
    payload_storage_path TEXT,  -- GCS path to artifact payload
    payload_artifact_id TEXT,  -- Reference to storage artifact_id
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    regenerable BOOLEAN DEFAULT TRUE,
    retention_policy TEXT DEFAULT 'session',
    
    -- Intent & Execution Context
    intent_type TEXT,
    intent_id TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Constraints
ALTER TABLE artifacts ADD CONSTRAINT artifacts_lifecycle_state_check 
    CHECK (lifecycle_state IN ('draft', 'accepted', 'obsolete'));

ALTER TABLE artifacts ADD CONSTRAINT artifacts_owner_check 
    CHECK (owner IN ('client', 'platform', 'shared'));

ALTER TABLE artifacts ADD CONSTRAINT artifacts_purpose_check 
    CHECK (purpose IN ('decision_support', 'delivery', 'governance', 'learning'));

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_artifacts_tenant_id ON artifacts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_session_id ON artifacts(session_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_solution_id ON artifacts(solution_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_execution_id ON artifacts(execution_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_artifact_type ON artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_artifacts_realm ON artifacts(realm);
CREATE INDEX IF NOT EXISTS idx_artifacts_lifecycle_state ON artifacts(lifecycle_state);
CREATE INDEX IF NOT EXISTS idx_artifacts_owner ON artifacts(owner);
CREATE INDEX IF NOT EXISTS idx_artifacts_purpose ON artifacts(purpose);
CREATE INDEX IF NOT EXISTS idx_artifacts_created_at ON artifacts(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_artifacts_tenant_lifecycle ON artifacts(tenant_id, lifecycle_state);
CREATE INDEX IF NOT EXISTS idx_artifacts_tenant_type ON artifacts(tenant_id, artifact_type);
CREATE INDEX IF NOT EXISTS idx_artifacts_session_type ON artifacts(session_id, artifact_type) WHERE session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_artifacts_lifecycle_owner ON artifacts(lifecycle_state, owner);

-- RLS Policies (Row Level Security)
ALTER TABLE artifacts ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see artifacts in their tenant
CREATE POLICY "Users can view artifacts in their tenant"
    ON artifacts FOR SELECT
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Policy: Users can insert artifacts in their tenant
CREATE POLICY "Users can insert artifacts in their tenant"
    ON artifacts FOR INSERT
    WITH CHECK (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Policy: Users can update artifacts in their tenant
CREATE POLICY "Users can update artifacts in their tenant"
    ON artifacts FOR UPDATE
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Policy: Users can delete artifacts in their tenant
CREATE POLICY "Users can delete artifacts in their tenant"
    ON artifacts FOR DELETE
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Trigger: Auto-update updated_at
CREATE OR REPLACE FUNCTION update_artifacts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_artifacts_updated_at
    BEFORE UPDATE ON artifacts
    FOR EACH ROW
    EXECUTE FUNCTION update_artifacts_updated_at();

-- Comments for documentation
COMMENT ON TABLE artifacts IS 'Artifact Plane registry - Purpose-Bound Outcomes with lifecycle management';
COMMENT ON COLUMN artifacts.artifact_id IS 'Primary key, artifact identifier';
COMMENT ON COLUMN artifacts.tenant_id IS 'Tenant for multi-tenancy isolation';
COMMENT ON COLUMN artifacts.session_id IS 'Session identifier (optional)';
COMMENT ON COLUMN artifacts.solution_id IS 'Solution identifier (optional)';
COMMENT ON COLUMN artifacts.execution_id IS 'Execution identifier for lineage';
COMMENT ON COLUMN artifacts.artifact_type IS 'Type of artifact: roadmap, poc, blueprint, sop, workflow, report, etc.';
COMMENT ON COLUMN artifacts.realm IS 'Realm that created the artifact: outcomes, journey, insights, content';
COMMENT ON COLUMN artifacts.lifecycle_state IS 'Lifecycle state: draft, accepted, obsolete';
COMMENT ON COLUMN artifacts.owner IS 'Owner: client, platform, shared';
COMMENT ON COLUMN artifacts.purpose IS 'Purpose: decision_support, delivery, governance, learning';
COMMENT ON COLUMN artifacts.lifecycle_transitions IS 'JSONB array of lifecycle transition records for audit trail';
COMMENT ON COLUMN artifacts.payload_storage_path IS 'GCS path to artifact payload';
COMMENT ON COLUMN artifacts.payload_artifact_id IS 'Reference to storage artifact_id';
COMMENT ON COLUMN artifacts.metadata IS 'Additional metadata JSONB';
COMMENT ON COLUMN artifacts.regenerable IS 'Whether artifact can be regenerated';
COMMENT ON COLUMN artifacts.retention_policy IS 'Retention policy: session, persistent, etc.';
