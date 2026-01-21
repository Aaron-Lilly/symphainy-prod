# Supabase Key Variable Name Fix

## Issue
Supabase updated their variable naming convention:
- **New**: `SUPABASE_PUBLISHABLE_KEY` and `SUPABASE_SECRET_KEY`
- **Old (deprecated)**: `SUPABASE_KEY`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`

Our codebase was using the old variable names, causing "Invalid API key" errors.

## ✅ Fixes Applied

### 1. `config_helper.py`
- **`get_supabase_anon_key()`**: Already checked `SUPABASE_PUBLISHABLE_KEY` first ✅
- **`get_supabase_service_key()`**: Updated to check `SUPABASE_SECRET_KEY` first, then `SUPABASE_SERVICE_KEY` (fallback)

### 2. `env_contract.py`
- **`SUPABASE_ANON_KEY`**: Already checked `SUPABASE_PUBLISHABLE_KEY` first ✅
- **`SUPABASE_SERVICE_KEY`**: Updated to check `SUPABASE_SECRET_KEY` first, then `SUPABASE_SERVICE_KEY` (fallback)

### 3. `experience_main.py`
- Updated to use `get_supabase_anon_key()` and `get_supabase_service_key()` helpers instead of direct `getattr()`
- Ensures consistent variable lookup across the codebase

## Variable Priority (After Fix)

### Anon/Publishable Key:
1. `SUPABASE_PUBLISHABLE_KEY` (new, preferred) ✅
2. `SUPABASE_ANON_KEY` (legacy, fallback)
3. `SUPABASE_KEY` (generic, fallback)

### Service/Secret Key:
1. `SUPABASE_SECRET_KEY` (new, preferred) ✅
2. `SUPABASE_SERVICE_KEY` (legacy, fallback)
3. `SUPABASE_KEY` (generic, fallback)

## Result
- ✅ Test passed: Workflow Creation Capability test now works
- ✅ Token validation working: Experience API can validate tokens
- ✅ Authentication flow complete: Registration → Token → API calls all working

## Files Modified
1. `symphainy_platform/config/config_helper.py`
2. `symphainy_platform/config/env_contract.py`
3. `experience_main.py`
