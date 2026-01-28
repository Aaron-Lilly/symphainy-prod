# Symphainy Coexistence Fabric - Startup Guide

## Overview

This guide documents the complete startup process for the Symphainy Coexistence Fabric platform, including all services, containers, and how to access them.

## Architecture

The platform consists of:
- **Infrastructure Services**: Redis, ArangoDB, Consul
- **Backend Services**: Runtime (port 8000), Experience (port 8001)
- **Frontend Service**: Next.js application (port 3000)
- **Edge Router**: Traefik (port 80) - routes all traffic

## Prerequisites

1. Docker and Docker Compose installed
2. `.env.secrets` file in `symphainy_coexistence_fabric/` directory (for LLM API keys, etc.)
3. Frontend code available at `../symphainy-frontend/`

## Quick Start

### 1. Navigate to Project Directory

```bash
cd /home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric
```

### 2. Start All Services

Use the startup script (recommended):

```bash
./startup.sh
```

Or manually with Docker Compose:

```bash
docker-compose up -d
```

### 3. Verify Services

Check service status:

```bash
docker-compose ps
```

All services should show as "healthy" or "running":
- ✅ `symphainy-redis` - healthy
- ✅ `symphainy-arango` - healthy
- ✅ `symphainy-consul` - healthy
- ✅ `symphainy-runtime` - healthy
- ✅ `symphainy-experience` - healthy
- ✅ `symphainy-traefik` - running
- ⚠️ `symphainy-frontend` - may be building (can take 5-10 minutes first time)

### 4. Access the Platform

Once all services are healthy:

- **Frontend UI**: http://35.215.64.103 (routed through Traefik)
- **Traefik Dashboard**: http://35.215.64.103:8080
- **Runtime API**: http://35.215.64.103/api/runtime (via Traefik)
- **Experience API**: http://35.215.64.103/api/sessions (via Traefik)

## Service Details

### Infrastructure Services

#### Redis
- **Container**: `symphainy-redis`
- **Port**: 6379 (exposed for direct access)
- **Health Check**: `redis-cli ping`
- **Data Volume**: `redis_data`

#### ArangoDB
- **Container**: `symphainy-arango`
- **Port**: 8529 (exposed for direct access)
- **Health Check**: `nc -z 127.0.0.1 8529`
- **Default Password**: `test_password` (set via `ARANGO_ROOT_PASSWORD`)
- **Database**: `symphainy_platform` (auto-created)
- **Data Volume**: `arango_data`

#### Consul
- **Container**: `symphainy-consul`
- **Port**: 8500 (exposed for direct access)
- **Health Check**: HTTP check on `/v1/status/leader`
- **UI**: http://35.215.64.103:8500
- **Data Volume**: `consul_data`

### Backend Services

#### Runtime Service
- **Container**: `symphainy-runtime`
- **Port**: 8000 (internal), exposed via Traefik
- **Health Check**: `curl -f http://localhost:8000/health`
- **Traefik Routes**:
  - `/api/runtime/*` (except `/api/runtime/agent`)
  - `/api/intent/*`
  - `/api/session/*`
  - `/api/execution/*`
  - `/api/realms/*`
- **Dockerfile**: `Dockerfile.runtime`

#### Experience Service
- **Container**: `symphainy-experience`
- **Port**: 8001 (internal), exposed via Traefik
- **Health Check**: TCP check on port 8001
- **Traefik Routes**:
  - `/api/sessions/*`
  - `/api/session/*`
  - `/api/intent/*`
  - `/api/ws/*`
  - `/api/admin/*`
  - `/api/auth/*`
  - `/api/runtime/agent/*` (WebSocket)
- **Dockerfile**: `Dockerfile.runtime` (shared with Runtime)

### Frontend Service

#### Frontend (Next.js)
- **Container**: `symphainy-frontend`
- **Port**: 3000 (internal), exposed via Traefik
- **Health Check**: `wget --spider http://localhost:3000`
- **Traefik Route**: All paths NOT starting with `/api` → Frontend
- **Build Context**: `../symphainy-frontend/`
- **Dockerfile**: `Dockerfile` (in frontend directory)
- **Note**: First build can take 5-10 minutes

### Edge Router

#### Traefik
- **Container**: `symphainy-traefik`
- **Ports**: 
  - 80 (HTTP - main entry point)
  - 8080 (Dashboard)
- **Configuration**: Auto-discovers services via Docker labels
- **Dashboard**: http://35.215.64.103:8080

## Traefik Routing Rules

Traefik uses priority-based routing (higher priority = checked first):

1. **Priority 99**: Health checks (`/health`, `/api/health`)
2. **Priority 20**: WebSocket routes (`/api/runtime/agent`)
3. **Priority 10**: API routes (Runtime, Experience)
4. **Priority 1**: Frontend (catch-all for non-API paths)

### Route Examples

- `http://35.215.64.103/` → Frontend (homepage)
- `http://35.215.64.103/api/runtime/health` → Runtime service
- `http://35.215.64.103/api/sessions` → Experience service
- `http://35.215.64.103/api/runtime/agent` → Experience WebSocket

## Environment Variables

Key environment variables (set in `.env.secrets` or `docker-compose.yml`):

```bash
# Infrastructure
REDIS_URL=redis://redis:6379
ARANGO_URL=http://arango:8529
ARANGO_ROOT_PASSWORD=test_password
ARANGO_USERNAME=root
ARANGO_DATABASE=symphainy_platform

# Services
RUNTIME_PORT=8000
EXPERIENCE_PORT=8001
CONSUL_HOST=consul
CONSUL_PORT=8500

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://35.215.64.103
NEXT_PUBLIC_API_BASE=http://35.215.64.103
NEXT_PUBLIC_API_BASE_URL=http://35.215.64.103
NEXT_PUBLIC_FRONTEND_URL=http://35.215.64.103

# CORS
CORS_ALLOWED_ORIGINS=http://35.215.64.103,http://35.215.64.103:3000,http://localhost:3000
```

## Troubleshooting

### Services Not Starting

1. **Check logs**:
   ```bash
   docker-compose logs <service-name>
   ```

2. **Check health status**:
   ```bash
   docker-compose ps
   ```

3. **Rebuild containers** (if code changed):
   ```bash
   docker-compose build <service-name>
   docker-compose up -d <service-name>
   ```

### Port Conflicts

If you see "bind: address already in use":
```bash
# Find process using port
sudo lsof -i :<port>

# Kill process
sudo kill <PID>
```

### Frontend Build Failures

The frontend build can fail due to:
- TypeScript errors (check `next.config.js` - `ignoreBuildErrors: false`)
- Missing dependencies
- Syntax errors in React components

**Quick fix**: Temporarily set `ignoreBuildErrors: true` in `next.config.js` to allow build with warnings.

### ArangoDB Health Check Failing

If ArangoDB shows "unhealthy":
- Wait 30-60 seconds (startup period)
- Check logs: `docker-compose logs arango`
- Verify password matches `ARANGO_ROOT_PASSWORD`

### Traefik Not Routing

1. Check Traefik dashboard: http://35.215.64.103:8080
2. Verify service labels in `docker-compose.yml`
3. Check Traefik logs: `docker-compose logs traefik`
4. Ensure services are healthy before Traefik starts

## Running Tests

### Real Infrastructure Tests

```bash
cd /home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric
python3 -m pytest tests/3d/real_infrastructure/ -v -m real_infrastructure
```

**Prerequisites**: All services must be running and healthy.

**Test Coverage**:
- ✅ Redis connectivity (connection, set/get)
- ✅ ArangoDB connectivity (connection, create/read)
- ✅ Authentication flow
- ✅ File upload
- ✅ File parsing
- ✅ Chat agents (GuideAgent)
- ✅ Navigation
- ✅ LLM integration (if API keys configured)

## Common Commands

### Start Services
```bash
./startup.sh                    # Recommended: phased startup with health checks
docker-compose up -d            # Start all services
docker-compose up -d <service>   # Start specific service
```

### Stop Services
```bash
docker-compose down             # Stop and remove containers
docker-compose stop             # Stop containers (keep data)
docker-compose stop <service>   # Stop specific service
```

### View Logs
```bash
docker-compose logs -f          # Follow all logs
docker-compose logs -f <service> # Follow specific service logs
docker-compose logs --tail=100  # Last 100 lines
```

### Rebuild Services
```bash
docker-compose build            # Rebuild all services
docker-compose build <service>  # Rebuild specific service
docker-compose up -d --build    # Rebuild and start
```

### Check Status
```bash
docker-compose ps               # Service status
docker-compose ps -a            # All containers (including stopped)
docker stats                    # Resource usage
```

### Clean Up
```bash
docker-compose down -v          # Remove containers and volumes (⚠️ deletes data)
docker system prune             # Clean up unused Docker resources
```

## File Structure

```
symphainy_coexistence_fabric/
├── docker-compose.yml          # Service definitions
├── Dockerfile.runtime          # Backend services Dockerfile
├── startup.sh                 # Startup orchestration script
├── .env.secrets               # Environment variables (not in git)
├── tests/
│   └── 3d/
│       └── real_infrastructure/  # Real infrastructure tests
└── symphainy_platform/        # Platform code

../symphainy-frontend/          # Frontend application
├── Dockerfile                  # Frontend Dockerfile
└── ...                        # Next.js application
```

## Next Steps

1. **First Time Setup**:
   - Ensure `.env.secrets` exists with required API keys
   - Run `./startup.sh` and wait for all services to be healthy
   - Access frontend at http://35.215.64.103

2. **Development**:
   - Make code changes
   - Rebuild affected services: `docker-compose build <service>`
   - Restart: `docker-compose up -d <service>`

3. **Testing**:
   - Run real infrastructure tests: `pytest tests/3d/real_infrastructure/`
   - Verify all critical paths work

4. **Production**:
   - Update environment variables for production
   - Ensure proper security (passwords, API keys)
   - Configure firewall rules for port 80

## Notes

- **First Build**: Frontend build takes 5-10 minutes on first run
- **Health Checks**: Services have startup periods (30-40s) before health checks pass
- **Data Persistence**: Redis, ArangoDB, and Consul data persists in Docker volumes
- **Network**: All services communicate via `symphainy_net` bridge network
- **Traefik**: Auto-discovers services via Docker labels - no manual config needed

## Support

For issues:
1. Check service logs: `docker-compose logs <service>`
2. Verify health status: `docker-compose ps`
3. Check Traefik dashboard: http://35.215.64.103:8080
4. Review this guide's troubleshooting section

---

**Last Updated**: January 27, 2026
**Platform Version**: Symphainy Coexistence Fabric
**VM Public IP**: 35.215.64.103
