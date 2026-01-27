/**
 * Quick Smoke Test - File Management Group
 * 
 * Validates the first implementations work correctly
 */

import * as fs from 'fs';
import * as path from 'path';

const PROJECT_ROOT = path.join(__dirname, '..');

interface TestResult {
  name: string;
  passed: boolean;
  message: string;
}

const results: TestResult[] = [];

function test(name: string, fn: () => boolean, message: string) {
  try {
    const passed = fn();
    results.push({ name, passed, message });
    console.log(`${passed ? '✅' : '❌'} ${name}: ${message}`);
  } catch (error: any) {
    results.push({ name, passed: false, message: `${message} - Error: ${error.message}` });
    console.log(`❌ ${name}: ${message} - Error: ${error.message}`);
  }
}

console.log('🚀 Quick Smoke Test - File Management Group\n');
console.log('='.repeat(60));

// Test 1: Hooks can be imported
test(
  'Hooks can be imported',
  () => {
    const useFileAPI = path.join(PROJECT_ROOT, 'shared/hooks/useFileAPI.ts');
    const useContentAPI = path.join(PROJECT_ROOT, 'shared/hooks/useContentAPI.ts');
    return fs.existsSync(useFileAPI) && fs.existsSync(useContentAPI);
  },
  'useFileAPI and useContentAPI hooks exist'
);

// Test 2: Updated components use hooks
test(
  'FileDashboard uses useFileAPI',
  () => {
    const file = path.join(PROJECT_ROOT, 'components/content/FileDashboard.tsx');
    const content = fs.readFileSync(file, 'utf-8');
    return content.includes('useFileAPI') && !content.includes('from "@/lib/api/fms"');
  },
  'FileDashboard imports useFileAPI, no direct lib/api imports'
);

test(
  'FileUploader uses useFileAPI',
  () => {
    const file = path.join(PROJECT_ROOT, 'components/content/FileUploader.tsx');
    const content = fs.readFileSync(file, 'utf-8');
    return content.includes('useFileAPI') && !content.includes('from "@/lib/api/fms"') && !content.includes('from "@/lib/api/file-processing"');
  },
  'FileUploader imports useFileAPI, no direct lib/api imports'
);

test(
  'ParsePreview uses useFileAPI',
  () => {
    const file = path.join(PROJECT_ROOT, 'components/content/ParsePreview.tsx');
    const content = fs.readFileSync(file, 'utf-8');
    return content.includes('useFileAPI') && !content.includes('from "@/lib/api/fms"');
  },
  'ParsePreview imports useFileAPI, no direct lib/api imports'
);

test(
  'SimpleFileDashboard uses useContentAPI',
  () => {
    const file = path.join(PROJECT_ROOT, 'components/content/SimpleFileDashboard.tsx');
    const content = fs.readFileSync(file, 'utf-8');
    return content.includes('useContentAPI') && !content.includes('from "@/lib/api/content"');
  },
  'SimpleFileDashboard imports useContentAPI, no direct lib/api imports'
);

// Test 3: Hooks use SessionBoundaryProvider
test(
  'useFileAPI uses SessionBoundaryProvider',
  () => {
    const file = path.join(PROJECT_ROOT, 'shared/hooks/useFileAPI.ts');
    const content = fs.readFileSync(file, 'utf-8');
    return content.includes('useSessionBoundary');
  },
  'useFileAPI hook uses SessionBoundaryProvider'
);

test(
  'useContentAPI uses SessionBoundaryProvider',
  () => {
    const file = path.join(PROJECT_ROOT, 'shared/hooks/useContentAPI.ts');
    const content = fs.readFileSync(file, 'utf-8');
    return content.includes('useSessionBoundary');
  },
  'useContentAPI hook uses SessionBoundaryProvider'
);

// Test 4: No manual token passing in updated components
test(
  'FileDashboard has no manual token passing',
  () => {
    const file = path.join(PROJECT_ROOT, 'components/content/FileDashboard.tsx');
    const content = fs.readFileSync(file, 'utf-8');
    // Should not have patterns like: listFiles(token) or await listFiles(guideSessionToken)
    const hasManualToken = /listFiles\(.*token|deleteFile\(.*token/.test(content);
    return !hasManualToken;
  },
  'FileDashboard does not pass tokens manually to API calls'
);

test(
  'FileUploader has no manual token passing',
  () => {
    const file = path.join(PROJECT_ROOT, 'components/content/FileUploader.tsx');
    const content = fs.readFileSync(file, 'utf-8');
    // Should not have: uploadAndProcessFile(..., token)
    const hasManualToken = /uploadAndProcessFile\([^)]*token/.test(content);
    return !hasManualToken;
  },
  'FileUploader does not pass tokens manually to API calls'
);

test(
  'ParsePreview has no manual token passing',
  () => {
    const file = path.join(PROJECT_ROOT, 'components/content/ParsePreview.tsx');
    const content = fs.readFileSync(file, 'utf-8');
    // Should not have: parseFile(uuid, token)
    const hasManualToken = /parseFile\([^)]*token/.test(content);
    return !hasManualToken;
  },
  'ParsePreview does not pass tokens manually to API calls'
);

test(
  'SimpleFileDashboard has no manual token passing',
  () => {
    const file = path.join(PROJECT_ROOT, 'components/content/SimpleFileDashboard.tsx');
    const content = fs.readFileSync(file, 'utf-8');
    // Should not have: listContentFiles(token)
    const hasManualToken = /listContentFiles\(.*token/.test(content);
    return !hasManualToken;
  },
  'SimpleFileDashboard does not pass tokens manually to API calls'
);

// Test 5: ServiceLayerAPI exists and has required functions
test(
  'ServiceLayerAPI has required functions',
  () => {
    const file = path.join(PROJECT_ROOT, 'shared/services/ServiceLayerAPI.ts');
    const content = fs.readFileSync(file, 'utf-8');
    return content.includes('loginUser') && 
           content.includes('registerUser') && 
           content.includes('sendAgentEvent');
  },
  'ServiceLayerAPI has loginUser, registerUser, sendAgentEvent'
);

// Summary
console.log('\n' + '='.repeat(60));
console.log('\n📊 Test Summary\n');

const passed = results.filter(r => r.passed).length;
const total = results.length;
const allPassed = results.every(r => r.passed);

console.log(`Total Tests: ${total}`);
console.log(`Passed: ${passed}`);
console.log(`Failed: ${total - passed}`);
console.log(`\nOverall: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}\n`);

if (!allPassed) {
  console.log('Failed Tests:');
  results.filter(r => !r.passed).forEach(r => {
    console.log(`  ❌ ${r.name}: ${r.message}`);
  });
}

process.exit(allPassed ? 0 : 1);
