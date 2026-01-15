-- Policy Registry Schema
-- Flexible JSONB structure (defer full schema definition)
-- Phase 1: Create tables
-- Phase 2: Full schema definition (if needed)

-- Policy Rules Table
CREATE TABLE IF NOT EXISTS policy_rules (
    policy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_type VARCHAR(100) NOT NULL,  -- auth, isolation, data_access, execution, tenant_override
    policy_data JSONB NOT NULL,          -- Flexible JSONB structure
    tenant_id UUID,                       -- Optional tenant ID for tenant-specific policies
    action VARCHAR(255),                  -- Optional action filter
    resource VARCHAR(255),                -- Optional resource filter
    version VARCHAR(50) DEFAULT '1.0.0',
    status VARCHAR(50) DEFAULT 'active',   -- active, deprecated, maintenance
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_policy_rules_type ON policy_rules(policy_type);
CREATE INDEX IF NOT EXISTS idx_policy_rules_tenant ON policy_rules(tenant_id);
CREATE INDEX IF NOT EXISTS idx_policy_rules_action ON policy_rules(action);
CREATE INDEX IF NOT EXISTS idx_policy_rules_status ON policy_rules(status);
CREATE INDEX IF NOT EXISTS idx_policy_rules_jsonb ON policy_rules USING GIN(policy_data);

-- Comments
COMMENT ON TABLE policy_rules IS 'Policy Registry - Data-backed catalog for policy rules (flexible JSONB structure)';
COMMENT ON COLUMN policy_rules.policy_data IS 'Flexible JSONB structure for policy data (defer full schema definition)';
