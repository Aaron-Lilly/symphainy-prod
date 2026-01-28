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

module.exports = {
  useGlobalSession,
  GlobalSessionProvider,
  useSession,
  SessionProvider,
  default: GlobalSessionProvider,
};
