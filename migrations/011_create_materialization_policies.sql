-- Migration: Create materialization_policies table
-- Date: January 20, 2026
-- Purpose: Store materialization policies with tenant-scoped support and platform defaults
-- Breaking Change: No - New table

-- Create materialization_policies table
CREATE TABLE IF NOT EXISTS materialization_policies (
    -- Primary Key
    policy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Policy Scope
    tenant_id UUID,  -- NULL for platform-level default policies
    solution_id UUID,  -- Optional: solution-specific policy (overrides tenant policy)
    
    -- Policy Configuration
    policy_name TEXT NOT NULL,  -- Human-readable policy name
    policy_version INTEGER DEFAULT 1,  -- Policy version for versioning
    
    -- Policy Rules (JSONB for flexibility)
    policy_rules JSONB NOT NULL DEFAULT '{}'::jsonb,  -- Policy configuration
    -- Structure:
    -- {
    --   "allow_all_types": true/false,
    --   "allowed_types": ["full_artifact", "deterministic", "semantic_embedding", ...],
    --   "default_ttl_days": 30,
    --   "default_backing_store": "gcs",
    --   "restrictions": {...}
    -- }
    
    -- Policy Metadata
    is_platform_default BOOLEAN DEFAULT FALSE,  -- True for platform-level defaults
    is_active BOOLEAN DEFAULT TRUE,  -- Can disable policies without deleting
    description TEXT,  -- Policy description
    
    -- Audit
    created_by TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Constraints
-- Only one platform default policy per version
CREATE UNIQUE INDEX IF NOT EXISTS idx_materialization_policies_platform_default 
    ON materialization_policies(policy_version) 
    WHERE is_platform_default = TRUE AND tenant_id IS NULL;

-- Only one active tenant policy per tenant
CREATE UNIQUE INDEX IF NOT EXISTS idx_materialization_policies_tenant_active 
    ON materialization_policies(tenant_id, policy_version) 
    WHERE tenant_id IS NOT NULL AND is_active = TRUE;

-- Only one active solution policy per solution
CREATE UNIQUE INDEX IF NOT EXISTS idx_materialization_policies_solution_active 
    ON materialization_policies(solution_id, policy_version) 
    WHERE solution_id IS NOT NULL AND is_active = TRUE;

-- Indexes for queries
CREATE INDEX IF NOT EXISTS idx_materialization_policies_tenant_id 
    ON materialization_policies(tenant_id) 
    WHERE tenant_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_materialization_policies_solution_id 
    ON materialization_policies(solution_id) 
    WHERE solution_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_materialization_policies_active 
    ON materialization_policies(is_active) 
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_materialization_policies_platform_default 
    ON materialization_policies(is_platform_default) 
    WHERE is_platform_default = TRUE;

-- RLS Policies (Row Level Security)
ALTER TABLE materialization_policies ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view policies for their tenant or platform defaults
CREATE POLICY "Users can view policies in their tenant"
    ON materialization_policies FOR SELECT
    USING (
        tenant_id = (auth.jwt() ->> 'tenant_id')::uuid 
        OR is_platform_default = TRUE
    );

-- Policy: Only admins can insert/update/delete policies
-- (For MVP, we'll use service role key, so this is permissive)
CREATE POLICY "Service role can manage policies"
    ON materialization_policies FOR ALL
    USING (true)
    WITH CHECK (true);

-- Trigger: Auto-update updated_at
CREATE OR REPLACE FUNCTION update_materialization_policies_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_materialization_policies_updated_at
    BEFORE UPDATE ON materialization_policies
    FOR EACH ROW
    EXECUTE FUNCTION update_materialization_policies_updated_at();

-- Insert MVP permissive platform default policy
INSERT INTO materialization_policies (
    tenant_id,
    policy_name,
    policy_version,
    policy_rules,
    is_platform_default,
    is_active,
    description,
    created_by
) VALUES (
    NULL,  -- Platform default
    'MVP Permissive Policy',
    1,
    '{
        "allow_all_types": true,
        "allowed_types": ["reference", "partial_extraction", "deterministic", "semantic_embedding", "full_artifact"],
        "default_ttl_days": 30,
        "default_backing_store": "gcs",
        "no_restrictions": true,
        "policy_version": "mvp_1.0"
    }'::jsonb,
    TRUE,
    TRUE,
    'MVP permissive policy - allows all materialization types with 30-day TTL. Can be tightened for production without code changes.',
    'system'
) ON CONFLICT DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE materialization_policies IS 'Materialization policies with tenant-scoped support and platform defaults';
COMMENT ON COLUMN materialization_policies.policy_id IS 'Primary key, policy identifier';
COMMENT ON COLUMN materialization_policies.tenant_id IS 'Tenant ID (NULL for platform defaults)';
COMMENT ON COLUMN materialization_policies.solution_id IS 'Optional solution-specific policy (overrides tenant policy)';
COMMENT ON COLUMN materialization_policies.policy_name IS 'Human-readable policy name';
COMMENT ON COLUMN materialization_policies.policy_version IS 'Policy version for versioning';
COMMENT ON COLUMN materialization_policies.policy_rules IS 'JSONB policy configuration (allow_all_types, allowed_types, default_ttl_days, etc.)';
COMMENT ON COLUMN materialization_policies.is_platform_default IS 'True for platform-level default policies';
COMMENT ON COLUMN materialization_policies.is_active IS 'Can disable policies without deleting';
