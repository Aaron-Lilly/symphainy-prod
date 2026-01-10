/**
 * Global Teardown for Playwright E2E Tests
 * 
 * This file runs once after all tests to clean up the test environment
 */

import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Cleaning up global test environment...');
  
  // Clean up test files (optional - uncomment if you want to clean up)
  // const testFilesDir = path.join(process.cwd(), 'test-files');
  // if (fs.existsSync(testFilesDir)) {
  //   fs.rmSync(testFilesDir, { recursive: true, force: true });
  //   console.log('🗑️  Cleaned up test files');
  // }
  
  console.log('✅ Global teardown complete');
}

export default globalTeardown; 