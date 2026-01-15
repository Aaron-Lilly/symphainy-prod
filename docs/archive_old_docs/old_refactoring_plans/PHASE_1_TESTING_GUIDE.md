# Phase 1: Security Guard Testing Guide

**Date:** January 2026  
**Status:** ✅ **READY FOR TESTING**  
**Purpose:** Test that new Security Guard implementation works with real Supabase

---

## Quick Start

### 1. Ensure .env.secrets Has Test Credentials

Your `.env.secrets` file (in project root) should have:

```bash
# TEST Supabase Project (preferred - avoids rate limiting)
TEST_SUPABASE_URL="https://your-test-project.supabase.co"
TEST_SUPABASE_ANON_KEY="your-test-anon-key"
TEST_SUPABASE_SERVICE_KEY="your-test-service-key"

# Production Supabase (fallback)
SUPABASE_URL="https://your-production-project.supabase.co"
SUPABASE_ANON_KEY="your-production-anon-key"
SUPABASE_SERVICE_KEY="your-production-service-key"
```

**Important:** Tests prioritize TEST_SUPABASE_* to avoid rate limiting on production.

---

### 2. Run Tests

**Option A: Use Test Runner Script (Recommended)**

```bash
cd /home/founders/demoversion/symphainy_source_code
./tests/integration/smart_city/run_security_guard_tests.sh
```

**Option B: Run with Pytest**

```bash
cd /home/founders/demoversion/symphainy_source_code
pytest tests/integration/smart_city/test_security_guard_e2e.py -v
```

---

## What Gets Tested

### ✅ Authentication Flow
- User signup (creates account in Supabase)
- User login (authenticates with Supabase)
- Token validation
- SecurityContext creation (Platform SDK translation)

### ✅ Authorization Flow
- Permission checking (Authorization Abstraction)
- Role-based access
- Admin override

### ✅ Tenancy Flow
- Tenant assignment (from user_tenants table or metadata)
- Tenant resolution (Platform SDK)
- Tenant isolation (Security Guard Primitive)

### ✅ Full Flow
- Realm → Platform SDK → Runtime → Security Guard Primitive
- Policy evaluation
- Zero-trust enforcement

### ✅ Functionality Comparison
- Equivalent authentication functionality
- Better separation of concerns

---

## Expected Test Results

All tests should **PASS** with real Supabase. Tests verify:

1. ✅ Users can signup and login
2. ✅ SecurityContext is correctly created
3. ✅ Tenants are assigned and resolved
4. ✅ Authorization checks work
5. ✅ Platform SDK prepares runtime contract shape
6. ✅ Security Guard Primitive makes policy decisions
7. ✅ Full flow works end-to-end

---

## Troubleshooting

### Issue: "Supabase configuration not available"

**Solution:** Ensure `.env.secrets` exists in project root with TEST_SUPABASE_* variables.

### Issue: "Rate limiting" errors

**Solution:** Use TEST_SUPABASE_* variables (not production SUPABASE_*). Tests automatically prioritize test project.

### Issue: "User already exists" errors

**Solution:** Tests create unique users (UUID-based), but if you see this, it's OK - tests handle existing users.

### Issue: "python-dotenv not available"

**Solution:** Install with `pip install python-dotenv` or `poetry add python-dotenv`.

---

## Test Output

When tests run successfully, you should see:

```
✅ Loaded .env.secrets from: /path/to/.env.secrets
✅ Using TEST Supabase project (from .env.secrets): https://...
✅ User signup and authentication successful: user_id
✅ User login successful: user_id
✅ Tenant resolution successful: tenant_id=...
✅ Authorization check successful: permissions=[...]
✅ Platform SDK ensure_user_can successful: allowed=True
✅ Security Guard Primitive policy decisions successful
✅ Full flow successful: Realm → Platform SDK → Runtime → Security Guard Primitive
✅ Equivalent authentication functionality verified
✅ Better separation of concerns verified
```

---

## Success Criteria

Tests pass when:
- [x] Users can signup/login with real Supabase
- [x] SecurityContext is correctly created
- [x] Tenants are assigned and resolved
- [x] Authorization checks work
- [x] Platform SDK prepares runtime contract shape
- [x] Security Guard Primitive makes policy decisions
- [x] Full flow works end-to-end
- [x] Equivalent or better functionality than old Security Guard

---

## Next Steps After Tests Pass

Once tests pass, we can:
1. ✅ Proceed with Phase 2 (batch refactor all abstractions)
2. ✅ Proceed with Phase 3 (batch refactor all primitives)
3. ✅ Validate the pattern works for other roles
