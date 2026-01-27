#!/bin/bash
set -e

# Get script directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get project root (parent of scripts directory)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Docker Cleanup Script ==="
echo "Project root: $PROJECT_ROOT"

echo "Current Docker disk usage:"
docker system df

echo ""
echo "Stopping all containers..."
docker-compose down

echo ""
echo "Cleaning unused containers, networks, and images..."
docker system prune -a -f

echo ""
echo "Cleaning unused volumes..."
docker volume prune -f

echo ""
echo "Cleaning build cache..."
docker builder prune -a -f

echo ""
echo "Final disk usage:"
docker system df

echo ""
echo "Overall disk space:"
df -h | head -3

echo ""
echo "=== Cleanup Complete ==="
