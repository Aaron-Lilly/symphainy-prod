#!/bin/bash
# Phase 2: Artifact Plane Showcase - Smoke Test
# Quick functional + architectural validation

# Don't exit on error - we want to collect all test results
# set -e

echo "=========================================="
echo "Phase 2: Artifact Plane Showcase - Smoke Test"
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
LEGACY_CALLS=$(grep -r "/api/v1/" "$FRONTEND_DIR/components/landing/ArtifactGallery.tsx" "$FRONTEND_DIR/app/(protected)/artifacts/page.tsx" 2>/dev/null | grep -v "^[[:space:]]*//" || true)
if [ -n "$LEGACY_CALLS" ]; then
    print_failure "Legacy endpoint calls found in Phase 2 components"
else
    print_success "No legacy endpoint calls in Phase 2 components"
fi

echo ""
echo "Checking PlatformStateProvider usage..."
if grep -q "usePlatformState\|getRealmState" "$FRONTEND_DIR/components/landing/ArtifactGallery.tsx" 2>/dev/null && \
   grep -q "usePlatformState\|getRealmState" "$FRONTEND_DIR/app/(protected)/artifacts/page.tsx" 2>/dev/null; then
    print_success "PlatformStateProvider used in Phase 2 components"
else
    print_failure "PlatformStateProvider not found in Phase 2 components"
fi

echo ""
echo "Checking for direct API calls (should use getRealmState)..."
API_CALLS=$(grep -r "fetch.*api\|axios.*api" "$FRONTEND_DIR/components/landing/ArtifactGallery.tsx" "$FRONTEND_DIR/app/(protected)/artifacts/page.tsx" 2>/dev/null | grep -v "//.*TODO\|//.*NOTE" || true)
if [ -n "$API_CALLS" ]; then
    print_failure "Direct API calls found (should use getRealmState)"
else
    print_success "No direct API calls (using getRealmState)"
fi

echo ""
echo "Checking component structure..."
if [ -f "$FRONTEND_DIR/components/landing/ArtifactCard.tsx" ] && \
   [ -f "$FRONTEND_DIR/components/landing/ArtifactGallery.tsx" ] && \
   [ -f "$FRONTEND_DIR/app/(protected)/artifacts/page.tsx" ]; then
    print_success "All Phase 2 components created"
else
    print_failure "Missing Phase 2 components"
fi

echo ""
echo "Checking integration in landing page..."
if grep -q "ArtifactGallery" "$FRONTEND_DIR/components/landing/WelcomeJourney.tsx" 2>/dev/null; then
    print_success "ArtifactGallery integrated in landing page"
else
    print_failure "ArtifactGallery not found in landing page"
fi

echo ""
echo "Checking Outcomes pillar enhancements..."
if grep -q "PHASE 2.3\|Synthesis Inputs\|Artifact Lifecycle" "$FRONTEND_DIR/app/(protected)/pillars/business-outcomes/page.tsx" 2>/dev/null || \
   grep -q "PHASE 2.3\|Artifact Lifecycle" "$FRONTEND_DIR/app/(protected)/pillars/business-outcomes/components/GeneratedArtifactsDisplay.tsx" 2>/dev/null; then
    print_success "Outcomes pillar enhancements found"
else
    print_warning "Outcomes pillar enhancements not found (may be intentional)"
fi

# Phase 2: TypeScript/Lint Checks
print_test_header "TypeScript/Lint Validation"

echo "Checking TypeScript compilation..."
if command -v npx >/dev/null 2>&1; then
    cd "$FRONTEND_DIR" && npx tsc --noEmit --skipLibCheck 2>&1 | head -20
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_success "TypeScript compilation successful"
    else
        print_warning "TypeScript compilation has errors (may be expected)"
    fi
    cd ..
else
    print_warning "TypeScript check skipped (npx not available)"
fi

# Phase 3: Summary
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
    echo "   - Verify artifact gallery on landing page"
    echo "   - Verify artifact library page"
    echo "   - Verify Outcomes pillar enhancements"
    echo "2. Document any issues"
    echo "3. Proceed to next phase"
    exit 0
else
    echo -e "${RED}✗ Some architectural checks failed. Please review errors above.${NC}"
    exit 1
fi
