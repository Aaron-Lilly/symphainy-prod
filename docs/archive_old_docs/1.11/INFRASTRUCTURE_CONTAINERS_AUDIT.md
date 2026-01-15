# Infrastructure Containers Audit

**Date:** January 2026  
**Status:** 🔍 **AUDIT IN PROGRESS**

---

## Current State

### ✅ What We Have in docker-compose.yml

1. **Redis** ✅
   - Port: 6379
   - Purpose: Hot state, WAL, cache
   - Status: ✅ Present

2. **ArangoDB** ✅
   - Port: 8529
   - Purpose: Durable/queryable state graph
   - Status: ✅ Present

### ❌ What's Missing

1. **Consul** ❌
   - Port: 8500
   - Purpose: Service discovery, KV store
   - Status: ❌ **MISSING** (we have ConsulAdapter, need Consul)

2. **Traefik** ❌
   - Ports: 80, 443, 8080
   - Purpose: Reverse proxy, load balancer, routing
   - Status: ❌ **MISSING** (mentioned in plan, needed for routing)

3. **OpenTelemetry Collector** ❌
   - Ports: 4317 (gRPC), 4318 (HTTP), 8888 (metrics)
   - Purpose: Observability data collection
   - Status: ❌ **MISSING** (Nurse service needs this)

4. **Tempo** ❌
   - Port: 3200
   - Purpose: Distributed tracing backend
   - Status: ❌ **MISSING** (for distributed tracing)

5. **Grafana** ❌
   - Port: 3000
   - Purpose: Visualization and monitoring
   - Status: ❌ **MISSING** (for observability dashboards)

---

## What We Actually Need

### Required for New Architecture

1. **Redis** ✅ - Hot state, WAL
2. **ArangoDB** ✅ - Durable state graph
3. **Consul** ❌ - Service discovery (we have ConsulAdapter)
4. **Traefik** ❌ - Reverse proxy (for routing platform services)
5. **OpenTelemetry Collector** ❌ - Observability (Nurse service)
6. **Tempo** ❌ - Distributed tracing (for observability)
7. **Grafana** ❌ - Visualization (for monitoring)

### Optional (Can Add Later)

- **Meilisearch** - Search engine (if needed for knowledge discovery)
- **Celery** - Background tasks (if needed for async processing)
- **OPA** - Policy engine (if needed for policy enforcement)

---

## Recommendation

**Add to docker-compose.yml:**
1. Consul (required - we have ConsulAdapter)
2. Traefik (required - for routing)
3. OpenTelemetry Collector (required - for observability)
4. Tempo (required - for distributed tracing)
5. Grafana (required - for visualization)

**Priority:**
- **High:** Consul, Traefik
- **Medium:** OpenTelemetry Collector, Tempo
- **Low:** Grafana (can add later)

---

## Next Steps

1. Update docker-compose.yml with missing infrastructure
2. Update env_contract.py with new environment variables
3. Test infrastructure startup
4. Verify all services can connect
