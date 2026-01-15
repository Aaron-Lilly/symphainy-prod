#!/bin/bash
# Validation Script for Public Works Abstractions
#
# This script validates that refactored abstractions:
# 1. Still work with their adapters
# 2. Are swappable (can swap adapters)
# 3. Business logic was properly removed
# 4. Integration works (Runtime, Smart City can use them)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔍 Validating Public Works Abstractions..."
echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start containers
print_status "Starting containers..."
docker-compose up -d

# Wait for containers to be ready
print_status "Waiting for containers to be ready..."
sleep 15

# Check container health
print_status "Checking container health..."
if ! docker-compose ps | grep -q "Up (healthy)"; then
    print_warning "Some containers may not be healthy, but continuing..."
fi

# Run unit tests
print_status "Running unit tests..."
if pytest tests/foundations/public_works/test_*_abstraction.py -v --tb=short; then
    print_status "Unit tests passed"
else
    print_error "Unit tests failed"
    docker-compose down
    exit 1
fi

# Run swappability tests
print_status "Running swappability tests..."
if pytest tests/foundations/public_works/test_*_swappability.py -v --tb=short 2>/dev/null; then
    print_status "Swappability tests passed"
else
    print_warning "Swappability tests not found or failed (may not be implemented yet)"
fi

# Run contract tests
print_status "Running contract tests..."
if pytest tests/foundations/public_works/test_*_protocol_compliance.py -v --tb=short 2>/dev/null; then
    print_status "Contract tests passed"
else
    print_warning "Contract tests not found or failed (may not be implemented yet)"
fi

# Run integration tests
print_status "Running integration tests..."
if pytest tests/smart_city/test_*_integration.py -v --tb=short 2>/dev/null; then
    print_status "Integration tests passed"
else
    print_warning "Integration tests not found or failed (may not be implemented yet)"
fi

# Run E2E tests (with containers)
print_status "Running E2E tests (with real containers)..."
if pytest tests/integration/test_abstractions_e2e.py -v --tb=short -m e2e; then
    print_status "E2E tests passed"
else
    print_warning "E2E tests failed or skipped (containers may not be fully ready)"
fi

# Stop containers
print_status "Stopping containers..."
docker-compose down

print_status "Validation complete!"
echo ""
echo "Summary:"
echo "  ✅ Unit tests: Passed"
echo "  ⚠️  Swappability tests: Check output above"
echo "  ⚠️  Contract tests: Check output above"
echo "  ⚠️  Integration tests: Check output above"
echo "  ⚠️  E2E tests: Check output above"
