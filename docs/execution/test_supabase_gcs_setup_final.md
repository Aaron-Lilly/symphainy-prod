# Test Supabase and GCS Setup - Final ✅

**Status:** ✅ **Both Services Available**  
**Date:** January 2026  
**Goal:** Use hosted test Supabase project and GCS emulator

---

## Summary

Both GCS and Supabase are now available in the test environment:
- ✅ **GCS Emulator** - fake-gcs-server containerized
- ✅ **Supabase** - Hosted test project (no rate limiting)
- ✅ **Test Fixtures** - Load credentials from `.env.secrets`
- ✅ **Realm Tests** - Updated to use Public Works fixture

---

## Configuration

### Supabase (Hosted Test Project)

**Source:** `.env.secrets` file

**Variables Used:**
- `SUPABASE_URL` - Test project URL
- `SUPABASE_PUBLISHABLE_KEY` - Anon key
- `SUPABASE_SECRET_KEY` - Service key
- `SUPABASE_JWKS_URL` - JWKS URL
- `SUPABASE_JWT_ISSUER` - JWT issuer

**Test Project:**
- Project Ref: `eocztpcvzcdqgygxlnqg`
- URL: `https://eocztpcvzcdqgygxlnqg.supabase.co`
- **No rate limiting** ✅

### GCS (Emulator)

**Service:** `gcs-emulator` (fake-gcs-server)
- **Image:** `fsouza/fake-gcs-server:latest`
- **Ports:** 9023 (API), 9024 (HTTP)
- **Backend:** Memory (ephemeral)
- **Test Bucket:** `symphainy-test-bucket` (auto-created)

---

## Test Fixtures

### ✅ `test_supabase` Fixture

**Behavior:**
- Loads credentials from `.env.secrets` automatically
- Uses hosted test Supabase project
- Skips if credentials not found

```python
@pytest.fixture
async def test_supabase(test_infrastructure) -> SupabaseAdapter:
    """Get Supabase adapter connected to hosted test Supabase project."""
```

### ✅ `test_gcs` Fixture

**Behavior:**
- Uses fake-gcs-server emulator
- Sets `STORAGE_EMULATOR_HOST` automatically
- Creates test bucket if needed

```python
@pytest.fixture
async def test_gcs(test_infrastructure) -> GCSAdapter:
    """Get GCS adapter connected to fake-gcs-server emulator."""
```

---

## Docker Compose Services

### Core Services (Containerized)
- ✅ Redis (Port 6380)
- ✅ ArangoDB (Port 8530)
- ✅ Consul (Port 8501)
- ✅ Meilisearch (Port 7701)
- ✅ **GCS Emulator** (Port 9023) ⭐ NEW

### External Services (Hosted)
- ✅ **Supabase** (Hosted test project) ⭐ NEW

---

## Setup Instructions

### 1. Ensure `.env.secrets` Exists

The test fixtures automatically load from `.env.secrets`:

```bash
# Verify .env.secrets exists
ls -la .env.secrets

# Should contain:
# SUPABASE_URL=https://eocztpcvzcdqgygxlnqg.supabase.co
# SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
# SUPABASE_SECRET_KEY=sb_secret_...
# SUPABASE_JWKS_URL=https://...
# SUPABASE_JWT_ISSUER=https://...
```

### 2. Start Test Infrastructure

```bash
# Start containerized services (GCS emulator, Redis, ArangoDB, etc.)
docker-compose -f docker-compose.test.yml up -d

# Verify services are running
docker-compose -f docker-compose.test.yml ps
```

### 3. Set Up Supabase Schema

```bash
# Run migration script to create required tables
python3 tests/infrastructure/setup_supabase_test_schema.py
```

### 4. Run Tests

```bash
# Run all realm tests
pytest tests/integration/realms/ -v

# Run specific realm
pytest tests/integration/realms/test_insights_realm.py -v
```

---

## Files Modified

1. ✅ `docker-compose.test.yml` - Added GCS emulator, removed local Supabase
2. ✅ `tests/infrastructure/test_fixtures.py` - Loads from `.env.secrets`, uses hosted Supabase
3. ✅ `tests/infrastructure/docker_compose_test.py` - Updated default services
4. ✅ `tests/integration/realms/test_insights_realm.py` - Updated to use Public Works

---

## Key Benefits

1. **Simpler Setup** ✅
   - No complex local Supabase stack
   - Uses existing hosted test project

2. **No Rate Limiting** ✅
   - Test Supabase project has no rate limits
   - Perfect for integration tests

3. **Automatic Credential Loading** ✅
   - Loads from `.env.secrets` automatically
   - No manual configuration needed

4. **Production-Like Testing** ✅
   - Real Supabase (hosted)
   - Real GCS behavior (emulator)

---

**GCS and Supabase Ready! Tests Can Now Run Without Skipping** 🚀
