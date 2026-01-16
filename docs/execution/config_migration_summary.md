# Config Migration Summary

**Status:** ✅ Complete  
**Created:** January 2026  
**Goal:** Move `/config` to correct location and update imports

---

## Changes Made

### 1. Moved Config Directory ✅

**From:** `/config` (root level)  
**To:** `symphainy_platform/config/`

**Command:**
```bash
mv config symphainy_platform/config
```

---

### 2. Updated Imports ✅

**Files Updated:**
1. `main.py` (line 23)
   - Changed: `from config import get_env_contract`
   - To: `from symphainy_platform.config import get_env_contract`

2. `runtime_main.py` (line 25)
   - Changed: `from config import get_env_contract`
   - To: `from symphainy_platform.config import get_env_contract`

3. `experience_main.py` (line 23)
   - Changed: `from config import get_env_contract`
   - To: `from symphainy_platform.config import get_env_contract`

---

### 3. Updated Seed Script ✅

**File:** `symphainy_platform/scripts/seed_default_guides.py`

**Changes:**
- ✅ Updated path resolution (goes up 2 levels from `scripts/` to project root)
- ✅ Added automatic `.env.secrets` loading
- ✅ Uses `config_helper` functions to find and load `.env.secrets`
- ✅ Better error messages if credentials are missing

**Now the script:**
1. Automatically finds `.env.secrets` in:
   - `symphainy_platform/.env.secrets` (preferred)
   - Project root `.env.secrets` (fallback)
2. Loads environment variables from `.env.secrets`
3. Uses them for Supabase connection
4. Provides helpful error messages if credentials are missing

---

## Verification

✅ **Config Import Test:**
```bash
python3 -c "from symphainy_platform.config import get_env_contract; print('✅ Works')"
```

✅ **Seed Script Import Test:**
```bash
python3 -c "from symphainy_platform.scripts.seed_default_guides import seed_default_guides; print('✅ Works')"
```

---

## Usage

### Running Seed Script (Now Simplified)

**Before (required manual env var setup):**
```bash
export SUPABASE_URL="https://..."
export SUPABASE_SERVICE_KEY="..."
python3 scripts/seed_default_guides.py
```

**After (automatic .env.secrets loading):**
```bash
# Just run it - it will find .env.secrets automatically
python3 symphainy_platform/scripts/seed_default_guides.py
```

**Or from project root:**
```bash
python3 -m symphainy_platform.scripts.seed_default_guides
```

---

## File Structure After Migration

```
symphainy_source_code/
├── symphainy_platform/
│   ├── config/                    ✅ Moved here
│   │   ├── __init__.py
│   │   ├── config_helper.py
│   │   └── env_contract.py
│   └── scripts/
│       └── seed_default_guides.py  ✅ Updated to load .env.secrets
├── main.py                        ✅ Updated import
├── runtime_main.py                ✅ Updated import
└── experience_main.py             ✅ Updated import
```

---

## Next Steps

1. ✅ Config moved and imports updated
2. ✅ Seed script updated to load .env.secrets automatically
3. ⏳ Archive old directories (`/civic_systems`, `/platform/runtime`) - pending user confirmation
4. ⏳ Investigate `/libraries` - pending user decision

---

## Notes

- All entry points now use `symphainy_platform.config`
- Seed script can now run inline without manual env var setup
- `.env.secrets` should be placed in `symphainy_platform/.env.secrets` or project root
