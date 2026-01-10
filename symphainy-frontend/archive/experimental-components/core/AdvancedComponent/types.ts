/**
 * Advanced Component Types
 * Type definitions for advanced component functionality
 */

import React, { ReactNode } from 'react';

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