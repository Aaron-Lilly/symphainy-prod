#!/bin/bash
# Phase 3: Coexistence Fabric Showcase - Smoke Test
# Quick functional + architectural validation

# Don't exit on error - we want to collect all test results
# set -e

echo "=========================================="
echo "Phase 3: Coexistence Fabric Showcase - Smoke Test"
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

# Phase 1: Architectural Validation
print_test_header "Architectural Validation"

FRONTEND_DIR="symphainy-frontend"

echo "Checking for legacy endpoint calls..."
LEGACY_CALLS=$(grep -r "/api/v1/" "$FRONTEND_DIR/components/landing/CoexistenceExplanation.tsx" "$FRONTEND_DIR/components/landing/CoexistenceDiagram.tsx" "$FRONTEND_DIR/app/(protected)/pillars/journey/page.tsx" "$FRONTEND_DIR/app/(protected)/pillars/business-outcomes/page.tsx" 2>/dev/null | grep -v "^[[:space:]]*//" || true)
if [ -n "$LEGACY_CALLS" ]; then
    print_failure "Legacy endpoint calls found in Phase 3 components"
else
    print_success "No legacy endpoint calls in Phase 3 components"
fi

echo ""
echo "Checking component structure..."
if [ -f "$FRONTEND_DIR/components/landing/CoexistenceExplanation.tsx" ] && \
   [ -f "$FRONTEND_DIR/components/landing/CoexistenceDiagram.tsx" ]; then
    print_success "All Phase 3 components created"
else
    print_failure "Missing Phase 3 components"
fi

echo ""
echo "Checking integration in landing page..."
if grep -q "CoexistenceExplanation" "$FRONTEND_DIR/components/landing/WelcomeJourney.tsx" 2>/dev/null; then
    print_success "CoexistenceExplanation integrated in landing page"
else
    print_failure "CoexistenceExplanation not found in landing page"
fi

echo ""
echo "Checking Journey pillar enhancements..."
if grep -q "PHASE 3.2\|Coexistence Analysis\|SOP.*Workflow" "$FRONTEND_DIR/app/(protected)/pillars/journey/page.tsx" 2>/dev/null || \
   grep -q "PHASE 3.2\|boundary-crossing\|SOP.*Policy\|Workflow.*Practice" "$FRONTEND_DIR/app/(protected)/pillars/journey/components/CoexistenceBlueprint/components.tsx" 2>/dev/null; then
    print_success "Journey pillar enhancements found"
else
    print_warning "Journey pillar enhancements not found (may be intentional)"
fi

echo ""
echo "Checking Outcomes pillar enhancements..."
if grep -q "PHASE 3.3\|Coexistence Context\|boundary-crossing\|Cross-Pillar" "$FRONTEND_DIR/app/(protected)/pillars/business-outcomes/page.tsx" 2>/dev/null; then
    print_success "Outcomes pillar coexistence context found"
else
    print_warning "Outcomes pillar coexistence context not found (may be intentional)"
fi

echo ""
echo "Checking for direct API calls (should be informational only)..."
API_CALLS=$(grep -r "fetch.*api\|axios.*api\|submitIntent" "$FRONTEND_DIR/components/landing/CoexistenceExplanation.tsx" "$FRONTEND_DIR/components/landing/CoexistenceDiagram.tsx" 2>/dev/null | grep -v "//.*TODO\|//.*NOTE" || true)
if [ -n "$API_CALLS" ]; then
    print_failure "Direct API calls found (should be informational only)"
else
    print_success "No direct API calls (informational components only)"
fi

# Phase 2: Summary
print_test_header "Test Summary"

echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "Warnings: $WARNINGS"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All architectural checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Execute manual functional testing in browser:"
    echo "   - Verify coexistence explanation on landing page"
    echo "   - Verify coexistence diagram displays"
    echo "   - Verify Journey pillar enhancements"
    echo "   - Verify Outcomes pillar coexistence context"
    echo "2. Document any issues"
    echo "3. Proceed to next phase"
    exit 0
else
    echo -e "${RED}✗ Some architectural checks failed. Please review errors above.${NC}"
    exit 1
fi
