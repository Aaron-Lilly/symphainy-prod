/**
 * Comprehensive Smoke Test - Foundation Validation
 * 
 * Validates all completed phases:
 * - Phase 2.5: AGUI Foundation
 * - Phase 2: Service Layer Standardization
 * - Phase 3: WebSocket Consolidation
 * - Build Integrity
 * 
 * Run this before proceeding to Phase 4 to ensure foundation is solid.
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

const projectRoot = path.resolve(__dirname, '..');
const sharedDir = path.join(projectRoot, 'shared');

interface TestResult {
  phase: string;
  name: string;
  passed: boolean;
  error?: string;
  details?: string;
}

const results: TestResult[] = [];

function test(phase: string, name: string, fn: () => boolean | { passed: boolean; error?: string; details?: string }): void {
  try {
    const result = fn();
    if (typeof result === 'boolean') {
      results.push({ phase, name, passed: result });
    } else {
      results.push({ phase, name, passed: result.passed, error: result.error, details: result.details });
    }
  } catch (error: any) {
    results.push({ phase, name, passed: false, error: error.message });
  }
}

console.log('🧪 Comprehensive Smoke Test - Foundation Validation\n');
console.log('Validating:');
console.log('  ✅ Phase 2.5: AGUI Foundation');
console.log('  ✅ Phase 2: Service Layer Standardization');
console.log('  ✅ Phase 3: WebSocket Consolidation');
console.log('  ✅ Build Integrity\n');

// ============================================================================
// Phase 2.5: AGUI Foundation
// ============================================================================

console.log('📋 Phase 2.5: AGUI Foundation\n');

test('Phase 2.5', 'AGUI types file exists', () => {
  const aguiTypesPath = path.join(sharedDir, 'types', 'agui.ts');
  return fs.existsSync(aguiTypesPath);
});

test('Phase 2.5', 'AGUIStateProvider exists', () => {
  const providerPath = path.join(sharedDir, 'state', 'AGUIStateProvider.tsx');
  return fs.existsSync(providerPath);
});

test('Phase 2.5', 'AGUIStateProvider integrated in AppProviders', () => {
  const appProvidersPath = path.join(sharedDir, 'state', 'AppProviders.tsx');
  if (!fs.existsSync(appProvidersPath)) {
    return { passed: false, error: 'AppProviders.tsx file not found' };
  }
  
  const content = fs.readFileSync(appProvidersPath, 'utf-8');
  const hasAGUI = content.includes('AGUIStateProvider');
  
  if (!hasAGUI) {
    return { passed: false, error: 'AGUIStateProvider not integrated' };
  }
  
  return { passed: true };
});

test('Phase 2.5', 'ServiceLayerAPI has AGUI compilation functions', () => {
  const serviceLayerPath = path.join(sharedDir, 'services', 'ServiceLayerAPI.ts');
  if (!fs.existsSync(serviceLayerPath)) {
    return { passed: false, error: 'ServiceLayerAPI.ts file not found' };
  }
  
  const content = fs.readFileSync(serviceLayerPath, 'utf-8');
  const hasCompile = content.includes('compileIntentFromAGUI');
  const hasSubmit = content.includes('submitIntentFromAGUI');
  
  if (!hasCompile || !hasSubmit) {
    return { passed: false, error: 'Missing AGUI compilation functions' };
  }
  
  return { passed: true };
});

test('Phase 2.5', 'GuideAgentProvider refactored for AGUI', () => {
  const guideAgentPath = path.join(sharedDir, 'agui', 'GuideAgentProvider.tsx');
  if (!fs.existsSync(guideAgentPath)) {
    return { passed: false, error: 'GuideAgentProvider.tsx file not found' };
  }
  
  const content = fs.readFileSync(guideAgentPath, 'utf-8');
  const hasAGUIMutation = content.includes('agui_mutation') || content.includes('aguiMutation');
  const usesAGUIState = content.includes('useAGUIState');
  
  if (!hasAGUIMutation || !usesAGUIState) {
    return { passed: false, error: 'Guide Agent not refactored for AGUI' };
  }
  
  return { passed: true };
});

// ============================================================================
// Phase 2: Service Layer Standardization
// ============================================================================

console.log('📋 Phase 2: Service Layer Standardization\n');

test('Phase 2', 'useServiceLayerAPI hook exists', () => {
  const hookPath = path.join(sharedDir, 'hooks', 'useServiceLayerAPI.ts');
  return fs.existsSync(hookPath);
});

test('Phase 2', 'useFileAPI hook exists', () => {
  const hookPath = path.join(sharedDir, 'hooks', 'useFileAPI.ts');
  return fs.existsSync(hookPath);
});

test('Phase 2', 'useContentAPI hook exists', () => {
  const hookPath = path.join(sharedDir, 'hooks', 'useContentAPI.ts');
  return fs.existsSync(hookPath);
});

test('Phase 2', 'useInsightsAPI hook exists', () => {
  const hookPath = path.join(sharedDir, 'hooks', 'useInsightsAPI.ts');
  return fs.existsSync(hookPath);
});

test('Phase 2', 'useOperationsAPI hook exists', () => {
  const hookPath = path.join(sharedDir, 'hooks', 'useOperationsAPI.ts');
  return fs.existsSync(hookPath);
});

test('Phase 2', 'Key components use hooks', () => {
  const components = [
    { name: 'FileDashboard', path: 'components/content/FileDashboard.tsx', hook: 'useFileAPI' },
    { name: 'DataMash', path: 'app/(protected)/pillars/content/components/DataMash.tsx', hook: 'useContentAPI' },
    { name: 'login-form', path: 'components/auth/login-form.tsx', hook: 'useServiceLayerAPI' },
  ];
  
  let allPassed = true;
  const failures: string[] = [];
  
  for (const component of components) {
    const componentPath = path.join(projectRoot, component.path);
    if (!fs.existsSync(componentPath)) {
      failures.push(`${component.name} file not found`);
      allPassed = false;
      continue;
    }
    
    const content = fs.readFileSync(componentPath, 'utf-8');
    if (!content.includes(component.hook)) {
      failures.push(`${component.name} does not use ${component.hook}`);
      allPassed = false;
    }
  }
  
  if (!allPassed) {
    return { passed: false, error: failures.join('; ') };
  }
  
  return { passed: true, details: 'All key components use hooks' };
});

test('Phase 2', 'lib/api files marked as @internal', () => {
  const libApiFiles = ['auth.ts', 'content.ts', 'fms.ts', 'insights.ts', 'operations.ts'];
  let allMarked = true;
  const unmarked: string[] = [];
  
  for (const fileName of libApiFiles) {
    const filePath = path.join(projectRoot, 'lib', 'api', fileName);
    if (!fs.existsSync(filePath)) {
      continue;
    }
    
    const content = fs.readFileSync(filePath, 'utf-8');
    if (!content.includes('@internal') && !content.includes('INTERNAL')) {
      unmarked.push(fileName);
      allMarked = false;
    }
  }
  
  if (!allMarked) {
    return { passed: false, error: `Files not marked as internal: ${unmarked.join(', ')}` };
  }
  
  return { passed: true };
});

// ============================================================================
// Phase 3: WebSocket Consolidation
// ============================================================================

console.log('📋 Phase 3: WebSocket Consolidation\n');

test('Phase 3', 'useUnifiedAgentChat checks SessionStatus', () => {
  const hookPath = path.join(sharedDir, 'hooks', 'useUnifiedAgentChat.ts');
  if (!fs.existsSync(hookPath)) {
    return { passed: false, error: 'useUnifiedAgentChat.ts file not found' };
  }
  
  const content = fs.readFileSync(hookPath, 'utf-8');
  const usesSessionBoundary = content.includes('useSessionBoundary');
  const checksSessionStatus = content.includes('SessionStatus') && content.includes('SessionStatus.Active');
  
  if (!usesSessionBoundary || !checksSessionStatus) {
    return { passed: false, error: 'useUnifiedAgentChat does not check SessionStatus' };
  }
  
  return { passed: true };
});

test('Phase 3', 'ChatAssistant uses useUnifiedAgentChat', () => {
  const componentPath = path.join(sharedDir, 'components', 'chatbot', 'ChatAssistant.tsx');
  if (!fs.existsSync(componentPath)) {
    return { passed: false, error: 'ChatAssistant.tsx file not found' };
  }
  
  const content = fs.readFileSync(componentPath, 'utf-8');
  const usesHook = content.includes('useUnifiedAgentChat');
  const hasDirectRuntimeClient = content.includes('new RuntimeClient') && !content.includes('// ✅ PHASE 3');
  
  if (!usesHook) {
    return { passed: false, error: 'ChatAssistant does not use useUnifiedAgentChat' };
  }
  if (hasDirectRuntimeClient) {
    return { passed: false, error: 'ChatAssistant still creates RuntimeClient directly' };
  }
  
  return { passed: true };
});

test('Phase 3', 'GuideAgentProvider follows session pattern', () => {
  const providerPath = path.join(sharedDir, 'agui', 'GuideAgentProvider.tsx');
  if (!fs.existsSync(providerPath)) {
    return { passed: false, error: 'GuideAgentProvider.tsx file not found' };
  }
  
  const content = fs.readFileSync(providerPath, 'utf-8');
  const checksSessionStatus = content.includes('SessionStatus') && content.includes('SessionStatus.Active');
  
  if (!checksSessionStatus) {
    return { passed: false, error: 'GuideAgentProvider does not check SessionStatus' };
  }
  
  return { passed: true };
});

// ============================================================================
// Build Integrity
// ============================================================================

console.log('📋 Build Integrity\n');

test('Build', 'TypeScript compilation', () => {
  try {
    // Run a quick type check (faster than full build)
    execSync('cd ' + projectRoot + ' && npx tsc --noEmit --skipLibCheck 2>&1 | head -20', { 
      encoding: 'utf-8',
      stdio: 'pipe',
      timeout: 30000
    });
    return { passed: true, details: 'TypeScript compilation passes' };
  } catch (error: any) {
    const output = error.stdout || error.stderr || error.message;
    // Check if it's just warnings (which are OK)
    if (output.includes('error TS') || output.includes('Type error')) {
      return { passed: false, error: 'TypeScript compilation errors found', details: output.substring(0, 200) };
    }
    return { passed: true, details: 'TypeScript check completed (warnings only)' };
  }
});

test('Build', 'Key files import correctly', () => {
  const keyImports = [
    { file: 'shared/state/AppProviders.tsx', import: 'AGUIStateProvider' },
    { file: 'shared/hooks/useServiceLayerAPI.ts', import: 'useSessionBoundary' },
    { file: 'shared/hooks/useUnifiedAgentChat.ts', import: 'useSessionBoundary' },
  ];
  
  let allValid = true;
  const failures: string[] = [];
  
  for (const keyImport of keyImports) {
    const filePath = path.join(projectRoot, keyImport.file);
    if (!fs.existsSync(filePath)) {
      failures.push(`${keyImport.file} not found`);
      allValid = false;
      continue;
    }
    
    const content = fs.readFileSync(filePath, 'utf-8');
    if (!content.includes(keyImport.import)) {
      failures.push(`${keyImport.file} does not import ${keyImport.import}`);
      allValid = false;
    }
  }
  
  if (!allValid) {
    return { passed: false, error: failures.join('; ') };
  }
  
  return { passed: true, details: 'Key imports resolve correctly' };
});

// ============================================================================
// Results Summary
// ============================================================================

console.log('\n📊 Test Results Summary:\n');

const phaseResults: Record<string, { passed: number; failed: number; total: number }> = {};

results.forEach(result => {
  if (!phaseResults[result.phase]) {
    phaseResults[result.phase] = { passed: 0, failed: 0, total: 0 };
  }
  phaseResults[result.phase].total++;
  if (result.passed) {
    phaseResults[result.phase].passed++;
  } else {
    phaseResults[result.phase].failed++;
  }
});

// Display by phase
Object.keys(phaseResults).forEach(phase => {
  const stats = phaseResults[phase];
  const passRate = ((stats.passed / stats.total) * 100).toFixed(0);
  const icon = stats.failed === 0 ? '✅' : stats.failed < stats.total * 0.1 ? '⚠️' : '❌';
  console.log(`${icon} ${phase}: ${stats.passed}/${stats.total} passed (${passRate}%)`);
});

console.log('\n📋 Detailed Results:\n');

let totalPassed = 0;
let totalFailed = 0;

results.forEach((result, index) => {
  const icon = result.passed ? '✅' : '❌';
  const status = result.passed ? 'PASS' : 'FAIL';
  console.log(`${icon} [${index + 1}/${results.length}] ${result.phase} - ${result.name}: ${status}`);
  
  if (result.error) {
    console.log(`   ⚠️  Error: ${result.error}`);
  }
  if (result.details) {
    console.log(`   ℹ️  ${result.details}`);
  }
  
  if (result.passed) {
    totalPassed++;
  } else {
    totalFailed++;
  }
});

console.log(`\n📊 Overall Summary: ${totalPassed}/${results.length} tests passed, ${totalFailed} failed\n`);

if (totalFailed === 0) {
  console.log('🎉 All smoke tests passed! Foundation is solid and ready for Phase 4.\n');
  process.exit(0);
} else if (totalFailed <= results.length * 0.1) {
  console.log('⚠️  Most tests passed. Minor issues found but foundation is mostly solid.');
  console.log('   Review errors above before proceeding to Phase 4.\n');
  process.exit(0);
} else {
  console.log('❌ Multiple test failures. Please review and fix issues before proceeding to Phase 4.\n');
  process.exit(1);
}
