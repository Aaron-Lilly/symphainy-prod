-- ============================================================================
-- Intent Executions Table Migration
-- ============================================================================
-- Purpose: Create intent_executions table for durable, resumable intent context
--          This stores pending intents where ingestion_profile lives
-- Date: January 26, 2026
-- Status: Intent Execution Log Implementation
-- ============================================================================

-- ============================================================================
-- 1. Create intent_executions table
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.intent_executions (
    -- Identity
    intent_id TEXT NOT NULL PRIMARY KEY,
    intent_type TEXT NOT NULL,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'pending',
    
    -- Target artifact (what this intent operates on)
    target_artifact_id TEXT,
    
    -- Intent context (ingestion_profile, parse_options, etc.)
    context JSONB NOT NULL DEFAULT '{}',
    
    -- Ownership
    tenant_id UUID NOT NULL,
    session_id UUID,
    created_by TEXT,
    
    -- Execution tracking
    execution_id TEXT,  -- If executed
    completed_at TIMESTAMP WITH TIME ZONE,
    error TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT intent_executions_status_check CHECK (
        status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled')
    )
) TABLESPACE pg_default;

-- ============================================================================
-- 2. Create indexes for querying
-- ============================================================================

-- Status queries (pending intents for UI)
CREATE INDEX IF NOT EXISTS idx_intent_executions_status 
    ON public.intent_executions (status);

-- Target artifact queries (pending intents for a specific artifact)
CREATE INDEX IF NOT EXISTS idx_intent_executions_target_artifact 
    ON public.intent_executions (target_artifact_id)
    WHERE target_artifact_id IS NOT NULL;

-- Intent type queries
CREATE INDEX IF NOT EXISTS idx_intent_executions_intent_type 
    ON public.intent_executions (intent_type);

-- Tenant + status queries (most common UI query)
CREATE INDEX IF NOT EXISTS idx_intent_executions_tenant_status 
    ON public.intent_executions (tenant_id, status);

-- Context queries (for filtering by ingestion_profile, etc.)
CREATE INDEX IF NOT EXISTS idx_intent_executions_context 
    ON public.intent_executions USING GIN (context);

-- Session queries
CREATE INDEX IF NOT EXISTS idx_intent_executions_session 
    ON public.intent_executions (session_id)
    WHERE session_id IS NOT NULL;

-- ============================================================================
-- 3. Create update trigger function (reuse existing)
-- ============================================================================

-- Function should already exist from artifact_index migration
-- If not, create it
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 4. Create update trigger
-- ============================================================================

DROP TRIGGER IF EXISTS update_intent_executions_updated_at ON public.intent_executions;

CREATE TRIGGER update_intent_executions_updated_at
    BEFORE UPDATE ON public.intent_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 5. Add comments for documentation
-- ============================================================================

COMMENT ON TABLE public.intent_executions IS 
    'Durable intent execution log. Stores pending/resumable intents where ingestion_profile and other context lives.';

COMMENT ON COLUMN public.intent_executions.intent_id IS 
    'Unique intent identifier';

COMMENT ON COLUMN public.intent_executions.intent_type IS 
    'Type of intent: parse_content, extract_embeddings, etc.';

COMMENT ON COLUMN public.intent_executions.status IS 
    'Intent status: pending, in_progress, completed, failed, cancelled';

COMMENT ON COLUMN public.intent_executions.target_artifact_id IS 
    'Artifact this intent operates on (e.g., file_id for parse_content)';

COMMENT ON COLUMN public.intent_executions.context IS 
    'Intent context: ingestion_profile, parse_options, etc. This is where ingestion_profile lives.';

COMMENT ON COLUMN public.intent_executions.execution_id IS 
    'Execution ID if intent has been executed';

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- Next Steps:
-- 1. Implement RegistryAbstraction intent execution methods
-- 2. Update ContentOrchestrator to create pending intents
-- 3. Update ContentOrchestrator to use pending intents when parsing
-- ============================================================================
