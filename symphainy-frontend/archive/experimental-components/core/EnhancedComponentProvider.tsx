/**
 * Enhanced Component Provider
 * React context provider for advanced component functionality
 */

import React, { createContext, useContext, useRef, useEffect, useCallback } from 'react';
import { getGlobalConfig } from '../../config';
import { ComponentConfig } from './AdvancedComponent';
import { LifecycleConfig } from './lifecycle';
import { OptimizationConfig } from './optimization';
import { CompositionConfig } from './composition';

interface EnhancedComponentContextValue {
  componentConfig: ComponentConfig;
  lifecycleConfig: LifecycleConfig;
  optimizationConfig: OptimizationConfig;
  compositionConfig: CompositionConfig;
  isEnabled: boolean;
}

const EnhancedComponentContext = createContext<EnhancedComponentContextValue | null>(null);

interface EnhancedComponentProviderProps {
  children: React.ReactNode;
  config?: {
    component?: Partial<ComponentConfig>;
    lifecycle?: Partial<LifecycleConfig>;
    optimization?: Partial<OptimizationConfig>;
    composition?: Partial<CompositionConfig>;
  };
}

// Context Composition Hook
export function useContextComposition<T>(context: React.Context<T>, defaultValue: T) {
  const value = useContext(context);
  return value !== null ? value : defaultValue;
}

// Render Props Hook
export function useRenderProps<T>(
  render: (props: T) => React.ReactNode,
  props: T
) {
  return render(props);
}

// Compound Component Hook
export function useCompoundComponent<T extends Record<string, any>>(
  components: T,
  props: any
) {
  return Object.keys(components).reduce((acc, key) => {
    acc[key] = React.cloneElement(components[key], props);
    return acc;
  }, {} as T);
}

// Higher Order Component Creator
export function createHOC<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  enhancer: (props: P) => P
) {
  return React.forwardRef<any, P>((props, ref) => {
    const enhancedProps = enhancer(props);
    return <WrappedComponent {...enhancedProps} ref={ref} />;
  });
}

// Component Composition Hook
export function useComponentComposition<T extends Record<string, any>>(
  baseProps: T,
  compositions: Array<(props: T) => T>
) {
  return compositions.reduce((props, composition) => composition(props), baseProps);
}

// Context Provider Creator
export function createContextProvider<T>(
  defaultValue: T,
  reducer?: (state: T, action: any) => T
) {
  const Context = createContext<T>(defaultValue);
  
  const Provider: React.FC<{ children: React.ReactNode; value?: T }> = ({ 
    children, 
    value = defaultValue 
  }) => {
    const [state, dispatch] = React.useReducer(
      reducer || ((state: T) => state),
      value
    );
    
    return (
      <Context.Provider value={state}>
        {children}
      </Context.Provider>
    );
  };
  
  return { Context, Provider };
}

// Component Registry Hook
export function useComponentRegistry() {
  const registry = useRef<Map<string, React.ComponentType<any>>>(new Map());
  
  const register = useCallback((name: string, component: React.ComponentType<any>) => {
    registry.current.set(name, component);
  }, []);
  
  const get = useCallback((name: string) => {
    return registry.current.get(name);
  }, []);
  
  const unregister = useCallback((name: string) => {
    registry.current.delete(name);
  }, []);
  
  return { register, get, unregister };
}

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