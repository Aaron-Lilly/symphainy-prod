# Testing Guide

This document provides comprehensive guidance on testing strategies, patterns, and best practices for the Symphainy frontend application.

## 📋 Table of Contents

- [Overview](#overview)
- [Testing Strategy](#testing-strategy)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Testing Tools](#testing-tools)
- [Test Patterns](#test-patterns)
- [Best Practices](#best-practices)

## 🎯 Overview

The Symphainy frontend testing strategy includes:

- **Unit Testing** - Testing individual components and functions
- **Integration Testing** - Testing component interactions
- **End-to-End Testing** - Testing complete user workflows
- **Performance Testing** - Testing application performance
- **Accessibility Testing** - Testing accessibility compliance
- **Visual Testing** - Testing UI consistency

## 🧪 Testing Strategy

### Testing Pyramid

```
    E2E Tests (Few)
        /\
       /  \
      /    \
   Integration Tests (Some)
      /\
     /  \
    /    \
 Unit Tests (Many)
```

### Test Coverage Goals

```typescript
// Coverage targets
const coverageTargets = {
  statements: 80,
  branches: 80,
  functions: 80,
  lines: 80,
};
```

### Testing Priorities

1. **Critical Paths** - User authentication, data upload, analysis
2. **Core Components** - UI components, service layer
3. **Edge Cases** - Error handling, boundary conditions
4. **Performance** - Load times, memory usage
5. **Accessibility** - Screen readers, keyboard navigation

## 🔬 Unit Testing

### Component Testing

```typescript
// components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant styles correctly', () => {
    render(<Button variant="destructive">Delete</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-destructive');
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### Hook Testing

```typescript
// hooks/useCounter.test.ts
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  it('initializes with custom value', () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });

  it('increments count', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });

  it('decrements count', () => {
    const { result } = renderHook(() => useCounter(5));
    
    act(() => {
      result.current.decrement();
    });
    
    expect(result.current.count).toBe(4);
  });

  it('resets count', () => {
    const { result } = renderHook(() => useCounter(5));
    
    act(() => {
      result.current.reset();
    });
    
    expect(result.current.count).toBe(0);
  });
});
```

### Service Testing

```typescript
// services/APIService.test.ts
import { APIService } from './APIService';

// Mock fetch
global.fetch = jest.fn();

describe('APIService', () => {
  let apiService: APIService;

  beforeEach(() => {
    apiService = new APIService();
    (fetch as jest.Mock).mockClear();
  });

  it('makes GET request successfully', async () => {
    const mockResponse = { data: 'test' };
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await apiService.get('/api/test');
    expect(result.data).toEqual(mockResponse);
    expect(fetch).toHaveBeenCalledWith('/api/test', expect.any(Object));
  });

  it('handles API errors', async () => {
    (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    await expect(apiService.get('/api/test')).rejects.toThrow('Network error');
  });

  it('retries failed requests', async () => {
    const mockResponse = { data: 'success' };
    
    (fetch as jest.Mock)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

    const result = await apiService.get('/api/test', { retries: 1 });
    expect(result.data).toEqual(mockResponse);
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});
```

### Utility Function Testing

```typescript
// utils/formatDate.test.ts
import { formatDate, parseDate } from './formatDate';

describe('Date Utils', () => {
  it('formats date correctly', () => {
    const date = new Date('2023-01-15T10:30:00Z');
    const formatted = formatDate(date);
    expect(formatted).toBe('Jan 15, 2023');
  });

  it('parses date string correctly', () => {
    const dateString = '2023-01-15';
    const parsed = parseDate(dateString);
    expect(parsed).toEqual(new Date('2023-01-15'));
  });

  it('handles invalid date input', () => {
    expect(() => formatDate('invalid')).toThrow('Invalid date');
  });
});
```

## 🔗 Integration Testing

### Component Integration

```typescript
// components/UserForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserForm } from './UserForm';
import { UserProvider } from '../context/UserContext';

describe('UserForm Integration', () => {
  it('submits form and updates user context', async () => {
    const mockUpdateUser = jest.fn();
    
    render(
      <UserProvider>
        <UserForm onUpdate={mockUpdateUser} />
      </UserProvider>
    );

    fireEvent.change(screen.getByLabelText('Name'), {
      target: { value: 'John Doe' },
    });
    
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'john@example.com' },
    });
    
    fireEvent.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(mockUpdateUser).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com',
      });
    });
  });
});
```

### Service Integration

```typescript
// services/UserService.test.ts
import { UserService } from './UserService';
import { APIService } from './APIService';

jest.mock('./APIService');

describe('UserService Integration', () => {
  let userService: UserService;
  let mockApiService: jest.Mocked<APIService>;

  beforeEach(() => {
    mockApiService = new APIService() as jest.Mocked<APIService>;
    userService = new UserService(mockApiService);
  });

  it('creates user and returns user data', async () => {
    const userData = { name: 'John', email: 'john@example.com' };
    const createdUser = { id: 1, ...userData };
    
    mockApiService.post.mockResolvedValueOnce({
      data: createdUser,
      status: 201,
      success: true,
    });

    const result = await userService.createUser(userData);
    
    expect(result).toEqual(createdUser);
    expect(mockApiService.post).toHaveBeenCalledWith('/api/users', userData);
  });
});
```

### State Management Integration

```typescript
// state/userState.test.ts
import { renderHook, act } from '@testing-library/react';
import { useUserState } from './userState';

describe('User State Integration', () => {
  it('manages user state correctly', () => {
    const { result } = renderHook(() => useUserState());

    act(() => {
      result.current.setUser({ id: 1, name: 'John' });
    });

    expect(result.current.user).toEqual({ id: 1, name: 'John' });
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('clears user state on logout', () => {
    const { result } = renderHook(() => useUserState());

    act(() => {
      result.current.setUser({ id: 1, name: 'John' });
    });

    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });
});
```

## 🚀 End-to-End Testing

### User Workflow Testing

```typescript
// tests/e2e/user-workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Workflow', () => {
  test('complete user registration and login', async ({ page }) => {
    // Navigate to registration page
    await page.goto('/register');
    
    // Fill registration form
    await page.fill('[data-testid="name-input"]', 'John Doe');
    await page.fill('[data-testid="email-input"]', 'john@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    
    // Submit registration
    await page.click('[data-testid="register-button"]');
    
    // Wait for redirect to login
    await page.waitForURL('/login');
    
    // Login with credentials
    await page.fill('[data-testid="email-input"]', 'john@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Verify successful login
    await page.waitForURL('/dashboard');
    await expect(page.locator('[data-testid="user-name"]')).toContainText('John Doe');
  });

  test('upload file and view analysis', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'john@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Navigate to content pillar
    await page.goto('/pillars/content');
    
    // Upload file
    await page.setInputFiles('[data-testid="file-input"]', 'test-files/sample.csv');
    await page.click('[data-testid="upload-button"]');
    
    // Wait for upload completion
    await page.waitForSelector('[data-testid="upload-success"]');
    
    // Navigate to insights pillar
    await page.goto('/pillars/insight');
    
    // Verify analysis is available
    await expect(page.locator('[data-testid="analysis-results"]')).toBeVisible();
  });
});
```

### Cross-Pillar Integration Testing

```typescript
// tests/e2e/cross-pillar.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Cross-Pillar Integration', () => {
  test('data flows between pillars correctly', async ({ page }) => {
    // Login and upload data
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'john@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Upload file in content pillar
    await page.goto('/pillars/content');
    await page.setInputFiles('[data-testid="file-input"]', 'test-files/data.csv');
    await page.click('[data-testid="upload-button"]');
    await page.waitForSelector('[data-testid="upload-success"]');
    
    // Check insights pillar for data
    await page.goto('/pillars/insight');
    await expect(page.locator('[data-testid="data-available"]')).toBeVisible();
    
    // Run analysis
    await page.click('[data-testid="run-analysis-button"]');
    await page.waitForSelector('[data-testid="analysis-complete"]');
    
    // Check operations pillar for workflow
    await page.goto('/pillars/operation');
    await expect(page.locator('[data-testid="workflow-available"]')).toBeVisible();
  });
});
```

### API Integration Testing

```typescript
// tests/e2e/api-integration.spec.ts
import { test, expect } from '@playwright/test';

test.describe('API Integration', () => {
  test('API endpoints work correctly', async ({ request }) => {
    // Test health endpoint
    const healthResponse = await request.get('/api/health');
    expect(healthResponse.ok()).toBeTruthy();
    expect(await healthResponse.json()).toEqual({ status: 'healthy' });
    
    // Test file upload
    const uploadResponse = await request.post('/api/content/upload', {
      data: {
        file: {
          name: 'test.csv',
          mimeType: 'text/csv',
          buffer: Buffer.from('test,data\n1,2\n3,4'),
        },
      },
    });
    expect(uploadResponse.ok()).toBeTruthy();
    
    // Test analysis endpoint
    const analysisResponse = await request.post('/api/insights/analyze', {
      data: {
        fileId: 'test-file-id',
        analysisType: 'basic',
      },
    });
    expect(analysisResponse.ok()).toBeTruthy();
  });
});
```

## 🛠️ Testing Tools

### Jest Configuration

```javascript
// jest.config.js
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  testEnvironment: 'jsdom',
  collectCoverageFrom: [
    'components/**/*.{ts,tsx}',
    'shared/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  testMatch: [
    '<rootDir>/__tests__/**/*.test.{ts,tsx}',
    '<rootDir>/components/**/*.test.{ts,tsx}',
    '<rootDir>/shared/**/*.test.{ts,tsx}',
  ],
};

module.exports = createJestConfig(customJestConfig);
```

### Jest Setup

```javascript
// jest.setup.js
import '@testing-library/jest-dom';

// Mock fetch
global.fetch = jest.fn();

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});
```

### Playwright Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

## 🎯 Test Patterns

### Page Object Pattern

```typescript
// tests/page-objects/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.page.fill('[data-testid="email-input"]', email);
    await this.page.fill('[data-testid="password-input"]', password);
    await this.page.click('[data-testid="login-button"]');
  }

  async expectLoginSuccess() {
    await this.page.waitForURL('/dashboard');
  }

  async expectLoginError() {
    await expect(this.page.locator('[data-testid="error-message"]')).toBeVisible();
  }
}

// Usage in tests
test('user can login successfully', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('john@example.com', 'password123');
  await loginPage.expectLoginSuccess();
});
```

### Test Data Factory

```typescript
// tests/factories/UserFactory.ts
export class UserFactory {
  static create(overrides: Partial<User> = {}): User {
    return {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      role: 'user',
      ...overrides,
    };
  }

  static createMany(count: number, overrides: Partial<User> = {}): User[] {
    return Array.from({ length: count }, (_, index) =>
      this.create({ id: index + 1, ...overrides })
    );
  }
}

// Usage in tests
const user = UserFactory.create({ role: 'admin' });
const users = UserFactory.createMany(5, { role: 'user' });
```

### Mock Service Pattern

```typescript
// tests/mocks/APIServiceMock.ts
export class APIServiceMock {
  private responses = new Map<string, any>();

  mockGet(url: string, response: any) {
    this.responses.set(`GET:${url}`, response);
  }

  mockPost(url: string, response: any) {
    this.responses.set(`POST:${url}`, response);
  }

  async get(url: string) {
    const response = this.responses.get(`GET:${url}`);
    if (!response) {
      throw new Error(`No mock response for GET ${url}`);
    }
    return response;
  }

  async post(url: string, data: any) {
    const response = this.responses.get(`POST:${url}`);
    if (!response) {
      throw new Error(`No mock response for POST ${url}`);
    }
    return response;
  }
}

// Usage in tests
const mockApi = new APIServiceMock();
mockApi.mockGet('/api/users', { data: users });
mockApi.mockPost('/api/users', { data: newUser });
```

## 🎯 Best Practices

### 1. Test Organization

- **Group related tests** using `describe` blocks
- **Use descriptive test names** that explain the behavior
- **Follow AAA pattern** (Arrange, Act, Assert)
- **Keep tests independent** and isolated

### 2. Test Data Management

- **Use factories** for creating test data
- **Clean up test data** after each test
- **Use realistic data** that matches production
- **Avoid hardcoded values** in tests

### 3. Assertions

- **Use specific assertions** instead of generic ones
- **Test one thing per test** for clarity
- **Use meaningful error messages** in assertions
- **Test both positive and negative cases**

### 4. Performance

- **Mock external dependencies** to speed up tests
- **Use test databases** for integration tests
- **Parallelize tests** when possible
- **Optimize test setup** and teardown

### 5. Maintenance

- **Update tests** when code changes
- **Refactor tests** to reduce duplication
- **Monitor test coverage** and maintain targets
- **Review test failures** promptly

### 6. Accessibility

- **Test keyboard navigation** in E2E tests
- **Verify screen reader compatibility**
- **Test color contrast** and visual accessibility
- **Include accessibility assertions** in component tests

---

**Last Updated**: [Automated Update]
**Version**: 1.0.0 