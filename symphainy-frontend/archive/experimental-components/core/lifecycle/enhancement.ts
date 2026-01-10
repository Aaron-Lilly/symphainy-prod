/**
 * Lifecycle Enhancement Features
 * Advanced error boundary, performance monitoring, caching, and optimization features
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';

// Advanced Error Boundary Component
export class AdvancedErrorBoundary extends React.Component {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('AdvancedErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong. Please try again.</div>;
    }
    return this.props.children;
  }
}

// Performance Monitoring Hook
export function usePerformanceMonitoring(componentName: string) {
  const renderCount = useRef(0);
  const startTime = useRef(performance.now());

  useEffect(() => {
    renderCount.current += 1;
    const endTime = performance.now();
    const renderTime = endTime - startTime.current;
    
    console.log(`${componentName} render #${renderCount.current}: ${renderTime.toFixed(2)}ms`);
    startTime.current = performance.now();
  });
}

// Lazy Loading Hook
export function useLazyLoading<T>(data: T[], pageSize: number = 10) {
  const [visibleItems, setVisibleItems] = useState<T[]>(data.slice(0, pageSize));
  const [hasMore, setHasMore] = useState(data.length > pageSize);

  const loadMore = useCallback(() => {
    const currentLength = visibleItems.length;
    const newItems = data.slice(currentLength, currentLength + pageSize);
    setVisibleItems(prev => [...prev, ...newItems]);
    setHasMore(currentLength + pageSize < data.length);
  }, [data, visibleItems.length, pageSize]);

  return { visibleItems, hasMore, loadMore };
}

// Caching Hook
export function useCaching<T>(key: string, data: T, ttl: number = 300000) {
  const [cachedData, setCachedData] = useState<T | null>(null);
  const cacheTime = useRef<number>(0);

  useEffect(() => {
    const now = Date.now();
    const cached = localStorage.getItem(key);
    
    if (cached && (now - cacheTime.current) < ttl) {
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
  }, [key, data, ttl]);

  return cachedData;
}

// Deep Memo Hook
export function useDeepMemo<T>(value: T, deps: any[]) {
  const prevValue = useRef<T>();
  const prevDeps = useRef<any[]>();

  if (!prevDeps.current || !deps.every((dep, i) => dep === prevDeps.current![i])) {
    prevValue.current = value;
    prevDeps.current = deps;
  }

  return prevValue.current!;
}

// Optimized Callback Hook
export function useOptimizedCallback<T extends (...args: any[]) => any>(
  callback: T,
  deps: any[]
): T {
  return useCallback(callback, deps);
}

// Virtualization Hook
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

// Render Optimization Hook
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