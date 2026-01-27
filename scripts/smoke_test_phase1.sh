#!/bin/bash
# Phase 1: Foundation & Agent Visibility - Smoke Test
# Quick functional + architectural validation

set -e

echo "=========================================="
echo "Phase 1: Agent Visibility - Smoke Test"
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

echo "Checking for Jotai atom usage (should be removed)..."
if grep -v "^[[:space:]]*//" "$FRONTEND_DIR/shared/components/MainLayout.tsx" 2>/dev/null | grep -q "mainChatbotOpenAtom\|shouldShowSecondaryChatbotAtom"; then
    print_failure "Jotai atoms still present in MainLayout (uncommented)"
else
    print_success "No Jotai atoms in MainLayout (uncommented)"
fi

echo ""
echo "Checking PlatformStateProvider usage..."
if grep -q "usePlatformState\|PlatformStateProvider" "$FRONTEND_DIR/shared/components/MainLayout.tsx" 2>/dev/null; then
    print_success "PlatformStateProvider used in MainLayout"
else
    print_failure "PlatformStateProvider not found in MainLayout"
fi

echo ""
echo "Checking SessionBoundaryProvider usage..."
if grep -q "useSessionBoundary\|SessionBoundaryProvider" "$FRONTEND_DIR/shared/components/MainLayout.tsx" 2>/dev/null; then
    print_success "SessionBoundaryProvider used in MainLayout"
else
    print_failure "SessionBoundaryProvider not found in MainLayout"
fi

echo ""
echo "Checking agent info setup in pillar pages..."
PILLAR_PAGES=(
    "$FRONTEND_DIR/app/(protected)/pillars/content/page.tsx"
    "$FRONTEND_DIR/app/(protected)/pillars/insights/page.tsx"
    "$FRONTEND_DIR/app/(protected)/pillars/journey/page.tsx"
    "$FRONTEND_DIR/app/(protected)/pillars/business-outcomes/page.tsx"
)

for page in "${PILLAR_PAGES[@]}"; do
    if [ -f "$page" ]; then
        if grep -q "setChatbotAgentInfo\|SecondaryChatbotAgent" "$page" 2>/dev/null; then
            print_success "Agent info setup found in $(basename $page)"
        else
            print_warning "Agent info setup not found in $(basename $page)"
        fi
    else
        print_warning "Pillar page not found: $page"
    fi
done

echo ""
echo "Checking chat panel default visibility..."
if grep -q "chatPanelExplicitlyClosed\|chatPanelRequested.*true" "$FRONTEND_DIR/shared/components/MainLayout.tsx" 2>/dev/null; then
    print_success "Chat panel default visibility configured"
else
    print_warning "Chat panel default visibility configuration unclear"
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
    echo "   - Verify chat panel is visible by default"
    echo "   - Verify agent indicators"
    echo "   - Verify pillar badges"
    echo "2. Document any issues"
    echo "3. Proceed to next phase"
    exit 0
else
    echo -e "${RED}✗ Some architectural checks failed. Please review errors above.${NC}"
    exit 1
fi
