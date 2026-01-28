#!/bin/bash
# Startup script for Symphainy Coexistence Fabric
# Usage: ./startup.sh

set -e

# Ensure we're in the project root (where docker-compose.yml is)
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this from the project root."
    exit 1
fi

echo "🚀 Starting Symphainy Coexistence Fabric..."
echo "Project root: $(pwd)"
echo ""

# Phase 1: Infrastructure
echo "📦 Phase 1: Starting infrastructure services..."
docker-compose up -d redis arango consul
echo "⏳ Waiting for infrastructure to be healthy (60s)..."
sleep 60

# Verify infrastructure
echo "🔍 Verifying infrastructure health..."
docker-compose ps redis arango consul | grep -E "healthy|running" || echo "⚠️  Some infrastructure services may not be healthy yet"

# Phase 2: Application Services
echo ""
echo "🎯 Phase 2: Starting application services..."
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

# Final verification
echo ""
echo "✅ Startup complete! Verifying services..."
sleep 10
docker-compose ps

echo ""
echo "🎉 Symphainy Coexistence Fabric is ready!"
echo ""
echo "   Service Endpoints:"
echo "   - Runtime:    http://localhost:8000/health"
echo "   - Experience: http://localhost:8001/health"
echo "   - Redis:      localhost:6379"
echo "   - ArangoDB:   http://localhost:8529"
echo "   - Consul:     http://localhost:8500"
echo ""
echo "   To run real infrastructure tests:"
echo "   pytest tests/3d/real_infrastructure/ -v -m real_infrastructure"
echo ""
