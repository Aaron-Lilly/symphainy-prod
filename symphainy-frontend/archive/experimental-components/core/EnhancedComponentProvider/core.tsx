/**
 * Enhanced Component Provider Core
 * Main provider component for enhanced component functionality
 */

import React, { useContext } from 'react';
import { getGlobalConfig } from '../../../config';
import { ComponentConfig } from '../AdvancedComponent';
import { LifecycleConfig } from '../lifecycle';
import { OptimizationConfig } from '../optimization';
import { CompositionConfig } from '../composition';
import { 
  EnhancedComponentContext, 
  EnhancedComponentContextValue, 
  EnhancedComponentProviderProps 
} from './context';

export function EnhancedComponentProvider({ 
  children, 
  config = {} 
}: EnhancedComponentProviderProps) {
  const globalConfig = getGlobalConfig();
  const isEnabled = globalConfig.getSection('features').realTimeUpdates;

  const componentConfig: ComponentConfig = {
    enableLazyLoading: true,
    enableErrorBoundary: true,
    enablePerformanceMonitoring: true,
    enableCaching: true,
    cacheTimeout: 300000,
    ...config.component,
  };

  const lifecycleConfig: LifecycleConfig = {
    enableVisibilityTracking: true,
    enableActivityTracking: true,
    enableAutoCleanup: true,
    cleanupTimeout: 300000,
    visibilityThreshold: 0.1,
    ...config.lifecycle,
  };

  const optimizationConfig: OptimizationConfig = {
    enableMemoization: true,
    enableCallbackOptimization: true,
    enableRefOptimization: true,
    enableTransitionOptimization: true,
    enableVirtualization: true,
    memoizationDepth: 3,
    ...config.optimization,
  };

  const compositionConfig: CompositionConfig = {
    enableContextComposition: true,
    enableRenderProps: true,
    enableCompoundComponents: true,
    enableHigherOrderComponents: true,
    ...config.composition,
  };

  const contextValue: EnhancedComponentContextValue = {
    componentConfig,
    lifecycleConfig,
    optimizationConfig,
    compositionConfig,
    isEnabled,
  };

  return (
    <EnhancedComponentContext.Provider value={contextValue}>
      {children}
    </EnhancedComponentContext.Provider>
  );
}

// Hook to use enhanced component context
export function useEnhancedComponentContext() {
  const context = useContext(EnhancedComponentContext);
  if (!context) {
    throw new Error('useEnhancedComponentContext must be used within EnhancedComponentProvider');
  }
  return context;
} 