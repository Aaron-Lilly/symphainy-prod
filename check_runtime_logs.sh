#!/bin/bash
# Check runtime container logs
# Usage: ./check_runtime_logs.sh

set -e

# Ensure we're in the project root
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this from the project root."
    exit 1
fi

echo "🔍 Runtime Container Status:"
echo "================================"
docker-compose ps runtime

echo ""
echo "📋 Runtime Container Logs (last 100 lines):"
echo "================================"
docker-compose logs --tail=100 runtime

echo ""
echo "📋 Runtime Container Logs (all, with timestamps):"
echo "================================"
docker logs symphainy-runtime --tail=200 2>&1

echo ""
echo "🔍 Runtime Container Details:"
echo "================================"
docker inspect symphainy-runtime --format='{{.State.Status}} - {{.State.Error}}' 2>&1 || echo "Container may not exist"

echo ""
echo "✅ Log check complete!"
