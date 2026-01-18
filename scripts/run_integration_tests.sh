#!/bin/bash
# Integration Test Runner - Runs tests in priority order

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
TOTAL=0

run_test() {
    local test_file=$1
    local test_name=$2
    TOTAL=$((TOTAL + 1))
    echo ""
    echo "${BLUE}Running: $test_name${NC}"
    if python3 -m pytest "$test_file" -v --tb=short 2>&1 || python3 "$test_file" 2>&1; then
        echo "${GREEN}✅ PASSED${NC}"
        PASSED=$((PASSED + 1))
    else
        echo "${RED}❌ FAILED${NC}"
        FAILED=$((FAILED + 1))
    fi
}

echo "=== INTEGRATION TEST SUITE ==="
run_test "tests/integration/runtime/test_runtime_spine.py" "Runtime Spine"
run_test "tests/integration/runtime/test_execution_lifecycle.py" "Execution Lifecycle"
run_test "tests/integration/infrastructure/test_state_abstraction.py" "State Abstraction"
run_test "tests/integration/infrastructure/test_transactional_outbox.py" "Transactional Outbox"
run_test "tests/integration/infrastructure/test_arango_adapter.py" "ArangoDB Adapter"
run_test "tests/integration/runtime/test_state_surface.py" "State Surface"
run_test "tests/integration/runtime/test_wal.py" "Write-Ahead Log"
run_test "tests/integration/realms/test_content_realm.py" "Content Realm"
run_test "tests/integration/realms/test_journey_realm.py" "Journey Realm"
run_test "tests/integration/realms/test_insights_realm.py" "Insights Realm"
run_test "tests/integration/realms/test_outcomes_realm.py" "Outcomes Realm"
run_test "tests/integration/experience/test_admin_dashboard.py" "Admin Dashboard"

echo ""
echo "=== SUMMARY ==="
echo "Total: $TOTAL | Passed: $PASSED | Failed: $FAILED"
