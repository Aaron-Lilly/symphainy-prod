-- Migration: Create Agentic Telemetry Registry
-- Purpose: Store agent execution logs, tool usage, and health metrics
-- Date: January 2026

-- Agent Execution Log Table
CREATE TABLE IF NOT EXISTS agentic_execution_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    session_id TEXT,
    execution_id TEXT,
    prompt_hash TEXT,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost DECIMAL(10, 6) DEFAULT 0.0,
    latency_ms INTEGER,
    model_name TEXT,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for execution log
CREATE INDEX IF NOT EXISTS idx_agentic_execution_log_agent_id 
    ON agentic_execution_log(agent_id);
CREATE INDEX IF NOT EXISTS idx_agentic_execution_log_tenant_id 
    ON agentic_execution_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agentic_execution_log_session_id 
    ON agentic_execution_log(session_id);
CREATE INDEX IF NOT EXISTS idx_agentic_execution_log_created_at 
    ON agentic_execution_log(created_at);
CREATE INDEX IF NOT EXISTS idx_agentic_execution_log_prompt_hash 
    ON agentic_execution_log(prompt_hash);

-- Agent Tool Usage Log Table
CREATE TABLE IF NOT EXISTS agentic_tool_usage_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    server_name TEXT,
    parameters JSONB,
    result JSONB,
    success BOOLEAN DEFAULT true,
    latency_ms INTEGER,
    tenant_id TEXT NOT NULL,
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for tool usage log
CREATE INDEX IF NOT EXISTS idx_agentic_tool_usage_log_agent_id 
    ON agentic_tool_usage_log(agent_id);
CREATE INDEX IF NOT EXISTS idx_agentic_tool_usage_log_tool_name 
    ON agentic_tool_usage_log(tool_name);
CREATE INDEX IF NOT EXISTS idx_agentic_tool_usage_log_tenant_id 
    ON agentic_tool_usage_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agentic_tool_usage_log_created_at 
    ON agentic_tool_usage_log(created_at);

-- Agent Health Metrics Table
CREATE TABLE IF NOT EXISTS agentic_health_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    health_status JSONB NOT NULL,
    tenant_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for health metrics
CREATE INDEX IF NOT EXISTS idx_agentic_health_metrics_agent_id 
    ON agentic_health_metrics(agent_id);
CREATE INDEX IF NOT EXISTS idx_agentic_health_metrics_tenant_id 
    ON agentic_health_metrics(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agentic_health_metrics_created_at 
    ON agentic_health_metrics(created_at);

-- RLS Policies (Tenant-isolated)
ALTER TABLE agentic_execution_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE agentic_tool_usage_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE agentic_health_metrics ENABLE ROW LEVEL SECURITY;

-- Execution Log Policies
CREATE POLICY "tenant_read_execution_logs" ON agentic_execution_log
    FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id', true)::TEXT);

CREATE POLICY "tenant_insert_execution_logs" ON agentic_execution_log
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::TEXT);

-- Tool Usage Log Policies
CREATE POLICY "tenant_read_tool_usage_logs" ON agentic_tool_usage_log
    FOR SELECT
    USING (tenant_id = current_setting('app.current_tenant_id', true)::TEXT);

CREATE POLICY "tenant_insert_tool_usage_logs" ON agentic_tool_usage_log
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::TEXT);

-- Health Metrics Policies
CREATE POLICY "tenant_read_health_metrics" ON agentic_health_metrics
    FOR SELECT
    USING (
        tenant_id = current_setting('app.current_tenant_id', true)::TEXT
        OR tenant_id IS NULL  -- Platform-wide metrics
    );

CREATE POLICY "tenant_insert_health_metrics" ON agentic_health_metrics
    FOR INSERT
    WITH CHECK (
        tenant_id = current_setting('app.current_tenant_id', true)::TEXT
        OR tenant_id IS NULL  -- Platform-wide metrics
    );

-- Comments
COMMENT ON TABLE agentic_execution_log IS 
    'Agent execution logs - tracks LLM calls, tokens, costs, latency';
COMMENT ON TABLE agentic_tool_usage_log IS 
    'Agent tool usage logs - tracks MCP tool calls and results';
COMMENT ON TABLE agentic_health_metrics IS 
    'Agent health metrics - tracks agent availability and performance';
