/**
 * Optimization Memoization
 * Memoization and deep comparison utilities
 */

import React, { useMemo, useCallback, useRef } from 'react';

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

// Optimized callback with dependency tracking
export function useOptimizedCallback<T extends (...args: any[]) => any>(
  callback: T,
  dependencies: React.DependencyList,
  optimizationLevel: 'none' | 'basic' | 'deep' = 'basic'
): T {
  if (optimizationLevel === 'none') {
    return callback;
  }

  if (optimizationLevel === 'basic') {
    return useCallback(callback, dependencies);
  }

  // Deep optimization
  return useCallback(callback, dependencies) as T;
}

// Create optimized component with custom comparison
export function createOptimizedComponent<P extends object>(
  Component: React.ComponentType<P>,
  comparisonFn?: (prevProps: P, nextProps: P) => boolean
) {
  return React.memo(Component, comparisonFn);
} 
// Virtualization hook for optimization
export function useVirtualization<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number
) {
  const [scrollTop, setScrollTop] = useState(0);
  
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  );
  
  const visibleItems = items.slice(startIndex, endIndex);
  const offsetY = startIndex * itemHeight;
  
  return { visibleItems, offsetY, setScrollTop };
}

// Render optimization hook
export function useRenderOptimization(componentName: string) {
  const renderCount = useRef(0);
  
  useEffect(() => {
    renderCount.current += 1;
    if (renderCount.current > 10) {
      console.warn(`${componentName} has rendered ${renderCount.current} times. Consider optimization.`);
    }
  });
  
  return renderCount.current;
}
