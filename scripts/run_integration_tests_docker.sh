#!/bin/bash
# Run Integration Tests with Docker Compose
#
# This script:
# 1. Starts the test infrastructure (docker-compose.test.yml)
# 2. Waits for all services to be healthy
# 3. Runs the integration tests
# 4. Optionally tears down infrastructure
#
# Usage:
#   ./scripts/run_integration_tests_docker.sh [--keep-up] [--runtime] [--e2e]
#
# Options:
#   --keep-up   Don't tear down infrastructure after tests
#   --runtime   Include runtime service (slower startup)
#   --e2e       Run full E2E tests (includes frontend, slowest)
#   --verbose   Show more output
#   --help      Show this help message

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
KEEP_UP=false
INCLUDE_RUNTIME=false
INCLUDE_E2E=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --keep-up)
            KEEP_UP=true
            shift
            ;;
        --runtime)
            INCLUDE_RUNTIME=true
            shift
            ;;
        --e2e)
            INCLUDE_E2E=true
            INCLUDE_RUNTIME=true  # E2E implies runtime
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            head -25 "$0" | tail -20
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo ""
echo "=============================================="
echo -e "  ${BLUE}Integration Test Runner${NC}"
echo "=============================================="
echo ""

# Function to cleanup on exit
cleanup() {
    if [ "$KEEP_UP" = false ]; then
        echo -e "\n${YELLOW}Tearing down test infrastructure...${NC}"
        docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true
    else
        echo -e "\n${YELLOW}Leaving infrastructure running (--keep-up)${NC}"
        echo "To stop: docker-compose -f docker-compose.test.yml down -v"
    fi
}

# Trap exit for cleanup
trap cleanup EXIT

# Step 1: Start infrastructure
echo -e "${BLUE}Starting test infrastructure...${NC}"

COMPOSE_PROFILES=""
if [ "$INCLUDE_E2E" = true ]; then
    COMPOSE_PROFILES="--profile e2e"
fi

if [ "$VERBOSE" = true ]; then
    docker-compose -f docker-compose.test.yml $COMPOSE_PROFILES up -d --build
else
    docker-compose -f docker-compose.test.yml $COMPOSE_PROFILES up -d --build 2>&1 | grep -v "^Creating\|^Starting\|^Container"
fi

# Step 2: Wait for services
echo -e "${BLUE}Waiting for services to be healthy...${NC}"

WAIT_MODE="--infra"
if [ "$INCLUDE_RUNTIME" = true ]; then
    WAIT_MODE="--runtime"
fi
if [ "$INCLUDE_E2E" = true ]; then
    WAIT_MODE="--e2e"
fi

./scripts/wait-for-services.sh $WAIT_MODE

# Step 3: Create test bucket in GCS emulator
echo -e "${BLUE}Setting up GCS test bucket...${NC}"
curl -s -X POST "http://localhost:9023/storage/v1/b?project=test-project" \
    -H "Content-Type: application/json" \
    -d '{"name": "symphainy-test-bucket"}' > /dev/null 2>&1 || true

# Step 4: Set environment variables
export TEST_USE_REAL_INFRASTRUCTURE=true
export TEST_REDIS_HOST=localhost
export TEST_REDIS_PORT=6380
export TEST_ARANGO_PORT=8530
export TEST_ARANGO_ROOT_PASSWORD=test_password
export TEST_CONSUL_PORT=8501
export TEST_MEILISEARCH_PORT=7701
export TEST_MEILISEARCH_MASTER_KEY=test_master_key
export TEST_GCS_EMULATOR_PORT=9023
export TEST_GCS_EMULATOR_HOST=http://localhost
export STORAGE_EMULATOR_HOST=http://localhost:9023
export PYTHONPATH="$PROJECT_ROOT"

if [ "$INCLUDE_RUNTIME" = true ]; then
    export TEST_RUNTIME_HOST=localhost
    export TEST_RUNTIME_PORT=8100
fi

if [ "$INCLUDE_E2E" = true ]; then
    export TEST_FRONTEND_HOST=localhost
    export TEST_FRONTEND_PORT=3100
fi

# Step 5: Run tests
echo ""
echo -e "${BLUE}Running integration tests...${NC}"
echo ""

TEST_MARKERS="-m integration"
TEST_DIRS="tests/integration/"

if [ "$INCLUDE_E2E" = true ]; then
    TEST_MARKERS="-m 'integration or e2e'"
    TEST_DIRS="tests/integration/ tests/e2e/"
fi

# Run pytest
if [ "$VERBOSE" = true ]; then
    python3 -m pytest $TEST_DIRS \
        -v \
        --tb=short \
        $TEST_MARKERS \
        --ignore=tests/integration/README.md \
        --ignore=tests/integration/*.md \
        --ignore=tests/e2e/README.md \
        --ignore=tests/e2e/*.md
    TEST_EXIT=$?
else
    python3 -m pytest $TEST_DIRS \
        -v \
        --tb=line \
        $TEST_MARKERS \
        --ignore=tests/integration/README.md \
        --ignore=tests/integration/*.md \
        --ignore=tests/e2e/README.md \
        --ignore=tests/e2e/*.md
    TEST_EXIT=$?
fi

# Step 6: Report results
echo ""
echo "=============================================="

if [ $TEST_EXIT -eq 0 ]; then
    echo -e "${GREEN}All integration tests passed!${NC}"
else
    echo -e "${RED}Some tests failed (exit code: $TEST_EXIT)${NC}"
fi

echo "=============================================="
echo ""

exit $TEST_EXIT
