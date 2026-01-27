#!/bin/bash
# Simple rebuild script - run from project root
# Usage: ./rebuild.sh

set -e

# Ensure we're in the project root (where docker-compose.yml is)
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this from the project root."
    exit 1
fi

echo "🔨 Rebuilding all containers..."
echo "Project root: $(pwd)"
echo ""

# Clean up first (optional - comment out if you don't want cleanup)
read -p "Clean up Docker before rebuilding? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Cleaning up Docker..."
    docker system prune -a -f
    docker volume prune -f
    docker builder prune -a -f
    echo ""
fi

# Stop all containers
echo "🛑 Stopping all containers..."
docker-compose down

# Build all containers
echo ""
echo "🔨 Building all containers (this may take several minutes)..."
docker-compose build

# Start all services
echo ""
echo "🚀 Starting all services..."
docker-compose up -d

# Wait for services
echo ""
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# Show status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Rebuild complete!"
echo ""
echo "🎯 Test your services:"
echo "   Frontend: http://35.215.64.103"
echo "   Runtime: http://35.215.64.103:8000/health"
echo "   Experience: http://35.215.64.103:8001/health"
