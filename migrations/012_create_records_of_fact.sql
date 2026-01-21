-- Migration: Create records_of_fact table
-- Date: January 20, 2026
-- Purpose: Track Records of Fact (persistent meaning) promoted from Working Materials
-- Breaking Change: No - New table

-- Create records_of_fact table
CREATE TABLE IF NOT EXISTS records_of_fact (
    -- Primary Key
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity & Ownership
    tenant_id UUID NOT NULL,
    
    -- Record Type
    record_type TEXT NOT NULL,  -- 'deterministic_embedding', 'semantic_embedding', 'interpretation', 'conclusion'
    
    -- Source Reference (Working Material that was promoted)
    source_file_id UUID,  -- Reference to project_files.uuid (may expire)
    source_boundary_contract_id UUID,  -- Reference to data_boundary_contracts.contract_id
    source_expired_at TIMESTAMPTZ,  -- When source Working Material expired (NULL if not expired)
    
    -- Storage References
    -- For embeddings: reference to embeddings table
    embedding_id UUID,  -- References embeddings.id (if record_type is embedding)
    arango_collection TEXT,  -- ArangoDB collection name
    arango_key TEXT,  -- ArangoDB document key
    
    -- For interpretations: reference to interpretations table
    interpretation_id UUID,  -- References interpretations.id (if record_type is interpretation)
    
    -- Record Content
    record_content JSONB,  -- The actual record content (meaning, conclusion, etc.)
    
    -- Metadata
    model_name TEXT,  -- Model used (for embeddings)
    confidence_score FLOAT,  -- Confidence score (if applicable)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    promoted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- When promoted from Working Material
    promoted_by TEXT,  -- Who/what initiated the promotion
    
    -- Audit
    promotion_reason TEXT,  -- Reason for promotion
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Constraints
ALTER TABLE records_of_fact ADD CONSTRAINT records_of_fact_record_type_check 
    CHECK (record_type IN ('deterministic_embedding', 'semantic_embedding', 'interpretation', 'conclusion'));

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_records_of_fact_tenant_id 
    ON records_of_fact(tenant_id);

CREATE INDEX IF NOT EXISTS idx_records_of_fact_record_type 
    ON records_of_fact(record_type);

CREATE INDEX IF NOT EXISTS idx_records_of_fact_source_file_id 
    ON records_of_fact(source_file_id) 
    WHERE source_file_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_records_of_fact_source_expired_at 
    ON records_of_fact(source_expired_at) 
    WHERE source_expired_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_records_of_fact_embedding_id 
    ON records_of_fact(embedding_id) 
    WHERE embedding_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_records_of_fact_interpretation_id 
    ON records_of_fact(interpretation_id) 
    WHERE interpretation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_records_of_fact_arango_collection_key 
    ON records_of_fact(arango_collection, arango_key) 
    WHERE arango_collection IS NOT NULL AND arango_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_records_of_fact_promoted_at 
    ON records_of_fact(promoted_at DESC);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_records_of_fact_tenant_type 
    ON records_of_fact(tenant_id, record_type);

CREATE INDEX IF NOT EXISTS idx_records_of_fact_source_expired 
    ON records_of_fact(tenant_id, source_expired_at) 
    WHERE source_expired_at IS NOT NULL;

-- RLS Policies (Row Level Security)
ALTER TABLE records_of_fact ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see records in their tenant
CREATE POLICY "Users can view records in their tenant"
    ON records_of_fact FOR SELECT
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Policy: Service role can manage records
CREATE POLICY "Service role can manage records"
    ON records_of_fact FOR ALL
    USING (true)
    WITH CHECK (true);

-- Comments for documentation
COMMENT ON TABLE records_of_fact IS 'Records of Fact - Persistent meaning promoted from Working Materials';
COMMENT ON COLUMN records_of_fact.record_id IS 'Primary key, record identifier';
COMMENT ON COLUMN records_of_fact.tenant_id IS 'Tenant for multi-tenancy isolation';
COMMENT ON COLUMN records_of_fact.record_type IS 'Type of record: deterministic_embedding, semantic_embedding, interpretation, conclusion';
COMMENT ON COLUMN records_of_fact.source_file_id IS 'Reference to source Working Material (may expire)';
COMMENT ON COLUMN records_of_fact.source_boundary_contract_id IS 'Reference to boundary contract that authorized materialization';
COMMENT ON COLUMN records_of_fact.source_expired_at IS 'When source Working Material expired (NULL if not expired) - meaning persists independently';
COMMENT ON COLUMN records_of_fact.embedding_id IS 'Reference to embeddings table (if record_type is embedding)';
COMMENT ON COLUMN records_of_fact.arango_collection IS 'ArangoDB collection name where embedding is stored';
COMMENT ON COLUMN records_of_fact.arango_key IS 'ArangoDB document key for the embedding';
COMMENT ON COLUMN records_of_fact.interpretation_id IS 'Reference to interpretations table (if record_type is interpretation)';
COMMENT ON COLUMN records_of_fact.record_content IS 'The actual record content (meaning, conclusion, etc.)';
COMMENT ON COLUMN records_of_fact.promoted_at IS 'When record was promoted from Working Material to Record of Fact';
COMMENT ON COLUMN records_of_fact.promoted_by IS 'Who/what initiated the promotion';
COMMENT ON COLUMN records_of_fact.promotion_reason IS 'Reason for promotion';
