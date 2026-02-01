"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { TenantConfig, TenantId, getTenantConfig, getAvailableTenants } from '@/shared/config/tenants';

interface TenantContextType {
  // Current tenant
  currentTenant: TenantConfig;
  tenantId: TenantId;
  
  // Tenant switching
  setTenant: (tenantId: TenantId) => void;
  availableTenants: Array<{ id: TenantId; name: string; description: string }>;
  
  // Feature checks (convenience methods)
  hasFeature: (pillar: string, feature: string) => boolean;
  isTabEnabled: (pillar: string, tab: string) => boolean;
}

const TenantContext = createContext<TenantContextType | undefined>(undefined);

export const useTenant = (): TenantContextType => {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error('useTenant must be used within TenantProvider');
  }
  return context;
};

interface TenantProviderProps {
  children: React.ReactNode;
  initialTenantId?: TenantId;
}

export const TenantProvider: React.FC<TenantProviderProps> = ({
  children,
  initialTenantId = 'base',
}) => {
  const [tenantId, setTenantIdState] = useState<TenantId>(initialTenantId);
  const [currentTenant, setCurrentTenant] = useState<TenantConfig>(getTenantConfig(initialTenantId));

  // Load tenant from session storage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedTenantId = sessionStorage.getItem('tenant_id') as TenantId;
      if (storedTenantId && storedTenantId !== tenantId) {
        // Validate it's a known tenant
        const validTenants: TenantId[] = ['base', 'aar', 'pso', 'vlp'];
        if (validTenants.includes(storedTenantId)) {
          setTenantIdState(storedTenantId);
          setCurrentTenant(getTenantConfig(storedTenantId));
        }
      }
    }
  }, []);

  const setTenant = useCallback((newTenantId: TenantId) => {
    setTenantIdState(newTenantId);
    setCurrentTenant(getTenantConfig(newTenantId));
    
    // Persist to session storage
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('tenant_id', newTenantId);
    }
  }, []);

  const hasFeature = useCallback((pillar: string, feature: string): boolean => {
    const pillarConfig = currentTenant.features[pillar as keyof typeof currentTenant.features];
    if (!pillarConfig || !pillarConfig.enabled) return false;
    
    // Check if the feature exists and is truthy
    const featureValue = pillarConfig[feature as keyof typeof pillarConfig];
    return featureValue === true;
  }, [currentTenant]);

  const isTabEnabled = useCallback((pillar: string, tab: string): boolean => {
    const pillarConfig = currentTenant.features[pillar as keyof typeof currentTenant.features];
    if (!pillarConfig || !pillarConfig.enabled) return false;
    
    // Check if pillar has tabs configuration
    if ('tabs' in pillarConfig && pillarConfig.tabs) {
      const tabs = pillarConfig.tabs as Record<string, boolean>;
      return tabs[tab] === true;
    }
    return true;
  }, [currentTenant]);

  const value: TenantContextType = {
    currentTenant,
    tenantId,
    setTenant,
    availableTenants: getAvailableTenants(),
    hasFeature,
    isTabEnabled,
  };

  return (
    <TenantContext.Provider value={value}>
      {children}
    </TenantContext.Provider>
  );
};
