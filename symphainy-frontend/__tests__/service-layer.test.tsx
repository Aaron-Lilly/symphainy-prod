/**
 * Service Layer Test Suite
 * 
 * Tests the service layer components including:
 * - API service with error handling and retry logic
 * - WebSocket service with connection management
 * - Service layer manager and configuration
 * - Session integration and authentication
 */

import React from 'react';
import { renderHook, act, waitFor } from '@testing-library/react';
import { 
  APIService, 
  WebSocketService, 
  ServiceLayerManager,
  useServiceLayer,
  createServiceConfig,
  initializeServiceLayer,
} from '../shared/services';
import { SessionProvider, useSessionContext } from '../shared/components/SessionProvider';

// Mock fetch for API testing
global.fetch = jest.fn();

// Mock WebSocket for WebSocket testing
global.WebSocket = jest.fn();

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <SessionProvider autoInitialize={false}>
    {children}
  </SessionProvider>
);

describe('Service Layer', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('API Service', () => {
    let apiService: APIService;

    beforeEach(() => {
      apiService = new APIService({
        baseURL: 'http://test-api.com',
        timeout: 5000,
        maxRetries: 2,
        retryDelay: 100,
      });
    });

    it('should make successful GET request', async () => {
      const mockResponse = { data: 'test data' };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve(mockResponse),
      });

      const result = await apiService.get('/test');

      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockResponse);
      expect(result.status).toBe(200);
      expect(fetch).toHaveBeenCalledWith(
        'http://test-api.com/test',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should handle API errors gracefully', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ message: 'Resource not found' }),
      });

      await expect(apiService.get('/not-found')).rejects.toThrow('HTTP 404 error');
    });

    it('should retry failed requests', async () => {
      const mockResponse = { data: 'success' };
      
      // First two calls fail, third succeeds
      (fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          statusText: 'OK',
          headers: new Headers({ 'content-type': 'application/json' }),
          json: () => Promise.resolve(mockResponse),
        });

      const result = await apiService.get('/test', { retries: 2 });

      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockResponse);
      expect(result.retryCount).toBe(2);
      expect(fetch).toHaveBeenCalledTimes(3);
    });

    it('should handle timeout errors', async () => {
      (fetch as jest.Mock).mockImplementation(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 100)
        )
      );

      await expect(apiService.get('/timeout', { timeout: 50 })).rejects.toThrow('Request timeout');
    });

    it('should add authentication headers when session is available', async () => {
      const mockResponse = { data: 'authenticated' };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve(mockResponse),
      });

      // Mock session context
      const mockSessionContext = {
        sessionState: {
          globalToken: 'test-token',
        },
      };
      apiService.setSessionContext(mockSessionContext);

      await apiService.get('/authenticated', { requireAuth: true });

      expect(fetch).toHaveBeenCalledWith(
        'http://test-api.com/authenticated',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
          }),
        })
      );
    });

    it('should handle different response types', async () => {
      const textResponse = 'plain text response';
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Headers({ 'content-type': 'text/plain' }),
        text: () => Promise.resolve(textResponse),
      });

      const result = await apiService.get('/text');

      expect(result.data).toBe(textResponse);
    });
  });

  describe('WebSocket Service', () => {
    let webSocketService: WebSocketService;
    let mockWebSocket: any;

    beforeEach(() => {
      webSocketService = new WebSocketService({
        baseURL: 'ws://test-ws.com',
        reconnectAttempts: 2,
        reconnectDelay: 100,
      });

      // Mock WebSocket implementation
      mockWebSocket = {
        readyState: 1, // OPEN
        send: jest.fn(),
        close: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
      };
      (global.WebSocket as jest.Mock).mockImplementation(() => mockWebSocket);
    });

    it('should connect to WebSocket successfully', async () => {
      const connectionId = await webSocketService.connect('/test');

      expect(connectionId).toBeDefined();
      expect(webSocketService.isConnected(connectionId)).toBe(true);
      expect(global.WebSocket).toHaveBeenCalledWith('ws://test-ws.com/test');
    });

    it('should handle connection failures', async () => {
      (global.WebSocket as jest.Mock).mockImplementation(() => {
        const ws = { ...mockWebSocket };
        setTimeout(() => {
          ws.onerror(new Error('Connection failed'));
        }, 0);
        return ws;
      });

      await expect(webSocketService.connect('/test')).rejects.toThrow('WebSocket connection error');
    });

    it('should send messages when connected', async () => {
      const connectionId = await webSocketService.connect('/test');
      const message = { type: 'test', data: 'hello', timestamp: Date.now() };

      await webSocketService.send(connectionId, message);

      expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify(message));
    });

    it('should queue messages when disconnected', async () => {
      const connectionId = await webSocketService.connect('/test');
      
      // Simulate disconnection
      mockWebSocket.readyState = 3; // CLOSED
      const message = { type: 'test', data: 'queued', timestamp: Date.now() };

      await webSocketService.send(connectionId, message);

      // Message should be queued (no error thrown)
      expect(mockWebSocket.send).not.toHaveBeenCalled();
    });

    it('should handle message subscriptions', async () => {
      const connectionId = await webSocketService.connect('/test');
      const listener = jest.fn();
      
      const unsubscribe = webSocketService.subscribe(connectionId, 'test-event', listener);

      // Simulate receiving a message
      const message = { type: 'test-event', data: 'test data', timestamp: Date.now() };
      mockWebSocket.onmessage({ data: JSON.stringify(message) });

      expect(listener).toHaveBeenCalledWith(message);

      // Test unsubscribe
      unsubscribe();
      listener.mockClear();
      
      mockWebSocket.onmessage({ data: JSON.stringify(message) });
      expect(listener).not.toHaveBeenCalled();
    });

    it('should handle automatic reconnection', async () => {
      const connectionId = await webSocketService.connect('/test');

      // Simulate disconnection
      mockWebSocket.onclose({ code: 1000, reason: 'Normal closure' });

      // Should attempt reconnection
      expect(webSocketService.getConnectionStatus(connectionId)).toBe('disconnected');
    });

    it('should add authentication to WebSocket URL', async () => {
      const mockSessionContext = {
        sessionState: {
          globalToken: 'test-token',
        },
      };
      webSocketService.setSessionContext(mockSessionContext);

      await webSocketService.connect('/authenticated', { requireAuth: true });

      expect(global.WebSocket).toHaveBeenCalledWith(
        'ws://test-ws.com/authenticated?token=test-token'
      );
    });
  });

  describe('Service Layer Manager', () => {
    let manager: ServiceLayerManager;

    beforeEach(() => {
      manager = new ServiceLayerManager();
    });

    it('should initialize with session context', () => {
      const mockSessionContext = {
        sessionState: { globalToken: 'test-token' },
      };

      manager.initialize(mockSessionContext);

      expect(manager.getAPIService()).toBeDefined();
      expect(manager.getWebSocketService()).toBeDefined();
    });

    it('should update configuration for all services', () => {
      const config = {
        api: { timeout: 10000 },
        websocket: { reconnectAttempts: 5 },
      };

      manager.updateConfig(config);

      const apiConfig = manager.getAPIService().getConfig();
      const wsConfig = manager.getWebSocketService().getConfig();

      expect(apiConfig.timeout).toBe(10000);
      expect(wsConfig.reconnectAttempts).toBe(5);
    });

    it('should cleanup all services', () => {
      const webSocketService = manager.getWebSocketService();
      const disconnectSpy = jest.spyOn(webSocketService, 'disconnectAll');

      manager.cleanup();

      expect(disconnectSpy).toHaveBeenCalled();
    });
  });

  describe('React Hooks', () => {
    it('should provide service layer through hook', () => {
      const { result } = renderHook(() => useServiceLayer(), {
        wrapper: TestWrapper,
      });

      expect(result.current.api).toBeDefined();
      expect(result.current.websocket).toBeDefined();
      expect(result.current.manager).toBeDefined();
    });

    it('should initialize services with session context', async () => {
      const { result } = renderHook(() => useServiceLayer(), {
        wrapper: TestWrapper,
      });

      await waitFor(() => {
        expect(result.current.manager).toBeDefined();
      });
    });
  });

  describe('Configuration', () => {
    it('should create development configuration', () => {
      const config = createServiceConfig('development');

      expect(config.api.baseURL).toBe('http://127.0.0.1:8000');
      expect(config.websocket.baseURL).toBe('ws://127.0.0.1:8000');
    });

    it('should create staging configuration', () => {
      const config = createServiceConfig('staging');

      expect(config.api.baseURL).toContain('staging');
      expect(config.websocket.baseURL).toContain('staging');
      expect(config.api.timeout).toBe(45000);
      expect(config.api.maxRetries).toBe(5);
    });

    it('should create production configuration', () => {
      const config = createServiceConfig('production');

      expect(config.api.baseURL).toContain('production');
      expect(config.websocket.baseURL).toContain('production');
      expect(config.api.timeout).toBe(60000);
      expect(config.api.maxRetries).toBe(7);
    });

    it('should initialize service layer with environment config', () => {
      const manager = initializeServiceLayer('development');

      expect(manager).toBeDefined();
      const apiConfig = manager.getAPIService().getConfig();
      expect(apiConfig.baseURL).toBe('http://127.0.0.1:8000');
    });
  });

  describe('Integration Tests', () => {
    it('should handle API and WebSocket services together', async () => {
      const manager = new ServiceLayerManager();
      const mockSessionContext = {
        sessionState: { globalToken: 'test-token' },
      };

      manager.initialize(mockSessionContext);

      // Test API service
      const mockResponse = { data: 'api response' };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve(mockResponse),
      });

      const apiResult = await manager.getAPIService().get('/test');
      expect(apiResult.success).toBe(true);

      // Test WebSocket service
      (global.WebSocket as jest.Mock).mockImplementation(() => mockWebSocket);
      const wsConnectionId = await manager.getWebSocketService().connect('/test');
      expect(wsConnectionId).toBeDefined();
    });

    it('should handle service errors gracefully', async () => {
      const manager = new ServiceLayerManager();
      const mockSessionContext = {
        sessionState: { globalToken: 'test-token' },
      };

      manager.initialize(mockSessionContext);

      // Test API error handling
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(manager.getAPIService().get('/error')).rejects.toThrow('Network error');

      // Test WebSocket error handling
      (global.WebSocket as jest.Mock).mockImplementation(() => {
        const ws = { ...mockWebSocket };
        setTimeout(() => ws.onerror(new Error('Connection failed')), 0);
        return ws;
      });

      await expect(manager.getWebSocketService().connect('/error')).rejects.toThrow('WebSocket connection error');
    });
  });
}); 