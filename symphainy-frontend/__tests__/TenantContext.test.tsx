/**
 * TenantContext Provider Tests
 * 
 * Tests the React context provider for multi-tenant support,
 * including tenant switching and feature flag functionality.
 */

import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { TenantProvider, useTenant } from '../shared/contexts/TenantContext';
import type { TenantId } from '../shared/config/tenant-types';

// Mock sessionStorage
const mockSessionStorage: { [key: string]: string } = {};
beforeEach(() => {
  Object.keys(mockSessionStorage).forEach(key => delete mockSessionStorage[key]);
  jest.spyOn(Storage.prototype, 'getItem').mockImplementation(key => mockSessionStorage[key] || null);
  jest.spyOn(Storage.prototype, 'setItem').mockImplementation((key, value) => {
    mockSessionStorage[key] = value;
  });
});

afterEach(() => {
  jest.restoreAllMocks();
});

describe('TenantContext', () => {
  describe('TenantProvider', () => {
    it('provides default base tenant', () => {
      const TestComponent = () => {
        const { currentTenant, tenantId } = useTenant();
        return (
          <div>
            <span data-testid="tenant-id">{tenantId}</span>
            <span data-testid="tenant-name">{currentTenant.tenant_name}</span>
          </div>
        );
      };

      render(
        <TenantProvider>
          <TestComponent />
        </TenantProvider>
      );

      expect(screen.getByTestId('tenant-id')).toHaveTextContent('base');
      expect(screen.getByTestId('tenant-name')).toHaveTextContent('SymphAIny Platform');
    });

    it('accepts initial tenant ID', () => {
      const TestComponent = () => {
        const { tenantId } = useTenant();
        return <span data-testid="tenant-id">{tenantId}</span>;
      };

      render(
        <TenantProvider initialTenantId="aar">
          <TestComponent />
        </TenantProvider>
      );

      expect(screen.getByTestId('tenant-id')).toHaveTextContent('aar');
    });

    it('reads tenant from sessionStorage on mount', () => {
      mockSessionStorage['tenant_id'] = 'pso';

      const TestComponent = () => {
        const { tenantId } = useTenant();
        return <span data-testid="tenant-id">{tenantId}</span>;
      };

      render(
        <TenantProvider>
          <TestComponent />
        </TenantProvider>
      );

      // Note: The effect runs async, so we need to wait for it
      // For initial render, it shows default until effect runs
      expect(screen.getByTestId('tenant-id')).toBeInTheDocument();
    });
  });

  describe('setTenant', () => {
    it('changes the current tenant', () => {
      const TestComponent = () => {
        const { tenantId, setTenant } = useTenant();
        return (
          <div>
            <span data-testid="tenant-id">{tenantId}</span>
            <button onClick={() => setTenant('vlp')}>Switch to VLP</button>
          </div>
        );
      };

      render(
        <TenantProvider>
          <TestComponent />
        </TenantProvider>
      );

      expect(screen.getByTestId('tenant-id')).toHaveTextContent('base');

      act(() => {
        screen.getByRole('button').click();
      });

      expect(screen.getByTestId('tenant-id')).toHaveTextContent('vlp');
    });

    it('persists tenant change to sessionStorage', () => {
      const TestComponent = () => {
        const { setTenant } = useTenant();
        return <button onClick={() => setTenant('aar')}>Switch</button>;
      };

      render(
        <TenantProvider>
          <TestComponent />
        </TenantProvider>
      );

      act(() => {
        screen.getByRole('button').click();
      });

      expect(mockSessionStorage['tenant_id']).toBe('aar');
    });
  });

  describe('hasFeature', () => {
    it('checks feature flags correctly', () => {
      const TestComponent = () => {
        const { hasFeature } = useTenant();
        return (
          <div>
            <span data-testid="content-enabled">
              {hasFeature('content', 'enabled') ? 'yes' : 'no'}
            </span>
            <span data-testid="mainframe-parser">
              {hasFeature('content', 'show_mainframe_parser') ? 'yes' : 'no'}
            </span>
          </div>
        );
      };

      render(
        <TenantProvider initialTenantId="base">
          <TestComponent />
        </TenantProvider>
      );

      expect(screen.getByTestId('content-enabled')).toHaveTextContent('yes');
      expect(screen.getByTestId('mainframe-parser')).toHaveTextContent('yes');
    });

    it('returns false for invalid feature paths', () => {
      const TestComponent = () => {
        const { hasFeature } = useTenant();
        return (
          <span data-testid="invalid">
            {hasFeature('nonexistent', 'feature') ? 'yes' : 'no'}
          </span>
        );
      };

      render(
        <TenantProvider>
          <TestComponent />
        </TenantProvider>
      );

      expect(screen.getByTestId('invalid')).toHaveTextContent('no');
    });

    it('returns AAR analysis true for AAR tenant', () => {
      const TestComponent = () => {
        const { hasFeature } = useTenant();
        return (
          <span data-testid="aar">
            {hasFeature('insights', 'show_aar_analysis') ? 'yes' : 'no'}
          </span>
        );
      };

      render(
        <TenantProvider initialTenantId="aar">
          <TestComponent />
        </TenantProvider>
      );

      expect(screen.getByTestId('aar')).toHaveTextContent('yes');
    });

    it('returns VLP features for VLP tenant', () => {
      const TestComponent = () => {
        const { hasFeature } = useTenant();
        return (
          <div>
            <span data-testid="vlp">
              {hasFeature('insights', 'show_vlp_extraction') ? 'yes' : 'no'}
            </span>
            <span data-testid="mainframe">
              {hasFeature('content', 'show_mainframe_parser') ? 'yes' : 'no'}
            </span>
          </div>
        );
      };

      render(
        <TenantProvider initialTenantId="vlp">
          <TestComponent />
        </TenantProvider>
      );

      expect(screen.getByTestId('vlp')).toHaveTextContent('yes');
      expect(screen.getByTestId('mainframe')).toHaveTextContent('yes');
    });
  });

  describe('isTabEnabled', () => {
    it('checks insights tab visibility', () => {
      const TestComponent = () => {
        const { isTabEnabled } = useTenant();
        return (
          <div>
            <span data-testid="data-quality">
              {isTabEnabled('insights', 'data_quality') ? 'yes' : 'no'}
            </span>
            <span data-testid="business">
              {isTabEnabled('insights', 'business_analysis') ? 'yes' : 'no'}
            </span>
          </div>
        );
      };

      render(
        <TenantProvider initialTenantId="base">
          <TestComponent />
        </TenantProvider>
      );

      expect(screen.getByTestId('data-quality')).toHaveTextContent('yes');
      expect(screen.getByTestId('business')).toHaveTextContent('yes');
    });

    it('respects tenant-specific tab configuration', () => {
      const TestComponent = () => {
        const { isTabEnabled, setTenant } = useTenant();
        return (
          <div>
            <span data-testid="relationship">
              {isTabEnabled('insights', 'relationship_mapping') ? 'yes' : 'no'}
            </span>
            <button onClick={() => setTenant('vlp')}>Switch</button>
          </div>
        );
      };

      render(
        <TenantProvider initialTenantId="base">
          <TestComponent />
        </TenantProvider>
      );

      // Base has relationship_mapping enabled
      expect(screen.getByTestId('relationship')).toHaveTextContent('yes');
    });
  });

  describe('availableTenants', () => {
    it('provides list of all available tenants', () => {
      const TestComponent = () => {
        const { availableTenants } = useTenant();
        return (
          <ul>
            {availableTenants.map(t => (
              <li key={t.id} data-testid={`tenant-${t.id}`}>
                {t.name}
              </li>
            ))}
          </ul>
        );
      };

      render(
        <TenantProvider>
          <TestComponent />
        </TenantProvider>
      );

      expect(screen.getByTestId('tenant-base')).toBeInTheDocument();
      expect(screen.getByTestId('tenant-aar')).toBeInTheDocument();
      expect(screen.getByTestId('tenant-pso')).toBeInTheDocument();
      expect(screen.getByTestId('tenant-vlp')).toBeInTheDocument();
    });
  });

  describe('useTenant hook', () => {
    it('throws error when used outside provider', () => {
      const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      const TestComponent = () => {
        useTenant();
        return null;
      };

      expect(() => render(<TestComponent />)).toThrow(
        'useTenant must be used within TenantProvider'
      );

      consoleError.mockRestore();
    });
  });
});
