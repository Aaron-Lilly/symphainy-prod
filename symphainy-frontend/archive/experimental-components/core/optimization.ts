/**
 * Component Optimization Utilities
 * Performance optimization tools for React components
 */

import React, { 
  memo, 
  useMemo, 
  useCallback, 
  useRef, 
  useEffect,
  useState,
  useTransition,
  startTransition
} from 'react';

export interface OptimizationConfig {
  enableMemoization: boolean;
  enableCallbackOptimization: boolean;
  enableRefOptimization: boolean;
  enableTransitionOptimization: boolean;
  enableVirtualization: boolean;
  memoizationDepth: number;
}

export interface VirtualizationConfig {
  itemHeight: number;
  containerHeight: number;
  overscan: number;
  enableDynamicHeight: boolean;
}

// Memoization with deep comparison
export function useDeepMemo<T>(
  factory: () => T,
  dependencies: React.DependencyList,
  depth: number = 3
): T {
  const prevDepsRef = useRef<React.DependencyList>([]);
  const prevResultRef = useRef<T | null>(null);

  const areDepsEqual = useCallback((prev: React.DependencyList, next: React.DependencyList): boolean => {
    if (prev.length !== next.length) return false;
    
    for (let i = 0; i < prev.length; i++) {
      if (!deepEqual(prev[i], next[i], depth)) {
        return false;
      }
    }
    return true;
  }, [depth]);

  return useMemo(() => {
    if (areDepsEqual(prevDepsRef.current, dependencies)) {
      return prevResultRef.current!;
    }

    const result = factory();
    prevDepsRef.current = dependencies;
    prevResultRef.current = result;
    return result;
  }, dependencies);
}

// Deep equality check
function deepEqual(a: any, b: any, depth: number): boolean {
  if (depth === 0) return a === b;
  if (a === b) return true;
  if (a == null || b == null) return a === b;
  if (typeof a !== typeof b) return false;
  
  if (typeof a === 'object') {
    if (Array.isArray(a) !== Array.isArray(b)) return false;
    
    if (Array.isArray(a)) {
      if (a.length !== b.length) return false;
      for (let i = 0; i < a.length; i++) {
        if (!deepEqual(a[i], b[i], depth - 1)) return false;
      }
      return true;
    }
    
    const keysA = Object.keys(a);
    const keysB = Object.keys(b);
    
    if (keysA.length !== keysB.length) return false;
    
    for (const key of keysA) {
      if (!keysB.includes(key)) return false;
      if (!deepEqual(a[key], b[key], depth - 1)) return false;
    }
    
    return true;
  }
  
  return a === b;
}

// Optimized callback with dependency tracking
export function useOptimizedCallback<T extends (...args: any[]) => any>(
  callback: T,
  dependencies: React.DependencyList,
  optimizationLevel: 'none' | 'basic' | 'deep' = 'basic'
): T {
  const callbackRef = useRef<T>(callback);
  const depsRef = useRef<React.DependencyList>(dependencies);

  useEffect(() => {
    callbackRef.current = callback;
  });

  return useCallback((...args: Parameters<T>) => {
    if (optimizationLevel === 'none') {
      return callbackRef.current(...args);
    }

    const currentDeps = dependencies;
    const prevDeps = depsRef.current;

    if (optimizationLevel === 'deep') {
      if (!deepEqual(prevDeps, currentDeps, 3)) {
        depsRef.current = currentDeps;
        return callbackRef.current(...args);
      }
    } else {
      if (prevDeps.length !== currentDeps.length || 
          prevDeps.some((dep, i) => dep !== currentDeps[i])) {
        depsRef.current = currentDeps;
        return callbackRef.current(...args);
      }
    }

    return callbackRef.current(...args);
  }, dependencies) as T;
}

// Virtualization hook for large lists
export function useVirtualization<T>(
  items: T[],
  config: VirtualizationConfig
) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const visibleRange = useMemo(() => {
    const startIndex = Math.floor(scrollTop / config.itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(config.containerHeight / config.itemHeight) + config.overscan,
      items.length
    );
    
    return {
      start: Math.max(0, startIndex - config.overscan),
      end: endIndex,
    };
  }, [scrollTop, config, items.length]);

  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.start, visibleRange.end).map((item, index) => ({
      item,
      index: visibleRange.start + index,
      offsetTop: (visibleRange.start + index) * config.itemHeight,
    }));
  }, [items, visibleRange]);

  const totalHeight = useMemo(() => {
    return items.length * config.itemHeight;
  }, [items.length, config.itemHeight]);

  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(event.currentTarget.scrollTop);
  }, []);

  return {
    visibleItems,
    totalHeight,
    containerRef,
    handleScroll,
    scrollTop,
  };
}

// Transition optimization hook
export function useTransitionOptimization() {
  const [isPending, startTransitionFn] = useTransition();
  const [optimizedState, setOptimizedState] = useState<any>(null);

  const setOptimizedStateWithTransition = useCallback((newState: any) => {
    startTransitionFn(() => {
      setOptimizedState(newState);
    });
  }, [startTransitionFn]);

  return {
    isPending,
    optimizedState,
    setOptimizedStateWithTransition,
  };
}

// Render optimization hook
export function useRenderOptimization(
  componentName: string,
  config: Partial<OptimizationConfig> = {}
) {
  const [renderCount, setRenderCount] = useState(0);
  const [lastRenderTime, setLastRenderTime] = useState(0);
  const renderStartTime = useRef<number>(0);

  useEffect(() => {
    renderStartTime.current = performance.now();
    setRenderCount(prev => prev + 1);

    return () => {
      const renderTime = performance.now() - renderStartTime.current;
      setLastRenderTime(renderTime);
      
      if (renderTime > 16) { // Longer than one frame
        console.warn(`${componentName} took ${renderTime.toFixed(2)}ms to render`);
      }
    };
  });

  return {
    renderCount,
    lastRenderTime,
    isSlowRender: lastRenderTime > 16,
  };
}

// Component memoization with custom comparison
export function createOptimizedComponent<P extends object>(
  Component: React.ComponentType<P>,
  comparisonFn?: (prevProps: P, nextProps: P) => boolean
) {
  return memo(Component, comparisonFn);
}

// Batch update hook
export function useBatchUpdates() {
  const [batch, setBatch] = useState<any[]>([]);
  const batchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const addToBatch = useCallback((update: any) => {
    setBatch(prev => [...prev, update]);
  }, []);

  const flushBatch = useCallback(() => {
    if (batchTimeoutRef.current) {
      clearTimeout(batchTimeoutRef.current);
    }
    
    batchTimeoutRef.current = setTimeout(() => {
      setBatch([]);
      batchTimeoutRef.current = null;
    }, 0);
  }, []);

  useEffect(() => {
    if (batch.length > 0) {
      flushBatch();
    }
  }, [batch, flushBatch]);

  return {
    batch,
    addToBatch,
    flushBatch,
  };
} 