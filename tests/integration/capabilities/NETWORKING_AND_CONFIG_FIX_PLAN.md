# Networking and Configuration Fix Plan

## Goals

1. ✅ **Fix Networking**: Resolve DNS/service discovery issues
2. ✅ **Externalize Config**: Prepare for Option C while keeping .env.secrets support
3. ✅ **Keep Telemetry**: All observability services stay (essential)

---

## Issue 1: Networking/DNS Resolution

### Problem
- Runtime container cannot resolve `redis` and `arango` service names
- Error: "Temporary failure in name resolution"

### Root Cause Analysis
- Services are on same network (`symphainy_net`)
- DNS resolution timing issue or service name mismatch
- May need explicit service aliases or health check dependencies

### Fix Strategy

1. **Verify Service Names**
   - Ensure docker-compose service names match what code expects
   - Check if services need explicit aliases

2. **Add Proper Dependencies**
   - Add `depends_on` with `condition: service_healthy` for redis/arango
   - Ensure runtime waits for dependencies to be healthy

3. **Add Health Checks**
   - Verify redis/arango have proper health checks
   - Ensure health checks are working

4. **Fix DNS Resolution**
   - Add explicit service aliases if needed
   - Check network configuration

---

## Issue 2: Configuration Externalization

### Current State
- Services use hardcoded service names (`redis:6379`, `arango:8529`)
- Configuration mixed between docker-compose and code
- `.env.secrets` used for sensitive data (LLM keys, GCS, Supabase)

### Goal
- Support both local (docker) and hosted (Option C) modes
- Keep `.env.secrets` support for tests/prod
- Externalize service URLs via environment variables

### Strategy

1. **Environment Variable Abstraction**
   - Use `REDIS_URL`, `ARANGO_URL`, etc. from environment
   - Support both local (`redis:6379`) and hosted (`upstash.io:6379`) formats
   - Default to docker service names if not set

2. **Configuration Helper**
   - Create/update config helper to:
     - Load `.env.secrets` for sensitive data
     - Support environment variable overrides
     - Provide sensible defaults for local development

3. **Docker Compose Updates**
   - Add environment variables for service URLs
   - Support both local and external service modes
   - Keep `.env.secrets` file support

4. **Test Support**
   - Ensure tests can use `.env.secrets` for real LLM calls
   - Support real Supabase, GCS, etc. in tests
   - Allow override via environment variables

---

## Implementation Plan

### Step 1: Fix Networking (NO FALLBACKS)

1. Check service names in docker-compose.yml
2. Add health check dependencies
3. Verify DNS resolution
4. Test connectivity

### Step 2: Externalize Configuration

1. Create configuration abstraction layer
2. Update docker-compose to use env vars
3. Update code to use config abstraction
4. Ensure .env.secrets still works
5. Test both local and external modes

---

## Files to Modify

1. `docker-compose.yml` - Add health checks, dependencies, env vars
2. Configuration helper - Support env vars + .env.secrets
3. Service initialization - Use config abstraction
4. Tests - Ensure .env.secrets support

---

## Testing

1. Verify DNS resolution works
2. Test with local services (docker)
3. Test with external services (Option C prep)
4. Test with .env.secrets for real LLM/GCS/Supabase
5. Run capability tests to validate
