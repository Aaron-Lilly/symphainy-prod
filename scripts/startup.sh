#!/bin/bash
# startup.sh - Start all Symphainy Platform services in correct order
# Usage: ./scripts/startup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🚀 Starting Symphainy Platform..."
echo ""

# Phase 1: Infrastructure
echo "📦 Phase 1: Starting infrastructure services..."
docker-compose up -d redis arango consul meilisearch tempo
echo "⏳ Waiting for infrastructure to be healthy (60s)..."
sleep 60

# Verify infrastructure
echo "🔍 Verifying infrastructure health..."
docker-compose ps redis arango consul meilisearch tempo | grep -E "healthy|running" || echo "⚠️  Some infrastructure services may not be healthy yet"

# Phase 2: Monitoring
echo ""
echo "📊 Phase 2: Starting monitoring services..."
docker-compose up -d prometheus otel-collector
sleep 10

# Phase 3: Application Services
echo ""
echo "🎯 Phase 3: Starting application services..."
echo "   Starting runtime..."
docker-compose up -d runtime
echo "⏳ Waiting for runtime to be healthy (60s)..."
sleep 60

# Verify runtime
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Runtime is healthy"
else
    echo "   ⚠️  Runtime health check failed, but continuing..."
fi

echo "   Starting experience..."
docker-compose up -d experience
echo "⏳ Waiting for experience to be healthy (60s)..."
sleep 60

# Verify experience
if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "   ✅ Experience is healthy"
else
    echo "   ⚠️  Experience health check failed, but continuing..."
fi

echo "   Starting realms..."
docker-compose up -d realms
sleep 10

# Phase 4: Proxy and UI
echo ""
echo "🌐 Phase 4: Starting proxy and UI..."
docker-compose up -d traefik grafana
sleep 10

# Final verification
echo ""
echo "✅ Startup complete! Verifying services..."
sleep 10
docker-compose ps

echo ""
echo "🎉 Symphainy Platform is ready!"
echo ""
echo "   Service Endpoints:"
echo "   - Runtime:    http://localhost:8000/health"
echo "   - Experience: http://localhost:8001/health"
echo "   - Grafana:    http://localhost:3000 (admin/admin)"
echo "   - Traefik:    http://localhost:8080"
echo "   - Prometheus: http://localhost:9090"
echo ""
