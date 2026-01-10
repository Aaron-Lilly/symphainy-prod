# Performance Guide

This document provides comprehensive guidance on performance optimization, monitoring, and best practices for the Symphainy frontend application.

## 📋 Table of Contents

- [Overview](#overview)
- [Performance Metrics](#performance-metrics)
- [Bundle Optimization](#bundle-optimization)
- [Runtime Optimization](#runtime-optimization)
- [Caching Strategies](#caching-strategies)
- [Monitoring & Analytics](#monitoring--analytics)
- [Performance Testing](#performance-testing)
- [Best Practices](#best-practices)

## 🎯 Overview

Performance optimization in the Symphainy frontend focuses on:

- **Core Web Vitals** - LCP, FID, CLS optimization
- **Bundle Size** - Code splitting and tree shaking
- **Runtime Performance** - Component optimization and memoization
- **Caching** - Browser and CDN caching strategies
- **Monitoring** - Real-time performance tracking
- **Testing** - Performance regression testing

## 📊 Performance Metrics

### Core Web Vitals

```typescript
// monitoring/core-web-vitals.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

export const trackCoreWebVitals = () => {
  // Cumulative Layout Shift (CLS)
  getCLS((metric) => {
    console.log('CLS:', metric.value);
    // Send to analytics
  });

  // First Input Delay (FID)
  getFID((metric) => {
    console.log('FID:', metric.value);
    // Send to analytics
  });

  // First Contentful Paint (FCP)
  getFCP((metric) => {
    console.log('FCP:', metric.value);
    // Send to analytics
  });

  // Largest Contentful Paint (LCP)
  getLCP((metric) => {
    console.log('LCP:', metric.value);
    // Send to analytics
  });

  // Time to First Byte (TTFB)
  getTTFB((metric) => {
    console.log('TTFB:', metric.value);
    // Send to analytics
  });
};
```

### Performance Targets

```typescript
// performance/targets.ts
export const performanceTargets = {
  // Core Web Vitals targets
  coreWebVitals: {
    lcp: 2500, // 2.5 seconds
    fid: 100,  // 100 milliseconds
    cls: 0.1,  // 0.1
    fcp: 1800, // 1.8 seconds
    ttfb: 800, // 800 milliseconds
  },

  // Bundle size targets
  bundleSize: {
    main: 200,    // 200KB
    vendor: 300,  // 300KB
    total: 500,   // 500KB
  },

  // Runtime performance targets
  runtime: {
    renderTime: 16,     // 16ms (60fps)
    memoryUsage: 50,    // 50MB
    cpuUsage: 30,       // 30%
  },
};
```

### Performance Monitoring

```typescript
// monitoring/performance-monitor.ts
export class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map();

  // Track custom metrics
  trackMetric(name: string, value: number) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name)!.push(value);
  }

  // Get average metric
  getAverageMetric(name: string): number {
    const values = this.metrics.get(name) || [];
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  }

  // Track component render time
  trackComponentRender(componentName: string, renderTime: number) {
    this.trackMetric(`${componentName}_render_time`, renderTime);
  }

  // Track API response time
  trackApiResponse(url: string, responseTime: number) {
    this.trackMetric(`${url}_response_time`, responseTime);
  }

  // Generate performance report
  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      metrics: {},
    };

    for (const [name, values] of this.metrics) {
      report.metrics[name] = {
        average: this.getAverageMetric(name),
        min: Math.min(...values),
        max: Math.max(...values),
        count: values.length,
      };
    }

    return report;
  }
}
```

## 📦 Bundle Optimization

### Code Splitting

```typescript
// components/lazy-components.ts
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const HeavyChart = lazy(() => import('./HeavyChart'));
const DataGrid = lazy(() => import('./DataGrid'));
const WorkflowEditor = lazy(() => import('./WorkflowEditor'));

// Lazy loading wrapper
export const LazyComponent = ({ 
  component: Component, 
  fallback = <div>Loading...</div> 
}: { 
  component: React.ComponentType; 
  fallback?: React.ReactNode; 
}) => (
  <Suspense fallback={fallback}>
    <Component />
  </Suspense>
);

// Usage
export const ChartSection = () => (
  <LazyComponent component={HeavyChart} />
);
```

### Dynamic Imports

```typescript
// utils/dynamic-imports.ts
export const loadComponent = async (componentName: string) => {
  switch (componentName) {
    case 'chart':
      return import('../components/Chart');
    case 'grid':
      return import('../components/DataGrid');
    case 'editor':
      return import('../components/Editor');
    default:
      throw new Error(`Unknown component: ${componentName}`);
  }
};

// Usage in components
const [Component, setComponent] = useState<React.ComponentType | null>(null);

useEffect(() => {
  loadComponent('chart').then((module) => {
    setComponent(() => module.default);
  });
}, []);
```

### Tree Shaking

```typescript
// utils/tree-shaking.ts
// Import only what you need
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
// Instead of: import * from '@/components/ui';

// Use named exports
export { Button, Card, Input } from '@/components/ui';
// Instead of: export * from '@/components/ui';
```

### Bundle Analysis

```bash
# Analyze bundle size
npm run analyze

# Check bundle composition
npx @next/bundle-analyzer

# Monitor bundle size over time
npm run build:analyze
```

## ⚡ Runtime Optimization

### Component Optimization

```typescript
// components/optimized-components.tsx
import React, { memo, useMemo, useCallback } from 'react';

// Memoized component
export const ExpensiveComponent = memo(({ data, onUpdate }: Props) => {
  // Memoize expensive calculations
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      processed: expensiveCalculation(item),
    }));
  }, [data]);

  // Memoize callbacks
  const handleUpdate = useCallback((id: string, value: any) => {
    onUpdate(id, value);
  }, [onUpdate]);

  return (
    <div>
      {processedData.map(item => (
        <DataItem 
          key={item.id} 
          data={item} 
          onUpdate={handleUpdate} 
        />
      ))}
    </div>
  );
});

// Virtual scrolling for large lists
export const VirtualList = ({ items, itemHeight, containerHeight }: VirtualListProps) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight),
      items.length
    );
    
    return items.slice(startIndex, endIndex);
  }, [items, scrollTop, itemHeight, containerHeight]);

  return (
    <div 
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
    >
      <div style={{ height: items.length * itemHeight }}>
        <div style={{ transform: `translateY(${scrollTop}px)` }}>
          {visibleItems.map(item => (
            <ListItem key={item.id} item={item} height={itemHeight} />
          ))}
        </div>
      </div>
    </div>
  );
};
```

### State Optimization

```typescript
// hooks/optimized-state.ts
import { useMemo, useCallback } from 'react';
import { useAtom } from 'jotai';

// Optimized state selector
export const useOptimizedSelector = <T>(
  atom: any,
  selector: (state: any) => T,
  deps: any[] = []
) => {
  const [state] = useAtom(atom);
  
  return useMemo(() => selector(state), [state, ...deps]);
};

// Optimized state updater
export const useOptimizedUpdater = <T>(
  atom: any,
  updater: (state: T) => T
) => {
  const [, setState] = useAtom(atom);
  
  return useCallback((value: T) => {
    setState(updater);
  }, [setState, updater]);
};

// Usage
const filteredData = useOptimizedSelector(
  dataAtom,
  (state) => state.items.filter(item => item.active),
  [activeFilter]
);
```

### Event Optimization

```typescript
// utils/event-optimization.ts
import { debounce, throttle } from 'lodash';

// Debounced search
export const useDebouncedSearch = (callback: (query: string) => void, delay: number = 300) => {
  const debouncedCallback = useMemo(
    () => debounce(callback, delay),
    [callback, delay]
  );

  return debouncedCallback;
};

// Throttled scroll handler
export const useThrottledScroll = (callback: (event: Event) => void, delay: number = 16) => {
  const throttledCallback = useMemo(
    () => throttle(callback, delay),
    [callback, delay]
  );

  return throttledCallback;
};

// Usage
const SearchComponent = () => {
  const [query, setQuery] = useState('');
  const debouncedSearch = useDebouncedSearch((searchQuery) => {
    // Perform search
    performSearch(searchQuery);
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    debouncedSearch(value);
  };

  return <input value={query} onChange={handleInputChange} />;
};
```

## 💾 Caching Strategies

### Browser Caching

```typescript
// caching/browser-cache.ts
export const browserCache = {
  // Cache API responses
  cacheApiResponse: async (url: string, response: Response, ttl: number = 3600) => {
    const cache = await caches.open('api-cache');
    const cachedResponse = new Response(response.body, {
      headers: {
        ...response.headers,
        'cache-control': `max-age=${ttl}`,
      },
    });
    await cache.put(url, cachedResponse);
  },

  // Get cached response
  getCachedResponse: async (url: string): Promise<Response | null> => {
    const cache = await caches.open('api-cache');
    return await cache.match(url);
  },

  // Clear cache
  clearCache: async () => {
    const cache = await caches.open('api-cache');
    await cache.keys().then(keys => Promise.all(keys.map(key => cache.delete(key))));
  },
};
```

### Service Worker Caching

```typescript
// service-worker/cache-strategy.ts
const CACHE_NAME = 'symphainy-cache-v1';
const STATIC_CACHE = 'symphainy-static-v1';
const API_CACHE = 'symphainy-api-v1';

// Cache strategies
export const cacheStrategies = {
  // Cache first for static assets
  cacheFirst: async (request: Request) => {
    const cache = await caches.open(STATIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const response = await fetch(request);
    await cache.put(request, response.clone());
    return response;
  },

  // Network first for API requests
  networkFirst: async (request: Request) => {
    const cache = await caches.open(API_CACHE);
    
    try {
      const response = await fetch(request);
      await cache.put(request, response.clone());
      return response;
    } catch (error) {
      const cachedResponse = await cache.match(request);
      if (cachedResponse) {
        return cachedResponse;
      }
      throw error;
    }
  },

  // Stale while revalidate
  staleWhileRevalidate: async (request: Request) => {
    const cache = await caches.open(STATIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    const fetchPromise = fetch(request).then(response => {
      cache.put(request, response.clone());
      return response;
    });
    
    return cachedResponse || fetchPromise;
  },
};
```

### Memory Caching

```typescript
// caching/memory-cache.ts
export class MemoryCache {
  private cache = new Map<string, { value: any; expiry: number }>();
  private maxSize: number;

  constructor(maxSize: number = 100) {
    this.maxSize = maxSize;
  }

  set(key: string, value: any, ttl: number = 3600000) {
    // Evict if cache is full
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      value,
      expiry: Date.now() + ttl,
    });
  }

  get(key: string): any {
    const item = this.cache.get(key);
    
    if (!item) {
      return null;
    }

    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }

    return item.value;
  }

  clear() {
    this.cache.clear();
  }

  size() {
    return this.cache.size;
  }
}

// Global cache instance
export const globalCache = new MemoryCache(100);
```

## 📈 Monitoring & Analytics

### Performance Analytics

```typescript
// analytics/performance-analytics.ts
export const performanceAnalytics = {
  // Track page load performance
  trackPageLoad: () => {
    if (typeof window !== 'undefined') {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      
      const metrics = {
        dns: navigation.domainLookupEnd - navigation.domainLookupStart,
        tcp: navigation.connectEnd - navigation.connectStart,
        ttfb: navigation.responseStart - navigation.requestStart,
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        load: navigation.loadEventEnd - navigation.loadEventStart,
      };

      // Send to analytics
      this.sendMetrics('page_load', metrics);
    }
  },

  // Track component performance
  trackComponentPerformance: (componentName: string, renderTime: number) => {
    this.sendMetrics('component_render', {
      component: componentName,
      renderTime,
      timestamp: Date.now(),
    });
  },

  // Track API performance
  trackApiPerformance: (url: string, responseTime: number, status: number) => {
    this.sendMetrics('api_call', {
      url,
      responseTime,
      status,
      timestamp: Date.now(),
    });
  },

  // Send metrics to analytics service
  sendMetrics: (event: string, data: any) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', event, data);
    }
  },
};
```

### Real-time Monitoring

```typescript
// monitoring/real-time-monitor.ts
export class RealTimeMonitor {
  private metrics: Map<string, number[]> = new Map();
  private interval: NodeJS.Timeout | null = null;

  start() {
    this.interval = setInterval(() => {
      this.collectMetrics();
    }, 5000); // Collect every 5 seconds
  }

  stop() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
  }

  private collectMetrics() {
    if (typeof window !== 'undefined') {
      // Memory usage
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        this.trackMetric('memory_used', memory.usedJSHeapSize);
        this.trackMetric('memory_total', memory.totalJSHeapSize);
      }

      // Frame rate
      this.trackFrameRate();

      // Network activity
      this.trackNetworkActivity();
    }
  }

  private trackFrameRate() {
    let frameCount = 0;
    let lastTime = performance.now();

    const countFrames = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime - lastTime >= 1000) {
        const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        this.trackMetric('fps', fps);
        frameCount = 0;
        lastTime = currentTime;
      }
      
      requestAnimationFrame(countFrames);
    };

    requestAnimationFrame(countFrames);
  }

  private trackNetworkActivity() {
    // Track active connections
    const connections = performance.getEntriesByType('resource');
    this.trackMetric('active_connections', connections.length);
  }

  private trackMetric(name: string, value: number) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name)!.push(value);
  }

  getMetrics() {
    const result: Record<string, { average: number; current: number }> = {};
    
    for (const [name, values] of this.metrics) {
      result[name] = {
        average: values.reduce((sum, val) => sum + val, 0) / values.length,
        current: values[values.length - 1] || 0,
      };
    }
    
    return result;
  }
}
```

## 🧪 Performance Testing

### Lighthouse Testing

```bash
# Install Lighthouse CI
npm install -g @lhci/cli

# Run Lighthouse tests
lhci autorun

# Lighthouse configuration
# lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['warn', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'categories:seo': ['warn', { minScore: 0.9 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

### Performance Testing Scripts

```typescript
// testing/performance-tests.ts
import { chromium } from 'playwright';

export const runPerformanceTests = async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Measure page load time
  const startTime = Date.now();
  await page.goto('http://localhost:3000');
  const loadTime = Date.now() - startTime;

  // Measure Core Web Vitals
  const metrics = await page.evaluate(() => {
    return new Promise((resolve) => {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        resolve(entries.map(entry => ({
          name: entry.name,
          value: entry.value,
        })));
      });
      
      observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
    });
  });

  // Measure bundle size
  const bundleSize = await page.evaluate(() => {
    const resources = performance.getEntriesByType('resource');
    return resources.reduce((total, resource) => total + resource.transferSize, 0);
  });

  await browser.close();

  return {
    loadTime,
    metrics,
    bundleSize,
  };
};
```

### Load Testing

```typescript
// testing/load-test.ts
import { chromium } from 'playwright';

export const runLoadTest = async (concurrentUsers: number = 10) => {
  const results: any[] = [];
  const promises: Promise<any>[] = [];

  for (let i = 0; i < concurrentUsers; i++) {
    promises.push(simulateUser(i));
  }

  const userResults = await Promise.all(promises);
  results.push(...userResults);

  return analyzeResults(results);
};

const simulateUser = async (userId: number) => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const startTime = Date.now();

  try {
    // Navigate to page
    await page.goto('http://localhost:3000');
    
    // Simulate user interactions
    await page.click('[data-testid="upload-button"]');
    await page.waitForSelector('[data-testid="file-input"]');
    
    // Measure response times
    const responseTimes = await page.evaluate(() => {
      return performance.getEntriesByType('navigation').map(entry => ({
        name: entry.name,
        duration: entry.duration,
      }));
    });

    await browser.close();

    return {
      userId,
      duration: Date.now() - startTime,
      responseTimes,
      success: true,
    };
  } catch (error) {
    await browser.close();
    return {
      userId,
      duration: Date.now() - startTime,
      error: error.message,
      success: false,
    };
  }
};

const analyzeResults = (results: any[]) => {
  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  return {
    totalUsers: results.length,
    successful: successful.length,
    failed: failed.length,
    averageResponseTime: successful.reduce((sum, r) => sum + r.duration, 0) / successful.length,
    successRate: successful.length / results.length,
  };
};
```

## 🎯 Best Practices

### 1. Code Optimization

- **Use React.memo** for expensive components
- **Implement useMemo** for expensive calculations
- **Use useCallback** for event handlers
- **Avoid inline objects and functions** in render
- **Implement virtual scrolling** for large lists

### 2. Bundle Optimization

- **Code split** by routes and features
- **Tree shake** unused code
- **Optimize images** and use modern formats
- **Minimize dependencies** and use smaller alternatives
- **Use dynamic imports** for heavy components

### 3. Caching Strategy

- **Implement browser caching** for static assets
- **Use service workers** for offline functionality
- **Cache API responses** appropriately
- **Implement memory caching** for frequently accessed data
- **Use CDN** for global content delivery

### 4. Monitoring

- **Track Core Web Vitals** continuously
- **Monitor bundle size** over time
- **Set up performance alerts** for regressions
- **Use real-time monitoring** for production
- **Implement error tracking** for performance issues

### 5. Testing

- **Run performance tests** in CI/CD
- **Set performance budgets** and enforce them
- **Test on multiple devices** and network conditions
- **Monitor performance regressions** automatically
- **Use Lighthouse CI** for continuous monitoring

---

**Last Updated**: [Automated Update]
**Version**: 1.0.0 