-- Migration: Create Platform DNA registry tables
-- Date: January 20, 2026
-- Purpose: Store Platform DNA (generalized, curated capabilities) in versioned, immutable registries
-- Breaking Change: No - New tables

-- ============================================================================
-- Solution Registry
-- ============================================================================

CREATE TABLE IF NOT EXISTS solution_registry (
    -- Primary Key
    registry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    solution_id TEXT NOT NULL,  -- Human-readable solution identifier
    solution_name TEXT NOT NULL,
    solution_version INTEGER NOT NULL DEFAULT 1,
    
    -- Generalization (de-identified, abstracted from client context)
    solution_definition JSONB NOT NULL,  -- Generalized solution definition (no client context)
    solution_type TEXT,  -- Type of solution (e.g., "workflow_optimization", "data_analysis")
    
    -- Source (link to Purpose-Bound Outcome that was promoted)
    source_artifact_id TEXT,  -- Reference to artifacts.artifact_id
    source_tenant_id UUID,  -- Original tenant (for audit, not used in solution)
    promoted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    promoted_by TEXT NOT NULL,  -- Curator who promoted
    
    -- Versioning (immutable)
    parent_registry_id UUID,  -- Links to previous version (self-reference)
    is_current_version BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    description TEXT,
    tags TEXT[],  -- Tags for discovery
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL
);

-- Constraints
CREATE UNIQUE INDEX IF NOT EXISTS idx_solution_registry_id_version 
    ON solution_registry(solution_id, solution_version);

CREATE INDEX IF NOT EXISTS idx_solution_registry_current 
    ON solution_registry(solution_id, is_current_version) 
    WHERE is_current_version = TRUE;

CREATE INDEX IF NOT EXISTS idx_solution_registry_type 
    ON solution_registry(solution_type);

CREATE INDEX IF NOT EXISTS idx_solution_registry_source_artifact 
    ON solution_registry(source_artifact_id) 
    WHERE source_artifact_id IS NOT NULL;

-- ============================================================================
-- Intent Registry
-- ============================================================================

CREATE TABLE IF NOT EXISTS intent_registry (
    -- Primary Key
    registry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    intent_id TEXT NOT NULL,  -- Human-readable intent identifier
    intent_name TEXT NOT NULL,
    intent_version INTEGER NOT NULL DEFAULT 1,
    
    -- Generalization (de-identified, abstracted from client context)
    intent_definition JSONB NOT NULL,  -- Generalized intent definition (no client context)
    intent_type TEXT NOT NULL,  -- Type of intent (e.g., "analyze_data", "create_workflow")
    
    -- Source (link to Purpose-Bound Outcome that was promoted)
    source_artifact_id TEXT,  -- Reference to artifacts.artifact_id
    source_tenant_id UUID,  -- Original tenant (for audit, not used in intent)
    promoted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    promoted_by TEXT NOT NULL,  -- Curator who promoted
    
    -- Versioning (immutable)
    parent_registry_id UUID,  -- Links to previous version (self-reference)
    is_current_version BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    description TEXT,
    tags TEXT[],  -- Tags for discovery
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL
);

-- Constraints
CREATE UNIQUE INDEX IF NOT EXISTS idx_intent_registry_id_version 
    ON intent_registry(intent_id, intent_version);

CREATE INDEX IF NOT EXISTS idx_intent_registry_current 
    ON intent_registry(intent_id, is_current_version) 
    WHERE is_current_version = TRUE;

CREATE INDEX IF NOT EXISTS idx_intent_registry_type 
    ON intent_registry(intent_type);

CREATE INDEX IF NOT EXISTS idx_intent_registry_source_artifact 
    ON intent_registry(source_artifact_id) 
    WHERE source_artifact_id IS NOT NULL;

-- ============================================================================
-- Realm Registry
-- ============================================================================

CREATE TABLE IF NOT EXISTS realm_registry (
    -- Primary Key
    registry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    realm_id TEXT NOT NULL,  -- Human-readable realm identifier
    realm_name TEXT NOT NULL,
    realm_version INTEGER NOT NULL DEFAULT 1,
    
    -- Generalization (de-identified, abstracted from client context)
    realm_definition JSONB NOT NULL,  -- Generalized realm definition (no client context)
    realm_type TEXT NOT NULL,  -- Type of realm (e.g., "content", "journey", "insights", "outcomes")
    
    -- Source (link to Purpose-Bound Outcome that was promoted)
    source_artifact_id TEXT,  -- Reference to artifacts.artifact_id
    source_tenant_id UUID,  -- Original tenant (for audit, not used in realm)
    promoted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    promoted_by TEXT NOT NULL,  -- Curator who promoted
    
    -- Versioning (immutable)
    parent_registry_id UUID,  -- Links to previous version (self-reference)
    is_current_version BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    description TEXT,
    tags TEXT[],  -- Tags for discovery
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL
);

-- Constraints
CREATE UNIQUE INDEX IF NOT EXISTS idx_realm_registry_id_version 
    ON realm_registry(realm_id, realm_version);

CREATE INDEX IF NOT EXISTS idx_realm_registry_current 
    ON realm_registry(realm_id, is_current_version) 
    WHERE is_current_version = TRUE;

CREATE INDEX IF NOT EXISTS idx_realm_registry_type 
    ON realm_registry(realm_type);

CREATE INDEX IF NOT EXISTS idx_realm_registry_source_artifact 
    ON realm_registry(source_artifact_id) 
    WHERE source_artifact_id IS NOT NULL;

-- ============================================================================
-- RLS Policies (Row Level Security)
-- ============================================================================

-- Solution Registry
ALTER TABLE solution_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view solution registry"
    ON solution_registry FOR SELECT
    USING (true);  -- Platform DNA is public (de-identified)

CREATE POLICY "Service role can manage solution registry"
    ON solution_registry FOR ALL
    USING (true)
    WITH CHECK (true);

-- Intent Registry
ALTER TABLE intent_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view intent registry"
    ON intent_registry FOR SELECT
    USING (true);  -- Platform DNA is public (de-identified)

CREATE POLICY "Service role can manage intent registry"
    ON intent_registry FOR ALL
    USING (true)
    WITH CHECK (true);

-- Realm Registry
ALTER TABLE realm_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view realm registry"
    ON realm_registry FOR SELECT
    USING (true);  -- Platform DNA is public (de-identified)

CREATE POLICY "Service role can manage realm registry"
    ON realm_registry FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE solution_registry IS 'Platform DNA: Generalized, curated solutions promoted from Purpose-Bound Outcomes';
COMMENT ON TABLE intent_registry IS 'Platform DNA: Generalized, curated intents promoted from Purpose-Bound Outcomes';
COMMENT ON TABLE realm_registry IS 'Platform DNA: Generalized, curated realms promoted from Purpose-Bound Outcomes';

COMMENT ON COLUMN solution_registry.solution_definition IS 'Generalized solution definition (de-identified, no client context)';
COMMENT ON COLUMN intent_registry.intent_definition IS 'Generalized intent definition (de-identified, no client context)';
COMMENT ON COLUMN realm_registry.realm_definition IS 'Generalized realm definition (de-identified, no client context)';

COMMENT ON COLUMN solution_registry.source_artifact_id IS 'Reference to Purpose-Bound Outcome that was promoted';
COMMENT ON COLUMN intent_registry.source_artifact_id IS 'Reference to Purpose-Bound Outcome that was promoted';
COMMENT ON COLUMN realm_registry.source_artifact_id IS 'Reference to Purpose-Bound Outcome that was promoted';

COMMENT ON COLUMN solution_registry.promoted_by IS 'Curator who approved the promotion';
COMMENT ON COLUMN intent_registry.promoted_by IS 'Curator who approved the promotion';
COMMENT ON COLUMN realm_registry.promoted_by IS 'Curator who approved the promotion';
