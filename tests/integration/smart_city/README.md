# Security Guard Integration Tests

## Overview

These tests validate that the new Security Guard implementation works with real Supabase and has equivalent or better functionality than the old implementation.

## Prerequisites

### Environment Variables (from .env.secrets)

**IMPORTANT:** Tests automatically load `.env.secrets` from project root and prioritize **TEST_SUPABASE_*** variables to avoid rate limiting on production.

Your `.env.secrets` file should contain:

```bash
# TEST Supabase Project (preferred - avoids rate limiting)
TEST_SUPABASE_URL="https://your-test-project.supabase.co"
TEST_SUPABASE_ANON_KEY="your-test-anon-key"
TEST_SUPABASE_SERVICE_KEY="your-test-service-key"  # Optional but recommended

# Production Supabase (fallback - may have rate limiting)
SUPABASE_URL="https://your-production-project.supabase.co"
SUPABASE_ANON_KEY="your-production-anon-key"
SUPABASE_SERVICE_KEY="your-production-service-key"
```

**Priority:** Tests use TEST_SUPABASE_* first (to avoid rate limiting), then fall back to SUPABASE_* if test credentials not available.

### Supabase Setup

1. **Create a Supabase project** (or use existing test project)
2. **Enable Authentication** in Supabase dashboard
3. **Create `user_tenants` table** (if not exists):
   ```sql
   CREATE TABLE IF NOT EXISTS user_tenants (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     user_id UUID NOT NULL REFERENCES auth.users(id),
     tenant_id UUID NOT NULL,
     roles TEXT[],
     permissions TEXT[],
     created_at TIMESTAMP DEFAULT NOW()
   );
   ```
4. **Enable Row Level Security (RLS)** if needed

## Running Tests

### Option 1: Use Test Runner Script (Recommended)

```bash
cd /home/founders/demoversion/symphainy_source_code
./tests/integration/smart_city/run_security_guard_tests.sh
```

### Option 2: Run with Pytest Directly

```bash
cd /home/founders/demoversion/symphainy_source_code
pytest tests/integration/smart_city/test_security_guard_e2e.py -v
```

### Run Specific Test

```bash
pytest tests/integration/smart_city/test_security_guard_e2e.py::TestSecurityGuardE2E::test_user_signup_and_authentication -v
```

### Run with Verbose Output

```bash
pytest tests/integration/smart_city/test_security_guard_e2e.py -v -s
```

**Note:** Tests automatically load `.env.secrets` and use TEST_SUPABASE_* variables to avoid rate limiting.

## Test Coverage

### Authentication Flow
- ✅ User signup
- ✅ User login
- ✅ Token validation
- ✅ SecurityContext creation

### Authorization Flow
- ✅ Permission checking
- ✅ Role-based access
- ✅ Admin override

### Tenancy Flow
- ✅ Tenant assignment
- ✅ Tenant resolution
- ✅ Tenant isolation

### Full Flow
- ✅ Realm → Platform SDK → Runtime → Security Guard Primitive
- ✅ Policy evaluation
- ✅ Zero-trust enforcement

## Expected Results

All tests should pass with real Supabase. If tests fail:

1. **Check Supabase credentials** - Verify environment variables are set correctly
2. **Check Supabase project** - Ensure authentication is enabled
3. **Check database tables** - Ensure `user_tenants` table exists
4. **Check network** - Ensure you can reach Supabase API

## Notes

- Tests create unique users for each run (using UUID)
- Tests clean up after themselves (users remain in Supabase but are isolated)
- Tests use real Supabase - no mocks
- Tests validate equivalent or better functionality than old Security Guard
