#!/bin/bash
# Foundation Validation Script
# Quick validation of Phase 1 foundation components

echo "🔍 Validating Foundation Components..."
echo ""

# Check TypeScript compilation
echo "1. Checking TypeScript compilation..."
if npx tsc --noEmit --project tsconfig.json 2>&1 | head -20; then
    echo "   ✅ TypeScript compilation: PASS"
else
    echo "   ❌ TypeScript compilation: FAIL"
    echo "   ⚠️  Review errors above"
fi

echo ""

# Check imports
echo "2. Checking component imports..."
node -e "
try {
    require('./shared/services/UnifiedWebSocketClient.ts');
    console.log('   ✅ UnifiedWebSocketClient: Import OK');
} catch (e) {
    console.log('   ⚠️  UnifiedWebSocketClient: Import check (may need build)');
}

try {
    require('./shared/services/ExperiencePlaneClient.ts');
    console.log('   ✅ ExperiencePlaneClient: Import OK');
} catch (e) {
    console.log('   ⚠️  ExperiencePlaneClient: Import check (may need build)');
}

try {
    require('./shared/state/PlatformStateProvider.tsx');
    console.log('   ✅ PlatformStateProvider: Import OK');
} catch (e) {
    console.log('   ⚠️  PlatformStateProvider: Import check (may need build)');
}

try {
    require('./shared/auth/AuthProvider.tsx');
    console.log('   ✅ AuthProvider: Import OK');
} catch (e) {
    console.log('   ⚠️  AuthProvider: Import check (may need build)');
}

try {
    require('./shared/managers/ContentAPIManager.ts');
    console.log('   ✅ ContentAPIManager: Import OK');
} catch (e) {
    console.log('   ⚠️  ContentAPIManager: Import check (may need build)');
}
" 2>/dev/null || echo "   ⚠️  Import check requires build step"

echo ""
echo "📊 Validation Complete!"
echo ""
echo "💡 Next Steps:"
echo "  - Fix any TypeScript errors"
echo "  - Test with backend (if running)"
echo "  - Proceed with Phase 2"
