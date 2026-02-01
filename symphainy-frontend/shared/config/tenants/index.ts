import { TenantConfig, TenantId } from '../tenant-types';
import { baseTenantConfig } from './base';
import { aarTenantConfig } from './aar';
import { psoTenantConfig } from './pso';
import { vlpTenantConfig } from './vlp';

export const TENANT_CONFIGS: Record<TenantId, TenantConfig> = {
  base: baseTenantConfig,
  aar: aarTenantConfig,
  pso: psoTenantConfig,
  vlp: vlpTenantConfig,
};

export function getTenantConfig(tenantId: string): TenantConfig {
  const config = TENANT_CONFIGS[tenantId as TenantId];
  if (!config) {
    console.warn(`Unknown tenant: ${tenantId}, falling back to base`);
    return baseTenantConfig;
  }
  return config;
}

export function getAvailableTenants(): Array<{ id: TenantId; name: string; description: string }> {
  return Object.entries(TENANT_CONFIGS).map(([id, config]) => ({
    id: id as TenantId,
    name: config.tenant_name,
    description: config.tenant_description,
  }));
}

export type { TenantConfig, TenantId };
export { baseTenantConfig, aarTenantConfig, psoTenantConfig, vlpTenantConfig };
