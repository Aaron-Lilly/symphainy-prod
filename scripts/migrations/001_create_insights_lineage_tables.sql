-- Migration: Create Insights Realm Lineage Tracking Tables
-- Created: January 2026
-- Purpose: Track parsed results and embeddings for complete lineage

-- Table: parsed_results
-- Tracks parsed results and links to source files
CREATE TABLE IF NOT EXISTS parsed_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    file_id UUID NOT NULL,  -- References files(id) - will add FK constraint if files table exists
    parsed_result_id TEXT NOT NULL,  -- Reference ID
    gcs_path TEXT NOT NULL,  -- Where parsed results stored in GCS
    parser_type TEXT NOT NULL,  -- "mainframe", "csv", "json", "pdf", etc.
    parser_config JSONB,  -- Parser configuration used
    record_count INTEGER,
    status TEXT,  -- "success", "partial", "failed"
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, parsed_result_id)
);

CREATE INDEX IF NOT EXISTS idx_parsed_results_file_id ON parsed_results(file_id);
CREATE INDEX IF NOT EXISTS idx_parsed_results_tenant_id ON parsed_results(tenant_id);
CREATE INDEX IF NOT EXISTS idx_parsed_results_parser_type ON parsed_results(parser_type);

-- Table: embeddings
-- Tracks embeddings and links to parsed results + source files
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    file_id UUID NOT NULL,  -- References files(id) - will add FK constraint if files table exists
    parsed_result_id UUID,  -- References parsed_results(id) - will add FK constraint
    embedding_id TEXT NOT NULL,  -- Reference ID for embedding in ArangoDB
    arango_collection TEXT NOT NULL,  -- ArangoDB collection name
    arango_key TEXT NOT NULL,  -- ArangoDB document key
    embedding_count INTEGER,  -- Number of embeddings generated
    model_name TEXT,  -- Embedding model used
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, embedding_id)
);

CREATE INDEX IF NOT EXISTS idx_embeddings_file_id ON embeddings(file_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_parsed_result_id ON embeddings(parsed_result_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_tenant_id ON embeddings(tenant_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_embedding_id ON embeddings(embedding_id);

-- Add comments for documentation
COMMENT ON TABLE parsed_results IS 'Tracks parsed results and links to source files for lineage tracking';
COMMENT ON TABLE embeddings IS 'Tracks embeddings and links to parsed results + source files for lineage tracking';

COMMENT ON COLUMN parsed_results.parsed_result_id IS 'Reference ID for parsed results in GCS';
COMMENT ON COLUMN parsed_results.gcs_path IS 'GCS path where parsed results are stored';
COMMENT ON COLUMN embeddings.embedding_id IS 'Reference ID for embedding in ArangoDB';
COMMENT ON COLUMN embeddings.arango_collection IS 'ArangoDB collection name where embeddings are stored';
COMMENT ON COLUMN embeddings.arango_key IS 'ArangoDB document key for the embedding';

-- Table: guides
-- Stores guides (fact patterns + output templates) for guided discovery
CREATE TABLE IF NOT EXISTS guides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    guide_id TEXT NOT NULL,  -- Reference ID
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL,  -- "default" | "user_uploaded" | "user_created"
    fact_pattern JSONB NOT NULL,  -- Entities, relationships, attributes
    output_template JSONB NOT NULL,  -- Output structure template
    version TEXT DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID,  -- User who created (if user_created)
    
    UNIQUE(tenant_id, guide_id)
);

CREATE INDEX IF NOT EXISTS idx_guides_tenant_id ON guides(tenant_id);
CREATE INDEX IF NOT EXISTS idx_guides_type ON guides(type);
CREATE INDEX IF NOT EXISTS idx_guides_guide_id ON guides(guide_id);

COMMENT ON TABLE guides IS 'Stores guides (fact patterns + output templates) for guided discovery';
COMMENT ON COLUMN guides.guide_id IS 'Reference ID for the guide';
COMMENT ON COLUMN guides.fact_pattern IS 'Fact pattern (entities, relationships, attributes)';
COMMENT ON COLUMN guides.output_template IS 'Output structure template';

-- Table: interpretations
-- Tracks data interpretations (self-discovery and guided) for lineage
CREATE TABLE IF NOT EXISTS interpretations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    file_id UUID NOT NULL,  -- References files(id)
    parsed_result_id UUID,  -- References parsed_results(id)
    embedding_id UUID,  -- References embeddings(id)
    guide_id UUID,  -- References guides(id) - if guided discovery
    interpretation_type TEXT NOT NULL,  -- "self_discovery" | "guided"
    interpretation_result JSONB NOT NULL,  -- Full interpretation results
    confidence_score FLOAT,
    coverage_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, id)
);

CREATE INDEX IF NOT EXISTS idx_interpretations_file_id ON interpretations(file_id);
CREATE INDEX IF NOT EXISTS idx_interpretations_parsed_result_id ON interpretations(parsed_result_id);
CREATE INDEX IF NOT EXISTS idx_interpretations_embedding_id ON interpretations(embedding_id);
CREATE INDEX IF NOT EXISTS idx_interpretations_guide_id ON interpretations(guide_id);
CREATE INDEX IF NOT EXISTS idx_interpretations_tenant_id ON interpretations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_interpretations_type ON interpretations(interpretation_type);

-- Table: analyses
-- Tracks business analyses (structured and unstructured) for lineage
CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    file_id UUID NOT NULL,  -- References files(id)
    parsed_result_id UUID,  -- References parsed_results(id)
    interpretation_id UUID,  -- References interpretations(id) - if based on interpretation
    analysis_type TEXT NOT NULL,  -- "structured" | "unstructured"
    analysis_result JSONB NOT NULL,  -- Full analysis results
    deep_dive BOOLEAN DEFAULT FALSE,  -- Whether Insights Liaison Agent was used
    agent_session_id TEXT,  -- Insights Liaison Agent session ID if deep_dive=true
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, id)
);

CREATE INDEX IF NOT EXISTS idx_analyses_file_id ON analyses(file_id);
CREATE INDEX IF NOT EXISTS idx_analyses_parsed_result_id ON analyses(parsed_result_id);
CREATE INDEX IF NOT EXISTS idx_analyses_interpretation_id ON analyses(interpretation_id);
CREATE INDEX IF NOT EXISTS idx_analyses_tenant_id ON analyses(tenant_id);
CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analyses_deep_dive ON analyses(deep_dive);

COMMENT ON TABLE interpretations IS 'Tracks data interpretations (self-discovery and guided) for lineage tracking';
COMMENT ON TABLE analyses IS 'Tracks business analyses (structured and unstructured) for lineage tracking';

COMMENT ON COLUMN interpretations.interpretation_type IS 'Type of interpretation: self_discovery or guided';
COMMENT ON COLUMN interpretations.interpretation_result IS 'Full interpretation results (entities, relationships, etc.)';
COMMENT ON COLUMN analyses.analysis_type IS 'Type of analysis: structured or unstructured';
COMMENT ON COLUMN analyses.analysis_result IS 'Full analysis results (statistical, semantic, etc.)';
COMMENT ON COLUMN analyses.deep_dive IS 'Whether Insights Liaison Agent was engaged for deep dive';
COMMENT ON COLUMN analyses.agent_session_id IS 'Insights Liaison Agent session ID if deep_dive=true';
