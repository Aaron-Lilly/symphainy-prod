/**
 * Session Management Test Suite
 * 
 * Tests the unified session management system including:
 * - Session initialization and state management
 * - Session operations (refresh, clear)
 * - Chatbot state management
 * - Error handling and recovery
 * - Session expiration and activity tracking
 */

import React from 'react';
import { renderHook, act, waitFor } from '@testing-library/react';
import { SessionProvider, useSessionContext } from '../shared/components/SessionProvider';
import { useSession } from '../shared/hooks/useSession';

// Mock API functions
jest.mock('../lib/api/operations', () => ({
  getSessionElements: jest.fn(),
  clearSessionElements: jest.fn(),
}));

import { getSessionElements, clearSessionElements } from '../lib/api/operations';

const mockGetSessionElements = getSessionElements as jest.MockedFunction<typeof getSessionElements>;
const mockClearSessionElements = clearSessionElements as jest.MockedFunction<typeof clearSessionElements>;

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode; initialToken?: string }> = ({ 
  children, 
  initialToken = null 
}) => (
  <SessionProvider initialToken={initialToken} autoInitialize={true}>
    {children}
  </SessionProvider>
);

describe('Session Management System', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Session Initialization', () => {
    it('should initialize session with valid token', async () => {
      const mockSessionData = {
        valid: true,
        action: 'continue',
        session_state: {
          has_sop: true,
          has_workflow: false,
          section2_complete: false,
        },
        elements: { sop: { id: 'sop1' }, workflow: null },
      };

      mockGetSessionElements.mockResolvedValue(mockSessionData);

      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      expect(result.current.sessionState.isAuthenticated).toBe(true);
      expect(result.current.sessionState.globalToken).toBe('test-token');
      expect(result.current.sessionState.has_sop).toBe(true);
      expect(result.current.sessionState.has_workflow).toBe(false);
      expect(result.current.sessionElements).toEqual(mockSessionData.elements);
    });

    it('should handle initialization failure gracefully', async () => {
      mockGetSessionElements.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="invalid-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      expect(result.current.sessionState.error).toBe('Network error');
      expect(result.current.sessionState.isAuthenticated).toBe(false);
    });

    it('should not auto-initialize without token', async () => {
      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper>{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      expect(result.current.sessionState.isAuthenticated).toBe(false);
      expect(result.current.sessionState.globalToken).toBe(null);
      expect(mockGetSessionElements).not.toHaveBeenCalled();
    });
  });

  describe('Session Operations', () => {
    it('should refresh session successfully', async () => {
      const mockSessionData = {
        valid: true,
        action: 'continue',
        session_state: {
          has_sop: true,
          has_workflow: true,
          section2_complete: true,
        },
        elements: { sop: { id: 'sop1' }, workflow: { id: 'workflow1' } },
      };

      mockGetSessionElements.mockResolvedValue(mockSessionData);

      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      // Update session state to simulate changes
      act(() => {
        result.current.updateSessionState({
          has_sop: false,
          has_workflow: false,
        });
      });

      expect(result.current.sessionState.has_sop).toBe(false);
      expect(result.current.sessionState.has_workflow).toBe(false);

      // Refresh session
      await act(async () => {
        await result.current.refreshSession();
      });

      expect(result.current.sessionState.has_sop).toBe(true);
      expect(result.current.sessionState.has_workflow).toBe(true);
      expect(result.current.sessionState.section2_complete).toBe(true);
    });

    it('should clear session successfully', async () => {
      mockGetSessionElements.mockResolvedValue({
        valid: true,
        action: 'continue',
        session_state: { has_sop: false, has_workflow: false, section2_complete: false },
        elements: null,
      });

      mockClearSessionElements.mockResolvedValue(undefined);

      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      expect(result.current.sessionState.isAuthenticated).toBe(true);

      // Clear session
      await act(async () => {
        await result.current.clearSession();
      });

      expect(result.current.sessionState.isAuthenticated).toBe(false);
      expect(result.current.sessionState.globalToken).toBe(null);
      expect(result.current.sessionElements).toBe(null);
      expect(mockClearSessionElements).toHaveBeenCalledWith('test-token');
    });

    it('should handle session refresh failure', async () => {
      mockGetSessionElements
        .mockResolvedValueOnce({
          valid: true,
          action: 'continue',
          session_state: { has_sop: false, has_workflow: false, section2_complete: false },
          elements: null,
        })
        .mockRejectedValueOnce(new Error('Refresh failed'));

      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      // Refresh session
      await act(async () => {
        await result.current.refreshSession();
      });

      expect(result.current.sessionState.error).toBe('Refresh failed');
      expect(result.current.sessionState.isLoading).toBe(false);
    });
  });

  describe('Chatbot State Management', () => {
    it('should manage chatbot open state', async () => {
      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      expect(result.current.sessionState.chatbotOpen).toBe(true);

      // Close chatbot
      act(() => {
        result.current.setChatbotOpen(false);
      });

      expect(result.current.sessionState.chatbotOpen).toBe(false);

      // Open chatbot
      act(() => {
        result.current.setChatbotOpen(true);
      });

      expect(result.current.sessionState.chatbotOpen).toBe(true);
    });

    it('should manage chatbot agent info', async () => {
      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      const newAgentInfo = {
        title: 'Test Agent',
        agent: 'test-agent',
        file_url: 'https://example.com/file',
        additional_info: 'Test info',
      };

      act(() => {
        result.current.setChatbotAgentInfo(newAgentInfo);
      });

      expect(result.current.sessionState.chatbotAgentInfo).toEqual(newAgentInfo);
    });
  });

  describe('Session Validation', () => {
    it('should validate session correctly', async () => {
      mockGetSessionElements.mockResolvedValue({
        valid: true,
        action: 'continue',
        session_state: { has_sop: false, has_workflow: false, section2_complete: false },
        elements: null,
      });

      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      expect(result.current.isSessionValid()).toBe(true);

      // Test invalid session
      act(() => {
        result.current.updateSessionState({
          isValid: false,
          globalToken: null,
        });
      });

      expect(result.current.isSessionValid()).toBe(false);
    });

    it('should calculate session age correctly', async () => {
      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      const sessionAge = result.current.getSessionAge();
      expect(sessionAge).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Session Expiration', () => {
    it('should detect session expiration', async () => {
      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => (
          <SessionProvider initialToken="test-token" sessionTimeoutMinutes={1}>
            {children}
          </SessionProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      // Set last activity to 2 minutes ago (expired)
      act(() => {
        result.current.updateSessionState({
          lastActivity: new Date(Date.now() - 2 * 60 * 1000),
        });
      });

      expect(result.current.isSessionExpired).toBe(true);
    });

    it('should not expire active session', async () => {
      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => (
          <SessionProvider initialToken="test-token" sessionTimeoutMinutes={30}>
            {children}
          </SessionProvider>
        ),
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      // Set last activity to 5 minutes ago (not expired)
      act(() => {
        result.current.updateSessionState({
          lastActivity: new Date(Date.now() - 5 * 60 * 1000),
        });
      });

      expect(result.current.isSessionExpired).toBe(false);
    });
  });

  describe('Activity Tracking', () => {
    it('should update last activity on user interaction', async () => {
      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      const initialActivity = result.current.sessionState.lastActivity;

      // Simulate user activity
      act(() => {
        result.current.updateLastActivity();
      });

      expect(result.current.sessionState.lastActivity).not.toBe(initialActivity);
      expect(result.current.sessionState.lastActivity).toBeInstanceOf(Date);
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      mockGetSessionElements.mockRejectedValue(new Error('API Error'));

      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      expect(result.current.sessionState.error).toBe('API Error');
      expect(result.current.sessionState.isLoading).toBe(false);
    });

    it('should clear errors on successful operations', async () => {
      mockGetSessionElements
        .mockRejectedValueOnce(new Error('Initial Error'))
        .mockResolvedValueOnce({
          valid: true,
          action: 'continue',
          session_state: { has_sop: false, has_workflow: false, section2_complete: false },
          elements: null,
        });

      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      expect(result.current.sessionState.error).toBe('Initial Error');

      // Refresh session to clear error
      await act(async () => {
        await result.current.refreshSession();
      });

      expect(result.current.sessionState.error).toBe(null);
    });
  });

  describe('Performance and Memory', () => {
    it('should not cause memory leaks', async () => {
      const { result, unmount } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      // Simulate multiple state updates
      for (let i = 0; i < 100; i++) {
        act(() => {
          result.current.updateSessionState({
            lastActivity: new Date(),
          });
        });
      }

      // Unmount should not cause errors
      expect(() => unmount()).not.toThrow();
    });

    it('should handle rapid state updates efficiently', async () => {
      const { result } = renderHook(() => useSessionContext(), {
        wrapper: ({ children }) => <TestWrapper initialToken="test-token">{children}</TestWrapper>,
      });

      await waitFor(() => {
        expect(result.current.isInitialized).toBe(true);
      });

      // Rapid state updates
      const startTime = Date.now();
      
      for (let i = 0; i < 50; i++) {
        act(() => {
          result.current.updateSessionState({
            lastActivity: new Date(),
          });
        });
      }

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Should complete quickly (less than 100ms)
      expect(duration).toBeLessThan(100);
    });
  });
}); 