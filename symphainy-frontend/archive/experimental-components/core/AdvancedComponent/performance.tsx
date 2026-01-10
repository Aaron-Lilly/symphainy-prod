/**
 * Advanced Component Performance
 * Performance monitoring and optimization features
 */

import React, { 
  useState, 
  useRef, 
  useEffect, 
  useMemo, 
  useCallback,
  ReactNode,
  ComponentType
} from 'react';
import { PerformanceMetrics, ComponentConfig } from './types';

// Performance Monitoring Hook
export function usePerformanceMonitoring(componentName: string) {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    renderTime: 0,
    mountTime: 0,
    updateTime: 0,
    memoryUsage: 0,
  });

  const renderStartTime = useRef<number>(0);
  const mountStartTime = useRef<number>(0);
  const isFirstRender = useRef<boolean>(true);

  useEffect(() => {
    if (isFirstRender.current) {
      mountStartTime.current = performance.now();
      isFirstRender.current = false;
    }

    renderStartTime.current = performance.now();

    return () => {
      const renderTime = performance.now() - renderStartTime.current;
      const mountTime = performance.now() - mountStartTime.current;
      
      setMetrics(prev => ({
        ...prev,
        renderTime,
        mountTime,
        updateTime: renderTime,
        memoryUsage: (performance as any).memory?.usedJSHeapSize || 0,
      }));

      console.log(`${componentName} performance:`, {
        renderTime: `${renderTime.toFixed(2)}ms`,
        mountTime: `${mountTime.toFixed(2)}ms`,
      });
    };
  });

  return metrics;
}

// Lazy Loading Hook
export function useLazyLoading<T>(
  importFn: () => Promise<{ default: React.ComponentType<T> }>,
  fallback?: ReactNode
) {
  const [Component, setComponent] = useState<React.ComponentType<T> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    importFn()
      .then(module => {
        setComponent(() => module.default);
        setIsLoading(false);
      })
      .catch(err => {
        setError(err);
        setIsLoading(false);
      });
  }, [importFn]);

  return { Component, isLoading, error, fallback };
}

// Caching Hook
export function useCaching<T>(
  key: string,
  data: T,
  timeout: number = 300000 // 5 minutes
) {
  const [cachedData, setCachedData] = useState<T | null>(null);
  const cacheTime = useRef<number>(0);

  useEffect(() => {
    const now = Date.now();
    const cached = localStorage.getItem(key);
    
    if (cached && (now - cacheTime.current) < timeout) {
      try {
        setCachedData(JSON.parse(cached));
      } catch {
        // Invalid cache, ignore
      }
    } else {
      setCachedData(data);
      localStorage.setItem(key, JSON.stringify(data));
      cacheTime.current = now;
    }
  }, [key, data, timeout]);

  return cachedData;
}

// Memoization Hook
export function useMemoization<T>(
  factory: () => T,
  dependencies: React.DependencyList,
  equalityFn?: (prev: T, next: T) => boolean
) {
  return useMemo(factory, dependencies);
}

// HOC with Advanced Features
export function withAdvancedFeatures<P extends object>(
  WrappedComponent: ComponentType<P>,
  config: Partial<ComponentConfig> = {}
) {
  return React.forwardRef<any, P>((props, ref) => {
    const componentName = WrappedComponent.displayName || WrappedComponent.name || 'Component';
    
    if (config.enablePerformanceMonitoring) {
      usePerformanceMonitoring(componentName);
    }

    return <WrappedComponent {...props} ref={ref} />;
  });
} 