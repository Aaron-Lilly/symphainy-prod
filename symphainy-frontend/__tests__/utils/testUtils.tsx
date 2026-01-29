/**
 * Test Utilities - Standard wrapper with all providers
 * 
 * NOTE: Provider mocks are in jest.setup.js - do NOT add jest.mock() here
 * as it won't work (jest.mock must be at module top level before imports)
 */
import React from 'react';
import { render, RenderOptions } from '@testing-library/react';

// Mock session boundary context value (for reference - actual mock in jest.setup.js)
export const mockSessionBoundaryValue = {
  sessionStatus: 'active' as const,
  sessionToken: 'test-session-token',
  tenantId: 'test-tenant',
  userId: 'test-user',
  session: { id: 'test-session-id' },
  isAuthenticated: true,
  isLoading: false,
  error: null,
  startSession: jest.fn().mockResolvedValue('test-session-token'),
  endSession: jest.fn().mockResolvedValue(undefined),
  refreshSession: jest.fn().mockResolvedValue('test-session-token'),
};

// Mock platform state context value (for reference - actual mock in jest.setup.js)
export const mockPlatformStateValue = {
  state: {
    session: {
      sessionId: 'test-session-id',
      tenantId: 'test-tenant',
      userId: 'test-user',
      session: null,
      isLoading: false,
      error: null,
    },
    execution: {
      executions: new Map(),
      activeExecutions: [],
      isLoading: false,
      error: null,
    },
    realm: {
      content: {},
      insights: {},
      journey: {},
      outcomes: {},
    },
    ui: {
      currentPillar: null,
      sidebarOpen: false,
      notifications: [],
      chatbot: {
        mainChatbotOpen: false,
        agentInfo: {
          title: '',
          agent: '',
          file_url: '',
          additional_info: '',
        },
        chatInputFocused: false,
        messageComposing: false,
      },
      analysisResults: {
        business: null,
        visualization: null,
        anomaly: null,
        eda: null,
      },
    },
  },
  submitIntent: jest.fn().mockResolvedValue('test-execution-id'),
  getExecutionStatus: jest.fn().mockResolvedValue({
    execution_id: 'test-execution-id',
    status: 'completed',
    intent_id: 'test-intent-id',
    artifacts: {},
  }),
  trackExecution: jest.fn(),
  untrackExecution: jest.fn(),
  setRealmState: jest.fn().mockResolvedValue(undefined),
  getRealmState: jest.fn().mockReturnValue({}),
  clearRealmState: jest.fn(),
  setCurrentPillar: jest.fn(),
  setSidebarOpen: jest.fn(),
  addNotification: jest.fn(),
  removeNotification: jest.fn(),
  setMainChatbotOpen: jest.fn(),
  setChatbotAgentInfo: jest.fn(),
  setChatInputFocused: jest.fn(),
  setMessageComposing: jest.fn(),
  setAnalysisResult: jest.fn(),
  clearAnalysisResults: jest.fn(),
  getShouldShowSecondaryChatbot: jest.fn().mockReturnValue(false),
  getPrimaryChatbotHeight: jest.fn().mockReturnValue('h-[87vh]'),
  getSecondaryChatbotPosition: jest.fn().mockReturnValue('translate-x-full opacity-0'),
  getPrimaryChatbotTransform: jest.fn().mockReturnValue('translate-y-0'),
  syncWithRuntime: jest.fn().mockResolvedValue(undefined),
};

/**
 * Standard wrapper for all tests
 * Uses mocked providers from jest.setup.js
 */
export const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>;
};

/**
 * Custom render function with all providers
 */
export function renderWithProviders(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: AllTheProviders, ...options });
}

// Re-export everything from testing-library
export * from '@testing-library/react';
export { renderWithProviders as render };
