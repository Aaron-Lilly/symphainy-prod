/**
 * Optimization Core
 * Core optimization utilities and hooks
 */

import React, { useTransition, startTransition, useRef, useEffect } from 'react';
import { OptimizationConfig } from './types';

// Transition optimization hook
export function useTransitionOptimization() {
  const [isPending, startTransitionOptimized] = useTransition();
  
  const optimizedTransition = (callback: () => void) => {
    startTransitionOptimized(callback);
  };

  return {
    isPending,
    startTransition: optimizedTransition
  };
}

// Render optimization hook
export function useRenderOptimization(
  componentName: string,
  config: Partial<OptimizationConfig> = {}
) {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(performance.now());
  const warningThreshold = config.memoizationDepth || 10;

  useEffect(() => {
    renderCount.current += 1;
    const currentTime = performance.now();
    const timeSinceLastRender = currentTime - lastRenderTime.current;
    
    if (renderCount.current > warningThreshold) {
      console.warn(
        `${componentName} has rendered ${renderCount.current} times ` +
        `(last render: ${timeSinceLastRender.toFixed(2)}ms ago). Consider optimization.`
      );
    }
    
    lastRenderTime.current = currentTime;
  });

  return {
    renderCount: renderCount.current,
    timeSinceLastRender: performance.now() - lastRenderTime.current
  };
}

// Ref optimization hook
export function useRefOptimization<T>(initialValue: T) {
  const ref = useRef<T>(initialValue);
  
  const setValue = (value: T) => {
    ref.current = value;
  };
  
  const getValue = () => ref.current;
  
  return { ref, setValue, getValue };
} 