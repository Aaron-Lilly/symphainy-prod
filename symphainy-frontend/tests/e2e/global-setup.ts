/**
 * Global Setup for Playwright E2E Tests
 * 
 * This file runs once before all tests to:
 * 1. Set up test files
 * 2. Authenticate once and save state for reuse in all tests
 * 
 * Following best practices: Authenticate once, reuse state for speed
 */

import { chromium, FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

async function globalSetup(config: FullConfig) {
  console.log('🔧 Setting up global test environment...');
  
  // Create test files directory if it doesn't exist
  const testFilesDir = path.join(process.cwd(), 'test-files');
  if (!fs.existsSync(testFilesDir)) {
    fs.mkdirSync(testFilesDir, { recursive: true });
  }
  
  // Create test files if they don't exist
  const testFiles = [
    {
      name: 'sample.csv',
      content: `Name,Age,Email,Status
John Doe,30,john@example.com,Active
Jane Smith,25,jane@example.com,Inactive
Bob Johnson,35,bob@example.com,Active
Alice Brown,28,alice@example.com,Active
Charlie Wilson,42,charlie@example.com,Inactive`
    },
    {
      name: 'mainframe.bin',
      content: Buffer.from([0x01, 0x02, 0x03, 0x04, 0x05]).toString('base64')
    },
    {
      name: 'copybook.cpy',
      content: `       01  CUSTOMER-RECORD.
           05  CUSTOMER-ID        PIC X(10).
           05  CUSTOMER-NAME      PIC X(50).
           05  CUSTOMER-ADDRESS   PIC X(100).
           05  CUSTOMER-PHONE     PIC X(15).
           05  CUSTOMER-EMAIL     PIC X(50).
           05  CUSTOMER-STATUS    PIC X(1).`
    },
    {
      name: 'corrupted.csv',
      content: `Name,Age,Email,Status
John Doe,30,john@example.com,Active
Jane Smith,25,jane@example.com,Inactive
Bob Johnson,35,bob@example.com,Active
Alice Brown,28,alice@example.com,Active
Charlie Wilson,42,charlie@example.com,Inactive
Invalid,Row,With,Extra,Columns`
    }
  ];
  
  // Write test files
  for (const file of testFiles) {
    const filePath = path.join(testFilesDir, file.name);
    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, file.content);
      console.log(`📄 Created test file: ${file.name}`);
    }
  }
  
  // ============================================
  // AUTHENTICATION SETUP (Best Practice)
  // ============================================
  // Authenticate once and save state for reuse in all tests
  // This avoids repeating authentication in every test, making tests faster
  
  const baseURL = config.projects[0]?.use?.baseURL || 'http://localhost:3000';
  const backendURL = process.env.TEST_BACKEND_URL || 'http://localhost:8000';
  
  // Get test credentials from environment or use defaults
  // Using pre-confirmed test user (testuser0@symphainy.com)
  // Other test users available: testuser1-3@symphainy.com for UAT/demos
  const testEmail = process.env.E2E_TEST_EMAIL || 'testuser0@symphainy.com';
  const testPassword = process.env.E2E_TEST_PASSWORD || 'TestPassword123!';
  
  console.log('🔐 Setting up authentication...');
  
  try {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Strategy 1: Authenticate via API (faster, more reliable)
    try {
      console.log('   Attempting API authentication...');
      
      // First, try to register the user (in case they don't exist)
      try {
        const registerResponse = await page.request.post(`${backendURL}/api/auth/register`, {
          data: {
            name: 'E2E Test User',
            email: testEmail,
            password: testPassword
          },
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (registerResponse.ok()) {
          console.log('   ✅ Test user registered');
        } else {
          const registerError = await registerResponse.text();
          // User might already exist, which is fine
          if (!registerError.includes('already exists') && !registerError.includes('already registered')) {
            console.log(`   ⚠️  Registration failed (non-critical): ${registerError}`);
          }
        }
      } catch (registerError) {
        // Registration failed, but continue with login attempt
        console.log('   ⚠️  Registration attempt failed (non-critical), continuing with login...');
      }
      
      // Now try to login
      const response = await page.request.post(`${backendURL}/api/auth/login`, {
        data: {
          email: testEmail,
          password: testPassword
        },
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok()) {
        const authData = await response.json();
        
        // Navigate to the app to establish session context
        await page.goto(baseURL);
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(2000); // Wait for React to hydrate
        
        // Set authentication state in localStorage (after page load to avoid SecurityError)
        // The AuthProvider reads from localStorage on mount
        const actualToken = authData.access_token || authData.token;
        if (!actualToken) {
          throw new Error('No token received from authentication response');
        }
        
        await page.evaluate((data) => {
          if (data.access_token || data.token) {
            localStorage.setItem('auth_token', data.access_token || data.token);
          }
          if (data.user) {
            localStorage.setItem('user_data', JSON.stringify({
              id: data.user.id || data.user.user_id,
              email: data.user.email,
              name: data.user.name || data.user.email?.split('@')[0] || 'Test User'
            }));
          }
        }, authData);
        
        // Wait a bit for AuthProvider to process the localStorage values
        await page.waitForTimeout(1000);
        
        // Verify authentication state is set
        const authToken = await page.evaluate(() => localStorage.getItem('auth_token'));
        if (!authToken || authToken === 'token_placeholder') {
          throw new Error('Authentication token not properly set in localStorage');
        }
        
        console.log('   ✅ API authentication successful');
      } else {
        throw new Error(`API auth failed: ${response.status()}`);
      }
    } catch (apiError) {
      // Strategy 2: Fallback to UI authentication
      console.log('   API auth failed, trying UI authentication...');
      await page.goto(baseURL);
      
      // Wait for page to load
      await page.waitForLoadState('networkidle');
      
      // Look for login form or try to navigate to login
      const loginButton = page.locator('text=/log in|sign in/i').first();
      const loginForm = page.locator('[data-testid*="login"], [data-testid*="email-input"]').first();
      
      if (await loginButton.count() > 0 && await loginButton.isVisible().catch(() => false)) {
        await loginButton.click();
        await page.waitForTimeout(1000);
      }
      
      // Fill login form if it exists
      const emailInput = page.locator('[data-testid*="email"], input[type="email"]').first();
      const passwordInput = page.locator('[data-testid*="password"], input[type="password"]').first();
      const submitButton = page.locator('[data-testid*="login"], button[type="submit"]').first();
      
      if (await emailInput.count() > 0) {
        await emailInput.fill(testEmail);
        await passwordInput.fill(testPassword);
        await submitButton.click();
        await page.waitForURL('**/pillars/**', { timeout: 10000 }).catch(() => {
          console.log('   ⚠️  Navigation timeout, but continuing...');
        });
        console.log('   ✅ UI authentication successful');
      } else {
        console.log('   ⚠️  No login form found, assuming already authenticated or auth not required');
      }
    }
    
    // Save authentication state for reuse in all tests
    const authDir = path.join(__dirname, '../.auth');
    if (!fs.existsSync(authDir)) {
      fs.mkdirSync(authDir, { recursive: true });
    }
    const storageStatePath = path.join(authDir, 'storageState.json');
    await context.storageState({ path: storageStatePath });
    
    await browser.close();
    console.log('   ✅ Authentication state saved to', storageStatePath);
    
  } catch (error) {
    console.warn('   ⚠️  Authentication setup failed:', error);
    console.warn('   Tests will run without authentication (may fail if auth is required)');
    
    // Create empty storage state so tests can still run
    const authDir = path.join(__dirname, '../.auth');
    if (!fs.existsSync(authDir)) {
      fs.mkdirSync(authDir, { recursive: true });
    }
    const storageStatePath = path.join(authDir, 'storageState.json');
    fs.writeFileSync(storageStatePath, JSON.stringify({
      cookies: [],
      origins: []
    }, null, 2));
  }
  
  console.log('✅ Global setup complete');
  console.log('💡 Note: Ensure frontend server is running on http://localhost:3000');
  console.log('💡 Note: Ensure backend server is running on http://localhost:8000 (for API auth)');
}

export default globalSetup; 