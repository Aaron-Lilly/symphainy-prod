-- Migration: Create Agent Posture Registry
-- Purpose: Store agent postures (Layer 2: Tenant/Solution scoped behavioral tuning)
-- Date: January 2026

-- Agent Posture Registry Table
CREATE TABLE IF NOT EXISTS agent_posture_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    tenant_id TEXT,  -- NULL = platform default
    solution_id TEXT,  -- NULL = tenant default
    posture_data JSONB NOT NULL,
    version TEXT DEFAULT '1.0',
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_id, tenant_id, solution_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_agent_posture_registry_agent_id 
    ON agent_posture_registry(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_posture_registry_tenant_id 
    ON agent_posture_registry(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agent_posture_registry_solution_id 
    ON agent_posture_registry(solution_id);
-- Composite index for fallback lookup
CREATE INDEX IF NOT EXISTS idx_agent_posture_registry_lookup 
    ON agent_posture_registry(agent_id, tenant_id, solution_id);

-- RLS Policies (Tenant-isolated)
ALTER TABLE agent_posture_registry ENABLE ROW LEVEL SECURITY;

-- Policy: Allow users to read postures for their tenant (or platform defaults)
CREATE POLICY "tenant_read_agent_postures" ON agent_posture_registry
    FOR SELECT
    USING (
        tenant_id = current_setting('app.current_tenant_id', true)::TEXT
        OR tenant_id IS NULL  -- Platform defaults
    );

-- Policy: Allow users to insert postures for their tenant
CREATE POLICY "tenant_insert_agent_postures" ON agent_posture_registry
    FOR INSERT
    WITH CHECK (
        tenant_id = current_setting('app.current_tenant_id', true)::TEXT
        OR tenant_id IS NULL  -- Platform defaults (admin only)
    );

-- Policy: Allow users to update postures for their tenant
CREATE POLICY "tenant_update_agent_postures" ON agent_posture_registry
    FOR UPDATE
    USING (
        tenant_id = current_setting('app.current_tenant_id', true)::TEXT
        OR tenant_id IS NULL  -- Platform defaults (admin only)
    )
    WITH CHECK (
        tenant_id = current_setting('app.current_tenant_id', true)::TEXT
        OR tenant_id IS NULL  -- Platform defaults (admin only)
    );

-- Policy: Allow users to delete postures for their tenant
CREATE POLICY "tenant_delete_agent_postures" ON agent_posture_registry
    FOR DELETE
    USING (
        tenant_id = current_setting('app.current_tenant_id', true)::TEXT
        OR tenant_id IS NULL  -- Platform defaults (admin only)
    );

-- Comments
COMMENT ON TABLE agent_posture_registry IS 
    'Agent Posture Registry - Tenant/Solution scoped behavioral tuning (Layer 2 of 4-layer model)';
COMMENT ON COLUMN agent_posture_registry.agent_id IS 
    'Agent identifier (references AgentDefinition)';
COMMENT ON COLUMN agent_posture_registry.tenant_id IS 
    'Tenant identifier (NULL = platform default)';
COMMENT ON COLUMN agent_posture_registry.solution_id IS 
    'Solution identifier (NULL = tenant default)';
COMMENT ON COLUMN agent_posture_registry.posture_data IS 
    'Full AgentPosture JSON (posture, llm_defaults, custom_properties)';
COMMENT ON COLUMN agent_posture_registry.version IS 
    'Version string for posture';

-- Note: Fallback hierarchy for get_posture():
-- 1. Solution-specific: (agent_id, tenant_id, solution_id)
-- 2. Tenant-specific: (agent_id, tenant_id, NULL)
-- 3. Platform default: (agent_id, NULL, NULL)
