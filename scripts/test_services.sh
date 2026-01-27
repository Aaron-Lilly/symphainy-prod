#!/bin/bash

# Get script directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get project root (parent of scripts directory)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Service Health Check ==="
echo "Project root: $PROJECT_ROOT"

echo "Container Status:"
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Service HTTP Status Checks:"
echo "Frontend (via Traefik): $(curl -s -o /dev/null -w "%{http_code}" http://35.215.64.103 2>/dev/null || echo 'FAIL')"
echo "Runtime Health: $(curl -s -o /dev/null -w "%{http_code}" http://35.215.64.103:8000/health 2>/dev/null || echo 'FAIL')"
echo "Experience Health: $(curl -s -o /dev/null -w "%{http_code}" http://35.215.64.103:8001/health 2>/dev/null || echo 'FAIL')"
echo "Traefik Dashboard: $(curl -s -o /dev/null -w "%{http_code}" http://35.215.64.103:8080 2>/dev/null || echo 'FAIL')"

echo ""
echo "Quick logs check (last 10 lines from key services):"
echo ""
echo "=== FRONTEND LOGS ==="
docker-compose logs --tail=10 frontend 2>/dev/null || echo "Frontend not running"

echo ""
echo "=== EXPERIENCE LOGS ==="
docker-compose logs --tail=10 experience 2>/dev/null || echo "Experience not running"

echo ""
echo "=== RUNTIME LOGS ==="
docker-compose logs --tail=10 runtime 2>/dev/null || echo "Runtime not running"

echo ""
echo "=== Health Check Complete ==="
