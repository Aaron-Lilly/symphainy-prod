/**
 * AdminAPIManager Tests
 * 
 * Tests the admin API manager for control tower functionality,
 * verifying it correctly builds URLs with tenant and session context.
 */

import { AdminAPIManager } from '../shared/managers/AdminAPIManager';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('AdminAPIManager', () => {
  let manager: AdminAPIManager;
  const TEST_SESSION_ID = 'test-session-123';
  const TEST_TENANT_ID = 'aar';
  
  beforeEach(() => {
    mockFetch.mockClear();
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ success: true }),
    });
    
    manager = new AdminAPIManager(TEST_SESSION_ID, TEST_TENANT_ID);
  });

  describe('constructor', () => {
    it('initializes with session and tenant IDs', () => {
      const mgr = new AdminAPIManager('session-1', 'vlp');
      expect(mgr).toBeDefined();
    });

    it('defaults tenant to null if not provided', () => {
      const mgr = new AdminAPIManager('session-1');
      expect(mgr).toBeDefined();
    });
  });

  describe('setContext', () => {
    it('updates session and tenant IDs', () => {
      manager.setContext('new-session', 'pso');
      expect(manager).toBeDefined();
    });
  });

  describe('URL building', () => {
    it('includes session_id and tenant_id in query params', async () => {
      await manager.getPlatformStatistics();
      
      expect(mockFetch).toHaveBeenCalledTimes(1);
      const calledUrl = mockFetch.mock.calls[0][0];
      
      expect(calledUrl).toContain('session_id=test-session-123');
      expect(calledUrl).toContain('tenant_id=aar');
    });

    it('constructs correct control room endpoint paths', async () => {
      await manager.getPlatformStatistics();
      
      const calledUrl = mockFetch.mock.calls[0][0];
      expect(calledUrl).toContain('/api/admin/control-room/statistics');
    });
  });

  describe('Control Room API methods', () => {
    it('getPlatformStatistics makes GET request to correct endpoint', async () => {
      await manager.getPlatformStatistics();
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/control-room/statistics');
      expect(options.method).toBe('GET');
    });

    it('getExecutionMetrics makes GET request with time_range param', async () => {
      await manager.getExecutionMetrics('4h');
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/control-room/execution-metrics');
      expect(url).toContain('time_range=4h');
      expect(options.method).toBe('GET');
    });

    it('getRealmHealth makes GET request', async () => {
      await manager.getRealmHealth();
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/control-room/realm-health');
      expect(options.method).toBe('GET');
    });

    it('getSolutionRegistryStatus makes GET request', async () => {
      await manager.getSolutionRegistryStatus();
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/control-room/solution-registry');
      expect(options.method).toBe('GET');
    });

    it('getSystemHealth makes GET request', async () => {
      await manager.getSystemHealth();
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/control-room/system-health');
      expect(options.method).toBe('GET');
    });
  });

  describe('Developer View API methods', () => {
    it('getDocumentation makes GET request', async () => {
      await manager.getDocumentation();
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/developer/documentation');
      expect(options.method).toBe('GET');
    });

    it('getDocumentation passes section param when provided', async () => {
      await manager.getDocumentation('architecture');
      
      const [url] = mockFetch.mock.calls[0];
      expect(url).toContain('section=architecture');
    });

    it('getCodeExamples makes GET request', async () => {
      await manager.getCodeExamples();
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/developer/code-examples');
      expect(options.method).toBe('GET');
    });

    it('getPatterns makes GET request', async () => {
      await manager.getPatterns();
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/developer/patterns');
      expect(options.method).toBe('GET');
    });

    it('validateSolution makes POST request', async () => {
      await manager.validateSolution({ solution_config: { name: 'test' } });
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/developer/validate-solution');
      expect(options.method).toBe('POST');
    });
  });

  describe('Business User View API methods', () => {
    it('getCompositionGuide makes GET request', async () => {
      await manager.getCompositionGuide();
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/business/composition-guide');
      expect(options.method).toBe('GET');
    });

    it('getSolutionTemplates makes GET request', async () => {
      await manager.getSolutionTemplates();
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/business/templates');
      expect(options.method).toBe('GET');
    });

    it('composeSolution makes POST request', async () => {
      await manager.composeSolution({ solution_config: { name: 'test' } });
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/business/compose');
      expect(options.method).toBe('POST');
    });

    it('listSolutions makes GET request', async () => {
      await manager.listSolutions();
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toContain('/api/admin/business/solutions');
      expect(options.method).toBe('GET');
    });
  });

  describe('error handling', () => {
    it('throws error on non-ok response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Internal Server Error',
        json: async () => ({ detail: 'Server error' }),
      });

      await expect(manager.getPlatformStatistics()).rejects.toThrow('Server error');
    });

    it('throws error with statusText when detail not available', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
        json: async () => ({}),
      });

      await expect(manager.getPlatformStatistics()).rejects.toThrow('Request failed: Not Found');
    });

    it('handles fetch errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(manager.getPlatformStatistics()).rejects.toThrow('Network error');
    });
  });

  describe('tenant context switching', () => {
    it('uses new tenant ID after setContext', async () => {
      manager.setContext(TEST_SESSION_ID, 'vlp');
      await manager.getPlatformStatistics();
      
      const calledUrl = mockFetch.mock.calls[0][0];
      expect(calledUrl).toContain('tenant_id=vlp');
    });

    it('uses new session ID after setContext', async () => {
      manager.setContext('new-session-456', TEST_TENANT_ID);
      await manager.getPlatformStatistics();
      
      const calledUrl = mockFetch.mock.calls[0][0];
      expect(calledUrl).toContain('session_id=new-session-456');
    });
  });
});
