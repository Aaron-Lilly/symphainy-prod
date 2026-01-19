-- Migration: Create data_boundary_contracts table
-- Date: January 2026
-- Purpose: Implement Data Boundary Contract architecture
--          Separates data access from materialization (resolves "data stays at door" anti-pattern)
-- Breaking Change: Yes - New foundational table

-- Create data_boundary_contracts table
CREATE TABLE IF NOT EXISTS data_boundary_contracts (
    -- Primary Key
    contract_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Contract Identity
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL,  -- User who requested access
    intent_id UUID,  -- Intent that triggered contract negotiation
    
    -- External Data Location (where data lives)
    external_source_type TEXT NOT NULL,  -- 'file', 'api', 'database', 'stream', etc.
    external_source_identifier TEXT NOT NULL,  -- File path, API endpoint, DB connection string, etc.
    external_source_metadata JSONB,  -- Additional source metadata
    
    -- Access Policy (can we read it?)
    access_granted BOOLEAN NOT NULL DEFAULT FALSE,
    access_granted_at TIMESTAMPTZ,
    access_granted_by TEXT,  -- Policy/system that granted access
    access_reason TEXT,  -- Why access was granted/denied
    access_conditions JSONB,  -- Conditions for access (e.g., encryption required)
    
    -- Materialization Policy (can we persist it? in what form? for how long?)
    materialization_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    materialization_type TEXT,  -- 'reference', 'partial_extraction', 'deterministic', 'semantic_embedding', 'full_artifact'
    materialization_scope JSONB,  -- What can be materialized (fields, sections, etc.)
    materialization_ttl INTERVAL,  -- Time to live (NULL = permanent, INTERVAL = temporary)
    materialization_expires_at TIMESTAMPTZ,  -- Calculated expiration time
    materialization_backing_store TEXT,  -- 'gcs', 'supabase', 'memory', 'none'
    materialization_policy_basis TEXT,  -- Which policy rule authorized this
    
    -- Retention and Purge
    retention_policy TEXT,  -- Retention policy name
    purge_after TIMESTAMPTZ,  -- When to purge materialized data
    auto_purge BOOLEAN DEFAULT FALSE,  -- Auto-purge when TTL expires
    
    -- Reference Control (who can reference it later?)
    reference_allowed BOOLEAN DEFAULT TRUE,
    reference_scope JSONB,  -- Who can reference (users, realms, etc.)
    
    -- Contract Lifecycle
    contract_status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'active', 'expired', 'revoked', 'fulfilled'
    negotiated_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    expired_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    revoked_reason TEXT,
    
    -- Audit Trail
    created_by TEXT,
    updated_by TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Contract Terms (full contract details)
    contract_terms JSONB,  -- Complete contract terms as JSON
    
    -- Constraints
    CONSTRAINT data_boundary_contracts_materialization_type_check 
        CHECK (materialization_type IS NULL OR materialization_type IN (
            'reference', 'partial_extraction', 'deterministic', 'semantic_embedding', 'full_artifact'
        )),
    CONSTRAINT data_boundary_contracts_status_check 
        CHECK (contract_status IN ('pending', 'active', 'expired', 'revoked', 'fulfilled'))
);

-- Indexes for Performance
CREATE INDEX idx_data_boundary_contracts_tenant_id ON data_boundary_contracts(tenant_id);
CREATE INDEX idx_data_boundary_contracts_user_id ON data_boundary_contracts(user_id);
CREATE INDEX idx_data_boundary_contracts_intent_id ON data_boundary_contracts(intent_id);
CREATE INDEX idx_data_boundary_contracts_external_source ON data_boundary_contracts(external_source_type, external_source_identifier);
CREATE INDEX idx_data_boundary_contracts_status ON data_boundary_contracts(contract_status);
CREATE INDEX idx_data_boundary_contracts_materialization_type ON data_boundary_contracts(materialization_type);
CREATE INDEX idx_data_boundary_contracts_expires_at ON data_boundary_contracts(materialization_expires_at) WHERE materialization_expires_at IS NOT NULL;
CREATE INDEX idx_data_boundary_contracts_purge_after ON data_boundary_contracts(purge_after) WHERE purge_after IS NOT NULL;
CREATE INDEX idx_data_boundary_contracts_tenant_status ON data_boundary_contracts(tenant_id, contract_status);

-- Row Level Security
ALTER TABLE data_boundary_contracts ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see contracts in their tenant
CREATE POLICY "Users can view contracts in their tenant"
    ON data_boundary_contracts FOR SELECT
    USING (tenant_id::text = current_setting('app.tenant_id', true));

-- Policy: Users can insert contracts in their tenant
CREATE POLICY "Users can insert contracts in their tenant"
    ON data_boundary_contracts FOR INSERT
    WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));

-- Policy: Users can update contracts in their tenant
CREATE POLICY "Users can update contracts in their tenant"
    ON data_boundary_contracts FOR UPDATE
    USING (tenant_id::text = current_setting('app.tenant_id', true));

-- Policy: Users can delete contracts in their tenant
CREATE POLICY "Users can delete contracts in their tenant"
    ON data_boundary_contracts FOR DELETE
    USING (tenant_id::text = current_setting('app.tenant_id', true));

-- Trigger for updated_at
CREATE TRIGGER update_data_boundary_contracts_updated_at
    BEFORE UPDATE ON data_boundary_contracts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE data_boundary_contracts IS 'Data Boundary Contracts - Governs access and materialization of external data. Owned by Data Steward (Smart City), not Content Realm.';
COMMENT ON COLUMN data_boundary_contracts.contract_id IS 'Primary key, unique contract identifier';
COMMENT ON COLUMN data_boundary_contracts.external_source_type IS 'Type of external source: file, api, database, stream, etc.';
COMMENT ON COLUMN data_boundary_contracts.external_source_identifier IS 'Identifier for external source (file path, API endpoint, etc.)';
COMMENT ON COLUMN data_boundary_contracts.access_granted IS 'Whether access to external data is granted';
COMMENT ON COLUMN data_boundary_contracts.materialization_allowed IS 'Whether materialization inside platform is allowed';
COMMENT ON COLUMN data_boundary_contracts.materialization_type IS 'Type of materialization: reference, partial_extraction, deterministic, semantic_embedding, full_artifact';
COMMENT ON COLUMN data_boundary_contracts.materialization_ttl IS 'Time to live for materialized data (NULL = permanent)';
COMMENT ON COLUMN data_boundary_contracts.materialization_backing_store IS 'Where to store materialized data: gcs, supabase, memory, none';
COMMENT ON COLUMN data_boundary_contracts.contract_status IS 'Contract lifecycle status: pending, active, expired, revoked, fulfilled';
