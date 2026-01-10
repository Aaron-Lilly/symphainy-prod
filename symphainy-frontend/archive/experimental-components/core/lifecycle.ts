/**
 * Component Lifecycle Management
 * Handles component lifecycle events and state management
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';

export interface LifecycleState {
  isMounted: boolean;
  isVisible: boolean;
  isActive: boolean;
  mountTime: number;
  lastActivity: number;
  renderCount: number;
}

export interface LifecycleConfig {
  enableVisibilityTracking: boolean;
  enableActivityTracking: boolean;
  enableAutoCleanup: boolean;
  cleanupTimeout: number;
  visibilityThreshold: number;
}

export interface LifecycleEvents {
  onMount?: () => void;
  onUnmount?: () => void;
  onVisibilityChange?: (isVisible: boolean) => void;
  onActivityChange?: (isActive: boolean) => void;
  onCleanup?: () => void;
}

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

// Lifecycle Management Hook
export function useLifecycle(
  config: Partial<LifecycleConfig> = {},
  events: LifecycleEvents = {}
) {
  const [state, setState] = useState<LifecycleState>({
    isMounted: false,
    isVisible: false,
    isActive: false,
    mountTime: 0,
    lastActivity: 0,
    renderCount: 0,
  });

  const configRef = useRef<LifecycleConfig>({
    enableVisibilityTracking: true,
    enableActivityTracking: true,
    enableAutoCleanup: true,
    cleanupTimeout: 300000, // 5 minutes
    visibilityThreshold: 0.1,
    ...config,
  });

  const cleanupTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const elementRef = useRef<HTMLElement | null>(null);

  // Mount/Unmount handling
  useEffect(() => {
    const mountTime = Date.now();
    setState(prev => ({
      ...prev,
      isMounted: true,
      mountTime,
      lastActivity: mountTime,
    }));

    events.onMount?.();

    return () => {
      setState(prev => ({ ...prev, isMounted: false }));
      events.onUnmount?.();
      
      if (cleanupTimeoutRef.current) {
        clearTimeout(cleanupTimeoutRef.current);
      }
      
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  // Visibility tracking
  useEffect(() => {
    if (!configRef.current.enableVisibilityTracking || !elementRef.current) {
      return;
    }

    observerRef.current = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        const isVisible = entry.isIntersecting;
        
        setState(prev => ({ ...prev, isVisible }));
        events.onVisibilityChange?.(isVisible);
      },
      { threshold: configRef.current.visibilityThreshold }
    );

    observerRef.current.observe(elementRef.current);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [events.onVisibilityChange]);

  // Activity tracking
  useEffect(() => {
    if (!configRef.current.enableActivityTracking) {
      return;
    }

    const updateActivity = () => {
      const now = Date.now();
      setState(prev => ({
        ...prev,
        lastActivity: now,
        isActive: true,
      }));
      events.onActivityChange?.(true);
    };

    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => {
      document.addEventListener(event, updateActivity, { passive: true });
    });

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, updateActivity);
      });
    };
  }, [events.onActivityChange]);

  // Auto cleanup
  useEffect(() => {
    if (!configRef.current.enableAutoCleanup) {
      return;
    }

    const checkInactivity = () => {
      const now = Date.now();
      const timeSinceActivity = now - state.lastActivity;
      
      if (timeSinceActivity > configRef.current.cleanupTimeout) {
        setState(prev => ({ ...prev, isActive: false }));
        events.onActivityChange?.(false);
        events.onCleanup?.();
      }
    };

    cleanupTimeoutRef.current = setInterval(checkInactivity, 60000); // Check every minute

    return () => {
      if (cleanupTimeoutRef.current) {
        clearInterval(cleanupTimeoutRef.current);
      }
    };
  }, [state.lastActivity, events.onActivityChange, events.onCleanup]);

  // Render count tracking
  useEffect(() => {
    setState(prev => ({
      ...prev,
      renderCount: prev.renderCount + 1,
    }));
  });

  // Element ref for visibility tracking
  const setElementRef = useCallback((element: HTMLElement | null) => {
    elementRef.current = element;
  }, []);

  return {
    state,
    setElementRef,
    updateActivity: useCallback(() => {
      const now = Date.now();
      setState(prev => ({
        ...prev,
        lastActivity: now,
        isActive: true,
      }));
      events.onActivityChange?.(true);
    }, [events.onActivityChange]),
  };
}

// Component Mount Hook
export function useComponentMount() {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    return () => setIsMounted(false);
  }, []);

  return isMounted;
}

// Component Visibility Hook
export function useComponentVisibility(threshold: number = 0.1) {
  const [isVisible, setIsVisible] = useState(false);
  const elementRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!elementRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        setIsVisible(entries[0].isIntersecting);
      },
      { threshold }
    );

    observer.observe(elementRef.current);

    return () => observer.disconnect();
  }, [threshold]);

  return { isVisible, elementRef };
}

// Component Activity Hook
export function useComponentActivity(timeout: number = 300000) {
  const [isActive, setIsActive] = useState(true);
  const lastActivityRef = useRef(Date.now());

  useEffect(() => {
    const updateActivity = () => {
      lastActivityRef.current = Date.now();
      setIsActive(true);
    };

    const checkInactivity = () => {
      const now = Date.now();
      if (now - lastActivityRef.current > timeout) {
        setIsActive(false);
      }
    };

    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => {
      document.addEventListener(event, updateActivity, { passive: true });
    });

    const interval = setInterval(checkInactivity, 60000);

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, updateActivity);
      });
      clearInterval(interval);
    };
  }, [timeout]);

  return isActive;
} 