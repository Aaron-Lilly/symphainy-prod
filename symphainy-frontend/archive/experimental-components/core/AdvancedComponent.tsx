/**
 * Advanced Component Core
 * Base component with performance optimization and advanced features
 */

import React, { 
  Component, 
  ErrorInfo, 
  ReactNode, 
  Suspense, 
  lazy, 
  memo,
  useMemo,
  useCallback,
  useEffect,
  useState,
  useRef
} from 'react';
import { getGlobalConfig } from '../../config';

export interface ComponentConfig {
  enableLazyLoading: boolean;
  enableErrorBoundary: boolean;
  enablePerformanceMonitoring: boolean;
  enableCaching: boolean;
  cacheTimeout: number;
}

export interface ComponentState {
  isLoading: boolean;
  hasError: boolean;
  error: Error | null;
  lastRender: number;
  renderCount: number;
}

export interface PerformanceMetrics {
  renderTime: number;
  mountTime: number;
  updateTime: number;
  memoryUsage: number;
}

// Advanced Error Boundary
export class AdvancedErrorBoundary extends Component<
  { children: ReactNode; fallback?: ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: ReactNode; fallback?: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('AdvancedErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

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
      
      if (isFirstRender.current) {
        const mountTime = performance.now() - mountStartTime.current;
        setMetrics(prev => ({ ...prev, mountTime, renderTime }));
      } else {
        setMetrics(prev => ({ ...prev, updateTime: renderTime }));
      }
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
  const cache = useRef<Map<string, { data: T; timestamp: number }>>(new Map());
  const [cachedData, setCachedData] = useState<T | null>(null);

  useEffect(() => {
    const now = Date.now();
    const cached = cache.current.get(key);

    if (cached && (now - cached.timestamp) < timeout) {
      setCachedData(cached.data);
    } else {
      cache.current.set(key, { data, timestamp: now });
      setCachedData(data);
    }
  }, [key, data, timeout]);

  const clearCache = useCallback(() => {
    cache.current.delete(key);
    setCachedData(null);
  }, [key]);

  return { cachedData, clearCache };
}

// Memoization Hook
export function useMemoization<T>(
  factory: () => T,
  dependencies: React.DependencyList,
  equalityFn?: (prev: T, next: T) => boolean
) {
  return useMemo(factory, dependencies);
}

// Advanced Component HOC
export function withAdvancedFeatures<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  config: Partial<ComponentConfig> = {}
) {
  const defaultConfig: ComponentConfig = {
    enableLazyLoading: true,
    enableErrorBoundary: true,
    enablePerformanceMonitoring: true,
    enableCaching: true,
    cacheTimeout: 300000,
    ...config,
  };

  const AdvancedComponent = (props: P) => {
    const [state, setState] = useState<ComponentState>({
      isLoading: false,
      hasError: false,
      error: null,
      lastRender: Date.now(),
      renderCount: 0,
    });

    const metrics = usePerformanceMonitoring(WrappedComponent.name);

    useEffect(() => {
      setState(prev => ({
        ...prev,
        lastRender: Date.now(),
        renderCount: prev.renderCount + 1,
      }));
    });

    if (state.hasError) {
      return (
        <div className="component-error">
          <h3>Component Error</h3>
          <p>{state.error?.message}</p>
          <button onClick={() => setState(prev => ({ ...prev, hasError: false, error: null }))}>
            Retry
          </button>
        </div>
      );
    }

    return (
      <AdvancedErrorBoundary>
        <Suspense fallback={<div>Loading...</div>}>
          <WrappedComponent {...props} />
        </Suspense>
      </AdvancedErrorBoundary>
    );
  };

  AdvancedComponent.displayName = `withAdvancedFeatures(${WrappedComponent.displayName || WrappedComponent.name})`;

  return memo(AdvancedComponent);
} 