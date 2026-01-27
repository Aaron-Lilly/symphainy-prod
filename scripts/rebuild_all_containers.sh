#!/bin/bash
set -e

# Get script directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get project root (parent of scripts directory)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Full Container Rebuild Script ==="
echo "This will rebuild and start ALL containers with fixes applied"
echo "Project root: $PROJECT_ROOT"

echo ""
echo "Step 1: Checking disk space..."
df -h | head -3
docker system df

echo ""
echo "Step 2: Stopping all containers..."
docker-compose down

echo ""
echo "Step 3: Building ALL containers (this may take several minutes)..."
echo "Building infrastructure services..."
docker-compose build arango redis consul

echo "Building runtime and experience services..."
docker-compose build runtime experience

echo "Building realms service..."
docker-compose build realms

echo "Building frontend with fixes..."
docker-compose build frontend

echo "Building monitoring services..."
docker-compose build prometheus grafana tempo otel-collector

echo ""
echo "Step 4: Starting ALL services..."
docker-compose up -d

echo ""
echo "Step 5: Waiting for services to start (30 seconds)..."
sleep 30

echo ""
echo "Step 6: Checking service status..."
docker-compose ps

echo ""
echo "Step 7: Testing service health..."
echo "Frontend: $(curl -s -o /dev/null -w "%{http_code}" http://35.215.64.103 2>/dev/null || echo 'FAIL')"
echo "Runtime: $(curl -s -o /dev/null -w "%{http_code}" http://35.215.64.103:8000/health 2>/dev/null || echo 'FAIL')"
echo "Experience: $(curl -s -o /dev/null -w "%{http_code}" http://35.215.64.103:8001/health 2>/dev/null || echo 'FAIL')"
echo "Traefik Dashboard: $(curl -s -o /dev/null -w "%{http_code}" http://35.215.64.103:8080 2>/dev/null || echo 'FAIL')"

echo ""
echo "Step 8: Final status check..."
echo "Services running:"
docker-compose ps --filter "status=running" --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=== Rebuild Complete ==="
echo ""
echo "🎯 READY FOR TESTING:"
echo "1. Frontend: http://35.215.64.103"
echo "2. Try logging in - should see error messages for invalid credentials"
echo "3. After valid login - should see no WebSocket 403 errors"
echo "4. Navigation should work between pillars"
echo ""
echo "✅ All authentication fixes have been deployed!"
