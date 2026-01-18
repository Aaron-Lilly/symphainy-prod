#!/bin/bash
# Rebuild Experience Service and Run Integration Tests
# Run this after Docker cleanup

set -e

echo "============================================================"
echo "Rebuilding Experience Service"
echo "============================================================"

cd /home/founders/demoversion/symphainy_source_code

# Rebuild
echo "Building Experience service..."
docker-compose build experience

# Start service
echo "Starting Experience service..."
docker-compose up -d experience

# Wait for service to be ready
echo "Waiting for Experience service to start (40 seconds)..."
sleep 40

# Check health
echo "Checking health..."
HEALTH=$(curl -s http://localhost:8001/health || echo "FAILED")
if [[ "$HEALTH" == *"healthy"* ]] || [[ "$HEALTH" == *"status"* ]]; then
    echo "✅ Experience service is healthy"
    echo "$HEALTH"
else
    echo "⚠️  Health check response: $HEALTH"
    echo "Checking logs..."
    docker-compose logs experience --tail 30
fi

# Run integration tests
echo ""
echo "============================================================"
echo "Running Integration Tests"
echo "============================================================"
python3 tests/integration/test_auth_and_websocket_inline.py

echo ""
echo "============================================================"
echo "Done!"
echo "============================================================"
