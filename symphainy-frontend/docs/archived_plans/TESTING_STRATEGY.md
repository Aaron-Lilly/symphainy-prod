# Testing Strategy

## Overview

This document outlines our comprehensive testing strategy for the Symphainy frontend application, leveraging our optimized architecture to make testing straightforward and effective.

## Testing Philosophy

### Before (Complex Mocking)
- **Problem**: Spent more time figuring out mocking patterns than writing code
- **Issue**: Complex component interactions made testing difficult
- **Result**: Low test coverage and unreliable tests

### After (Optimized Architecture)
- **Solution**: Focused components with clear interfaces
- **Benefit**: Straightforward testing without complex mocking
- **Result**: High test coverage with reliable, maintainable tests

## Testing Pyramid

```
    E2E Tests (Critical User Journeys)
         /|\
        / | \
       /  |  \
      /   |   \
     /    |    \
    /     |     \
   /      |      \
  /       |       \
 /        |        \
/_________|_________\

Integration Tests (Component Interactions)
     /|\
    / | \
   /  |  \
  /   |   \
 /    |    \
/_____|_____\

Unit Tests (Components, Hooks, Utilities)
   /|\
  / | \
 /  |  \
/___|___\
```

## Testing Tools

### 1. Unit Testing
- **Framework**: Jest + React Testing Library
- **Coverage**: Components, hooks, utilities
- **Focus**: Individual component behavior

### 2. Integration Testing
- **Framework**: Jest + React Testing Library
- **Coverage**: Component interactions, service integration
- **Focus**: Multi-component workflows

### 3. E2E Testing
- **Framework**: Playwright
- **Coverage**: Critical user journeys
- **Focus**: Complete user workflows

## Testing Utilities

### TestUtils.tsx
Our comprehensive testing utilities that work with our optimized architecture:

```typescript
// Easy component rendering with providers
import { render, MockData, TestEvents } from '@/shared/testing/TestUtils';

// Render component with all providers
render(<MyComponent />);

// Render with custom session data
render(<MyComponent />, { sessionData: MockData.session });

// Render without error boundary for testing
render(<MyComponent />, { errorBoundary: false });
```

### Mock Data
Centralized mock data for consistent testing:

```typescript
import { MockData } from '@/shared/testing/TestUtils';

// Use predefined mock data
const testData = MockData.gridData;
const testSession = MockData.session;
const testError = MockData.error;
```

### Error Testing
Built-in error testing utilities:

```typescript
import { ErrorTestUtils } from '@/shared/testing/TestUtils';

// Test error handling
await ErrorTestUtils.testErrorHandling(
  component,
  () => throwError(),
  'Expected error message'
);

// Test error recovery
await ErrorTestUtils.testErrorRecovery(
  component,
  () => throwError(),
  () => fixError()
);
```

## Testing Patterns

### 1. Component Testing Pattern

```typescript
describe('MyComponent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render correctly', () => {
      render(<MyComponent />);
      expect(screen.getByText('Expected Text')).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('should handle user input', async () => {
      render(<MyComponent />);
      
      const input = screen.getByRole('textbox');
      fireEvent.change(input, { target: { value: 'test' } });
      
      expect(input).toHaveValue('test');
    });
  });

  describe('Error Handling', () => {
    it('should handle errors gracefully', async () => {
      const ErrorComponent = () => {
        throw new Error('Test error');
      };

      render(<ErrorComponent />);
      await waitForError(screen);
      
      expect(screen.getByText('Test Error: Test error')).toBeInTheDocument();
    });
  });
});
```

### 2. Hook Testing Pattern

```typescript
describe('useMyHook', () => {
  it('should return expected values', () => {
    const { result } = renderHook(() => useMyHook());
    
    expect(result.current.value).toBe(expectedValue);
  });

  it('should handle state updates', () => {
    const { result } = renderHook(() => useMyHook());
    
    act(() => {
      result.current.updateValue('new value');
    });
    
    expect(result.current.value).toBe('new value');
  });
});
```

### 3. E2E Testing Pattern

```typescript
test('should complete user journey', async ({ page }) => {
  // Setup
  await page.goto('/login');
  
  // Action
  await page.fill('[data-testid="email-input"]', 'test@example.com');
  await page.fill('[data-testid="password-input"]', 'password123');
  await page.click('[data-testid="login-button"]');
  
  // Assert
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
});
```

## Test Categories

### 1. Unit Tests
**Location**: `__tests__/components/`, `__tests__/hooks/`, `__tests__/utils/`

**Focus**:
- Individual component rendering
- Hook behavior and state management
- Utility function logic
- Error boundary functionality

**Examples**:
- Component renders with correct props
- Hook returns expected values
- Utility function processes data correctly
- Error boundary catches and displays errors

### 2. Integration Tests
**Location**: `__tests__/integration/`

**Focus**:
- Component interactions
- Service layer integration
- State management across components
- Error handling across layers

**Examples**:
- Form submission with validation
- Data flow between components
- API integration with error handling
- Authentication flow

### 3. E2E Tests
**Location**: `tests/e2e/`

**Focus**:
- Complete user journeys
- Critical business workflows
- Cross-browser compatibility
- Performance under load

**Examples**:
- User registration and login
- File upload and processing
- Insights generation workflow
- Error recovery scenarios

## Testing Best Practices

### 1. Test Organization
```
__tests__/
├── components/
│   ├── MyComponent.test.tsx
│   └── AnotherComponent.test.tsx
├── hooks/
│   ├── useMyHook.test.tsx
│   └── useAnotherHook.test.tsx
├── utils/
│   ├── myUtil.test.ts
│   └── anotherUtil.test.ts
└── integration/
    ├── userFlow.test.tsx
    └── dataFlow.test.tsx

tests/
└── e2e/
    ├── critical-user-journeys.spec.ts
    ├── authentication.spec.ts
    └── file-upload.spec.ts
```

### 2. Test Naming
- **Descriptive**: `should display error message when API fails`
- **Action-oriented**: `should handle user input correctly`
- **Scenario-based**: `should complete login flow successfully`

### 3. Test Structure
```typescript
describe('ComponentName', () => {
  describe('Feature', () => {
    it('should behave correctly', () => {
      // Arrange
      // Act
      // Assert
    });
  });
});
```

### 4. Mocking Strategy
- **Minimal mocking**: Use our testing utilities instead of complex mocks
- **Service mocking**: Mock API calls at the service layer
- **Error simulation**: Use built-in error testing utilities

## Performance Testing

### 1. Component Performance
```typescript
it('should render within performance threshold', () => {
  const renderTime = PerformanceTestUtils.measureRenderTime(() => {
    render(<MyComponent />);
  });
  
  expect(renderTime).toBeLessThan(100); // 100ms threshold
});
```

### 2. Hook Performance
```typescript
it('should execute hook efficiently', () => {
  const hookTime = PerformanceTestUtils.measureHookTime(useMyHook, props);
  expect(hookTime).toBeLessThan(50); // 50ms threshold
});
```

### 3. E2E Performance
```typescript
test('should complete workflow within time limit', async ({ page }) => {
  const startTime = Date.now();
  
  // Complete workflow
  await page.goto('/start');
  await page.click('[data-testid="complete-button"]');
  
  const duration = Date.now() - startTime;
  expect(duration).toBeLessThan(5000); // 5 second threshold
});
```

## Error Testing

### 1. Component Errors
```typescript
it('should handle component errors', async () => {
  const ErrorComponent = () => {
    throw new Error('Component error');
  };

  render(<ErrorComponent />);
  await waitForError(screen);
  
  expect(screen.getByText('Component error')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
});
```

### 2. Network Errors
```typescript
it('should handle network errors', async () => {
  // Mock network error
  await page.route('**/api/**', route => {
    route.abort('failed');
  });
  
  // Trigger API call
  await page.click('[data-testid="fetch-button"]');
  
  // Verify error handling
  await expect(page.locator('[data-testid="network-error"]')).toBeVisible();
});
```

### 3. User Error Recovery
```typescript
it('should allow user to retry failed operations', async () => {
  // Simulate failure
  await ErrorTestUtils.testErrorHandling(component, () => fail());
  
  // Simulate recovery
  await ErrorTestUtils.testErrorRecovery(component, () => fail(), () => succeed());
});
```

## Accessibility Testing

### 1. ARIA Compliance
```typescript
it('should have proper ARIA labels', () => {
  render(<MyComponent />);
  
  expect(screen.getByLabelText('Email address')).toBeVisible();
  expect(screen.getByLabelText('Password')).toBeVisible();
});
```

### 2. Keyboard Navigation
```typescript
it('should support keyboard navigation', () => {
  render(<MyComponent />);
  
  const firstElement = screen.getByRole('button');
  firstElement.focus();
  
  expect(firstElement).toHaveFocus();
});
```

### 3. Screen Reader Support
```typescript
it('should be screen reader friendly', () => {
  render(<MyComponent />);
  
  expect(screen.getByRole('main')).toBeVisible();
  expect(screen.getByRole('navigation')).toBeVisible();
});
```

## Continuous Integration

### 1. Test Scripts
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:all": "npm run test && npm run test:e2e"
  }
}
```

### 2. CI Pipeline
```yaml
- name: Run Unit Tests
  run: npm run test:coverage

- name: Run E2E Tests
  run: npm run test:e2e

- name: Upload Test Results
  uses: actions/upload-artifact@v2
  with:
    name: test-results
    path: test-results/
```

### 3. Coverage Requirements
- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **E2E Tests**: All critical user journeys

## Test Maintenance

### 1. Regular Updates
- Update tests when components change
- Review and refactor test utilities
- Maintain mock data consistency

### 2. Performance Monitoring
- Track test execution times
- Monitor test flakiness
- Optimize slow tests

### 3. Documentation
- Keep test documentation updated
- Document complex test scenarios
- Maintain testing best practices

## Benefits of Our Approach

### 1. Developer Experience
- **Easy Testing**: No complex mocking required
- **Fast Feedback**: Quick test execution
- **Clear Structure**: Organized test files

### 2. Test Reliability
- **Stable Tests**: Less flaky due to simplified architecture
- **Maintainable**: Easy to update when components change
- **Comprehensive**: Covers all critical scenarios

### 3. Quality Assurance
- **High Coverage**: Comprehensive test coverage
- **Error Prevention**: Catches issues early
- **Regression Prevention**: Prevents breaking changes

## Conclusion

Our testing strategy leverages the optimized architecture to provide comprehensive, reliable, and maintainable tests. By focusing on clear component interfaces and minimal mocking, we've created a testing environment that supports rapid development while ensuring high quality.

The combination of unit tests, integration tests, and E2E tests provides complete coverage of our application, from individual component behavior to complete user workflows. This approach ensures that our application is robust, reliable, and ready for production use. 