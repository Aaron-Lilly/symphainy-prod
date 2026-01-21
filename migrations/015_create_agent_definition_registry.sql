-- Migration: Create Agent Definition Registry
-- Purpose: Store agent definitions (Layer 1: Platform DNA - stable identity)
-- Date: January 2026

-- Agent Definition Registry Table
CREATE TABLE IF NOT EXISTS agent_definition_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT UNIQUE NOT NULL,
    agent_type TEXT NOT NULL,
    definition_data JSONB NOT NULL,
    version TEXT DEFAULT '1.0.0',
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_agent_definition_registry_agent_id 
    ON agent_definition_registry(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_definition_registry_agent_type 
    ON agent_definition_registry(agent_type);

-- RLS Policies (Platform-owned, no tenant isolation)
ALTER TABLE agent_definition_registry ENABLE ROW LEVEL SECURITY;

-- Policy: Allow platform users to read all definitions
CREATE POLICY "platform_read_agent_definitions" ON agent_definition_registry
    FOR SELECT
    USING (true);

-- Policy: Allow platform users to insert definitions
CREATE POLICY "platform_insert_agent_definitions" ON agent_definition_registry
    FOR INSERT
    WITH CHECK (true);

-- Policy: Allow platform users to update definitions
CREATE POLICY "platform_update_agent_definitions" ON agent_definition_registry
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- Policy: Allow platform users to delete definitions
CREATE POLICY "platform_delete_agent_definitions" ON agent_definition_registry
    FOR DELETE
    USING (true);

-- Comments
COMMENT ON TABLE agent_definition_registry IS 
    'Agent Definition Registry - Platform-owned, stable agent identity (Layer 1 of 4-layer model)';
COMMENT ON COLUMN agent_definition_registry.agent_id IS 
    'Unique agent identifier';
COMMENT ON COLUMN agent_definition_registry.agent_type IS 
    'Agent type: stateless, conversational, specialized, orchestrator';
COMMENT ON COLUMN agent_definition_registry.definition_data IS 
    'Full AgentDefinition JSON (constitution, capabilities, permissions, collaboration_profile)';
COMMENT ON COLUMN agent_definition_registry.version IS 
    'Version string for definition';
