#!/bin/bash
# Check logs for all containers
# Usage: ./check_all_logs.sh [service_name]

set -e

# Ensure we're in the project root
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this from the project root."
    exit 1
fi

if [ -z "$1" ]; then
    echo "📋 All Container Status:"
    echo "================================"
    docker-compose ps
    
    echo ""
    echo "📋 Recent Logs for All Services (last 30 lines each):"
    echo "================================"
    docker-compose logs --tail=30
else
    SERVICE=$1
    echo "📋 Logs for $SERVICE (last 100 lines):"
    echo "================================"
    docker-compose logs --tail=100 $SERVICE
    
    echo ""
    echo "📋 Direct Docker Logs for $SERVICE:"
    echo "================================"
    docker logs "symphainy-$SERVICE" --tail=200 2>&1 || docker logs "$SERVICE" --tail=200 2>&1
fi

echo ""
echo "✅ Log check complete!"
