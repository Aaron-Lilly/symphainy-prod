// Mock for legacy session providers (replaced by SessionBoundaryProvider/PlatformStateProvider)

// GlobalSessionProvider mock
const useGlobalSession = () => ({
  guideSessionToken: 'mock-session-token',
  tenantId: 'mock-tenant',
  isAuthenticated: true,
  session: { id: 'mock-session-id' },
});

const GlobalSessionProvider = ({ children }) => children;

// SessionProvider mock
const useSession = () => ({
  sessionToken: 'mock-session-token',
  tenantId: 'mock-tenant',
  isLoading: false,
  error: null,
});

const SessionProvider = ({ children }) => children;

// SessionContext mock (for legacy session-management tests)
const useSessionContext = () => ({
  sessionToken: 'mock-session-token',
  tenantId: 'mock-tenant',
  sessionId: 'mock-session-id',
  isAuthenticated: true,
  isLoading: false,
  error: null,
  sessionState: {
    has_sop: true,
    has_workflow: false,
    section2_complete: false,
  },
  elements: {
    sop: { id: 'sop1' },
    workflow: null,
  },
  chatbotState: {
    isOpen: false,
    currentAgent: null,
    messages: [],
  },
  setChatbotOpen: jest.fn(),
  clearSession: jest.fn(),
  refreshSession: jest.fn().mockResolvedValue(undefined),
  updateSessionState: jest.fn(),
});

module.exports = {
  useGlobalSession,
  GlobalSessionProvider,
  useSession,
  useSessionContext,
  SessionProvider,
  default: GlobalSessionProvider,
};
