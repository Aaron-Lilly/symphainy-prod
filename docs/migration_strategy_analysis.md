# Migration Strategy Analysis: Existing Schema vs New Architecture

## Current Situation

### Existing Schema (001_create_project_files_schema_enhanced.sql)
- **Purpose**: FMS/file metadata storage solution
- **Status**: Already deployed and in use
- **Key Features**:
  - Comprehensive file metadata (ui_name, file_path, file_type, mime_type, etc.)
  - Processing tracking (processing_status, processing_errors)
  - Lineage tracking (root_file_uuid, parent_file_uuid, lineage_depth)
  - Security/compliance (access_level, permissions, data_classification)
  - **Explicitly removed**: `session_id` column (runtime concept, not persistent)

### New Architecture (003, 004, 005, 006)
- **003**: Creates `data_boundary_contracts` table (NEW table)
- **004**: Adds boundary contract fields to `project_files` (ALTER TABLE)
- **005**: Creates default contracts for existing data
- **006**: Updates existing contracts with workspace scope

## Compatibility Analysis

### ✅ Good News: They're Compatible!

**Migration 004 uses `ADD COLUMN IF NOT EXISTS`**, which means:
- It's designed to work with the existing 001 schema
- It adds new columns without breaking existing functionality
- Existing data remains intact

### Migration Order

1. **001** (if not already run) - Creates base `project_files` table
2. **003** - Creates `data_boundary_contracts` table (NEW, no conflicts)
3. **004** - Adds boundary contract columns to existing `project_files` table
4. **005** - Creates default contracts for existing `project_files` rows
5. **006** - Updates contracts with workspace scope

### Schema Evolution

```
001 (Base Schema)
  ↓
  + 003 (New table: data_boundary_contracts)
  ↓
  + 004 (Add columns to project_files)
  ↓
  = Final Schema (project_files with boundary contract support)
```

## Key Considerations

### 1. session_id Handling ✅ FIXED
- **Issue**: Code was trying to insert `session_id` as a column
- **Solution**: `session_id` is stored in `materialization_scope` JSONB field
- **Status**: Fixed in `register_materialization()` method

### 2. Foreign Key Constraint
- **004** adds: `boundary_contract_id UUID REFERENCES data_boundary_contracts(contract_id)`
- **Requirement**: Must run **003 before 004** (creates referenced table)
- **Nullable**: Column is nullable, so existing rows won't break

### 3. Existing Data
- **005** handles migration of existing `project_files` rows
- Creates default boundary contracts for files without contracts
- Links existing files to contracts

### 4. Backwards Compatibility
- Existing code that queries `project_files` will continue to work
- New columns are nullable, so old queries won't break
- New functionality (boundary contracts) is additive

## Recommended Approach

### Option 1: Incremental Migration (Recommended)
**Use existing 001 schema, add new columns via 004**

**Pros**:
- ✅ No data loss
- ✅ No breaking changes
- ✅ Existing functionality continues to work
- ✅ Can deploy incrementally

**Cons**:
- ⚠️ Some columns may be NULL for existing data (handled by 005)

**Steps**:
1. Keep 001 as-is (already deployed)
2. Run 003 (creates boundary_contracts table)
3. Run 004 (adds columns to project_files)
4. Run 005 (migrates existing data)
5. Run 006 (adds workspace scope)

### Option 2: Full Schema Rebuild (NOT Recommended)
**Drop and recreate project_files with all columns**

**Pros**:
- ✅ Clean schema from scratch

**Cons**:
- ❌ Data loss (unless you backup/restore)
- ❌ Breaking change
- ❌ Requires downtime
- ❌ More complex migration

## What We Need to Do

### ✅ Already Done
1. Fixed `register_materialization()` to not insert `session_id` column
2. Migration 004 uses `ADD COLUMN IF NOT EXISTS` (safe)
3. Migration 005 handles existing data

### ✅ Ready to Proceed
- **No changes needed to 001** - it's the base schema
- **004 will add new columns** to existing table
- **All migrations are compatible**

## Migration Execution Plan

```sql
-- Step 1: Create boundary contracts table (NEW)
-- Run: 003_create_data_boundary_contracts.sql

-- Step 2: Add boundary contract support to project_files (ALTER existing table)
-- Run: 004_add_boundary_contracts_to_materializations.sql

-- Step 3: Migrate existing data (create contracts for existing files)
-- Run: 005_create_default_boundary_contracts_for_existing_data.sql

-- Step 4: Add workspace scope to contracts
-- Run: 006_update_existing_contracts_with_workspace_scope.sql
```

## Verification Queries

After migrations, verify:

```sql
-- Check that new columns exist
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'project_files'
  AND column_name IN ('boundary_contract_id', 'representation_type', 'materialization_scope');

-- Check that boundary_contracts table exists
SELECT COUNT(*) FROM data_boundary_contracts;

-- Check that existing files have contracts
SELECT COUNT(*) FROM project_files WHERE boundary_contract_id IS NOT NULL;
```

## Conclusion

**✅ We can proceed with the new migrations on top of the existing 001 schema.**

The migrations are designed to be additive and non-breaking:
- 003 creates a new table (no conflicts)
- 004 adds columns to existing table (safe with IF NOT EXISTS)
- 005 and 006 migrate existing data

**No changes needed to 001** - it remains the base schema, and the new architecture builds on top of it.
