# VM Deployment Startup Guide

**Purpose:** Document the proper startup sequence for all Symphainy Platform containers in a VM deployment pattern.

**Last Updated:** January 2026

---

## 📋 Container Overview

### Infrastructure Services (Layer 0 - Adapters)
These services provide the foundational infrastructure that all application services depend on:

1. **redis** - Hot state storage (sessions, cache)
2. **arango** - Durable state storage (execution state, graph data)
3. **consul** - Service discovery and configuration
4. **meilisearch** - Semantic search engine
5. **tempo** - Distributed tracing backend
6. **prometheus** - Metrics collection
7. **grafana** - Metrics visualization
8. **otel-collector** - OpenTelemetry data collection

### Application Services (Platform Layers)
These are the Symphainy Platform services:

1. **runtime** - Runtime Plane (execution core, WAL, Saga, state management)
2. **experience** - Experience Plane (REST APIs, WebSocket, intent submission)
3. **realms** - Realm Plane (domain-specific logic - content, insights, journey, outcomes)

### Proxy/Reverse Proxy
1. **traefik** - Reverse proxy and load balancer

---

## 🚀 Startup Sequence

### Phase 1: Infrastructure Services (Start First)

These must be healthy before any application services can start:

```bash
# Start core infrastructure
docker-compose up -d redis arango consul meilisearch tempo

# Wait for health checks (typically 30-60 seconds)
docker-compose ps

# Verify all are healthy
docker-compose ps redis arango consul meilisearch tempo
```

**Expected Status:** All should show `healthy` status

**Dependencies:**
- `runtime` depends on: `redis`, `arango`, `consul` (all must be healthy)
- `experience` depends on: `redis`, `arango`, `consul` (all must be healthy)
- `realms` depends on: `redis`, `arango`, `consul` (all must be healthy)

### Phase 2: Monitoring Infrastructure

```bash
# Start monitoring services (depend on tempo)
docker-compose up -d prometheus otel-collector

# Wait for startup
sleep 10

# Verify
docker-compose ps prometheus otel-collector
```

**Dependencies:**
- `otel-collector` depends on: `tempo`
- `grafana` depends on: `prometheus`, `tempo`

### Phase 3: Application Services (Start in Order)

#### 3.1 Runtime Service (Must Start First)

The Runtime Plane is the execution core - all other application services depend on it:

```bash
# Start runtime (waits for redis, arango, consul to be healthy)
docker-compose up -d runtime

# Wait for runtime to be healthy (typically 30-60 seconds)
docker-compose ps runtime

# Verify runtime is healthy
curl http://localhost:8000/health
```

**Expected Status:** `healthy`  
**Health Check:** `http://localhost:8000/health` should return `200 OK`

**Dependencies:**
- `experience` depends on: `runtime` (must be healthy)
- `realms` depends on: `runtime` (must be started)
- `traefik` depends on: `runtime`

#### 3.2 Experience Service (Depends on Runtime)

```bash
# Start experience (waits for runtime to be healthy)
docker-compose up -d experience

# Wait for startup (typically 30-60 seconds)
docker-compose ps experience

# Verify experience is healthy
curl http://localhost:8001/health
```

**Expected Status:** `healthy`  
**Health Check:** `http://localhost:8001/health` should return `200 OK`

**Dependencies:**
- `traefik` depends on: `experience`

#### 3.3 Realms Service (Depends on Runtime)

```bash
# Start realms (waits for runtime to be started)
docker-compose up -d realms

# Wait for startup
docker-compose ps realms
```

**Expected Status:** `running` (may not have health check)

### Phase 4: Proxy and Monitoring UI

#### 4.1 Traefik (Reverse Proxy)

```bash
# Start traefik (depends on runtime and experience)
docker-compose up -d traefik

# Verify
docker-compose ps traefik
```

**Expected Status:** `running`  
**Access:** `http://localhost:8080` (Traefik dashboard)

#### 4.2 Grafana (Monitoring UI)

```bash
# Start grafana (depends on prometheus and tempo)
docker-compose up -d grafana

# Wait for startup
sleep 10

# Verify
docker-compose ps grafana
```

**Expected Status:** `running`  
**Access:** `http://localhost:3000` (default: admin/admin)

---

## 🎯 Quick Start (All Services)

For a complete startup of all services in the correct order:

```bash
# Navigate to project root
cd /home/founders/demoversion/symphainy_source_code

# Start all services (docker-compose respects dependencies)
docker-compose up -d

# Wait for all services to be healthy (2-3 minutes)
sleep 180

# Verify all services
docker-compose ps

# Check health endpoints
curl http://localhost:8000/health  # Runtime
curl http://localhost:8001/health # Experience
```

**Note:** Docker Compose will automatically start services in dependency order, but it's recommended to start infrastructure first to avoid timeouts.

---

## 🔍 Verification Checklist

After startup, verify all services:

```bash
# Check all container statuses
docker-compose ps

# Expected output:
# - redis: healthy
# - arango: healthy
# - consul: healthy
# - meilisearch: healthy
# - tempo: running
# - prometheus: running
# - otel-collector: running
# - runtime: healthy
# - experience: healthy
# - realms: running
# - traefik: running
# - grafana: running

# Check application health
curl http://localhost:8000/health  # Runtime
curl http://localhost:8001/health # Experience

# Check infrastructure
curl http://localhost:8500/v1/status/leader  # Consul
curl http://localhost:9090/-/healthy         # Prometheus
```

---

## 🛠️ Troubleshooting

### Issue: Runtime fails to start - "database not found"

**Cause:** ArangoDB database was cleared or not initialized.

**Solution:**
```bash
# ArangoDB should auto-create database on first connection
# If not, manually create it:
docker-compose exec arango arangosh --server.password changeme --javascript.execute-string "db._createDatabase('symphainy_platform')"

# Then restart runtime
docker-compose restart runtime
```

### Issue: Service stuck in "starting" or "unhealthy"

**Solution:**
```bash
# Check logs
docker-compose logs <service-name>

# Common issues:
# - Infrastructure not ready (wait longer)
# - Port conflicts (check ports)
# - Volume permissions (check volumes)
# - Environment variables missing (check .env files)
```

### Issue: Need to restart everything cleanly

**Solution:**
```bash
# Stop all services
docker-compose down

# Remove volumes (⚠️ WARNING: Deletes all data)
docker-compose down -v

# Rebuild and start
docker-compose build --no-cache
docker-compose up -d

# Wait for infrastructure
sleep 60

# Verify
docker-compose ps
```

---

## 📊 Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| redis | 6379 | Hot state storage |
| arango | 8529 | Durable state storage |
| consul | 8500 | Service discovery |
| meilisearch | 7700 | Semantic search |
| tempo | 3200 | Distributed tracing |
| prometheus | 9090 | Metrics |
| grafana | 3000 | Metrics UI |
| otel-collector | 4317, 4318 | OpenTelemetry |
| runtime | 8000 | Runtime Plane API |
| experience | 8001 | Experience Plane API |
| realms | 8002 | Realms API |
| traefik | 8080, 8081 | Reverse proxy |

---

## 🔄 Startup Script

For convenience, create a startup script:

```bash
#!/bin/bash
# startup.sh - Start all Symphainy Platform services

set -e

echo "🚀 Starting Symphainy Platform..."

# Phase 1: Infrastructure
echo "📦 Phase 1: Starting infrastructure services..."
docker-compose up -d redis arango consul meilisearch tempo
echo "⏳ Waiting for infrastructure to be healthy (60s)..."
sleep 60

# Phase 2: Monitoring
echo "📊 Phase 2: Starting monitoring services..."
docker-compose up -d prometheus otel-collector
sleep 10

# Phase 3: Application Services
echo "🎯 Phase 3: Starting application services..."
docker-compose up -d runtime
echo "⏳ Waiting for runtime to be healthy (60s)..."
sleep 60

docker-compose up -d experience
echo "⏳ Waiting for experience to be healthy (60s)..."
sleep 60

docker-compose up -d realms

# Phase 4: Proxy and UI
echo "🌐 Phase 4: Starting proxy and UI..."
docker-compose up -d traefik grafana

# Final verification
echo "✅ Startup complete! Verifying services..."
sleep 10
docker-compose ps

echo ""
echo "🎉 Symphainy Platform is ready!"
echo "   Runtime:    http://localhost:8000/health"
echo "   Experience: http://localhost:8001/health"
echo "   Grafana:    http://localhost:3000"
echo "   Traefik:    http://localhost:8080"
```

Save as `scripts/startup.sh` and make executable:
```bash
chmod +x scripts/startup.sh
./scripts/startup.sh
```

---

## 📝 Notes

1. **Health Checks:** Docker Compose uses health checks to determine when services are ready. Services with `depends_on` with `condition: service_healthy` will wait for dependencies to be healthy before starting.

2. **Startup Time:** Full platform startup typically takes 2-3 minutes:
   - Infrastructure: 30-60 seconds
   - Runtime: 30-60 seconds
   - Experience: 30-60 seconds
   - Other services: 10-30 seconds each

3. **Database Initialization:** ArangoDB should auto-create the database on first connection. If it doesn't, see troubleshooting section.

4. **Environment Variables:** Ensure `.env` files are configured:
   - `symphainy_platform/.env.secrets` - Required for runtime, experience, realms
   - Environment variables in `docker-compose.yml` can be overridden

5. **Volumes:** Data persists in Docker volumes. Use `docker-compose down -v` to clear all data (⚠️ destructive).

---

## 🔗 Related Documentation

- **Architecture Overview:** `docs/architecture/north_star.md`
- **Development Guide:** `docs/00_START_HERE.md`
- **Testing Guide:** `docs/backend_testing_plan.md`
- **API Documentation:** `docs/execution/api_contracts_frontend_integration.md`

---

**Last Updated:** January 2026
