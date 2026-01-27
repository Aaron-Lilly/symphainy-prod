/**
 * Test Utilities for Journey and Intent Testing
 * 
 * Provides mocks and helpers for testing intents and journeys
 */

import { PlatformState } from '@/shared/state/PlatformState';

/**
 * Mock Platform State for testing
 */
export function createMockPlatformState(overrides?: Partial<PlatformState>): PlatformState {
  const defaultState = {
    state: {
      session: {
        sessionId: 'test-session-id',
        tenantId: 'test-tenant-id',
        userId: 'test-user-id',
      },
      realm: {
        content: {
          files: [],
          parsedFiles: {},
          embeddings: {},
          interpretations: {},
          fileList: [],
        },
      },
      execution: {},
    },
    submitIntent: jest.fn(),
    trackExecution: jest.fn(),
    getExecutionStatus: jest.fn(),
  };

  return {
    ...defaultState,
    ...overrides,
  } as PlatformState;
}

/**
 * Mock Execution Status
 */
export interface MockExecutionStatus {
  status: 'pending' | 'completed' | 'failed';
  execution_id: string;
  artifacts?: Record<string, any>;
  error?: string;
}

/**
 * Create mock execution status
 */
export function createMockExecutionStatus(
  status: 'pending' | 'completed' | 'failed',
  executionId: string,
  artifacts?: Record<string, any>,
  error?: string
): MockExecutionStatus {
  return {
    status,
    execution_id: executionId,
    artifacts,
    error,
  };
}

/**
 * Mock successful intent execution
 */
export function mockSuccessfulIntent(
  platformState: PlatformState,
  intentName: string,
  artifacts: Record<string, any>
) {
  const executionId = `exec-${Date.now()}-${Math.random()}`;
  
  (platformState.submitIntent as jest.Mock).mockResolvedValue(executionId);
  (platformState.getExecutionStatus as jest.Mock).mockResolvedValue({
    status: 'completed',
    execution_id: executionId,
    artifacts,
  });
  
  return executionId;
}

/**
 * Mock failed intent execution
 */
export function mockFailedIntent(
  platformState: PlatformState,
  intentName: string,
  error: string
) {
  const executionId = `exec-${Date.now()}-${Math.random()}`;
  
  (platformState.submitIntent as jest.Mock).mockResolvedValue(executionId);
  (platformState.getExecutionStatus as jest.Mock).mockResolvedValue({
    status: 'failed',
    execution_id: executionId,
    error,
  });
  
  return executionId;
}

/**
 * Create mock file for testing
 */
export function createMockFile(
  name: string = 'test-file.txt',
  content: string = 'test content',
  size: number = 1000,
  type: string = 'text/plain'
): File {
  // Create a proper File-like object with arrayBuffer method
  const contentBuffer = new TextEncoder().encode(content);
  const blob = new Blob([contentBuffer], { type });
  
  const file = new File([blob], name, { type });
  Object.defineProperty(file, 'size', { value: size, writable: false, configurable: true });
  
  // Mock arrayBuffer method for Jest environment
  if (!file.arrayBuffer || typeof file.arrayBuffer !== 'function') {
    file.arrayBuffer = async function() {
      return contentBuffer.buffer;
    };
  }
  
  return file;
}

/**
 * Create mock file that exceeds size limit (for boundary violation tests)
 */
export function createMockLargeFile(
  name: string = 'large-file.txt',
  sizeMB: number = 101
): File {
  const size = sizeMB * 1024 * 1024; // Convert MB to bytes
  const content = 'x'.repeat(size);
  const blob = new Blob([content], { type: 'text/plain' });
  const file = new File([blob], name, { type: 'text/plain' });
  Object.defineProperty(file, 'size', { value: size });
  return file;
}

/**
 * Assert intent was called with correct parameters
 */
export function expectIntentCalled(
  platformState: PlatformState,
  intentName: string,
  expectedParams: Record<string, any>
) {
  expect(platformState.submitIntent).toHaveBeenCalledWith(
    intentName,
    expect.objectContaining(expectedParams)
  );
}

/**
 * Assert execution was tracked
 */
export function expectExecutionTracked(
  platformState: PlatformState,
  executionId: string
) {
  expect(platformState.trackExecution).toHaveBeenCalledWith(executionId);
}

/**
 * Reset all mocks
 */
export function resetAllMocks(platformState: PlatformState) {
  jest.clearAllMocks();
  (platformState.submitIntent as jest.Mock).mockClear();
  (platformState.trackExecution as jest.Mock).mockClear();
  (platformState.getExecutionStatus as jest.Mock).mockClear();
}
