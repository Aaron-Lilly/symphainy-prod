#!/bin/bash
# Comprehensive Upload Flow Test Script
# Tests functional, architectural, and SRE perspectives

set -e

echo "=========================================="
echo "Upload Flow Comprehensive Test"
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
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
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
CONTAINERS=("traefik" "frontend" "backend")
for container in "${CONTAINERS[@]}"; do
    # Try to find container with name containing the keyword
    container_id=$(docker ps --format '{{.Names}}' | grep -i "$container" | head -1)
    if [ -n "$container_id" ]; then
        check_container "$container_id"
    else
        print_warning "Container matching '$container' not found"
    fi
done

echo ""
echo "Checking container health..."
docker ps --format "table {{.Names}}\t{{.Status}}" | head -10

echo ""
echo "Checking Docker networks..."
docker network ls

# Phase 2: Functional Test (Manual)
print_test_header "Phase 2: Functional Test (Manual)"

echo "Please execute the upload flow in your browser:"
echo "  1. Navigate to Content Pillar Upload page"
echo "  2. Select a file"
echo "  3. Click 'Upload'"
echo "  4. Verify 'Save' button appears"
echo "  5. Click 'Save'"
echo "  6. Verify success message"
echo ""
echo "While testing, monitor:"
echo "  - Browser DevTools Network tab"
echo "  - Browser DevTools Console tab"
echo ""
read -p "Press Enter when you've completed the manual test..."

# Phase 3: Architectural Validation
print_test_header "Phase 3: Architectural Validation"

# Find backend container
BACKEND_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i "backend\|runtime\|api" | head -1)
FRONTEND_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i "frontend\|next" | head -1)

if [ -n "$BACKEND_CONTAINER" ]; then
    echo "Checking intent-based API usage..."
    check_logs "$BACKEND_CONTAINER" "intent.*submit\|/api/intent/submit" "Intent submissions found"
    
    echo ""
    echo "Checking for legacy endpoint usage (should be none)..."
    LEGACY_COUNT=$(docker logs "$FRONTEND_CONTAINER" 2>&1 | grep -i "/api/v1/" | wc -l)
    if [ "$LEGACY_COUNT" -eq 0 ]; then
        print_success "No legacy endpoint calls found"
    else
        print_warning "Found $LEGACY_COUNT legacy endpoint calls (may be from old requests)"
    fi
    
    echo ""
    echo "Checking ingest_file intent..."
    check_logs "$BACKEND_CONTAINER" "ingest_file" "ingest_file intent found"
    
    echo ""
    echo "Checking save_materialization intent..."
    check_logs "$BACKEND_CONTAINER" "save_materialization" "save_materialization intent found"
else
    print_warning "Backend container not found, skipping architectural validation"
fi

# Phase 4: SRE Boundary Validation
print_test_header "Phase 4: SRE Boundary Validation"

if [ -n "$BACKEND_CONTAINER" ]; then
    echo "Boundary 1-2: Traefik/Frontend"
    if [ -n "$FRONTEND_CONTAINER" ]; then
        TRAEFIK_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i "traefik" | head -1)
        if [ -n "$TRAEFIK_CONTAINER" ]; then
            check_logs "$TRAEFIK_CONTAINER" "upload\|intent" "Traefik routing logs"
        fi
        check_logs "$FRONTEND_CONTAINER" "upload\|intent" "Frontend request logs"
    fi
    
    echo ""
    echo "Boundary 3-5: Backend/Auth/Runtime"
    check_logs "$BACKEND_CONTAINER" "intent.*received\|execution.*started" "Intent execution started"
    check_errors "$BACKEND_CONTAINER" "401\|403\|unauthorized" "Authentication errors"
    
    echo ""
    echo "Boundary 6-7: Data Steward/Policy"
    check_logs "$BACKEND_CONTAINER" "data.*steward.*sdk\|data.*steward.*initialized" "Data Steward SDK initialized"
    check_logs "$BACKEND_CONTAINER" "boundary.*contract\|request.*data.*access" "Boundary contract creation"
    check_logs "$BACKEND_CONTAINER" "materialization.*policy.*store\|policy.*retrieved" "Policy store operations"
    check_errors "$BACKEND_CONTAINER" "data.*steward.*required\|data.*steward.*unavailable" "Data Steward errors"
    
    echo ""
    echo "Boundary 8-9: Ingestion/Storage"
    check_logs "$BACKEND_CONTAINER" "ingestion.*abstraction\|gcs.*upload\|file.*uploaded" "File ingestion"
    check_logs "$BACKEND_CONTAINER" "supabase\|file.*storage.*abstraction" "File storage operations"
    check_errors "$BACKEND_CONTAINER" "gcs.*error\|upload.*failed\|supabase.*error" "Storage errors"
    
    echo ""
    echo "Boundary 10-11: Materialization Authorization/Registration"
    check_logs "$BACKEND_CONTAINER" "materialization.*authorized\|save.*materialization" "Materialization authorization"
    check_logs "$BACKEND_CONTAINER" "materialization.*registered\|register.*materialization" "Materialization registration"
    check_errors "$BACKEND_CONTAINER" "boundary.*contract.*not.*found\|registration.*failed" "Materialization errors"
else
    print_warning "Backend container not found, skipping SRE boundary validation"
fi

# Summary
print_test_header "Test Summary"

echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "Warnings: $WARNINGS"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the output above.${NC}"
    exit 1
fi
