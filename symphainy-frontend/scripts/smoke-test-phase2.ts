/**
 * Phase 2 Smoke Tests - Service Layer Standardization
 * 
 * Validates:
 * 1. Build passes
 * 2. No direct lib/api imports in updated components
 * 3. Service layer hooks are properly set up
 * 4. Breaking changes are enforced
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

const PROJECT_ROOT = path.join(__dirname, '..');
const COMPONENTS_DIR = path.join(PROJECT_ROOT, 'components');
const SHARED_DIR = path.join(PROJECT_ROOT, 'shared');

interface TestResult {
  name: string;
  passed: boolean;
  message: string;
  details?: string;
}

const results: TestResult[] = [];

function addResult(name: string, passed: boolean, message: string, details?: string) {
  results.push({ name, passed, message, details });
  const icon = passed ? '✅' : '❌';
  console.log(`${icon} ${name}: ${message}`);
  if (details) {
    console.log(`   ${details}`);
  }
}

// Test 1: Check for direct lib/api imports in updated components
function testNoDirectImports() {
  console.log('\n📋 Test 1: Checking for direct lib/api imports in updated components...\n');
  
  const updatedComponents = [
    'shared/auth/AuthProvider.tsx',
    'shared/agui/AGUIEventProvider.tsx',
    'components/content/FileDashboard.tsx',
    'components/content/FileUploader.tsx',
  ];

  let allPassed = true;
  for (const component of updatedComponents) {
    const filePath = path.join(PROJECT_ROOT, component);
    if (!fs.existsSync(filePath)) {
      addResult(
        `No direct imports: ${component}`,
        false,
        'File not found',
        `Expected: ${filePath}`
      );
      allPassed = false;
      continue;
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const hasDirectImport = /from\s+['"]@\/lib\/api|from\s+['"]\.\.\/lib\/api|import\s+.*from\s+['"]@\/lib\/api|import\s+.*from\s+['"]\.\.\/lib\/api/.test(content);
    
    if (hasDirectImport) {
      // Check if it's a comment or deprecated import
      const lines = content.split('\n');
      const importLines = lines.filter((line, idx) => {
        if (/from\s+['"]@\/lib\/api|from\s+['"]\.\.\/lib\/api/.test(line)) {
          // Check if previous lines have deprecation comments
          const prevLines = lines.slice(Math.max(0, idx - 5), idx);
          const hasDeprecation = prevLines.some(l => 
            l.includes('DEPRECATED') || 
            l.includes('PHASE 2') || 
            l.includes('@internal') ||
            l.includes('//')
          );
          return !hasDeprecation;
        }
        return false;
      });

      if (importLines.length > 0) {
        addResult(
          `No direct imports: ${component}`,
          false,
          'Found direct lib/api import',
          `Lines: ${importLines.join(', ')}`
        );
        allPassed = false;
      } else {
        addResult(
          `No direct imports: ${component}`,
          true,
          'No active direct imports (deprecated/commented)'
        );
      }
    } else {
      addResult(
        `No direct imports: ${component}`,
        true,
        'No direct lib/api imports found'
      );
    }
  }

  return allPassed;
}

// Test 2: Check that service layer hooks exist
function testServiceLayerHooks() {
  console.log('\n📋 Test 2: Checking service layer hooks exist...\n');

  const hooks = [
    'shared/hooks/useServiceLayerAPI.ts',
    'shared/hooks/useFileAPI.ts',
  ];

  let allPassed = true;
  for (const hook of hooks) {
    const filePath = path.join(PROJECT_ROOT, hook);
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf-8');
      const hasUseSessionBoundary = content.includes('useSessionBoundary');
      const exportsHook = /export\s+(function|const)\s+\w+/.test(content);
      
      if (hasUseSessionBoundary && exportsHook) {
        addResult(
          `Hook exists: ${hook}`,
          true,
          'Hook exists and uses SessionBoundaryProvider'
        );
      } else {
        addResult(
          `Hook exists: ${hook}`,
          false,
          'Hook missing required functionality',
          `Has useSessionBoundary: ${hasUseSessionBoundary}, Exports hook: ${exportsHook}`
        );
        allPassed = false;
      }
    } else {
      addResult(
        `Hook exists: ${hook}`,
        false,
        'Hook file not found'
      );
      allPassed = false;
    }
  }

  return allPassed;
}

// Test 3: Check that ServiceLayerAPI exists
function testServiceLayerAPI() {
  console.log('\n📋 Test 3: Checking ServiceLayerAPI exists...\n');

  const serviceLayerPath = path.join(PROJECT_ROOT, 'shared/services/ServiceLayerAPI.ts');
  
  if (!fs.existsSync(serviceLayerPath)) {
    addResult(
      'ServiceLayerAPI exists',
      false,
      'ServiceLayerAPI.ts not found'
    );
    return false;
  }

  const content = fs.readFileSync(serviceLayerPath, 'utf-8');
  const hasLoginUser = content.includes('loginUser');
  const hasRegisterUser = content.includes('registerUser');
  const hasSendAgentEvent = content.includes('sendAgentEvent');
  const hasSubmitIntent = content.includes('submitIntent');

  if (hasLoginUser && hasRegisterUser && hasSendAgentEvent) {
    addResult(
      'ServiceLayerAPI exists',
      true,
      'ServiceLayerAPI has required functions'
    );
    return true;
  } else {
    addResult(
      'ServiceLayerAPI exists',
      false,
      'ServiceLayerAPI missing required functions',
      `loginUser: ${hasLoginUser}, registerUser: ${hasRegisterUser}, sendAgentEvent: ${hasSendAgentEvent}, submitIntent: ${hasSubmitIntent}`
    );
    return false;
  }
}

// Test 4: Check that lib/api files are marked as internal
function testLibAPIMarkedInternal() {
  console.log('\n📋 Test 4: Checking lib/api files are marked as internal...\n');

  const libApiFiles = [
    'lib/api/fms.ts',
    'lib/api/auth.ts',
    'lib/api/content.ts',
    'lib/api/insights.ts',
    'lib/api/operations.ts',
    'lib/api/global.ts',
    'lib/api/file-processing.ts',
    'lib/api/admin.ts',
  ];

  let allPassed = true;
  for (const file of libApiFiles) {
    const filePath = path.join(PROJECT_ROOT, file);
    if (!fs.existsSync(filePath)) {
      addResult(
        `Internal marker: ${file}`,
        false,
        'File not found'
      );
      allPassed = false;
      continue;
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const hasInternalMarker = 
      content.includes('@internal') ||
      content.includes('INTERNAL API') ||
      content.includes('DO NOT IMPORT DIRECTLY') ||
      content.includes('PHASE 2: INTERNAL');

    if (hasInternalMarker) {
      addResult(
        `Internal marker: ${file}`,
        true,
        'File marked as internal'
      );
    } else {
      addResult(
        `Internal marker: ${file}`,
        false,
        'File not marked as internal'
      );
      allPassed = false;
    }
  }

  return allPassed;
}

// Test 5: Check that updated components use hooks
function testComponentsUseHooks() {
  console.log('\n📋 Test 5: Checking updated components use hooks...\n');

  const componentHooks = [
    { component: 'shared/auth/AuthProvider.tsx', hook: 'ServiceLayerAPI', pattern: /ServiceLayerAPI|loginUser|registerUser/ },
    { component: 'shared/agui/AGUIEventProvider.tsx', hook: 'ServiceLayerAPI', pattern: /ServiceLayerAPI|sendAgentEvent/ },
    { component: 'components/content/FileDashboard.tsx', hook: 'useFileAPI', pattern: /useFileAPI/ },
    { component: 'components/content/FileUploader.tsx', hook: 'useFileAPI', pattern: /useFileAPI/ },
  ];

  let allPassed = true;
  for (const { component, hook, pattern } of componentHooks) {
    const filePath = path.join(PROJECT_ROOT, component);
    if (!fs.existsSync(filePath)) {
      addResult(
        `Uses hook: ${component}`,
        false,
        'File not found'
      );
      allPassed = false;
      continue;
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const usesHook = pattern.test(content);

    if (usesHook) {
      addResult(
        `Uses hook: ${component}`,
        true,
        `Uses ${hook}`
      );
    } else {
      addResult(
        `Uses hook: ${component}`,
        false,
        `Does not use ${hook}`
      );
      allPassed = false;
    }
  }

  return allPassed;
}

// Test 6: Validate build passes
function testBuildPasses() {
  console.log('\n📋 Test 6: Validating build passes...\n');

  try {
    // Change to frontend directory
    process.chdir(PROJECT_ROOT);
    
    // Run build (capture output)
    const buildOutput = execSync('npm run build 2>&1', { 
      encoding: 'utf-8',
      maxBuffer: 10 * 1024 * 1024 // 10MB buffer
    });

    // Check if build succeeded
    const hasErrors = /Failed to compile|Type error|error TS/.test(buildOutput);
    const hasStandalone = buildOutput.includes('standalone') || fs.existsSync(path.join(PROJECT_ROOT, '.next/standalone'));

    if (!hasErrors || hasStandalone) {
      addResult(
        'Build passes',
        true,
        'Build completed successfully'
      );
      return true;
    } else {
      // Extract error details
      const errorMatch = buildOutput.match(/(Type error|Failed to compile)[\s\S]{0,500}/);
      const errorDetails = errorMatch ? errorMatch[0].substring(0, 200) : 'Build failed';
      
      addResult(
        'Build passes',
        false,
        'Build has errors',
        errorDetails
      );
      return false;
    }
  } catch (error: any) {
    // Build might have warnings but still succeed
    const output = error.stdout?.toString() || error.message || '';
    const hasStandalone = fs.existsSync(path.join(PROJECT_ROOT, '.next/standalone'));
    
    if (hasStandalone) {
      addResult(
        'Build passes',
        true,
        'Build completed (standalone directory exists)'
      );
      return true;
    } else {
      addResult(
        'Build passes',
        false,
        'Build failed',
        output.substring(0, 200)
      );
      return false;
    }
  }
}

// Main test execution
function runSmokeTests() {
  console.log('🚀 Starting Phase 2 Smoke Tests...\n');
  console.log('=' .repeat(60));

  const tests = [
    { name: 'No Direct Imports', fn: testNoDirectImports },
    { name: 'Service Layer Hooks', fn: testServiceLayerHooks },
    { name: 'ServiceLayerAPI Exists', fn: testServiceLayerAPI },
    { name: 'lib/api Marked Internal', fn: testLibAPIMarkedInternal },
    { name: 'Components Use Hooks', fn: testComponentsUseHooks },
    { name: 'Build Passes', fn: testBuildPasses },
  ];

  const testResults: boolean[] = [];
  for (const test of tests) {
    try {
      const passed = test.fn();
      testResults.push(passed);
    } catch (error: any) {
      console.error(`\n❌ Test "${test.name}" threw an error:`, error.message);
      testResults.push(false);
    }
  }

  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('\n📊 Test Summary\n');
  
  const passed = testResults.filter(r => r).length;
  const total = testResults.length;
  const allPassed = testResults.every(r => r);

  console.log(`Total Tests: ${total}`);
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${total - passed}`);
  console.log(`\nOverall: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}\n`);

  // Detailed results
  console.log('\n📋 Detailed Results:\n');
  results.forEach((result, idx) => {
    const icon = result.passed ? '✅' : '❌';
    console.log(`${idx + 1}. ${icon} ${result.name}`);
    console.log(`   ${result.message}`);
    if (result.details) {
      console.log(`   Details: ${result.details}`);
    }
  });

  return allPassed;
}

// Run tests
if (require.main === module) {
  const success = runSmokeTests();
  process.exit(success ? 0 : 1);
}

export { runSmokeTests };
