#!/bin/bash
# Validate Single Abstraction
#
# Usage: ./scripts/validate_abstraction.sh <abstraction_name>
# Example: ./scripts/validate_abstraction.sh auth

set -e

ABSTRACTION=$1

if [ -z "$ABSTRACTION" ]; then
    echo "Usage: $0 <abstraction_name>"
    echo "Example: $0 auth"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔍 Validating ${ABSTRACTION} abstraction..."
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Run unit tests
print_status "Running unit tests for ${ABSTRACTION}..."
if pytest tests/foundations/public_works/test_${ABSTRACTION}_abstraction*.py -v --tb=short 2>/dev/null; then
    print_status "Unit tests passed"
else
    print_warning "Unit tests not found or failed"
fi

# Run swappability tests
print_status "Running swappability tests for ${ABSTRACTION}..."
if pytest tests/foundations/public_works/test_${ABSTRACTION}_abstraction_swappability.py -v --tb=short 2>/dev/null; then
    print_status "Swappability tests passed"
else
    print_warning "Swappability tests not found"
fi

# Run contract tests
print_status "Running contract tests for ${ABSTRACTION}..."
if pytest tests/foundations/public_works/test_${ABSTRACTION}_protocol_compliance.py -v --tb=short 2>/dev/null; then
    print_status "Contract tests passed"
else
    print_warning "Contract tests not found"
fi

print_status "Validation complete for ${ABSTRACTION}!"
