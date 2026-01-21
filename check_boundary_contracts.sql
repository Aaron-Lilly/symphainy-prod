-- Check if boundary contracts were created
SELECT 
    contract_id,
    contract_status,
    materialization_allowed,
    external_source_identifier,
    created_at
FROM data_boundary_contracts
ORDER BY created_at DESC
LIMIT 5;
