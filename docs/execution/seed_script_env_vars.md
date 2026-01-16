# Seed Script Environment Variables

**Updated:** January 2026  
**Purpose:** Document correct environment variable names for seed_default_guides.py

---

## Required Environment Variables

The seeding script uses these variable names from `.env.secrets`:

### 1. `SUPABASE_URL` ✅
- **Purpose:** Supabase project URL
- **Example:** `https://your-project.supabase.co`
- **Required:** Yes

### 2. `SUPABASE_SECRET_KEY` ✅
- **Purpose:** Supabase service/secret key for admin operations
- **Note:** This is the service key (not the anon/publishable key)
- **Required:** Yes
- **Fallback:** Script will also check `SUPABASE_SERVICE_KEY` (legacy) if `SUPABASE_SECRET_KEY` is not found

---

## Optional Environment Variables

These are available in `.env.secrets` but not required for seeding:

### 3. `SUPABASE_PUBLISHABLE_KEY`
- **Purpose:** Supabase publishable/anon key (for client-side operations)
- **Not used by:** Seed script (uses secret key instead)

### 4. `SUPABASE_JWKS_URL`
- **Purpose:** Supabase JWKS URL for JWT validation
- **Not used by:** Seed script

### 5. `SUPABASE_JWT_ISSUER`
- **Purpose:** Supabase JWT issuer
- **Not used by:** Seed script

### 6. `DATABASE_URL`
- **Purpose:** Direct PostgreSQL connection URL
- **Not used by:** Seed script (uses Supabase REST API via adapter)

---

## Variable Name Changes

**Old (incorrect):**
- `SUPABASE_SERVICE_KEY` ❌

**New (correct):**
- `SUPABASE_SECRET_KEY` ✅

**Note:** The script still supports `SUPABASE_SERVICE_KEY` as a fallback for backward compatibility, but `SUPABASE_SECRET_KEY` is preferred.

---

## Example .env.secrets

```bash
# Required for seeding
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=your-service-role-key-here

# Optional (available but not used by seed script)
SUPABASE_PUBLISHABLE_KEY=your-anon-key-here
SUPABASE_JWKS_URL=https://your-project.supabase.co/.well-known/jwks.json
SUPABASE_JWT_ISSUER=https://your-project.supabase.co
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
```

---

## Script Behavior

1. **Automatic Loading:** Script automatically finds and loads `.env.secrets` from:
   - `symphainy_platform/.env.secrets` (preferred)
   - Project root `.env.secrets` (fallback)

2. **Variable Resolution:**
   - First checks environment variables (already loaded from `.env.secrets`)
   - Uses `SUPABASE_SECRET_KEY` (preferred)
   - Falls back to `SUPABASE_SERVICE_KEY` (legacy support)

3. **Error Messages:**
   - Clear error messages if variables are missing
   - Lists expected variable names

---

## Usage

```bash
# Just run it - variables are loaded automatically from .env.secrets
python3 symphainy_platform/scripts/seed_default_guides.py
```

The script will:
1. ✅ Find `.env.secrets` automatically
2. ✅ Load `SUPABASE_URL` and `SUPABASE_SECRET_KEY`
3. ✅ Connect to Supabase
4. ✅ Seed 3 default guides

---

## Troubleshooting

### Error: "SUPABASE_URL must be set"
- **Solution:** Ensure `SUPABASE_URL` is in `.env.secrets`
- **Check:** File location (`symphainy_platform/.env.secrets` or project root)

### Error: "SUPABASE_SECRET_KEY must be set"
- **Solution:** Ensure `SUPABASE_SECRET_KEY` is in `.env.secrets`
- **Note:** This is the service key (not the anon/publishable key)
- **Fallback:** Script will also check `SUPABASE_SERVICE_KEY` if present

### Script can't find .env.secrets
- **Solution:** Place `.env.secrets` in:
  - `symphainy_platform/.env.secrets` (preferred)
  - Project root `.env.secrets` (fallback)
