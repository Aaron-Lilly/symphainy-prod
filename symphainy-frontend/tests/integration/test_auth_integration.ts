/**
 * Integration Tests for Supabase Authentication (Frontend)
 * 
 * Tests the frontend authentication functions with real backend:
 * - loginUser() function
 * - registerUser() function
 * - Integration with backend API
 * 
 * Run with: npm run test:integration
 * 
 * Prerequisites:
 * - Backend server running on http://localhost:8000
 * - Frontend server running on http://localhost:3000 (optional)
 * 
 * Note: These tests can be run with any test framework (Jest, Vitest, etc.)
 * They use standard fetch API and don't require React Testing Library
 */

// For Node.js environment, we'll use fetch directly
// In browser/test environment, import from lib/api/auth
// This allows tests to run in both Node.js and browser environments

// Mock or import based on environment
let loginUser: any;
let registerUser: any;

// Try to import from lib (works in Next.js/test environment)
try {
  const authModule = require('../../lib/api/auth');
  loginUser = authModule.loginUser;
  registerUser = authModule.registerUser;
} catch (e) {
  // Fallback: Define functions directly for Node.js testing
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  loginUser = async (credentials: { email: string; password: string }) => {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      return { success: false, message: errorText || 'Login failed' };
    }
    
    const data = await response.json();
    return {
      success: data.success || false,
      user: data.user,
      token: data.token || data.access_token,
      message: data.message || 'Login successful',
    };
  };
  
  registerUser = async (credentials: { name: string; email: string; password: string }) => {
    const response = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      return { success: false, message: errorText || 'Registration failed' };
    }
    
    const data = await response.json();
    return {
      success: data.success || false,
      user: data.user,
      token: data.token || data.access_token,
      message: data.message || 'Registration successful',
    };
  };
}

interface AuthResponse {
  success: boolean;
  user?: {
    id: string;
    email: string;
    name: string;
  };
  token?: string;
  message: string;
}

// Test configuration
const BACKEND_URL = process.env.TEST_BACKEND_URL || 'http://localhost:8000';
const TEST_EMAIL_DOMAIN = process.env.TEST_EMAIL_DOMAIN || 'example.com';
const TEST_PASSWORD = process.env.TEST_PASSWORD || 'TestPassword123!';

// Generate unique test email
function generateTestEmail(): string {
  const testId = Date.now().toString(36) + Math.random().toString(36).substring(2, 9);
  return `test-integration-${testId}@${TEST_EMAIL_DOMAIN}`;
}

// Jest-compatible test structure
// Can also be run with other test frameworks

describe('Auth Integration Tests (Frontend)', () => {
  let testEmail: string;
  let testName: string;
  let testPassword: string;

  beforeEach(() => {
    // Generate unique credentials for each test
    testEmail = generateTestEmail();
    testName = `Test User ${Date.now()}`;
    testPassword = TEST_PASSWORD;
  });

  describe('Backend Health Check', () => {
    it('should verify backend is accessible', async () => {
      const response = await fetch(`${BACKEND_URL}/api/auth/health`);
      expect(response.status).toBe(200);
      
      const data = await response.json();
      expect(data).toBeDefined();
    });
  });

  describe('User Registration', () => {
    it('should register a new user via frontend API', async () => {
      const result: AuthResponse = await registerUser({
        name: testName,
        email: testEmail,
        password: testPassword,
      });

      expect(result.success).toBe(true);
      expect(result.user).toBeDefined();
      expect(result.user?.email).toBe(testEmail);
      expect(result.token).toBeDefined();
      expect(result.message).toContain('successful');
    });

    it('should handle duplicate registration', async () => {
      // Register first time
      const firstResult = await registerUser({
        name: testName,
        email: testEmail,
        password: testPassword,
      });

      expect(firstResult.success).toBe(true);

      // Wait a moment for Supabase to process
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Try to register again
      const secondResult = await registerUser({
        name: testName,
        email: testEmail,
        password: testPassword,
      });

      // Should fail
      expect(secondResult.success).toBe(false);
      expect(secondResult.message).toBeDefined();
    });

    it('should handle invalid email format', async () => {
      const result = await registerUser({
        name: testName,
        email: 'invalid-email',
        password: testPassword,
      });

      // Backend should validate and reject
      expect(result.success).toBe(false);
    });

    it('should handle weak password', async () => {
      const result = await registerUser({
        name: testName,
        email: testEmail,
        password: '123', // Too short
      });

      // Backend should validate and reject
      expect(result.success).toBe(false);
    });
  });

  describe('User Login', () => {
    beforeEach(async () => {
      // Ensure user exists before login tests
      await registerUser({
        name: testName,
        email: testEmail,
        password: testPassword,
      });
      
      // Wait for Supabase to process
      await new Promise(resolve => setTimeout(resolve, 1000));
    });

    it('should login with valid credentials', async () => {
      const result: AuthResponse = await loginUser({
        email: testEmail,
        password: testPassword,
      });

      expect(result.success).toBe(true);
      expect(result.user).toBeDefined();
      expect(result.user?.email).toBe(testEmail);
      expect(result.token).toBeDefined();
      expect(result.message).toContain('successful');
    });

    it('should reject invalid email', async () => {
      const result = await loginUser({
        email: `nonexistent-${Date.now()}@${TEST_EMAIL_DOMAIN}`,
        password: testPassword,
      });

      expect(result.success).toBe(false);
      expect(result.message).toBeDefined();
    });

    it('should reject invalid password', async () => {
      const result = await loginUser({
        email: testEmail,
        password: 'WrongPassword123!',
      });

      expect(result.success).toBe(false);
      expect(result.message).toBeDefined();
    });
  });

  describe('Frontend-Backend Integration', () => {
    it('should maintain consistent response format', async () => {
      // Register
      const registerResult = await registerUser({
        name: testName,
        email: testEmail,
        password: testPassword,
      });

      expect(registerResult.success).toBe(true);
      
      // Verify response structure matches frontend expectations
      expect(registerResult).toHaveProperty('success');
      expect(registerResult).toHaveProperty('user');
      expect(registerResult).toHaveProperty('token');
      expect(registerResult).toHaveProperty('message');

      // Verify user object structure
      expect(registerResult.user).toHaveProperty('id');
      expect(registerResult.user).toHaveProperty('email');
      expect(registerResult.user).toHaveProperty('name');

      // Wait and login
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const loginResult = await loginUser({
        email: testEmail,
        password: testPassword,
      });

      expect(loginResult.success).toBe(true);
      
      // Verify login response structure
      expect(loginResult).toHaveProperty('success');
      expect(loginResult).toHaveProperty('user');
      expect(loginResult).toHaveProperty('token');
      expect(loginResult).toHaveProperty('message');
    });

    it('should handle network errors gracefully', async () => {
      // Temporarily use invalid backend URL
      const originalApiUrl = process.env.NEXT_PUBLIC_API_URL;
      process.env.NEXT_PUBLIC_API_URL = 'http://localhost:9999'; // Invalid port

      const result = await loginUser({
        email: testEmail,
        password: testPassword,
      });

      expect(result.success).toBe(false);
      expect(result.message).toBeDefined();

      // Restore original URL
      if (originalApiUrl) {
        process.env.NEXT_PUBLIC_API_URL = originalApiUrl;
      }
    });
  });

  describe('Token Validation', () => {
    it('should receive valid token format', async () => {
      // Register and get token
      const registerResult = await registerUser({
        name: testName,
        email: testEmail,
        password: testPassword,
      });

      expect(registerResult.success).toBe(true);
      expect(registerResult.token).toBeDefined();
      
      const token = registerResult.token!;
      
      // Basic token validation
      expect(typeof token).toBe('string');
      expect(token.length).toBeGreaterThan(0);
      
      // JWT tokens have 3 parts separated by dots
      if (token.includes('.')) {
        const parts = token.split('.');
        expect(parts.length).toBe(3);
      }
    });
  });
});

