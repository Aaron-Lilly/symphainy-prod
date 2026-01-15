-- Curator Registries Schema
-- Data-backed catalogs for capabilities, services, agents, contracts
-- Phase 1: Create tables
-- Phase 3: Full implementation

-- Capabilities Table
CREATE TABLE IF NOT EXISTS capabilities (
    capability_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capability_name VARCHAR(255) NOT NULL,
    capability_type VARCHAR(100),          -- service, agent, tool, etc.
    realm VARCHAR(100),                    -- content, insights, operations, solution
    service_name VARCHAR(255),             -- Links to service providing capability
    capability_data JSONB,                -- Flexible structure (contracts, metadata, etc.)
    version VARCHAR(50) DEFAULT '1.0.0',
    tenant_id UUID,
    status VARCHAR(50) DEFAULT 'active',  -- active, deprecated, maintenance, experimental
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(capability_name, version)
);

-- Services Table (projection of Consul + governance)
CREATE TABLE IF NOT EXISTS services (
    service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(255) NOT NULL,
    consul_service_id VARCHAR(255),       -- Link to Consul service
    realm VARCHAR(100),
    service_data JSONB,                   -- Capabilities, contracts, metadata
    version VARCHAR(50) DEFAULT '1.0.0',
    tenant_id UUID,
    status VARCHAR(50) DEFAULT 'active',  -- active, deprecated, maintenance
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(service_name, version)
);

-- Agents Table
CREATE TABLE IF NOT EXISTS agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(255) NOT NULL,
    realm VARCHAR(100),
    mcp_tools JSONB,                       -- List of MCP tool names (not globally registered)
    reasoning_scope VARCHAR(100),          -- grounded, expert, etc.
    agent_data JSONB,                      -- Additional agent metadata
    version VARCHAR(50) DEFAULT '1.0.0',
    tenant_id UUID,
    status VARCHAR(50) DEFAULT 'active',   -- active, deprecated, maintenance, experimental
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(agent_name, version)
);

-- Contracts Table
CREATE TABLE IF NOT EXISTS contracts (
    contract_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(255) NOT NULL,
    contract_type VARCHAR(100),            -- api, capability, etc.
    contract_schema JSONB NOT NULL,        -- OpenAPI, JSON Schema, etc.
    version VARCHAR(50) DEFAULT '1.0.0',
    tenant_id UUID,
    status VARCHAR(50) DEFAULT 'active',  -- active, deprecated, maintenance
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(service_name, contract_type, version)
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_capabilities_name ON capabilities(capability_name);
CREATE INDEX IF NOT EXISTS idx_capabilities_type ON capabilities(capability_type);
CREATE INDEX IF NOT EXISTS idx_capabilities_realm ON capabilities(realm);
CREATE INDEX IF NOT EXISTS idx_capabilities_service ON capabilities(service_name);
CREATE INDEX IF NOT EXISTS idx_capabilities_status ON capabilities(status);
CREATE INDEX IF NOT EXISTS idx_capabilities_jsonb ON capabilities USING GIN(capability_data);

CREATE INDEX IF NOT EXISTS idx_services_name ON services(service_name);
CREATE INDEX IF NOT EXISTS idx_services_consul ON services(consul_service_id);
CREATE INDEX IF NOT EXISTS idx_services_realm ON services(realm);
CREATE INDEX IF NOT EXISTS idx_services_status ON services(status);
CREATE INDEX IF NOT EXISTS idx_services_jsonb ON services USING GIN(service_data);

CREATE INDEX IF NOT EXISTS idx_agents_name ON agents(agent_name);
CREATE INDEX IF NOT EXISTS idx_agents_realm ON agents(realm);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_jsonb ON agents USING GIN(agent_data);
CREATE INDEX IF NOT EXISTS idx_agents_mcp_tools ON agents USING GIN(mcp_tools);

CREATE INDEX IF NOT EXISTS idx_contracts_service ON contracts(service_name);
CREATE INDEX IF NOT EXISTS idx_contracts_type ON contracts(contract_type);
CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);
CREATE INDEX IF NOT EXISTS idx_contracts_jsonb ON contracts USING GIN(contract_schema);

-- Comments
COMMENT ON TABLE capabilities IS 'Capability Registry - Data-backed catalog for capability definitions';
COMMENT ON TABLE services IS 'Service Registry - Projection of Consul (liveness) + governance metadata (meaning)';
COMMENT ON TABLE agents IS 'Agent Registry - Data-backed catalog for agent definitions';
COMMENT ON TABLE contracts IS 'Contract Registry - Data-backed catalog for service contracts';
