# Authentication Testing Strategy

## Overview

This document outlines the best-practice approach for testing authentication across different test layers, following industry standards and Playwright recommendations.

---

## Testing Pyramid

```
        /\
       /  \     E2E Tests (Few, Slow, Expensive)
      /____\    - Authenticate once, reuse state
     /      \   - Focus on user flows, not auth logic
    /________\  - Use storageState for speed
   /          \
  /____________\  Integration Tests (Some, Medium Speed)
 /              \ - Test with real Supabase
/________________\ - Use dedicated test accounts
                  - Verify auth integration works

Unit Tests (Many, Fast, Cheap)
- Test auth logic in isolation
- Mock all dependencies
- Test edge cases and error handling
```

---

## Layer 1: Unit Tests ✅

**Purpose**: Test authentication logic in isolation

**Location**: `tests/unit/**/test_auth*.{ts,tsx,py}`

**Strategy**:
- Mock all external dependencies (Supabase, API calls)
- Test pure functions and business logic
- Test error handling and edge cases
- Fast execution (< 1 second per test)

**Example**:
```typescript
// tests/unit/auth/test_auth_provider.ts
describe('AuthProvider', () => {
  it('should authenticate user with valid credentials', async () => {
    const mockSupabase = {
      auth: {
        signInWithPassword: jest.fn().mockResolvedValue({
          data: { user: mockUser, session: mockSession },
          error: null
        })
      }
    };
    
    const authProvider = new AuthProvider(mockSupabase);
    const result = await authProvider.login('test@example.com', 'password');
    
    expect(result.success).toBe(true);
    expect(mockSupabase.auth.signInWithPassword).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password'
    });
  });
});
```

**Backend Example** (Already exists):
```python
# backend/tests/test_auth.py
@patch('backend.services.auth_service.auth_service.signup')
def test_signup_success(self, mock_signup):
    # Mock Supabase response
    mock_signup.return_value = (mock_auth_response, None)
    # Test signup logic
    response = client.post("/auth/signup", json=signup_data)
    assert response.status_code == 201
```

---

## Layer 2: Integration Tests ✅

**Purpose**: Test authentication with real Supabase integration

**Location**: `tests/integration/**/test_auth*.{ts,tsx,py}`

**Strategy**:
- Use real Supabase (test project or dedicated test environment)
- Use dedicated test accounts (e.g., `test-e2e-{timestamp}@example.com`)
- Clean up test accounts after tests
- Test actual API integration
- Medium speed (1-5 seconds per test)

**Example**:
```typescript
// tests/integration/auth/test_supabase_integration.ts
describe('Supabase Auth Integration', () => {
  const testEmail = `test-e2e-${Date.now()}@example.com`;
  const testPassword = 'TestPassword123!';
  
  afterAll(async () => {
    // Clean up test account
    await supabase.auth.admin.deleteUser(testUserId);
  });
  
  it('should register and authenticate user with Supabase', async () => {
    // Real Supabase call
    const { data, error } = await supabase.auth.signUp({
      email: testEmail,
      password: testPassword
    });
    
    expect(error).toBeNull();
    expect(data.user).toBeDefined();
    expect(data.session).toBeDefined();
    
    // Test login
    const { data: loginData, error: loginError } = await supabase.auth.signInWithPassword({
      email: testEmail,
      password: testPassword
    });
    
    expect(loginError).toBeNull();
    expect(loginData.session).toBeDefined();
  });
});
```

**Backend Example**:
```python
# tests/integration/test_auth_integration.py
@pytest.mark.integration
def test_real_supabase_auth():
    """Test with real Supabase (requires SUPABASE_TEST_URL)"""
    test_email = f"test-{uuid.uuid4()}@example.com"
    
    # Real registration
    response = client.post("/api/auth/register", json={
        "email": test_email,
        "password": "TestPassword123!"
    })
    assert response.status_code == 200
    
    # Real login
    login_response = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "TestPassword123!"
    })
    assert login_response.status_code == 200
    assert login_response.json()["access_token"] is not None
```

---

## Layer 3: E2E Tests ✅ (Recommended Approach)

**Purpose**: Test complete user flows without repeating authentication

**Location**: `tests/e2e/**/*.spec.ts`

**Strategy**:
- **Authenticate once** in `global-setup.ts`
- **Save authentication state** (cookies, localStorage) to `storageState.json`
- **Reuse state** in all E2E tests via `playwright.config.ts`
- **Fast execution** (no auth overhead per test)
- **Focus on user flows**, not auth logic

**Implementation**:

### Step 1: Authenticate in Global Setup

```typescript
// tests/e2e/global-setup.ts
import { chromium, FullConfig } from '@playwright/test';
import * as path from 'path';

async function globalSetup(config: FullConfig) {
  // ... existing setup code ...
  
  // Authenticate once and save state
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Navigate to login page
  await page.goto('http://localhost:3000');
  
  // Perform authentication (adjust selectors based on your UI)
  const testEmail = process.env.E2E_TEST_EMAIL || 'test-e2e@example.com';
  const testPassword = process.env.E2E_TEST_PASSWORD || 'TestPassword123!';
  
  // Wait for auth form or auto-authenticate via API
  // Option 1: If you have a login form
  await page.fill('[data-testid="email-input"]', testEmail);
  await page.fill('[data-testid="password-input"]', testPassword);
  await page.click('[data-testid="login-button"]');
  await page.waitForURL('**/pillars/**', { timeout: 10000 });
  
  // Option 2: If you authenticate via API (recommended)
  // const response = await page.request.post('http://localhost:8000/api/auth/login', {
  //   data: { email: testEmail, password: testPassword }
  // });
  // const { access_token } = await response.json();
  // await page.addInitScript((token) => {
  //   localStorage.setItem('auth_token', token);
  // }, access_token);
  
  // Save authentication state
  const storageStatePath = path.join(__dirname, '../.auth/storageState.json');
  await context.storageState({ path: storageStatePath });
  
  await browser.close();
  console.log('✅ Authentication state saved');
}
```

### Step 2: Configure Playwright to Use Storage State

```typescript
// playwright.config.ts
export default defineConfig({
  // ... existing config ...
  
  use: {
    baseURL: 'http://localhost:3000',
    
    // Load authentication state for all tests
    storageState: path.join(__dirname, 'tests/.auth/storageState.json'),
    
    // ... other settings ...
  },
  
  // ... rest of config ...
});
```

### Step 3: Use Authenticated State in Tests

```typescript
// tests/e2e/semantic-components.spec.ts
test('FileUploader: Upload CSV file', async ({ page }) => {
  // Page is already authenticated via storageState
  // No need to login!
  await page.goto('/pillars/content');
  
  // Test your component
  const uploadArea = page.locator('[data-testid="content-pillar-file-upload-area"]');
  await expect(uploadArea).toBeVisible();
  // ... rest of test ...
});
```

---

## Alternative: Mock Authentication for E2E (Not Recommended)

If you want to completely bypass authentication in E2E tests:

```typescript
// tests/e2e/global-setup.ts
async function globalSetup(config: FullConfig) {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Mock authentication by setting localStorage
  await page.goto('http://localhost:3000');
  await page.addInitScript(() => {
    // Mock auth state
    localStorage.setItem('auth_token', 'mock-token');
    localStorage.setItem('user', JSON.stringify({
      id: 'test-user-id',
      email: 'test@example.com',
      name: 'Test User'
    }));
  });
  
  await context.storageState({ path: storageStatePath });
  await browser.close();
}
```

**⚠️ Warning**: This approach doesn't test real authentication, so you should still have integration tests.

---

## Recommended Approach for This Project

### ✅ **Hybrid Strategy** (Best of Both Worlds)

1. **Unit Tests**: Test auth logic with mocks (already exists)
2. **Integration Tests**: Test with real Supabase (create these)
3. **E2E Tests**: Authenticate once, reuse state (implement this)

### Implementation Plan

1. **Update `global-setup.ts`** to authenticate once
2. **Update `playwright.config.ts`** to use `storageState`
3. **Create integration test suite** for auth (optional but recommended)
4. **Update E2E tests** to remove auth logic (already done via storageState)

---

## Environment Variables

Create `.env.test` for E2E tests:

```bash
# E2E Test Authentication
E2E_TEST_EMAIL=test-e2e@example.com
E2E_TEST_PASSWORD=TestPassword123!

# Or use a dedicated test account
E2E_TEST_EMAIL=playwright-test@yourdomain.com
E2E_TEST_PASSWORD=SecureTestPassword123!
```

---

## Benefits of This Approach

✅ **Fast E2E Tests**: No auth overhead per test  
✅ **Real Authentication**: Tests use actual auth flow (once)  
✅ **Isolated Testing**: Unit tests test logic, integration tests test integration  
✅ **Maintainable**: Auth changes only require updating global-setup  
✅ **CI/CD Friendly**: Works in automated pipelines  

---

## Testing Checklist

- [ ] Unit tests for auth logic (with mocks)
- [ ] Integration tests for Supabase auth (real API)
- [ ] E2E global setup authenticates once
- [ ] Playwright config uses storageState
- [ ] E2E tests don't include auth logic
- [ ] Test accounts are cleaned up after tests
- [ ] Environment variables configured for test accounts

---

## References

- [Playwright: Authentication](https://playwright.dev/docs/auth)
- [Playwright: Global Setup](https://playwright.dev/docs/test-global-setup-teardown)
- [Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)




