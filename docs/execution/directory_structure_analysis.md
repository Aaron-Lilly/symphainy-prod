# Directory Structure Analysis

**Status:** Critical - Version Control Issues Identified  
**Created:** January 2026  
**Goal:** Identify and resolve duplicate directories at wrong level

---

## Problem Identified

The platform should be built within `symphainy_source_code/symphainy_platform/`, but there are duplicate directories at the root level:

1. **`/civic_systems`** - Older version, missing newer subdirectories
2. **`/platform/runtime`** - Older version of runtime
3. **`/config`** - Used by main entry points
4. **`/libraries`** - Contains policy subdirectory

---

## Analysis Results

### 1. `/civic_systems` vs `symphainy_platform/civic_systems`

**Root Level (`/civic_systems`):**
- Older version
- Missing: `agentic/`, `experience/` subdirectories
- Has: `platform_sdk/platform_sdk.py` (old file)
- Has: `smart_city/` (older structure)

**Correct Location (`symphainy_platform/civic_systems`):**
- ✅ Newer, complete version
- ✅ Has: `agentic/`, `experience/`, `platform_sdk/`, `smart_city/`
- ✅ Has: `guide_registry.py`, `solution_builder.py`, etc. (new files)

**Verdict:** Root-level `/civic_systems` is **OUTDATED** and should be **ARCHIVED**

---

### 2. `/platform/runtime` vs `symphainy_platform/runtime`

**Root Level (`/platform/runtime`):**
- Older version
- Has: `session.py`, `runtime_service.py`, `saga.py`, `wal.py`, `state_surface.py`
- Different `__init__.py` structure (imports old components)

**Correct Location (`symphainy_platform/runtime`):**
- ✅ Newer version
- ✅ Has: `intent_model.py`, `execution_context.py`, `data_brain.py`, etc.
- ✅ Different structure (newer architecture)

**Verdict:** Root-level `/platform/runtime` is **OUTDATED** and should be **ARCHIVED**

---

### 3. `/config`

**Root Level (`/config`):**
- Contains: `config_helper.py`, `env_contract.py`
- **USED BY:** `main.py`, `runtime_main.py`, `experience_main.py`
- Imports: `from config import get_env_contract`

**Correct Location:** Not present in `symphainy_platform/`

**Verdict:** `/config` is **ACTIVE** and **NEEDS TO BE MOVED** to `symphainy_platform/config/`

---

### 4. `/libraries`

**Root Level (`/libraries`):**
- Contains: `policy/` subdirectory
- **USED BY:** Unknown (needs investigation)

**Correct Location:** Not present in `symphainy_platform/`

**Verdict:** `/libraries` needs investigation - may need to be moved or archived

---

## Files Using Root-Level Directories

### Using `/config`:
- ✅ `main.py` - `from config import get_env_contract`
- ✅ `runtime_main.py` - `from config import get_env_contract`
- ✅ `experience_main.py` - `from config import get_env_contract`

### Using `/civic_systems`:
- ⚠️ `tests/integration/smart_city/test_librarian_e2e.py` - Uses old imports
- ⚠️ `archive_v1/` - Uses old imports (already archived)

### Using `/platform`:
- ❌ No active files found using root-level `/platform`

---

## Recommended Actions

### 1. Archive Outdated Directories ✅

**Move to archive:**
```bash
# Archive old civic_systems
mv civic_systems archive_v1/civic_systems_old

# Archive old platform/runtime
mv platform archive_v1/platform_old
```

**Reason:** These are outdated versions that conflict with the correct location.

---

### 2. Move `/config` to Correct Location ✅

**Action:**
```bash
# Move config to symphainy_platform
mv config symphainy_platform/config
```

**Update imports in:**
- `main.py`: `from symphainy_platform.config import get_env_contract`
- `runtime_main.py`: `from symphainy_platform.config import get_env_contract`
- `experience_main.py`: `from symphainy_platform.config import get_env_contract`

**Reason:** Config is actively used and should be part of the platform structure.

---

### 3. Investigate `/libraries` ⚠️

**Action:**
1. Search for imports of `libraries`
2. Determine if it's still used
3. If used: Move to `symphainy_platform/libraries/`
4. If unused: Archive to `archive_v1/libraries_old/`

---

### 4. Update Test Imports ⚠️

**Action:**
Update `tests/integration/smart_city/test_librarian_e2e.py`:
- Change: `from civic_systems.platform_sdk.platform_sdk import PlatformSDK`
- To: `from symphainy_platform.civic_systems.platform_sdk.platform_sdk import PlatformSDK`

(Or check if this test is still valid with new architecture)

---

## Directory Structure After Cleanup

**Correct Structure:**
```
symphainy_source_code/
├── symphainy_platform/          ✅ Correct location
│   ├── civic_systems/          ✅ Complete, up-to-date
│   ├── runtime/                ✅ Complete, up-to-date
│   ├── config/                 ✅ Moved from root
│   ├── libraries/              ⚠️ If needed
│   ├── foundations/
│   ├── realms/
│   └── experience/
├── archive_v1/                 ✅ Archive location
│   ├── civic_systems_old/      ✅ Archived
│   ├── platform_old/           ✅ Archived
│   └── libraries_old/          ⚠️ If archived
├── main.py                     ✅ Updated imports
├── runtime_main.py             ✅ Updated imports
└── experience_main.py          ✅ Updated imports
```

---

## Impact Assessment

### Low Risk:
- Archiving `/civic_systems` - No active imports found (except tests)
- Archiving `/platform/runtime` - No active imports found

### Medium Risk:
- Moving `/config` - Requires updating 3 entry point files
- Updating test imports - May need test updates

### High Risk:
- None identified

---

## Next Steps

1. ✅ **Confirm with user** before making changes
2. ✅ **Move `/config`** to `symphainy_platform/config/`
3. ✅ **Update imports** in main entry points
4. ✅ **Archive** old directories
5. ✅ **Investigate** `/libraries` usage
6. ✅ **Update tests** if needed

---

## Files to Update

### Import Updates Needed:
1. `main.py` - Line 23
2. `runtime_main.py` - Line 25
3. `experience_main.py` - Line 23
4. `tests/integration/smart_city/test_librarian_e2e.py` - Lines 25-27

### Directories to Archive:
1. `civic_systems/` → `archive_v1/civic_systems_old/`
2. `platform/` → `archive_v1/platform_old/`

### Directories to Move:
1. `config/` → `symphainy_platform/config/`

### Directories to Investigate:
1. `libraries/` - Check usage, then move or archive
