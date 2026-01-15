#!/bin/bash
# Security Guard E2E Test Runner
# 
# Runs Security Guard integration tests with real Supabase (TEST project from .env.secrets)
# 
# Usage:
#   ./run_security_guard_tests.sh
#   ./run_security_guard_tests.sh -v  # Verbose
#   ./run_security_guard_tests.sh -k test_user_signup  # Run specific test

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../../.." && pwd )"

echo "=========================================="
echo "Security Guard E2E Test Runner"
echo "=========================================="
echo "Project Root: $PROJECT_ROOT"
echo ""

# Check if .env.secrets exists
ENV_SECRETS="$PROJECT_ROOT/.env.secrets"
if [ ! -f "$ENV_SECRETS" ]; then
    echo "⚠️  WARNING: .env.secrets not found at $ENV_SECRETS"
    echo "   Tests will use environment variables or skip"
    echo ""
else
    echo "✅ Found .env.secrets at $ENV_SECRETS"
    echo "   Will load TEST_SUPABASE_* variables to avoid rate limiting"
    echo ""
fi

# Change to project root
cd "$PROJECT_ROOT"

# Run tests
echo "Running Security Guard E2E tests..."
echo ""

pytest tests/integration/smart_city/test_security_guard_e2e.py "$@"

echo ""
echo "=========================================="
echo "Tests Complete"
echo "=========================================="
