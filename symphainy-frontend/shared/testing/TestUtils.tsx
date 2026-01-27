/**
 * Testing Utilities for Optimized Architecture
 * 
 * Comprehensive testing utilities that work with our optimized component architecture,
 * making testing straightforward without complex mocking patterns.
 */

import React from 'react';
import { render, RenderOptions, RenderResult, renderHook, RenderHookOptions, RenderHookResult } from '@testing-library/react';
// ✅ PHASE 1: SessionProvider archived - use SessionBoundaryProvider in tests instead
import { SessionBoundaryProvider } from '../state/SessionBoundaryProvider';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { useErrorHandler } from '../hooks/useErrorHandler';

// ============================================
// Test Provider Wrapper
// ============================================

interface TestProviderProps {
  children: React.ReactNode;
  sessionData?: any;
  errorBoundary?: boolean;
  autoInitialize?: boolean;
}

export function TestProvider({ 
  children, 
  sessionData = null,
  errorBoundary = true,
  autoInitialize = false 
}: TestProviderProps) {
  // ✅ PHASE 1: Use SessionBoundaryProvider instead of archived SessionProvider
  const content = (
    <SessionBoundaryProvider>
      {children}
    </SessionBoundaryProvider>
  );

  if (errorBoundary) {
    return (
      <ErrorBoundary
        fallback={(error, errorInfo, retry) => (
          <div data-testid="error-boundary">
            <p>Test Error: {error.message}</p>
            <button onClick={retry}>Retry</button>
          </div>
        )}
      >
        {content}
      </ErrorBoundary>
    );
  }

  return content;
}

// ============================================
// Custom Render Functions
// ============================================

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  sessionData?: any;
  errorBoundary?: boolean;
  autoInitialize?: boolean;
}

export function renderWithProviders(
  ui: React.ReactElement,
  options: CustomRenderOptions = {}
): RenderResult {
  const {
    sessionData,
    errorBoundary = true,
    autoInitialize = false,
    ...renderOptions
  } = options;

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <TestProvider
      sessionData={sessionData}
      errorBoundary={errorBoundary}
      autoInitialize={autoInitialize}
    >
      {children}
    </TestProvider>
  );

  return render(ui, { wrapper: Wrapper, ...renderOptions });
}

// ============================================
// Hook Testing Utilities
// ============================================

interface CustomRenderHookOptions<TProps> extends Omit<RenderHookOptions<TProps>, 'wrapper'> {
  sessionData?: any;
  errorBoundary?: boolean;
  autoInitialize?: boolean;
}

export function renderHookWithProviders<TProps, TResult>(
  hook: (props: TProps) => TResult,
  options: CustomRenderHookOptions<TProps> = {}
): RenderHookResult<TProps, TResult> {
  const {
    sessionData,
    errorBoundary = true,
    autoInitialize = false,
    ...renderOptions
  } = options;

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <TestProvider
      sessionData={sessionData}
      errorBoundary={errorBoundary}
      autoInitialize={autoInitialize}
    >
      {children}
    </TestProvider>
  );

  return renderHook(hook, { wrapper: Wrapper as any, ...renderOptions });
}

// ============================================
// Mock Data Generators
// ============================================

export const MockData = {
  // Session data
  session: {
    user: {
      id: 'test-user-1',
      email: 'test@example.com',
      name: 'Test User',
    },
    isAuthenticated: true,
    token: 'test-token-123',
  },

  // Error data
  error: new Error('Test error message'),

  // Grid data
  gridData: {
    columns: ['Name', 'Age', 'Email', 'Status'],
    rows: [
      ['John Doe', 30, 'john@example.com', 'Active'],
      ['Jane Smith', 25, 'jane@example.com', 'Inactive'],
      ['Bob Johnson', 35, 'bob@example.com', 'Active'],
    ],
  },

  // Visualization data
  visualization: {
    type: 'bar',
    title: 'Test Chart',
    description: 'A test visualization',
    data: [
      { name: 'A', value: 10 },
      { name: 'B', value: 20 },
      { name: 'C', value: 15 },
    ],
    xKey: 'name',
    yKey: 'value',
  },

  // Alert data
  alert: {
    level: 'warning' as const,
    message: 'Test alert message',
    recommendation: 'Test recommendation',
    timestamp: Date.now(),
    id: 'test-alert-1',
  },

  // Agent message data
  agentMessage: {
    id: 'test-message-1',
    type: 'agent' as const,
    content: 'Test agent message',
    timestamp: Date.now(),
    metadata: { source: 'test' },
  },

  // Error message data
  errorMessage: {
    id: 'test-error-1',
    message: 'Test error message',
    type: 'error' as const,
    timestamp: Date.now(),
    details: 'Test error details',
  },

  // AGUI response data
  aguiResponse: {
    type: 'summary_output',
    data: {
      summary: 'Test summary content',
      content: 'Test content',
    },
    timestamp: Date.now(),
    id: 'test-response-1',
  },

  // Processed responses
  processedResponses: {
    summary_output: [
      {
        type: 'summary_output',
        data: { summary: 'Test summary 1' },
        timestamp: Date.now(),
        id: 'summary-1',
      },
    ],
    data_grid_response: [
      {
        type: 'data_grid_response',
        data: {
          columns: ['Name', 'Value'],
          rows: [['Test', 100]],
        },
        timestamp: Date.now(),
        id: 'grid-1',
      },
    ],
    visual_output: [
      {
        type: 'visual_output',
        data: {
          type: 'bar',
          title: 'Test Chart',
          data: [{ name: 'A', value: 10 }],
        },
        timestamp: Date.now(),
        id: 'visual-1',
      },
    ],
    agent_message: [
      {
        type: 'agent_message',
        data: {
          content: 'Test message',
          type: 'agent',
        },
        timestamp: Date.now(),
        id: 'message-1',
      },
    ],
    error: [
      {
        type: 'error',
        data: {
          message: 'Test error',
          level: 'warning',
        },
        timestamp: Date.now(),
        id: 'error-1',
      },
    ],
  },
};

// ============================================
// Async Testing Utilities
// ============================================

export async function waitForError(component: RenderResult, timeout = 1000): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error('Timeout waiting for error'));
    }, timeout);

    const checkForError = () => {
      const errorElement = component.container.querySelector('[data-testid="error-boundary"]');
      if (errorElement) {
        clearTimeout(timer);
        resolve();
      } else {
        setTimeout(checkForError, 10);
      }
    };

    checkForError();
  });
}

export async function waitForLoading(component: RenderResult, timeout = 1000): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error('Timeout waiting for loading state'));
    }, timeout);

    const checkForLoading = () => {
      const loadingElement = component.container.querySelector('[data-testid="loading"]');
      if (loadingElement) {
        clearTimeout(timer);
        resolve();
      } else {
        setTimeout(checkForLoading, 10);
      }
    };

    checkForLoading();
  });
}

export async function waitForData(component: RenderResult, timeout = 1000): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error('Timeout waiting for data'));
    }, timeout);

    const checkForData = () => {
      const dataElement = component.container.querySelector('[data-testid="data-loaded"]');
      if (dataElement) {
        clearTimeout(timer);
        resolve();
      } else {
        setTimeout(checkForData, 10);
      }
    };

    checkForData();
  });
}

// ============================================
// Component Testing Helpers
// ============================================

export function createTestComponent<TProps>(
  Component: React.ComponentType<TProps>,
  defaultProps: Partial<TProps> = {}
) {
  return (props: Partial<TProps> = {}) => {
    const mergedProps = { ...defaultProps, ...props } as TProps;
    return <Component {...mergedProps} />;
  };
}

export function createTestHook<TProps, TResult>(
  hook: (props: TProps) => TResult,
  defaultProps: Partial<TProps> = {}
) {
  return (props: Partial<TProps> = {}) => {
    const mergedProps = { ...defaultProps, ...props } as TProps;
    return hook(mergedProps);
  };
}

// ============================================
// Event Testing Utilities
// ============================================

export const TestEvents = {
  // Simulate user interactions
  click: (element: Element) => {
    element.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  },

  change: (element: Element, value: string) => {
    (element as HTMLInputElement).value = value;
    element.dispatchEvent(new Event('change', { bubbles: true }));
  },

  input: (element: Element, value: string) => {
    (element as HTMLInputElement).value = value;
    element.dispatchEvent(new Event('input', { bubbles: true }));
  },

  submit: (element: Element) => {
    element.dispatchEvent(new Event('submit', { bubbles: true }));
  },

  // Simulate keyboard events
  keyDown: (element: Element, key: string) => {
    element.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true }));
  },

  keyUp: (element: Element, key: string) => {
    element.dispatchEvent(new KeyboardEvent('keyup', { key, bubbles: true }));
  },

  // Simulate focus events
  focus: (element: Element) => {
    element.dispatchEvent(new Event('focus', { bubbles: true }));
  },

  blur: (element: Element) => {
    element.dispatchEvent(new Event('blur', { bubbles: true }));
  },
};

// ============================================
// Error Testing Utilities
// ============================================

export const ErrorTestUtils = {
  // Create different types of errors
  createNetworkError: () => new Error('Network error: Failed to fetch'),
  createAuthError: () => new Error('Authentication error: 401 Unauthorized'),
  createValidationError: () => new Error('Validation error: Invalid input'),
  createServerError: () => new Error('Server error: 500 Internal Server Error'),
  createTimeoutError: () => new Error('Timeout error: Request timed out'),

  // Test error handling
  async testErrorHandling(
    component: RenderResult,
    errorAction: () => void | Promise<void>,
    expectedError?: string
  ) {
    try {
      await errorAction();
    } catch (error) {
      // Error expected
    }

    await waitForError(component);
    
    if (expectedError) {
      expect(component.container).toHaveTextContent(expectedError);
    }
  },

  // Test error recovery
  async testErrorRecovery(
    component: RenderResult,
    errorAction: () => void | Promise<void>,
    recoveryAction: () => void | Promise<void>
  ) {
    // Trigger error
    await ErrorTestUtils.testErrorHandling(component, errorAction);

    // Perform recovery action
    await recoveryAction();

    // Verify error is cleared
    expect(component.container).not.toHaveTextContent('Test Error');
  },
};

// ============================================
// Performance Testing Utilities
// ============================================

export const PerformanceTestUtils = {
  // Measure render time
  measureRenderTime: (renderFn: () => void): number => {
    const start = performance.now();
    renderFn();
    const end = performance.now();
    return end - start;
  },

  // Measure hook execution time
  measureHookTime: <TProps, TResult>(
    hook: (props: TProps) => TResult,
    props: TProps
  ): number => {
    const start = performance.now();
    renderHook(hook, { initialProps: props });
    const end = performance.now();
    return end - start;
  },

  // Assert performance thresholds
  assertRenderTime: (renderFn: () => void, maxTime: number) => {
    const renderTime = PerformanceTestUtils.measureRenderTime(renderFn);
    expect(renderTime).toBeLessThan(maxTime);
  },

  assertHookTime: <TProps, TResult>(
    hook: (props: TProps) => TResult,
    props: TProps,
    maxTime: number
  ) => {
    const hookTime = PerformanceTestUtils.measureHookTime(hook, props);
    expect(hookTime).toBeLessThan(maxTime);
  },
};

// ============================================
// Mock Service Utilities
// ============================================

export const MockServices = {
  // Mock API responses
  api: {
    success: <T,>(data: T, delay = 100) => 
      new Promise<T>((resolve) => setTimeout(() => resolve(data), delay)),
    
    error: (error: Error, delay = 100) => 
      new Promise<never>((_, reject) => setTimeout(() => reject(error), delay)),
    
    networkError: (delay = 100) => 
      MockServices.api.error(new Error('Network error: Failed to fetch'), delay),
    
    authError: (delay = 100) => 
      MockServices.api.error(new Error('Authentication error: 401 Unauthorized'), delay),
  },

  // Mock WebSocket
  websocket: {
    messages: [] as any[],
    
    send: (message: any) => {
      MockServices.websocket.messages.push(message);
    },
    
    clear: () => {
      MockServices.websocket.messages = [];
    },
    
    getMessages: () => [...MockServices.websocket.messages],
  },

  // Mock storage
  storage: {
    data: new Map<string, any>(),
    
    setItem: (key: string, value: any) => {
      MockServices.storage.data.set(key, JSON.stringify(value));
    },
    
    getItem: (key: string) => {
      const value = MockServices.storage.data.get(key);
      return value ? JSON.parse(value) : null;
    },
    
    removeItem: (key: string) => {
      MockServices.storage.data.delete(key);
    },
    
    clear: () => {
      MockServices.storage.data.clear();
    },
  },
};

// ============================================
// Test Configuration
// ============================================

export const TestUtilsConfig = {
  // Default timeouts
  timeouts: {
    render: 1000,
    loading: 2000,
    error: 1000,
    data: 1000,
  },

  // Test data
  data: MockData,

  // Utilities
  utils: {
    render: renderWithProviders,
    renderHook: renderHookWithProviders,
    waitForError,
    waitForLoading,
    waitForData,
    createTestComponent,
    createTestHook,
  },

  // Events
  events: TestEvents,

  // Error testing
  error: ErrorTestUtils,

  // Performance testing
  performance: PerformanceTestUtils,

  // Mock services
  services: MockServices,
};

// ============================================
// Re-exports for convenience
// ============================================

export {
  renderWithProviders as render,
  renderHookWithProviders as renderHook,
}; 