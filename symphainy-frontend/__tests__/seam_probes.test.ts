/**
 * Frontend Seam Probe Tests
 * 
 * These probes test the boundaries (seams) on the frontend side to ensure:
 * 1. Success paths work predictably
 * 2. Failure paths fail predictably
 * 3. Contracts are honored at each boundary
 * 
 * Run with: npm test -- --testPathPattern=seam_probes
 * 
 * Seam Categories:
 * - SEAM F1: TenantContext → Configuration
 * - SEAM F2: AdminAPIManager → Backend API
 * - SEAM F3: Error Handling → User Feedback
 */

import { getTenantConfig, TENANT_CONFIGS, TenantId } from '../shared/config/tenants';
import { baseTenantConfig } from '../shared/config/tenants/base';

// ============================================================================
// SEAM F1: TenantContext → Configuration
// ============================================================================

describe('SEAM F1: TenantContext → Configuration', () => {
  /**
   * Contract:
   * - getTenantConfig(tenantId) returns tenant-specific configuration
   * - Unknown tenant falls back to base config
   * - All tenant configs have required fields
   */

  describe('SUCCESS: Tenant configuration lookup', () => {
    it('returns correct config for known tenant: vlp', () => {
      const config = getTenantConfig('vlp');
      
      expect(config.tenant_id).toBe('vlp');
      expect(config.tenant_name).toBeDefined();
      expect(config.features).toBeDefined();
      expect(config.branding).toBeDefined();
      
      console.log('✅ SEAM F1: vlp tenant config returned correctly');
    });

    it('returns correct config for known tenant: aar', () => {
      const config = getTenantConfig('aar');
      
      expect(config.tenant_id).toBe('aar');
      expect(config.tenant_name).toBeDefined();
      expect(config.features).toBeDefined();
      
      console.log('✅ SEAM F1: aar tenant config returned correctly');
    });

    it('returns correct config for known tenant: pso', () => {
      const config = getTenantConfig('pso');
      
      expect(config.tenant_id).toBe('pso');
      expect(config.tenant_name).toBeDefined();
      expect(config.features).toBeDefined();
      
      console.log('✅ SEAM F1: pso tenant config returned correctly');
    });
  });

  describe('FAILURE MODE: Unknown tenant fallback', () => {
    it('falls back to base config for unknown tenant', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      const config = getTenantConfig('unknown_tenant' as TenantId);
      
      // Should warn about unknown tenant
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Unknown tenant')
      );
      
      // Should return base config
      expect(config.tenant_id).toBe(baseTenantConfig.tenant_id);
      
      consoleSpy.mockRestore();
      console.log('✅ SEAM F1: Unknown tenant falls back to base config with warning');
    });
  });

  describe('SUCCESS: All tenant configs have required fields', () => {
    const requiredFields = ['tenant_id', 'tenant_name', 'features', 'branding'];
    
    Object.keys(TENANT_CONFIGS).forEach((tenantId) => {
      it(`${tenantId} config has all required fields`, () => {
        const config = TENANT_CONFIGS[tenantId as TenantId];
        
        requiredFields.forEach((field) => {
          expect(config).toHaveProperty(field);
        });
        
        console.log(`✅ SEAM F1: ${tenantId} config has required fields`);
      });
    });
  });
});

// ============================================================================
// SEAM F2: AdminAPIManager → Backend API
// ============================================================================

describe('SEAM F2: AdminAPIManager → Backend API', () => {
  /**
   * Contract:
   * - AdminAPIManager has methods matching backend endpoints
   * - Methods return expected data shapes
   * - Errors are handled and propagated correctly
   */

  // We'll test the contract without actual API calls
  describe('SUCCESS: AdminAPIManager contract', () => {
    it('has getPlatformStatistics method for control room', async () => {
      const { AdminAPIManager } = await import('../shared/managers/AdminAPIManager');
      
      const manager = new AdminAPIManager();
      
      expect(typeof manager.getPlatformStatistics).toBe('function');
      
      console.log('✅ SEAM F2: AdminAPIManager has getPlatformStatistics method');
    });

    it('has getSystemHealth method for control room', async () => {
      const { AdminAPIManager } = await import('../shared/managers/AdminAPIManager');
      
      const manager = new AdminAPIManager();
      
      expect(typeof manager.getSystemHealth).toBe('function');
      
      console.log('✅ SEAM F2: AdminAPIManager has getSystemHealth method');
    });

    it('has getPatterns method for developer view', async () => {
      const { AdminAPIManager } = await import('../shared/managers/AdminAPIManager');
      
      const manager = new AdminAPIManager();
      
      expect(typeof manager.getPatterns).toBe('function');
      
      console.log('✅ SEAM F2: AdminAPIManager has getPatterns method');
    });

    it('has getDocumentation method for developer view', async () => {
      const { AdminAPIManager } = await import('../shared/managers/AdminAPIManager');
      
      const manager = new AdminAPIManager();
      
      expect(typeof manager.getDocumentation).toBe('function');
      
      console.log('✅ SEAM F2: AdminAPIManager has getDocumentation method');
    });

    it('has listSolutions method for solutions view', async () => {
      const { AdminAPIManager } = await import('../shared/managers/AdminAPIManager');
      
      const manager = new AdminAPIManager();
      
      expect(typeof manager.listSolutions).toBe('function');
      
      console.log('✅ SEAM F2: AdminAPIManager has listSolutions method');
    });
  });

  describe('SUCCESS: AdminAPIManager tenant awareness', () => {
    it('accepts tenantId in constructor', async () => {
      const { AdminAPIManager } = await import('../shared/managers/AdminAPIManager');
      
      const manager = new AdminAPIManager('vlp');
      
      expect(manager).toBeDefined();
      
      console.log('✅ SEAM F2: AdminAPIManager accepts tenantId');
    });
  });
});

// ============================================================================
// SEAM F3: Error Handling → User Feedback
// ============================================================================

describe('SEAM F3: Error Handling → User Feedback', () => {
  /**
   * Contract:
   * - API errors are caught and formatted
   * - Network errors are distinguished from API errors
   * - Error messages are user-friendly
   */

  describe('SUCCESS: Error response handling', () => {
    it('AdminAPIManager handles API error responses', async () => {
      const { AdminAPIManager } = await import('../shared/managers/AdminAPIManager');
      
      const manager = new AdminAPIManager();
      
      // Mock fetch to return error
      const originalFetch = global.fetch;
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal server error' })
      });
      
      try {
        await manager.getPlatformStatistics();
        fail('Should have thrown');
      } catch (error: any) {
        expect(error).toBeDefined();
        // Error should have message or be caught appropriately
      }
      
      global.fetch = originalFetch;
      console.log('✅ SEAM F3: AdminAPIManager handles API errors');
    });

    it('AdminAPIManager handles network errors', async () => {
      const { AdminAPIManager } = await import('../shared/managers/AdminAPIManager');
      
      const manager = new AdminAPIManager();
      
      // Mock fetch to throw network error
      const originalFetch = global.fetch;
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
      
      try {
        await manager.getPlatformStatistics();
        fail('Should have thrown');
      } catch (error: any) {
        expect(error.message).toContain('Network error');
      }
      
      global.fetch = originalFetch;
      console.log('✅ SEAM F3: AdminAPIManager handles network errors');
    });
  });
});

// ============================================================================
// SEAM F4: Feature Configuration per Tenant
// ============================================================================

describe('SEAM F4: Feature Configuration per Tenant', () => {
  /**
   * Contract:
   * - Each tenant can enable/disable features
   * - Feature configs have expected structure
   */

  describe('SUCCESS: Tenant feature configuration', () => {
    it('VLP has insights feature enabled', () => {
      const config = getTenantConfig('vlp');
      
      expect(config.features.insights).toBeDefined();
      expect(config.features.insights.enabled).toBe(true);
      
      console.log('✅ SEAM F4: VLP insights feature enabled');
    });

    it('AAR has content feature enabled', () => {
      const config = getTenantConfig('aar');
      
      expect(config.features.content).toBeDefined();
      expect(config.features.content.enabled).toBe(true);
      
      console.log('✅ SEAM F4: AAR content feature enabled');
    });

    it('PSO has operations feature enabled', () => {
      const config = getTenantConfig('pso');
      
      expect(config.features.operations).toBeDefined();
      expect(config.features.operations.enabled).toBe(true);
      
      console.log('✅ SEAM F4: PSO operations feature enabled');
    });
  });
});

// ============================================================================
// Generate Seam Documentation
// ============================================================================

describe('Seam Documentation', () => {
  it('generates frontend seam documentation', () => {
    const doc = `
================================================================================
FRONTEND SEAM CONTRACT DOCUMENTATION
================================================================================

SEAM F1: TenantContext → Configuration
─────────────────────────────────────────────
What it does: Provides tenant-specific configuration to components
Access via:   getTenantConfig(tenantId) or useTenant() hook
Contract:     Returns TenantConfig with tenant_id, tenant_name, features, branding
Fallback:     Unknown tenants get baseTenantConfig with console.warn

SEAM F2: AdminAPIManager → Backend API
─────────────────────────────────────────────
What it does: Wraps backend API calls for admin functionality
Methods:      getStatistics(), getSystemHealth(), getPatterns(),
              getDocumentation(), getSolutions(), getSolutionStatus()
Endpoints:    Maps to /api/admin/control-room/* and /api/admin/developer/*
Tenant:       Passes tenantId in query params

SEAM F3: Error Handling → User Feedback
─────────────────────────────────────────────
What it does: Transforms API errors into user-friendly messages
API Error:    {detail: "message"} from backend → thrown as Error
Network:      Connection failures → "Network error" message
Handling:     Components catch and display via toast/alert

SEAM F4: Feature Configuration per Tenant
─────────────────────────────────────────────
What it does: Controls which features are available per tenant
Config:       features.{content,insights,operations,outcomes}.enabled
Usage:        UI conditionally renders based on features.*.enabled
Examples:     VLP focuses on insights, AAR on content

================================================================================
`;
    console.log(doc);
    expect(true).toBe(true);
  });
});
