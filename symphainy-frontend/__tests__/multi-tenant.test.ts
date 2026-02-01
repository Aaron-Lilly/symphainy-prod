/**
 * Multi-Tenant Configuration Tests
 * 
 * These tests validate the tenant configuration system
 * implemented for the multi-tenant demo support feature.
 */

import { 
  getTenantConfig, 
  getAvailableTenants,
  baseTenantConfig,
  aarTenantConfig,
  psoTenantConfig,
  vlpTenantConfig
} from '../shared/config/tenants';
import type { TenantId, TenantConfig } from '../shared/config/tenant-types';

describe('Tenant Configuration System', () => {
  describe('getTenantConfig', () => {
    it('returns base config by default', () => {
      const config = getTenantConfig('base');
      expect(config.tenant_id).toBe('base');
      expect(config.tenant_name).toBe('SymphAIny Platform');
    });

    it('returns AAR config when requested', () => {
      const config = getTenantConfig('aar');
      expect(config.tenant_id).toBe('aar');
      expect(config.tenant_name).toBe('Navy AAR Analysis Demo');
      expect(config.branding?.primary_color).toBe('#1e3a5f'); // Navy blue
    });

    it('returns PSO config when requested', () => {
      const config = getTenantConfig('pso');
      expect(config.tenant_id).toBe('pso');
      expect(config.tenant_name).toBe('Permit & Service Order Processing Demo');
      expect(config.branding?.primary_color).toBe('#2d5a27'); // Utility green
    });

    it('returns VLP config when requested', () => {
      const config = getTenantConfig('vlp');
      expect(config.tenant_id).toBe('vlp');
      expect(config.tenant_name).toBe('Variable Life Policy Processing Demo');
      expect(config.branding?.primary_color).toBe('#4a1c6b'); // Insurance purple
    });

    it('falls back to base config for unknown tenant', () => {
      const config = getTenantConfig('unknown' as TenantId);
      expect(config.tenant_id).toBe('base');
    });
  });

  describe('getAvailableTenants', () => {
    it('returns all four tenants', () => {
      const tenants = getAvailableTenants();
      expect(tenants).toHaveLength(4);
    });

    it('includes all tenant IDs', () => {
      const tenants = getAvailableTenants();
      const ids = tenants.map(t => t.id);
      expect(ids).toContain('base');
      expect(ids).toContain('aar');
      expect(ids).toContain('pso');
      expect(ids).toContain('vlp');
    });

    it('tenants have required properties', () => {
      const tenants = getAvailableTenants();
      tenants.forEach(tenant => {
        expect(tenant).toHaveProperty('id');
        expect(tenant).toHaveProperty('name');
        expect(tenant).toHaveProperty('description');
      });
    });
  });

  describe('Feature Configurations', () => {
    describe('Base tenant', () => {
      it('has all features enabled', () => {
        const config = baseTenantConfig;
        
        // Content features
        expect(config.features.content.enabled).toBe(true);
        expect(config.features.content.show_mainframe_parser).toBe(true);
        expect(config.features.content.show_edi_parser).toBe(true);
        
        // Insights features - all tabs enabled
        expect(config.features.insights.enabled).toBe(true);
        expect(config.features.insights.tabs?.data_quality).toBe(true);
        expect(config.features.insights.tabs?.business_analysis).toBe(true);
        
        // Operations features
        expect(config.features.operations.enabled).toBe(true);
        expect(config.features.operations.show_sop_generator).toBe(true);
        expect(config.features.operations.show_workflow_builder).toBe(true);
        expect(config.features.operations.show_coexistence_analysis).toBe(true);
        
        // Outcomes features
        expect(config.features.outcomes.enabled).toBe(true);
        expect(config.features.outcomes.show_blueprint_generator).toBe(true);
        expect(config.features.outcomes.show_roadmap_generator).toBe(true);
        expect(config.features.outcomes.show_poc_generator).toBe(true);
      });

      it('shows all demo-specific sections for testing', () => {
        const config = baseTenantConfig;
        expect(config.features.insights.show_aar_analysis).toBe(true);
        expect(config.features.insights.show_pso_viewer).toBe(true);
        expect(config.features.insights.show_vlp_extraction).toBe(true);
      });
    });

    describe('AAR tenant', () => {
      it('shows AAR analysis section only', () => {
        const config = aarTenantConfig;
        expect(config.features.insights.show_aar_analysis).toBe(true);
        expect(config.features.insights.show_pso_viewer).toBe(false);
        expect(config.features.insights.show_vlp_extraction).toBe(false);
      });

      it('has AAR-specific upload guidance', () => {
        const config = aarTenantConfig;
        expect(config.features.content.upload_guidance).toContain('After Action Report');
      });

      it('has AAR-specific agent context', () => {
        const config = aarTenantConfig;
        expect(config.agents?.guide_agent_prompt_context).toContain('After Action Report');
      });

      it('has sample AAR files defined', () => {
        const config = aarTenantConfig;
        expect(config.sample_data?.files).toBeDefined();
        expect(config.sample_data?.files?.length).toBeGreaterThan(0);
      });
    });

    describe('PSO tenant', () => {
      it('shows PSO viewer section only', () => {
        const config = psoTenantConfig;
        expect(config.features.insights.show_aar_analysis).toBe(false);
        expect(config.features.insights.show_pso_viewer).toBe(true);
        expect(config.features.insights.show_vlp_extraction).toBe(false);
      });

      it('shows EDI parser in content pillar', () => {
        const config = psoTenantConfig;
        expect(config.features.content.show_edi_parser).toBe(true);
        expect(config.features.content.show_mainframe_parser).toBe(false);
      });

      it('has PSO-specific upload guidance', () => {
        const config = psoTenantConfig;
        expect(config.features.content.upload_guidance).toContain('permit');
      });
    });

    describe('VLP tenant', () => {
      it('shows VLP extraction section only', () => {
        const config = vlpTenantConfig;
        expect(config.features.insights.show_aar_analysis).toBe(false);
        expect(config.features.insights.show_pso_viewer).toBe(false);
        expect(config.features.insights.show_vlp_extraction).toBe(true);
      });

      it('shows mainframe parser in content pillar', () => {
        const config = vlpTenantConfig;
        expect(config.features.content.show_mainframe_parser).toBe(true);
        expect(config.features.content.show_edi_parser).toBe(false);
      });

      it('has VLP-specific branding', () => {
        const config = vlpTenantConfig;
        expect(config.branding?.welcome_message).toContain('VLP');
      });
    });
  });

  describe('Configuration Schema Validation', () => {
    const allConfigs: TenantConfig[] = [
      baseTenantConfig,
      aarTenantConfig,
      psoTenantConfig,
      vlpTenantConfig
    ];

    it('all configs have unique tenant_ids', () => {
      const ids = allConfigs.map(c => c.tenant_id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });

    it('all configs have complete feature structure', () => {
      allConfigs.forEach(config => {
        // Content features
        expect(typeof config.features.content.enabled).toBe('boolean');
        
        // Insights features
        expect(typeof config.features.insights.enabled).toBe('boolean');
        expect(config.features.insights.tabs).toBeDefined();
        
        // Operations features
        expect(typeof config.features.operations.enabled).toBe('boolean');
        expect(typeof config.features.operations.show_sop_generator).toBe('boolean');
        
        // Outcomes features
        expect(typeof config.features.outcomes.enabled).toBe('boolean');
        expect(typeof config.features.outcomes.show_roadmap_generator).toBe('boolean');
      });
    });

    it('all configs have branding information', () => {
      allConfigs.forEach(config => {
        expect(config.branding).toBeDefined();
        expect(config.branding?.welcome_message).toBeDefined();
      });
    });
  });
});
