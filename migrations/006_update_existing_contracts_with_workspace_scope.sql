-- Migration: Update existing boundary contracts with workspace scope
-- Date: January 2026
-- Purpose: Add workspace scope to existing boundary contracts created before scope support
-- Breaking Change: No - Adds scope to existing contracts

-- Update existing boundary contracts to have workspace scope
-- This ensures all contracts have proper scope for workspace filtering
UPDATE data_boundary_contracts
SET 
    materialization_scope = jsonb_build_object(
        'user_id', user_id,
        'scope_type', 'workspace'
    ),
    reference_scope = jsonb_build_object(
        'users', jsonb_build_array(user_id),
        'scope_type', 'workspace'
    )
WHERE 
    materialization_scope IS NULL 
    OR materialization_scope = '{}'::jsonb
    OR reference_scope IS NULL
    OR reference_scope = '{}'::jsonb;

-- Update existing project_files (materializations) to link to boundary contracts
-- For files that don't have boundary_contract_id yet, create default contracts
INSERT INTO data_boundary_contracts (
    tenant_id,
    user_id,
    external_source_type,
    external_source_identifier,
    external_source_metadata,
    access_granted,
    access_granted_at,
    access_granted_by,
    access_reason,
    materialization_allowed,
    materialization_type,
    materialization_backing_store,
    materialization_policy_basis,
    materialization_scope,
    reference_scope,
    contract_status,
    activated_at,
    created_by,
    contract_terms
)
SELECT DISTINCT
    pf.tenant_id,
    pf.user_id,
    'file' as external_source_type,
    COALESCE(pf.file_path, pf.uuid::text) as external_source_identifier,
    jsonb_build_object(
        'ui_name', pf.ui_name,
        'file_type', pf.file_type,
        'mime_type', pf.mime_type,
        'ingestion_type', pf.ingestion_type,
        'legacy_migration', true
    ) as external_source_metadata,
    true as access_granted,
    pf.created_at as access_granted_at,
    'legacy_migration' as access_granted_by,
    'Legacy data - migrated from pre-boundary-contract system' as access_reason,
    true as materialization_allowed,
    'full_artifact' as materialization_type,
    'gcs' as materialization_backing_store,
    'mvp_workspace_policy' as materialization_policy_basis,
    jsonb_build_object(
        'user_id', pf.user_id,
        'scope_type', 'workspace'
    ) as materialization_scope,
    jsonb_build_object(
        'users', jsonb_build_array(pf.user_id),
        'scope_type', 'workspace'
    ) as reference_scope,
    'active' as contract_status,
    pf.created_at as activated_at,
    pf.user_id as created_by,
    jsonb_build_object(
        'legacy', true,
        'migration_date', NOW(),
        'original_ingestion_type', pf.ingestion_type
    ) as contract_terms
FROM project_files pf
WHERE pf.boundary_contract_id IS NULL
    AND pf.deleted = false
    AND NOT EXISTS (
        SELECT 1 FROM data_boundary_contracts dbc
        WHERE dbc.tenant_id = pf.tenant_id
            AND dbc.external_source_identifier = COALESCE(pf.file_path, pf.uuid::text)
            AND dbc.external_source_type = 'file'
    );

-- Update project_files to reference the newly created contracts
UPDATE project_files pf
SET 
    boundary_contract_id = (
        SELECT contract_id 
        FROM data_boundary_contracts dbc
        WHERE dbc.tenant_id = pf.tenant_id
            AND dbc.external_source_identifier = COALESCE(pf.file_path, pf.uuid::text)
            AND dbc.external_source_type = 'file'
            AND dbc.contract_terms->>'legacy' = 'true'
        ORDER BY dbc.created_at DESC
        LIMIT 1
    ),
    representation_type = 'full_artifact',
    materialization_policy_basis = 'mvp_workspace_policy',
    materialization_backing_store = 'gcs',
    source_external = true,
    source_location = pf.file_path,
    source_type = 'file'
WHERE pf.boundary_contract_id IS NULL
    AND pf.deleted = false;

-- Add comment
COMMENT ON TABLE data_boundary_contracts IS 'Data Boundary Contracts - Updated with workspace scope for MVP';
