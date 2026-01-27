#!/bin/bash
# Main startup script - run from project root
# Usage: ./startup.sh

set -e

# Ensure we're in the project root (where docker-compose.yml is)
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this from the project root."
    exit 1
fi

echo "🚀 Starting Symphainy Platform..."
echo "Project root: $(pwd)"
echo ""

# Use the existing startup script logic
bash scripts/startup.sh
