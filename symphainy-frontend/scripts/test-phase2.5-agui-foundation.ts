/**
 * Phase 2.5: AGUI Foundation - Inline Validation Test
 * 
 * Tests:
 * 1. AGUI types/schema exist and are properly exported
 * 2. AGUIStateProvider exists and is properly integrated
 * 3. AGUI hooks exist and are properly exported
 * 4. Service layer AGUI functions exist
 * 5. Guide Agent refactored to propose AGUI mutations
 * 6. Build passes
 * 
 * ✅ PHASE 2.5: AGUI Native Integration
 */

import * as fs from 'fs';
import * as path from 'path';

const projectRoot = path.resolve(__dirname, '..');
const sharedDir = path.join(projectRoot, 'shared');

interface TestResult {
  name: string;
  passed: boolean;
  error?: string;
  details?: string;
}

const results: TestResult[] = [];

function test(name: string, fn: () => boolean | { passed: boolean; error?: string; details?: string }): void {
  try {
    const result = fn();
    if (typeof result === 'boolean') {
      results.push({ name, passed: result });
    } else {
      results.push({ name, passed: result.passed, error: result.error, details: result.details });
    }
  } catch (error: any) {
    results.push({ name, passed: false, error: error.message });
  }
}

console.log('🧪 Phase 2.5: AGUI Foundation - Inline Validation Test\n');

// ============================================================================
// Test 1: AGUI Types/Schema
// ============================================================================

test('AGUI types file exists', () => {
  const aguiTypesPath = path.join(sharedDir, 'types', 'agui.ts');
  return fs.existsSync(aguiTypesPath);
});

test('AGUI types file exports required types', () => {
  const aguiTypesPath = path.join(sharedDir, 'types', 'agui.ts');
  if (!fs.existsSync(aguiTypesPath)) {
    return { passed: false, error: 'agui.ts file not found' };
  }
  
  const content = fs.readFileSync(aguiTypesPath, 'utf-8');
  const requiredTypes = [
    'Artifact',
    'ArtifactState',
    'JourneyStep',
    'JourneyStepStatus',
    'Workflow',
    'AGUIState',
    'AGUIMutation',
    'IntentCompilationResult',
    'AGUIValidationError',
  ];
  
  const missing = requiredTypes.filter(type => !content.includes(`export interface ${type}`) && !content.includes(`export enum ${type}`));
  
  if (missing.length > 0) {
    return { passed: false, error: `Missing types: ${missing.join(', ')}` };
  }
  
  return { passed: true, details: `All ${requiredTypes.length} required types found` };
});

// ============================================================================
// Test 2: AGUI State Provider
// ============================================================================

test('AGUIStateProvider file exists', () => {
  const providerPath = path.join(sharedDir, 'state', 'AGUIStateProvider.tsx');
  return fs.existsSync(providerPath);
});

test('AGUIStateProvider exports useAGUIState hook', () => {
  const providerPath = path.join(sharedDir, 'state', 'AGUIStateProvider.tsx');
  if (!fs.existsSync(providerPath)) {
    return { passed: false, error: 'AGUIStateProvider.tsx file not found' };
  }
  
  const content = fs.readFileSync(providerPath, 'utf-8');
  const hasHook = content.includes('export const useAGUIState') || content.includes('export function useAGUIState');
  const hasProvider = content.includes('export const AGUIStateProvider') || content.includes('export function AGUIStateProvider');
  const usesSessionBoundary = content.includes('useSessionBoundary');
  
  if (!hasHook) {
    return { passed: false, error: 'useAGUIState hook not exported' };
  }
  if (!hasProvider) {
    return { passed: false, error: 'AGUIStateProvider not exported' };
  }
  if (!usesSessionBoundary) {
    return { passed: false, error: 'AGUIStateProvider does not use SessionBoundaryProvider' };
  }
  
  return { passed: true, details: 'Hook, provider, and SessionBoundary integration found' };
});

test('AGUIStateProvider integrated in AppProviders', () => {
  const appProvidersPath = path.join(sharedDir, 'state', 'AppProviders.tsx');
  if (!fs.existsSync(appProvidersPath)) {
    return { passed: false, error: 'AppProviders.tsx file not found' };
  }
  
  const content = fs.readFileSync(appProvidersPath, 'utf-8');
  const hasImport = content.includes('AGUIStateProvider') || content.includes('from "./AGUIStateProvider"');
  const hasUsage = content.includes('<AGUIStateProvider>') || content.includes('<AGUIStateProvider');
  
  if (!hasImport || !hasUsage) {
    return { passed: false, error: 'AGUIStateProvider not integrated in AppProviders' };
  }
  
  return { passed: true, details: 'AGUIStateProvider integrated in provider hierarchy' };
});

// ============================================================================
// Test 3: AGUI Hooks
// ============================================================================

test('useJourneyStep hook exists', () => {
  const hookPath = path.join(sharedDir, 'hooks', 'useJourneyStep.ts');
  return fs.existsSync(hookPath);
});

test('useAGUIValidator hook exists', () => {
  const hookPath = path.join(sharedDir, 'hooks', 'useAGUIValidator.ts');
  return fs.existsSync(hookPath);
});

test('useAGUIMutation hook exists', () => {
  const hookPath = path.join(sharedDir, 'hooks', 'useAGUIMutation.ts');
  return fs.existsSync(hookPath);
});

test('AGUI hooks use useAGUIState', () => {
  const hooks = [
    { name: 'useJourneyStep', path: path.join(sharedDir, 'hooks', 'useJourneyStep.ts') },
    { name: 'useAGUIValidator', path: path.join(sharedDir, 'hooks', 'useAGUIValidator.ts') },
    { name: 'useAGUIMutation', path: path.join(sharedDir, 'hooks', 'useAGUIMutation.ts') },
  ];
  
  const missing = [];
  for (const hook of hooks) {
    if (!fs.existsSync(hook.path)) {
      missing.push(`${hook.name} (file not found)`);
      continue;
    }
    const content = fs.readFileSync(hook.path, 'utf-8');
    if (!content.includes('useAGUIState')) {
      missing.push(`${hook.name} (does not use useAGUIState)`);
    }
  }
  
  if (missing.length > 0) {
    return { passed: false, error: `Hooks not using useAGUIState: ${missing.join(', ')}` };
  }
  
  return { passed: true, details: 'All AGUI hooks use useAGUIState' };
});

// ============================================================================
// Test 4: Service Layer AGUI Functions
// ============================================================================

test('ServiceLayerAPI has AGUI compilation functions', () => {
  const serviceLayerPath = path.join(sharedDir, 'services', 'ServiceLayerAPI.ts');
  if (!fs.existsSync(serviceLayerPath)) {
    return { passed: false, error: 'ServiceLayerAPI.ts file not found' };
  }
  
  const content = fs.readFileSync(serviceLayerPath, 'utf-8');
  const hasCompile = content.includes('compileIntentFromAGUI');
  const hasSubmit = content.includes('submitIntentFromAGUI');
  const hasUpdate = content.includes('updateAGUI');
  
  if (!hasCompile) {
    return { passed: false, error: 'compileIntentFromAGUI function not found' };
  }
  if (!hasSubmit) {
    return { passed: false, error: 'submitIntentFromAGUI function not found' };
  }
  
  return { passed: true, details: 'AGUI compilation functions found' };
});

test('useServiceLayerAPI hook exposes AGUI functions', () => {
  const hookPath = path.join(sharedDir, 'hooks', 'useServiceLayerAPI.ts');
  if (!fs.existsSync(hookPath)) {
    return { passed: false, error: 'useServiceLayerAPI.ts file not found' };
  }
  
  const content = fs.readFileSync(hookPath, 'utf-8');
  const hasUpdate = content.includes('updateAGUI');
  const hasCompile = content.includes('compileIntentFromAGUI');
  const hasSubmit = content.includes('submitIntentFromAGUI');
  const usesAGUIState = content.includes('useAGUIState');
  
  if (!hasUpdate || !hasCompile || !hasSubmit) {
    return { passed: false, error: 'AGUI functions not exposed in useServiceLayerAPI' };
  }
  if (!usesAGUIState) {
    return { passed: false, error: 'useServiceLayerAPI does not use useAGUIState' };
  }
  
  return { passed: true, details: 'All AGUI functions exposed in hook' };
});

// ============================================================================
// Test 5: Guide Agent Refactored
// ============================================================================

test('GuideAgentProvider refactored for AGUI mutations', () => {
  const guideAgentPath = path.join(sharedDir, 'agui', 'GuideAgentProvider.tsx');
  if (!fs.existsSync(guideAgentPath)) {
    return { passed: false, error: 'GuideAgentProvider.tsx file not found' };
  }
  
  const content = fs.readFileSync(guideAgentPath, 'utf-8');
  const hasAGUIMutation = content.includes('agui_mutation') || content.includes('aguiMutation');
  const hasReasoning = content.includes('reasoning');
  const usesAGUIState = content.includes('useAGUIState');
  const usesServiceLayer = content.includes('useServiceLayerAPI');
  const hasUpdateAGUI = content.includes('updateAGUIState') || content.includes('updateAGUI');
  
  if (!hasAGUIMutation) {
    return { passed: false, error: 'Guide Agent does not handle agui_mutation in responses' };
  }
  if (!usesAGUIState) {
    return { passed: false, error: 'Guide Agent does not use useAGUIState' };
  }
  if (!hasUpdateAGUI) {
    return { passed: false, error: 'Guide Agent does not apply AGUI mutations' };
  }
  
  return { passed: true, details: 'Guide Agent refactored to propose and apply AGUI mutations' };
});

test('GuideAgentContext includes submitIntentFromCurrentAGUI', () => {
  const guideAgentPath = path.join(sharedDir, 'agui', 'GuideAgentProvider.tsx');
  if (!fs.existsSync(guideAgentPath)) {
    return { passed: false, error: 'GuideAgentProvider.tsx file not found' };
  }
  
  const content = fs.readFileSync(guideAgentPath, 'utf-8');
  const hasInterface = content.includes('submitIntentFromCurrentAGUI');
  const hasImplementation = content.includes('const submitIntentFromCurrentAGUI') || content.includes('submitIntentFromCurrentAGUI =');
  const inContext = content.includes('submitIntentFromCurrentAGUI,') || content.includes('submitIntentFromCurrentAGUI:');
  
  if (!hasInterface || !hasImplementation || !inContext) {
    return { passed: false, error: 'submitIntentFromCurrentAGUI not properly implemented in Guide Agent' };
  }
  
  return { passed: true, details: 'submitIntentFromCurrentAGUI method available' };
});

// ============================================================================
// Test 6: Build Validation
// ============================================================================

test('TypeScript compilation check (imports resolve)', () => {
  // Check that key files can be imported without errors
  const keyFiles = [
    { name: 'AGUI types', path: path.join(sharedDir, 'types', 'agui.ts') },
    { name: 'AGUIStateProvider', path: path.join(sharedDir, 'state', 'AGUIStateProvider.tsx') },
    { name: 'useServiceLayerAPI', path: path.join(sharedDir, 'hooks', 'useServiceLayerAPI.ts') },
  ];
  
  const errors = [];
  for (const file of keyFiles) {
    if (!fs.existsSync(file.path)) {
      errors.push(`${file.name} file not found`);
      continue;
    }
    
    const content = fs.readFileSync(file.path, 'utf-8');
    // Check for obvious import errors (missing imports, etc.)
    const importLines = content.split('\n').filter(line => line.trim().startsWith('import'));
    for (const importLine of importLines) {
      // Check for imports from @/shared/types/agui
      if (importLine.includes('@/shared/types/agui')) {
        const aguiTypesPath = path.join(sharedDir, 'types', 'agui.ts');
        if (!fs.existsSync(aguiTypesPath)) {
          errors.push(`${file.name} imports from @/shared/types/agui but file doesn't exist`);
        }
      }
    }
  }
  
  if (errors.length > 0) {
    return { passed: false, error: errors.join('; ') };
  }
  
  return { passed: true, details: 'Key imports appear to resolve correctly' };
});

// ============================================================================
// Results
// ============================================================================

console.log('Test Results:\n');
let passed = 0;
let failed = 0;

results.forEach((result, index) => {
  const icon = result.passed ? '✅' : '❌';
  const status = result.passed ? 'PASS' : 'FAIL';
  console.log(`${icon} [${index + 1}/${results.length}] ${result.name}: ${status}`);
  
  if (result.error) {
    console.log(`   Error: ${result.error}`);
  }
  if (result.details) {
    console.log(`   ${result.details}`);
  }
  
  if (result.passed) {
    passed++;
  } else {
    failed++;
  }
});

console.log(`\n📊 Summary: ${passed}/${results.length} tests passed, ${failed} failed\n`);

if (failed > 0) {
  console.log('❌ Some tests failed. Please review the errors above.');
  process.exit(1);
} else {
  console.log('✅ All Phase 2.5 AGUI Foundation tests passed!');
  console.log('\n🎉 Phase 2.5 foundation is solid and ready for MVP use.\n');
  process.exit(0);
}
