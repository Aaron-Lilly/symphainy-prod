#!/bin/bash
# Simple cleanup script - run from project root
# Usage: ./cleanup.sh

set -e

# Ensure we're in the project root
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this from the project root."
    exit 1
fi

echo "🧹 Docker Cleanup"
echo "Project root: $(pwd)"
echo ""

echo "Current Docker disk usage:"
docker system df

echo ""
read -p "Stop all containers first? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "Stopping all containers..."
    docker-compose down
fi

echo ""
read -p "Clean unused containers, networks, and images? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "Cleaning unused containers, networks, and images..."
    docker system prune -a -f
fi

echo ""
read -p "Clean unused volumes? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "Cleaning unused volumes..."
    docker volume prune -f
fi

echo ""
read -p "Clean build cache? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "Cleaning build cache..."
    docker builder prune -a -f
fi

echo ""
echo "Final disk usage:"
docker system df

echo ""
echo "Overall disk space:"
df -h | head -3

echo ""
echo "✅ Cleanup complete!"
