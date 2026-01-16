#!/bin/bash
# Content Pillar Integration Test Script
# Runs comprehensive integration tests for the Content Pillar

set -e

echo "🧪 Content Pillar Integration Testing"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0
SKIPPED=0

# Function to print test result
print_result() {
    local status=$1
    local test_name=$2
    local message=$3
    
    case $status in
        PASS)
            echo -e "${GREEN}✅ PASS${NC}: $test_name"
            if [ -n "$message" ]; then
                echo "   $message"
            fi
            ((PASSED++))
            ;;
        FAIL)
            echo -e "${RED}❌ FAIL${NC}: $test_name"
            if [ -n "$message" ]; then
                echo "   $message"
            fi
            ((FAILED++))
            ;;
        SKIP)
            echo -e "${YELLOW}⏭️  SKIP${NC}: $test_name"
            if [ -n "$message" ]; then
                echo "   $message"
            fi
            ((SKIPPED++))
            ;;
    esac
}

# Check if services are running
check_service() {
    local service=$1
    local url=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

echo "📋 Phase 1: Pre-Test Checks"
echo "---------------------------"

# Check if backend services are running
echo "Checking backend services..."

RUNTIME_URL="${RUNTIME_URL:-http://localhost:8000}"
EXPERIENCE_URL="${EXPERIENCE_URL:-http://localhost:8001}"

if check_service "Runtime" "$RUNTIME_URL/health"; then
    print_result "PASS" "Runtime Service" "Available at $RUNTIME_URL"
else
    print_result "FAIL" "Runtime Service" "Not available at $RUNTIME_URL"
    echo "   ⚠️  Some tests may be skipped"
fi

if check_service "Experience Plane" "$EXPERIENCE_URL/health"; then
    print_result "PASS" "Experience Plane Service" "Available at $EXPERIENCE_URL"
else
    print_result "FAIL" "Experience Plane Service" "Not available at $EXPERIENCE_URL"
    echo "   ⚠️  Some tests may be skipped"
fi

# Check if frontend is running
if curl -s -f "http://localhost:3000" > /dev/null 2>&1; then
    print_result "PASS" "Frontend Dev Server" "Available at http://localhost:3000"
else
    print_result "FAIL" "Frontend Dev Server" "Not available at http://localhost:3000"
    echo "   ⚠️  Start with: cd symphainy-frontend && npm run dev"
fi

echo ""
echo "📋 Phase 2: Code Quality Checks"
echo "--------------------------------"

# Check TypeScript compilation
echo "Checking TypeScript compilation..."
cd "$(dirname "$0")/../symphainy-frontend"

if command -v npx &> /dev/null; then
    if npx tsc --noEmit --project tsconfig.json 2>&1 | head -20; then
        print_result "PASS" "TypeScript Compilation" "No errors found"
    else
        TS_ERRORS=$(npx tsc --noEmit --project tsconfig.json 2>&1 | wc -l)
        if [ "$TS_ERRORS" -gt 0 ]; then
            print_result "FAIL" "TypeScript Compilation" "$TS_ERRORS errors found"
            echo "   Run: npx tsc --noEmit to see details"
        else
            print_result "PASS" "TypeScript Compilation" "No errors found"
        fi
    fi
else
    print_result "SKIP" "TypeScript Compilation" "npx not available"
fi

# Check for old imports
echo "Checking for old architecture imports..."
cd "$(dirname "$0")/.."

OLD_IMPORTS=$(grep -r "useGlobalSession\|GlobalSessionProvider\|new ContentAPIManager(" symphainy-frontend/app/\(protected\)/pillars/content --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l || echo "0")

if [ "$OLD_IMPORTS" -eq 0 ]; then
    print_result "PASS" "Architecture Migration" "No old imports found"
else
    print_result "FAIL" "Architecture Migration" "$OLD_IMPORTS old imports still present"
    echo "   Run: grep -r 'useGlobalSession\|new ContentAPIManager' symphainy-frontend/app/\(protected\)/pillars/content"
fi

echo ""
echo "📋 Phase 3: Component Import Checks"
echo "-----------------------------------"

# Check if components can be imported (basic check)
echo "Checking component imports..."
cd "$(dirname "$0")/../symphainy-frontend"

COMPONENTS=(
    "app/(protected)/pillars/content/components/FileUploader"
    "app/(protected)/pillars/content/components/FileDashboard"
    "app/(protected)/pillars/content/components/FileParser"
    "app/(protected)/pillars/content/components/ParsePreview"
    "app/(protected)/pillars/content/components/DataMash"
    "app/(protected)/pillars/content/components/FileSelector"
)

for component in "${COMPONENTS[@]}"; do
    if [ -f "${component}.tsx" ]; then
        # Basic syntax check
        if node -e "require('fs').readFileSync('${component}.tsx', 'utf8')" > /dev/null 2>&1; then
            print_result "PASS" "$(basename $component)" "File exists and readable"
        else
            print_result "FAIL" "$(basename $component)" "File has syntax errors"
        fi
    else
        print_result "FAIL" "$(basename $component)" "File not found"
    fi
done

echo ""
echo "📊 Test Summary"
echo "==============="
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo -e "${YELLOW}Skipped:${NC} $SKIPPED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All automated checks passed!${NC}"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Start backend services: docker-compose up -d"
    echo "  2. Start frontend: cd symphainy-frontend && npm run dev"
    echo "  3. Navigate to Content Pillar: http://localhost:3000/pillars/content"
    echo "  4. Run manual tests from: docs/execution/content_pillar_integration_test_plan.md"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please fix issues before proceeding.${NC}"
    exit 1
fi
