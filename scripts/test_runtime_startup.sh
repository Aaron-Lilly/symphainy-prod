#!/bin/bash
# Test Runtime Startup Script
# Tests that Runtime can start up and register Content Realm

set -e

echo "🧪 Testing Runtime Startup..."
echo ""

# Check if containers are running
echo "📦 Checking infrastructure containers..."
docker-compose ps redis arango consul | grep -q "Up" || {
    echo "⚠️ Infrastructure containers not running. Starting them..."
    docker-compose up -d redis arango consul
    echo "⏳ Waiting for containers to be healthy..."
    sleep 10
}

# Start Runtime service
echo "🚀 Starting Runtime service..."
docker-compose up -d runtime

# Wait for Runtime to be healthy
echo "⏳ Waiting for Runtime to be healthy..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Runtime is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Runtime failed to become healthy"
        docker-compose logs runtime
        exit 1
    fi
    sleep 2
done

# Check health endpoint
echo ""
echo "📊 Checking Runtime health..."
HEALTH=$(curl -s http://localhost:8000/health)
echo "$HEALTH" | jq .

# Check if Content Realm is registered
REALMS=$(echo "$HEALTH" | jq -r '.realms // 0')
if [ "$REALMS" -gt 0 ]; then
    echo "✅ Content Realm is registered ($REALMS realm(s))"
else
    echo "❌ Content Realm not registered"
    exit 1
fi

echo ""
echo "✅ Runtime startup test passed!"
