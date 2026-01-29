require("@testing-library/jest-dom");
require("whatwg-fetch");

// Set up test environment variables
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
process.env.NEXT_PUBLIC_BACKEND_URL = 'http://localhost:8000';
process.env.NODE_ENV = 'test';

if (typeof global.TextEncoder === "undefined") {
  global.TextEncoder = require("util").TextEncoder;
}
if (typeof global.TextDecoder === "undefined") {
  global.TextDecoder = require("util").TextDecoder;
}

// Default fetch mock - returns a reasonable default response
// Tests can override this with jest.spyOn or mockImplementation
global.fetch = jest.fn(() => 
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ success: true, data: null }),
    text: () => Promise.resolve(''),
    headers: new Headers(),
  })
);

// Reset fetch mock before each test
beforeEach(() => {
  global.fetch.mockClear();
});

// Mock SessionBoundaryProvider globally
jest.mock('@/shared/state/SessionBoundaryProvider', () => ({
  useSessionBoundary: () => ({
    sessionStatus: 'active',
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
  }),
  SessionBoundaryProvider: ({ children }) => children,
}));

// Mock PlatformStateProvider globally with functional state tracking
jest.mock('@/shared/state/PlatformStateProvider', () => {
  const React = require('react');
  
  // Create a shared state store that persists across calls
  let realmStateStore = {
    content: {},
    insights: {},
    journey: {},
    outcomes: {},
  };
  
  // Reset store before each test
  const resetStore = () => {
    realmStateStore = {
      content: {},
      insights: {},
      journey: {},
      outcomes: {},
    };
  };
  
  // Make reset function available globally for tests
  if (typeof global !== 'undefined') {
    global.__resetPlatformStateStore = resetStore;
  }
  
  const usePlatformState = () => ({
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
      realm: realmStateStore,
      ui: {
        currentPillar: null,
        sidebarOpen: false,
        notifications: [],
        chatbot: {
          mainChatbotOpen: false,
          agentInfo: { title: '', agent: '', file_url: '', additional_info: '' },
          chatInputFocused: false,
          messageComposing: false,
        },
        analysisResults: { business: null, visualization: null, anomaly: null, eda: null },
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
    setRealmState: jest.fn((realm, key, value) => {
      // Actually store the value
      if (!realmStateStore[realm]) {
        realmStateStore[realm] = {};
      }
      realmStateStore[realm][key] = value;
      return Promise.resolve();
    }),
    getRealmState: jest.fn((realm, key) => {
      // Actually retrieve the value
      if (realmStateStore[realm] && key in realmStateStore[realm]) {
        return realmStateStore[realm][key];
      }
      return undefined;
    }),
    clearRealmState: jest.fn((realm) => {
      realmStateStore[realm] = {};
    }),
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
  });
  
  const PlatformStateProvider = ({ children }) => children;
  
  return {
    usePlatformState,
    PlatformStateProvider,
    __resetStore: resetStore,
  };
});
