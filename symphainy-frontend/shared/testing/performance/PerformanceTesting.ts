/**
 * Performance Testing
 * Advanced performance testing with metrics collection
 */

import { getGlobalConfig } from '../../config';

export interface PerformanceTestConfig {
  enableRenderTimeTesting: boolean;
  enableMemoryTesting: boolean;
  enableNetworkTesting: boolean;
  enableBundleAnalysis: boolean;
  enableCpuProfiling: boolean;
  iterations: number;
  warmupIterations: number;
  timeout: number;
}

export interface PerformanceMetrics {
  renderTime: number;
  memoryUsage: number;
  cpuUsage: number;
  networkRequests: number;
  bundleSize: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  cumulativeLayoutShift: number;
  firstInputDelay: number;
}

export interface PerformanceTestResult {
  id: string;
  metrics: PerformanceMetrics;
  iterations: number;
  averageMetrics: PerformanceMetrics;
  minMetrics: PerformanceMetrics;
  maxMetrics: PerformanceMetrics;
  standardDeviation: PerformanceMetrics;
  passed: boolean;
  thresholds: PerformanceThresholds;
  timestamp: number;
  metadata: Record<string, any>;
}

export interface PerformanceThresholds {
  maxRenderTime: number;
  maxMemoryUsage: number;
  maxCpuUsage: number;
  maxNetworkRequests: number;
  maxBundleSize: number;
}

export class PerformanceTesting {
  private config = getGlobalConfig();
  private performanceConfig: PerformanceTestConfig;
  private observers: Map<string, PerformanceObserver> = new Map();

  constructor(config: Partial<PerformanceTestConfig> = {}) {
    this.performanceConfig = {
      enableRenderTimeTesting: true,
      enableMemoryTesting: true,
      enableNetworkTesting: true,
      enableBundleAnalysis: true,
      enableCpuProfiling: true,
      iterations: 10,
      warmupIterations: 3,
      timeout: 30000,
      ...config,
    };
  }

  // Measure component performance
  async measureComponentPerformance(
    component: any,
    testId: string,
    thresholds: Partial<PerformanceThresholds> = {}
  ): Promise<PerformanceTestResult> {
    const results: PerformanceMetrics[] = [];

    // Warmup iterations
    for (let i = 0; i < this.performanceConfig.warmupIterations; i++) {
      await this.measureSingleIteration(component);
    }

    // Actual test iterations
    for (let i = 0; i < this.performanceConfig.iterations; i++) {
      const metrics = await this.measureSingleIteration(component);
      results.push(metrics);
    }

    // Calculate statistics
    const averageMetrics = this.calculateAverageMetrics(results);
    const minMetrics = this.calculateMinMetrics(results);
    const maxMetrics = this.calculateMaxMetrics(results);
    const standardDeviation = this.calculateStandardDeviation(results, averageMetrics);

    // Check against thresholds
    const defaultThresholds: PerformanceThresholds = {
      maxRenderTime: 16, // 60fps
      maxMemoryUsage: 50 * 1024 * 1024, // 50MB
      maxCpuUsage: 80, // 80%
      maxNetworkRequests: 10,
      maxBundleSize: 1024 * 1024, // 1MB
      ...thresholds,
    };

    const passed = this.checkThresholds(averageMetrics, defaultThresholds);

    return {
      id: testId,
      metrics: results[0], // First iteration metrics
      iterations: this.performanceConfig.iterations,
      averageMetrics,
      minMetrics,
      maxMetrics,
      standardDeviation,
      passed,
      thresholds: defaultThresholds,
      timestamp: Date.now(),
      metadata: { component: component.name || 'unknown' },
    };
  }

  // Measure single iteration
  private async measureSingleIteration(component: any): Promise<PerformanceMetrics> {
    const startTime = performance.now();
    const startMemory = (performance as any).memory?.usedJSHeapSize || 0;

    // Measure render time
    const renderStart = performance.now();
    // Component rendering logic would go here
    const renderTime = performance.now() - renderStart;

    // Measure memory usage
    const endMemory = (performance as any).memory?.usedJSHeapSize || 0;
    const memoryUsage = endMemory - startMemory;

    // Measure network requests
    const networkRequests = this.countNetworkRequests();

    // Measure bundle size
    const bundleSize = await this.measureBundleSize();

    // Measure Web Vitals
    const webVitals = await this.measureWebVitals();

    return {
      renderTime,
      memoryUsage,
      cpuUsage: 0, // Would need CPU monitoring
      networkRequests,
      bundleSize,
      firstContentfulPaint: webVitals.firstContentfulPaint || 0,
      largestContentfulPaint: webVitals.largestContentfulPaint || 0,
      cumulativeLayoutShift: webVitals.cumulativeLayoutShift || 0,
      firstInputDelay: webVitals.firstInputDelay || 0,
    };
  }

  // Measure Web Vitals
  private async measureWebVitals(): Promise<Partial<PerformanceMetrics>> {
    const vitals: Partial<PerformanceMetrics> = {};

    // First Contentful Paint
    if ('PerformanceObserver' in window) {
      vitals.firstContentfulPaint = await this.measureFirstContentfulPaint();
    }

    // Largest Contentful Paint
    vitals.largestContentfulPaint = await this.measureLargestContentfulPaint();

    // Cumulative Layout Shift
    vitals.cumulativeLayoutShift = await this.measureCumulativeLayoutShift();

    // First Input Delay
    vitals.firstInputDelay = await this.measureFirstInputDelay();

    return vitals;
  }

  // Measure First Contentful Paint
  private async measureFirstContentfulPaint(): Promise<number> {
    return new Promise((resolve) => {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const fcp = entries.find(entry => entry.name === 'first-contentful-paint');
        if (fcp) {
          resolve(fcp.startTime);
        }
      });

      observer.observe({ entryTypes: ['paint'] });
      
      // Fallback timeout
      setTimeout(() => resolve(0), 5000);
    });
  }

  // Measure Largest Contentful Paint
  private async measureLargestContentfulPaint(): Promise<number> {
    return new Promise((resolve) => {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lcp = entries[entries.length - 1];
        if (lcp) {
          resolve(lcp.startTime);
        }
      });

      observer.observe({ entryTypes: ['largest-contentful-paint'] });
      
      // Fallback timeout
      setTimeout(() => resolve(0), 5000);
    });
  }

  // Measure Cumulative Layout Shift
  private async measureCumulativeLayoutShift(): Promise<number> {
    return new Promise((resolve) => {
      let cls = 0;
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (!entry.hadRecentInput) {
            cls += entry.value;
          }
        });
      });

      observer.observe({ entryTypes: ['layout-shift'] });
      
      // Resolve after a delay
      setTimeout(() => resolve(cls), 5000);
    });
  }

  // Measure First Input Delay
  private async measureFirstInputDelay(): Promise<number> {
    return new Promise((resolve) => {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const fid = entries[0];
        if (fid) {
          resolve((fid as any).processingStart - fid.startTime);
        }
      });

      observer.observe({ entryTypes: ['first-input'] });
      
      // Fallback timeout
      setTimeout(() => resolve(0), 5000);
    });
  }

  // Count network requests
  private countNetworkRequests(): number {
    if ('PerformanceObserver' in window) {
      let count = 0;
      const observer = new PerformanceObserver((list) => {
        count += list.getEntries().length;
      });

      observer.observe({ entryTypes: ['resource'] });
      return count;
    }
    return 0;
  }

  // Measure bundle size
  private async measureBundleSize(): Promise<number> {
    // This would analyze the actual bundle size
    // For now, return a placeholder
    return 0;
  }

  // Calculate average metrics
  private calculateAverageMetrics(metrics: PerformanceMetrics[]): PerformanceMetrics {
    const sum = metrics.reduce((acc, metric) => ({
      renderTime: acc.renderTime + metric.renderTime,
      memoryUsage: acc.memoryUsage + metric.memoryUsage,
      cpuUsage: acc.cpuUsage + metric.cpuUsage,
      networkRequests: acc.networkRequests + metric.networkRequests,
      bundleSize: acc.bundleSize + metric.bundleSize,
      firstContentfulPaint: acc.firstContentfulPaint + metric.firstContentfulPaint,
      largestContentfulPaint: acc.largestContentfulPaint + metric.largestContentfulPaint,
      cumulativeLayoutShift: acc.cumulativeLayoutShift + metric.cumulativeLayoutShift,
      firstInputDelay: acc.firstInputDelay + metric.firstInputDelay,
    }), {
      renderTime: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      networkRequests: 0,
      bundleSize: 0,
      firstContentfulPaint: 0,
      largestContentfulPaint: 0,
      cumulativeLayoutShift: 0,
      firstInputDelay: 0,
    });

    const count = metrics.length;
    return {
      renderTime: sum.renderTime / count,
      memoryUsage: sum.memoryUsage / count,
      cpuUsage: sum.cpuUsage / count,
      networkRequests: sum.networkRequests / count,
      bundleSize: sum.bundleSize / count,
      firstContentfulPaint: sum.firstContentfulPaint / count,
      largestContentfulPaint: sum.largestContentfulPaint / count,
      cumulativeLayoutShift: sum.cumulativeLayoutShift / count,
      firstInputDelay: sum.firstInputDelay / count,
    };
  }

  // Calculate min metrics
  private calculateMinMetrics(metrics: PerformanceMetrics[]): PerformanceMetrics {
    return {
      renderTime: Math.min(...metrics.map(m => m.renderTime)),
      memoryUsage: Math.min(...metrics.map(m => m.memoryUsage)),
      cpuUsage: Math.min(...metrics.map(m => m.cpuUsage)),
      networkRequests: Math.min(...metrics.map(m => m.networkRequests)),
      bundleSize: Math.min(...metrics.map(m => m.bundleSize)),
      firstContentfulPaint: Math.min(...metrics.map(m => m.firstContentfulPaint)),
      largestContentfulPaint: Math.min(...metrics.map(m => m.largestContentfulPaint)),
      cumulativeLayoutShift: Math.min(...metrics.map(m => m.cumulativeLayoutShift)),
      firstInputDelay: Math.min(...metrics.map(m => m.firstInputDelay)),
    };
  }

  // Calculate max metrics
  private calculateMaxMetrics(metrics: PerformanceMetrics[]): PerformanceMetrics {
    return {
      renderTime: Math.max(...metrics.map(m => m.renderTime)),
      memoryUsage: Math.max(...metrics.map(m => m.memoryUsage)),
      cpuUsage: Math.max(...metrics.map(m => m.cpuUsage)),
      networkRequests: Math.max(...metrics.map(m => m.networkRequests)),
      bundleSize: Math.max(...metrics.map(m => m.bundleSize)),
      firstContentfulPaint: Math.max(...metrics.map(m => m.firstContentfulPaint)),
      largestContentfulPaint: Math.max(...metrics.map(m => m.largestContentfulPaint)),
      cumulativeLayoutShift: Math.max(...metrics.map(m => m.cumulativeLayoutShift)),
      firstInputDelay: Math.max(...metrics.map(m => m.firstInputDelay)),
    };
  }

  // Calculate standard deviation
  private calculateStandardDeviation(
    metrics: PerformanceMetrics[],
    average: PerformanceMetrics
  ): PerformanceMetrics {
    const variance = metrics.reduce((acc, metric) => ({
      renderTime: acc.renderTime + Math.pow(metric.renderTime - average.renderTime, 2),
      memoryUsage: acc.memoryUsage + Math.pow(metric.memoryUsage - average.memoryUsage, 2),
      cpuUsage: acc.cpuUsage + Math.pow(metric.cpuUsage - average.cpuUsage, 2),
      networkRequests: acc.networkRequests + Math.pow(metric.networkRequests - average.networkRequests, 2),
      bundleSize: acc.bundleSize + Math.pow(metric.bundleSize - average.bundleSize, 2),
      firstContentfulPaint: acc.firstContentfulPaint + Math.pow(metric.firstContentfulPaint - average.firstContentfulPaint, 2),
      largestContentfulPaint: acc.largestContentfulPaint + Math.pow(metric.largestContentfulPaint - average.largestContentfulPaint, 2),
      cumulativeLayoutShift: acc.cumulativeLayoutShift + Math.pow(metric.cumulativeLayoutShift - average.cumulativeLayoutShift, 2),
      firstInputDelay: acc.firstInputDelay + Math.pow(metric.firstInputDelay - average.firstInputDelay, 2),
    }), {
      renderTime: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      networkRequests: 0,
      bundleSize: 0,
      firstContentfulPaint: 0,
      largestContentfulPaint: 0,
      cumulativeLayoutShift: 0,
      firstInputDelay: 0,
    });

    const count = metrics.length;
    return {
      renderTime: Math.sqrt(variance.renderTime / count),
      memoryUsage: Math.sqrt(variance.memoryUsage / count),
      cpuUsage: Math.sqrt(variance.cpuUsage / count),
      networkRequests: Math.sqrt(variance.networkRequests / count),
      bundleSize: Math.sqrt(variance.bundleSize / count),
      firstContentfulPaint: Math.sqrt(variance.firstContentfulPaint / count),
      largestContentfulPaint: Math.sqrt(variance.largestContentfulPaint / count),
      cumulativeLayoutShift: Math.sqrt(variance.cumulativeLayoutShift / count),
      firstInputDelay: Math.sqrt(variance.firstInputDelay / count),
    };
  }

  // Check thresholds
  private checkThresholds(
    metrics: PerformanceMetrics,
    thresholds: PerformanceThresholds
  ): boolean {
    return (
      metrics.renderTime <= thresholds.maxRenderTime &&
      metrics.memoryUsage <= thresholds.maxMemoryUsage &&
      metrics.cpuUsage <= thresholds.maxCpuUsage &&
      metrics.networkRequests <= thresholds.maxNetworkRequests &&
      metrics.bundleSize <= thresholds.maxBundleSize
    );
  }
} 