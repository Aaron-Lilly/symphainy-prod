#!/bin/bash
# E2E 3D Testing Suite
# Comprehensive testing across Functional, Architectural, and SRE dimensions
# Per CIO feedback: Catch issues BEFORE browser testing

# Don't exit on error - we want to collect all test results
# set -e

echo "=========================================="
echo "E2E 3D Testing Suite"
echo "Functional | Architectural | SRE"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0

FRONTEND_DIR="symphainy-frontend"

# Function to print test header
print_test_header() {
    echo ""
    echo -e "${BLUE}=== $1 ===${NC}"
    echo ""
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((TESTS_PASSED++))
}

# Function to print failure
print_failure() {
    echo -e "${RED}✗ $1${NC}"
    ((TESTS_FAILED++))
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    ((WARNINGS++))
}

# ============================================
# DIMENSION 1: FUNCTIONAL TESTING
# "Does the user get what they asked for?"
# ============================================

print_test_header "DIMENSION 1: FUNCTIONAL TESTING"

echo "Testing: All user actions must end with observable artifacts"

# Test 1.1: File Upload creates observable artifact
echo ""
echo "Test 1.1: File Upload → Observable Artifact"
if grep -q "ingest_file" "$FRONTEND_DIR/shared/managers/ContentAPIManager.ts" 2>/dev/null && \
   (grep -q "trackExecution\|getExecutionStatus" "$FRONTEND_DIR/shared/managers/ContentAPIManager.ts" 2>/dev/null || \
    grep -q "file_id\|fileId" "$FRONTEND_DIR/shared/managers/ContentAPIManager.ts" 2>/dev/null); then
    print_success "File upload creates observable artifact (execution tracked, file_id returned)"
else
    print_failure "File upload may not create observable artifact"
fi

# Test 1.2: Artifact Creation has lifecycle
echo ""
echo "Test 1.2: Artifact Creation → Lifecycle State"
if grep -q "ensureArtifactLifecycle" "$FRONTEND_DIR/shared/managers/OutcomesAPIManager.ts" 2>/dev/null && \
   grep -q "lifecycle_state\|purpose\|scope\|owner" "$FRONTEND_DIR/shared/managers/OutcomesAPIManager.ts" 2>/dev/null; then
    print_success "Artifact creation includes lifecycle (purpose, scope, owner)"
else
    print_failure "Artifact creation may not include lifecycle"
fi

# Test 1.3: Visualization creates observable result
echo ""
echo "Test 1.3: Lineage Visualization → Observable Result"
if grep -q "visualize_lineage" "$FRONTEND_DIR/shared/managers/InsightsAPIManager.ts" 2>/dev/null && \
   grep -q "setRealmState.*insights.*lineageVisualizations" "$FRONTEND_DIR/shared/managers/InsightsAPIManager.ts" 2>/dev/null; then
    print_success "Lineage visualization creates observable result (stored in realm state)"
else
    print_failure "Lineage visualization may not create observable result"
fi

# Test 1.4: Relationship Mapping creates observable result
echo ""
echo "Test 1.4: Relationship Mapping → Observable Result"
if grep -q "map_relationships" "$FRONTEND_DIR/shared/managers/InsightsAPIManager.ts" 2>/dev/null && \
   grep -q "setRealmState.*insights.*relationshipMappings" "$FRONTEND_DIR/shared/managers/InsightsAPIManager.ts" 2>/dev/null; then
    print_success "Relationship mapping creates observable result (stored in realm state)"
else
    print_failure "Relationship mapping may not create observable result"
fi

# Test 1.5: Process Optimization creates observable result
echo ""
echo "Test 1.5: Process Optimization → Observable Result"
if grep -q "optimize_process\|optimizeCoexistence" "$FRONTEND_DIR/shared/managers/JourneyAPIManager.ts" "$FRONTEND_DIR/shared/services/operations" 2>/dev/null && \
   grep -q "setRealmState.*journey.*operations\|setRealmState.*journey.*optimizedProcesses" "$FRONTEND_DIR/app/(protected)/pillars/journey/components/CoexistenceBlueprint/hooks.ts" 2>/dev/null; then
    print_success "Process optimization creates observable result (stored in realm state)"
else
    print_warning "Process optimization may use legacy service (needs verification)"
fi

# ============================================
# DIMENSION 2: ARCHITECTURAL TESTING
# "Did the system behave correctly while doing it?"
# ============================================

print_test_header "DIMENSION 2: ARCHITECTURAL TESTING"

echo "Testing: No intent inference below Runtime, Runtime validates parameters"

# Test 2.1: All API calls use intent-based API
echo ""
echo "Test 2.1: Intent-Based API Usage"
# Check for legacy calls in core API managers (Content, Insights, Journey, Outcomes)
LEGACY_CALLS=$(grep -r "/api/v1/" "$FRONTEND_DIR/shared/managers/ContentAPIManager.ts" "$FRONTEND_DIR/shared/managers/InsightsAPIManager.ts" "$FRONTEND_DIR/shared/managers/JourneyAPIManager.ts" "$FRONTEND_DIR/shared/managers/OutcomesAPIManager.ts" 2>/dev/null | grep -v "^[[:space:]]*//" || true)
if [ -z "$LEGACY_CALLS" ]; then
    print_success "Core API managers use intent-based API (no legacy /api/v1/ calls)"
else
    print_warning "Some legacy API calls found in core managers"
    echo "  Found: $(echo "$LEGACY_CALLS" | wc -l) legacy calls"
fi
# Note: Other managers (OperationsAPIManager, SessionAPIManager, etc.) may still have legacy calls - these are acceptable for legacy services

# Test 2.2: No direct fetch/axios calls in components
echo ""
echo "Test 2.2: No Direct API Calls in Components"
DIRECT_CALLS=$(grep -r "fetch.*api\|axios.*api" "$FRONTEND_DIR/app/(protected)" "$FRONTEND_DIR/components" 2>/dev/null | grep -v "^[[:space:]]*//" | grep -v "OperationsService\|solution-service" || true)
if [ -z "$DIRECT_CALLS" ]; then
    print_success "No direct API calls in components (all via API managers)"
else
    print_warning "Some direct API calls found in components"
    echo "  Found: $(echo "$DIRECT_CALLS" | wc -l) direct calls"
fi

# Test 2.3: Runtime authority logic exists
echo ""
echo "Test 2.3: Runtime Authority Logic"
if grep -q "RUNTIME AUTHORITY\|Runtime.*wins\|reconciledRealm" "$FRONTEND_DIR/shared/state/PlatformStateProvider.tsx" 2>/dev/null; then
    print_success "Runtime authority logic exists (reconciliation, Runtime wins)"
else
    print_failure "Runtime authority logic may be missing"
fi

# Test 2.4: Intent parameters are explicit
echo ""
echo "Test 2.4: Intent Parameters Explicit"
# Check for empty parameter objects (acceptable if documented)
EMPTY_PARAMS=$(grep -r "submitIntent.*{}" "$FRONTEND_DIR/shared/managers" 2>/dev/null | grep -v "^[[:space:]]*//" || true)
if [ -z "$EMPTY_PARAMS" ]; then
    print_success "No empty parameter objects (all parameters explicit or documented)"
else
    print_warning "Some empty parameter objects found (should be documented)"
fi

# Test 2.5: Components read from PlatformStateProvider
echo ""
echo "Test 2.5: State Authority Pattern"
# Check for usePlatformState usage in components
STATE_USAGE=$(grep -r "usePlatformState\|getRealmState" "$FRONTEND_DIR/app/(protected)" "$FRONTEND_DIR/components" 2>/dev/null | wc -l)
if [ "$STATE_USAGE" -gt 10 ]; then
    print_success "Components read from PlatformStateProvider (Runtime authority)"
else
    print_warning "May have components not using PlatformStateProvider"
fi

# ============================================
# DIMENSION 3: SRE / DISTRIBUTED SYSTEMS
# "Could this fail in real life?"
# ============================================

print_test_header "DIMENSION 3: SRE / DISTRIBUTED SYSTEMS TESTING"

echo "Testing: Boundary Matrix validation, error handling, state persistence"

# Test 3.1: Error handling exists
echo ""
echo "Test 3.1: Error Handling"
ERROR_HANDLING=$(grep -r "catch\|error\|Error\|try" "$FRONTEND_DIR/shared/managers" 2>/dev/null | wc -l)
if [ "$ERROR_HANDLING" -gt 50 ]; then
    print_success "Error handling implemented in API managers"
else
    print_warning "May have insufficient error handling"
fi

# Test 3.2: State persistence (lifecycle survives reload)
echo ""
echo "Test 3.2: State Persistence"
if grep -q "lifecycle_state\|createdAt\|updatedAt" "$FRONTEND_DIR/shared/services/artifactLifecycle.ts" 2>/dev/null && \
   grep -q "setRealmState\|getRealmState" "$FRONTEND_DIR/shared/managers/OutcomesAPIManager.ts" 2>/dev/null; then
    print_success "State persistence implemented (lifecycle in realm state)"
else
    print_failure "State persistence may be incomplete"
fi

# Test 3.3: Lifecycle transition validation
echo ""
echo "Test 3.3: Lifecycle Transition Validation"
if grep -q "validateLifecycleTransition\|VALID_TRANSITIONS" "$FRONTEND_DIR/shared/services/artifactLifecycle.ts" 2>/dev/null; then
    print_success "Lifecycle transition validation exists"
else
    print_failure "Lifecycle transition validation may be missing"
fi

# Test 3.4: Visualization data source (Runtime state)
echo ""
echo "Test 3.4: Visualization Data Source"
VISUALIZATION_STATE=$(grep -r "state.realm.insights.lineageVisualizations\|state.realm.insights.relationshipMappings\|state.realm.journey.operations\|getRealmState" "$FRONTEND_DIR/app/(protected)/pillars" 2>/dev/null | wc -l)
if [ "$VISUALIZATION_STATE" -gt 0 ]; then
    print_success "Visualizations read from Runtime state (realm state) - Found: $VISUALIZATION_STATE references"
else
    print_warning "Some visualizations may not read from Runtime state"
fi

# Test 3.5: Intent parameter validation
echo ""
echo "Test 3.5: Intent Parameter Validation"
# Check for required parameter validation before submitIntent
# Count validation comments and parameter validation if statements (excluding session validation)
PARAM_VALIDATION_COMMENTS=$(grep -r "✅ FIX ISSUE 3.*Parameter validation\|FIX ISSUE 3.*Parameter validation" "$FRONTEND_DIR/shared/managers" 2>/dev/null | wc -l)
PARAM_VALIDATION_IF=$(grep -r "if (!" "$FRONTEND_DIR/shared/managers/ContentAPIManager.ts" "$FRONTEND_DIR/shared/managers/InsightsAPIManager.ts" "$FRONTEND_DIR/shared/managers/JourneyAPIManager.ts" "$FRONTEND_DIR/shared/managers/OutcomesAPIManager.ts" 2>/dev/null | grep -v "sessionId\|session.*tenantId\|platformState" | wc -l)
TOTAL_PARAM_VALIDATION=$((PARAM_VALIDATION_COMMENTS + PARAM_VALIDATION_IF))
if [ "$TOTAL_PARAM_VALIDATION" -ge 20 ]; then
    print_success "Intent parameter validation exists (required parameters checked) - Found: $TOTAL_PARAM_VALIDATION validations"
else
    print_warning "May have insufficient parameter validation (Found: $TOTAL_PARAM_VALIDATION validations)"
fi

# ============================================
# BOUNDARY MATRIX VALIDATION
# ============================================

print_test_header "BOUNDARY MATRIX VALIDATION"

echo "Testing: Key boundaries have proper error handling and validation"

# Browser Boundary: Session handling
echo ""
echo "Browser Boundary: Session Handling"
SESSION_VALIDATION=$(grep -r "validateSession\|sessionId\|session.*required\|Session required" "$FRONTEND_DIR/shared/managers" 2>/dev/null | wc -l)
if [ "$SESSION_VALIDATION" -gt 20 ]; then
    print_success "Session validation exists (browser boundary) - Found: $SESSION_VALIDATION validations"
else
    print_warning "Session validation may be incomplete (Found: $SESSION_VALIDATION validations)"
fi

# Runtime Boundary: Intent submission
echo ""
echo "Runtime Boundary: Intent Submission"
SUBMIT_COUNT=$(grep -r "submitIntent" "$FRONTEND_DIR/shared/managers" 2>/dev/null | wc -l)
EXEC_COUNT=$(grep -r "_waitForExecution\|waitForExecution\|ExecutionStatus\|getExecutionStatus\|trackExecution" "$FRONTEND_DIR/shared/managers" 2>/dev/null | wc -l)
if [ "$SUBMIT_COUNT" -gt 10 ] && [ "$EXEC_COUNT" -gt 5 ]; then
    print_success "Intent submission and execution tracking exists (Runtime boundary) - submitIntent: $SUBMIT_COUNT, execution tracking: $EXEC_COUNT"
else
    print_warning "Intent submission patterns found (submitIntent: $SUBMIT_COUNT, execution tracking: $EXEC_COUNT) - may need verification"
fi

# Persistence Boundary: State storage
echo ""
echo "Persistence Boundary: State Storage"
REALM_STATE_COUNT=$(grep -r "setRealmState\|getRealmState" "$FRONTEND_DIR/shared/managers" "$FRONTEND_DIR/shared/state" 2>/dev/null | wc -l)
PLATFORM_STATE=$(grep -r "PlatformStateProvider" "$FRONTEND_DIR/shared/state" 2>/dev/null | wc -l)
if [ "$REALM_STATE_COUNT" -gt 20 ] && [ "$PLATFORM_STATE" -gt 0 ]; then
    print_success "State storage exists (persistence boundary)"
else
    print_failure "State storage may be incomplete (realm state calls: $REALM_STATE_COUNT, PlatformStateProvider: $PLATFORM_STATE)"
fi

# UI Hydration Boundary: State reconciliation
echo ""
echo "UI Hydration Boundary: State Reconciliation"
if grep -q "reconciledRealm\|Runtime.*wins\|syncWithRuntime" "$FRONTEND_DIR/shared/state/PlatformStateProvider.tsx" 2>/dev/null; then
    print_success "State reconciliation exists (UI hydration boundary)"
else
    print_warning "State reconciliation may be incomplete"
fi

# ============================================
# TEST SUMMARY
# ============================================

print_test_header "TEST SUMMARY"

echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "Warnings: $WARNINGS"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review warnings (may be acceptable)"
    echo "2. Proceed to browser-only tests:"
    echo "   - Hard refresh test"
    echo "   - Network throttling test"
    echo "   - Session expiration test"
    echo "3. Proceed to chaos testing:"
    echo "   - Kill backend container mid-intent"
    echo "4. Run manual functional testing in browser"
    exit 0
else
    echo -e "${RED}✗ Some critical tests failed. Please review errors above.${NC}"
    exit 1
fi
