/**
 * Phase 7: Routing Refactoring - Quick Validation Test
 * 
 * This is a simpler test that validates routing patterns without full browser automation.
 * Useful for quick validation before running full Playwright tests.
 */

import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

const PROJECT_ROOT = join(__dirname, '../..');

interface TestResult {
  name: string;
  passed: boolean;
  message: string;
}

const results: TestResult[] = [];

function test(name: string, fn: () => boolean | string): void {
  try {
    const result = fn();
    if (typeof result === 'string') {
      results.push({ name, passed: false, message: result });
    } else if (result === true) {
      results.push({ name, passed: true, message: 'Passed' });
    } else {
      results.push({ name, passed: false, message: 'Failed' });
    }
  } catch (error: any) {
    results.push({ name, passed: false, message: error.message || 'Error' });
  }
}

console.log('Phase 7: Routing Refactoring - Quick Validation\n');
console.log('='.repeat(60));

// Test 1: Route utilities exist
test('Route utilities file exists', () => {
  const filePath = join(PROJECT_ROOT, 'symphainy-frontend/shared/utils/routing.ts');
  return existsSync(filePath) || 'routing.ts not found';
});

// Test 2: Route utilities have required functions
test('Route utilities have required functions', () => {
  const filePath = join(PROJECT_ROOT, 'symphainy-frontend/shared/utils/routing.ts');
  if (!existsSync(filePath)) {
    return 'routing.ts not found';
  }
  
  const content = readFileSync(filePath, 'utf-8');
  const requiredFunctions = [
    'buildPillarRoute',
    'parseRouteParams',
    'extractRealm',
    'syncRouteToState',
    'syncStateToRoute',
    'isPillarRoute',
    'isMVPRoute'
  ];
  
  const missing = requiredFunctions.filter(fn => !content.includes(`function ${fn}`) && !content.includes(`export function ${fn}`));
  return missing.length === 0 || `Missing functions: ${missing.join(', ')}`;
});

// Test 3: TopNavBar uses routing utilities
test('TopNavBar uses routing utilities', () => {
  const filePath = join(PROJECT_ROOT, 'symphainy-frontend/shared/components/TopNavBar.tsx');
  if (!existsSync(filePath)) {
    return 'TopNavBar.tsx not found';
  }
  
  const content = readFileSync(filePath, 'utf-8');
  const hasRoutingUtils = content.includes('buildPillarRoute') || content.includes('extractRealm');
  const hasStateUpdate = content.includes('setCurrentPillar') || content.includes('usePlatformState');
  
  return (hasRoutingUtils && hasStateUpdate) || 'TopNavBar not using routing utilities or state management';
});

// Test 4: Content page syncs route params
test('Content page syncs route params to state', () => {
  const filePath = join(PROJECT_ROOT, 'symphainy-frontend/app/(protected)/pillars/content/page.tsx');
  if (!existsSync(filePath)) {
    return 'content/page.tsx not found';
  }
  
  const content = readFileSync(filePath, 'utf-8');
  const hasSync = content.includes('syncRouteToState') || content.includes('useSearchParams');
  const hasSuspense = content.includes('Suspense');
  
  return (hasSync && hasSuspense) || 'Content page not syncing route params to state';
});

// Test 5: Pillar data has correct route
test('Pillar data has correct journey route', () => {
  const filePath = join(PROJECT_ROOT, 'symphainy-frontend/shared/data/pillars.ts');
  if (!existsSync(filePath)) {
    return 'pillars.ts not found';
  }
  
  const content = readFileSync(filePath, 'utf-8');
  const hasCorrectRoute = content.includes('/pillars/journey') && !content.includes('/pillars/operation');
  
  return hasCorrectRoute || 'Pillar data has incorrect route (should be /pillars/journey, not /pillars/operation)';
});

// Test 6: PlatformStateProvider has realm state methods
test('PlatformStateProvider has realm state methods', () => {
  const filePath = join(PROJECT_ROOT, 'symphainy-frontend/shared/state/PlatformStateProvider.tsx');
  if (!existsSync(filePath)) {
    return 'PlatformStateProvider.tsx not found';
  }
  
  const content = readFileSync(filePath, 'utf-8');
  const hasSetRealmState = content.includes('setRealmState');
  const hasGetRealmState = content.includes('getRealmState');
  const hasSetCurrentPillar = content.includes('setCurrentPillar');
  
  return (hasSetRealmState && hasGetRealmState && hasSetCurrentPillar) || 'PlatformStateProvider missing realm state methods';
});

// Test 7: Routing audit document exists
test('Routing audit document exists', () => {
  const filePath1 = join(PROJECT_ROOT, 'docs/PHASE7_ROUTING_AUDIT.md');
  const filePath2 = join(PROJECT_ROOT, 'docs/PHASE7_ROUTE_AUDIT.md');
  return existsSync(filePath1) || existsSync(filePath2) || 'PHASE7 routing audit document not found';
});

// Test 8: Progress document exists
test('Progress document exists', () => {
  const filePath = join(PROJECT_ROOT, 'docs/PHASE7_PROGRESS.md');
  return existsSync(filePath) || 'PHASE7_PROGRESS.md not found';
});

// Print results
console.log('\nTest Results:');
console.log('-'.repeat(60));

let passed = 0;
let failed = 0;

results.forEach((result, index) => {
  const status = result.passed ? '✓' : '✗';
  const color = result.passed ? '\x1b[32m' : '\x1b[31m';
  const reset = '\x1b[0m';
  
  console.log(`${color}${status}${reset} [${index + 1}/${results.length}] ${result.name}`);
  if (!result.passed) {
    console.log(`    ${color}→${reset} ${result.message}`);
    failed++;
  } else {
    passed++;
  }
});

console.log('-'.repeat(60));
console.log(`\nSummary: ${passed} passed, ${failed} failed\n`);

if (failed === 0) {
  console.log('✓ All validation tests passed!');
  console.log('\nNext steps:');
  console.log('  1. Start containers: ./scripts/test-phase7-integration.sh');
  console.log('  2. Run full browser tests: npx playwright test test-phase7-routing.ts');
  console.log('  3. Manually test navigation and route syncing\n');
  process.exit(0);
} else {
  console.log('✗ Some validation tests failed');
  console.log('Please fix the issues before running integration tests\n');
  process.exit(1);
}
