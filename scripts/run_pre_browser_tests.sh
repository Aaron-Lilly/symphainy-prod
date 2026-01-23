#!/bin/bash
# run_pre_browser_tests.sh - Execute pre-browser testing strategy
# Usage: ./scripts/run_pre_browser_tests.sh [--phase N] [--verbose] [--skip-startup]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Parse arguments
PHASE=""
VERBOSE=""
SKIP_STARTUP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --phase)
            PHASE="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        --skip-startup)
            SKIP_STARTUP=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--phase N] [--verbose] [--skip-startup]"
            exit 1
            ;;
    esac
done

# Create results directory
RESULTS_DIR="$PROJECT_ROOT/docs/test_results"
mkdir -p "$RESULTS_DIR"
RESULTS_FILE="$RESULTS_DIR/$(date +%Y%m%d_%H%M%S)_test_results.md"

# Function to print section header
print_section() {
    echo ""
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Function to print test header
print_test() {
    echo -e "${BOLD}${BLUE}🧪 Testing: $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print failure
print_failure() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to run tests and capture results
run_test_suite() {
    local test_path="$1"
    local test_name="$2"
    local phase="$3"
    
    print_test "$test_name"
    
    if python3 -m pytest "$test_path" $VERBOSE --tb=short 2>&1 | tee -a "$RESULTS_FILE"; then
        print_success "$test_name passed"
        return 0
    else
        print_failure "$test_name failed"
        echo "## Test Failed: $test_name" >> "$RESULTS_FILE"
        echo "**Path:** \`$test_path\`" >> "$RESULTS_FILE"
        echo "**Phase:** $phase" >> "$RESULTS_FILE"
        echo "" >> "$RESULTS_FILE"
        return 1
    fi
}

# Initialize results file
cat > "$RESULTS_FILE" << EOF
# Test Execution Results

**Date:** $(date)
**Phase:** ${PHASE:-All}
**Status:** Running

## Test Execution Log

EOF

print_section "Pre-Browser Testing Strategy Execution"

# Phase 0: Startup (if not skipped)
if [ "$SKIP_STARTUP" = false ]; then
    print_section "Phase 0: Service Startup"
    
    print_test "Starting all services"
    if ./scripts/startup.sh 2>&1 | tee -a "$RESULTS_FILE"; then
        print_success "Services started"
    else
        print_failure "Service startup failed"
        exit 1
    fi
    
    # Wait for services to be ready
    print_test "Waiting for services to be healthy (60s)..."
    sleep 60
    
    # Verify services are up
    print_test "Verifying service health"
    if docker-compose ps | grep -q "healthy\|running"; then
        print_success "Services are healthy"
    else
        print_warning "Some services may not be healthy yet"
    fi
fi

# Phase 1: Foundation
if [ -z "$PHASE" ] || [ "$PHASE" = "1" ]; then
    print_section "Phase 1: Infrastructure Health & Connectivity (Foundation)"
    
    PHASE1_PASSED=0
    PHASE1_FAILED=0
    
    # Test 1.1: Service startup
    if run_test_suite "tests/smoke/test_service_startup.py" "Service Startup" "1.1"; then
        ((PHASE1_PASSED++))
    else
        ((PHASE1_FAILED++))
    fi
    
    # Test 1.2: Infrastructure health
    if run_test_suite "tests/integration/infrastructure/" "Infrastructure Health" "1.2"; then
        ((PHASE1_PASSED++))
    else
        ((PHASE1_FAILED++))
    fi
    
    # Test 1.3: Basic connectivity
    if run_test_suite "tests/integration/test_basic_integration.py" "Basic Connectivity" "1.3"; then
        ((PHASE1_PASSED++))
    else
        ((PHASE1_FAILED++))
    fi
    
    echo "" >> "$RESULTS_FILE"
    echo "## Phase 1 Summary" >> "$RESULTS_FILE"
    echo "- Passed: $PHASE1_PASSED" >> "$RESULTS_FILE"
    echo "- Failed: $PHASE1_FAILED" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"
    
    if [ $PHASE1_FAILED -gt 0 ]; then
        print_warning "Phase 1 had failures. Review results before proceeding."
    fi
fi

# Phase 2: Core Flows
if [ -z "$PHASE" ] || [ "$PHASE" = "2" ]; then
    print_section "Phase 2: Core Flows (API Contracts & Realm Flows)"
    
    PHASE2_PASSED=0
    PHASE2_FAILED=0
    
    # Test 2.1: API contracts
    if run_test_suite "tests/integration/test_basic_integration.py" "API Contracts" "2.1"; then
        ((PHASE2_PASSED++))
    else
        ((PHASE2_FAILED++))
    fi
    
    # Test 2.2: Experience API
    if run_test_suite "tests/integration/experience/" "Experience API" "2.2"; then
        ((PHASE2_PASSED++))
    else
        ((PHASE2_FAILED++))
    fi
    
    # Test 2.3: Realm flows
    if run_test_suite "tests/integration/realms/" "Realm Flows" "2.3"; then
        ((PHASE2_PASSED++))
    else
        ((PHASE2_FAILED++))
    fi
    
    # Test 2.4: Cross-realm flows
    if run_test_suite "tests/integration/test_architecture_integration.py" "Cross-Realm Flows" "2.4"; then
        ((PHASE2_PASSED++))
    else
        ((PHASE2_FAILED++))
    fi
    
    echo "" >> "$RESULTS_FILE"
    echo "## Phase 2 Summary" >> "$RESULTS_FILE"
    echo "- Passed: $PHASE2_PASSED" >> "$RESULTS_FILE"
    echo "- Failed: $PHASE2_FAILED" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"
    
    if [ $PHASE2_FAILED -gt 0 ]; then
        print_warning "Phase 2 had failures. Review results before proceeding."
    fi
fi

# Phase 3: Data & Resilience
if [ -z "$PHASE" ] || [ "$PHASE" = "3" ]; then
    print_section "Phase 3: Data Integrity & Resilience"
    
    PHASE3_PASSED=0
    PHASE3_FAILED=0
    
    # Test 3.1: Data integrity
    if run_test_suite "tests/integration/infrastructure/test_state_abstraction.py" "State Abstraction" "3.1"; then
        ((PHASE3_PASSED++))
    else
        ((PHASE3_FAILED++))
    fi
    
    if run_test_suite "tests/integration/test_artifact_storage_smoke.py" "Artifact Storage" "3.1"; then
        ((PHASE3_PASSED++))
    else
        ((PHASE3_FAILED++))
    fi
    
    if run_test_suite "tests/integration/runtime/test_wal.py" "Write-Ahead Log" "3.1"; then
        ((PHASE3_PASSED++))
    else
        ((PHASE3_FAILED++))
    fi
    
    # Test 3.2: Error handling
    if run_test_suite "tests/integration/test_error_handling_edge_cases.py" "Error Handling" "3.2"; then
        ((PHASE3_PASSED++))
    else
        ((PHASE3_FAILED++))
    fi
    
    echo "" >> "$RESULTS_FILE"
    echo "## Phase 3 Summary" >> "$RESULTS_FILE"
    echo "- Passed: $PHASE3_PASSED" >> "$RESULTS_FILE"
    echo "- Failed: $PHASE3_FAILED" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"
    
    if [ $PHASE3_FAILED -gt 0 ]; then
        print_warning "Phase 3 had failures. Review results before proceeding."
    fi
fi

# Phase 4: Performance
if [ -z "$PHASE" ] || [ "$PHASE" = "4" ]; then
    print_section "Phase 4: Performance & Pressure Tests"
    
    PHASE4_PASSED=0
    PHASE4_FAILED=0
    
    # Test 4.1: Performance
    if run_test_suite "tests/integration/test_performance_load.py" "Performance Tests" "4.1"; then
        ((PHASE4_PASSED++))
    else
        ((PHASE4_FAILED++))
    fi
    
    echo "" >> "$RESULTS_FILE"
    echo "## Phase 4 Summary" >> "$RESULTS_FILE"
    echo "- Passed: $PHASE4_PASSED" >> "$RESULTS_FILE"
    echo "- Failed: $PHASE4_FAILED" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"
    
    if [ $PHASE4_FAILED -gt 0 ]; then
        print_warning "Phase 4 had failures. Review results before proceeding."
    fi
fi

# Phase 5: Security
if [ -z "$PHASE" ] || [ "$PHASE" = "5" ]; then
    print_section "Phase 5: Authentication & Authorization"
    
    PHASE5_PASSED=0
    PHASE5_FAILED=0
    
    # Test 5.1: Security
    if run_test_suite "tests/integration/test_auth_security_comprehensive.py" "Security Tests" "5.1"; then
        ((PHASE5_PASSED++))
    else
        ((PHASE5_FAILED++))
    fi
    
    if run_test_suite "tests/integration/test_auth_and_websocket_inline.py" "Auth & WebSocket" "5.1"; then
        ((PHASE5_PASSED++))
    else
        ((PHASE5_FAILED++))
    fi
    
    echo "" >> "$RESULTS_FILE"
    echo "## Phase 5 Summary" >> "$RESULTS_FILE"
    echo "- Passed: $PHASE5_PASSED" >> "$RESULTS_FILE"
    echo "- Failed: $PHASE5_FAILED" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"
    
    if [ $PHASE5_FAILED -gt 0 ]; then
        print_warning "Phase 5 had failures. Review results before proceeding."
    fi
fi

# Final summary
print_section "Test Execution Complete"

echo "" >> "$RESULTS_FILE"
echo "## Final Summary" >> "$RESULTS_FILE"
echo "**Completed:** $(date)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "Results saved to: \`$RESULTS_FILE\`" >> "$RESULTS_FILE"

print_success "Test execution complete!"
print_success "Results saved to: $RESULTS_FILE"

# Display summary
echo ""
echo -e "${BOLD}Summary:${NC}"
echo "  Results file: $RESULTS_FILE"
echo ""
echo "Review the results file for detailed test output and any failures."
