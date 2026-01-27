#!/bin/bash
# Phase 1: Agent Visibility Comprehensive Test Script
# Tests functional, architectural, and SRE perspectives

# Don't exit on error - we want to collect all test results
# set -e

echo "=========================================="
echo "Phase 1: Agent Visibility Comprehensive Test"
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

# Function to check if container is running
check_container() {
    local container_name=$1
    if docker ps --format '{{.Names}}' | grep -q "${container_name}"; then
        print_success "Container '${container_name}' is running"
        return 0
    else
        print_failure "Container '${container_name}' is not running"
        return 1
    fi
}

# Function to check logs for pattern
check_logs() {
    local container=$1
    local pattern=$2
    local description=$3
    local count=$(docker logs "$container" 2>&1 | grep -i "$pattern" | wc -l)
    if [ "$count" -gt 0 ]; then
        print_success "$description (found $count matches)"
        return 0
    else
        print_warning "$description (no matches found)"
        return 1
    fi
}

# Function to check for errors in logs
check_errors() {
    local container=$1
    local pattern=$2
    local description=$3
    local errors=$(docker logs "$container" --tail 100 2>&1 | grep -i "$pattern" | tail -5)
    if [ -z "$errors" ]; then
        print_success "$description (no errors found)"
        return 0
    else
        print_failure "$description (errors found)"
        echo "$errors"
        return 1
    fi
}

# Phase 1: Pre-Test Validation
print_test_header "Phase 1: Pre-Test Validation"

echo "Checking Docker containers..."
CONTAINERS=("traefik" "frontend" "runtime")
for container in "${CONTAINERS[@]}"; do
    container_id=$(docker ps --format '{{.Names}}' | grep -i "$container" | head -1)
    if [ -n "$container_id" ]; then
        check_container "$container_id"
    else
        print_warning "Container matching '$container' not found"
    fi
done

echo ""
echo "Checking container health..."
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "traefik|frontend|runtime" || true

echo ""
echo "Checking frontend build..."
if docker logs symphainy-frontend 2>&1 | grep -qi "compiled\|ready"; then
    print_success "Frontend build successful"
else
    print_warning "Frontend build status unclear (check logs)"
fi

echo ""
echo "Checking backend health..."
if docker logs symphainy-runtime --tail 20 2>&1 | grep -qi "started\|ready\|uvicorn"; then
    print_success "Backend service running"
else
    print_warning "Backend service status unclear (check logs)"
fi

# Phase 2: Architectural Validation
print_test_header "Phase 2: Architectural Validation"

FRONTEND_DIR="symphainy-frontend"

echo "Checking for Jotai atom usage (should be removed)..."
# Check for uncommented Jotai atom usage (ignore commented lines)
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

# Phase 3: SRE Boundary Validation
print_test_header "Phase 3: SRE Boundary Validation"

echo "Boundary 1-2: Traefik/Frontend"
if check_logs "symphainy-traefik" "GET.*\.(js|css|html)" "Traefik routing frontend requests"; then
    : # Success already printed
fi

if check_errors "symphainy-frontend" "error\|failed\|crash" "Frontend errors"; then
    : # Success already printed
fi

echo ""
echo "Boundary 3: Frontend → PlatformStateProvider"
if check_logs "symphainy-frontend" "platform.*state\|context" "PlatformStateProvider usage"; then
    : # Success already printed
fi

echo ""
echo "Boundary 4: Frontend → SessionBoundaryProvider"
if check_logs "symphainy-frontend" "session.*boundary\|session.*state" "SessionBoundaryProvider usage"; then
    : # Success already printed
fi

echo ""
echo "Boundary 5: Frontend → Backend (WebSocket)"
if check_logs "symphainy-runtime" "websocket\|ws.*connect" "WebSocket connections"; then
    : # Success already printed
fi

if check_logs "symphainy-frontend" "websocket\|ws.*connect" "Frontend WebSocket connections"; then
    : # Success already printed
fi

echo ""
echo "Boundary 6: Agent Communication"
if check_logs "symphainy-runtime" "agent.*message\|guide.*agent\|liaison.*agent" "Agent communication"; then
    : # Success already printed
fi

# Phase 4: Summary
print_test_header "Test Summary"

echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "Warnings: $WARNINGS"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All automated tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Execute manual functional tests in browser"
    echo "2. Verify chat panel visibility"
    echo "3. Verify agent indicators"
    echo "4. Verify pillar badges"
    echo ""
    echo "See PHASE_1_3D_TESTING_STRATEGY.md for manual test steps."
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review errors above.${NC}"
    exit 1
fi
