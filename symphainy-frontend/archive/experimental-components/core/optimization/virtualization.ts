/**
 * Optimization Virtualization
 * Virtualization utilities for large lists and data
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { VirtualizationConfig } from './types';

// Virtualization hook for large lists
export function useVirtualization<T>(
  items: T[],
  config: VirtualizationConfig
) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const {
    itemHeight,
    containerHeight,
    overscan = 5,
    enableDynamicHeight = false
  } = config;

  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  const visibleItems = items.slice(startIndex, endIndex);
  const offsetY = startIndex * itemHeight;
  const totalHeight = items.length * itemHeight;

  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(event.currentTarget.scrollTop);
  }, []);

  return {
    visibleItems,
    offsetY,
    totalHeight,
    startIndex,
    endIndex,
    containerRef,
    handleScroll,
    setScrollTop
  };
}

// Batch updates hook
export function useBatchUpdates() {
  const [updates, setUpdates] = useState<Array<() => void>>([]);
  const isBatching = useRef(false);

  const batchUpdate = useCallback((update: () => void) => {
    if (isBatching.current) {
      setUpdates(prev => [...prev, update]);
    } else {
      update();
    }
  }, []);

  const startBatch = useCallback(() => {
    isBatching.current = true;
  }, []);

  const commitBatch = useCallback(() => {
    isBatching.current = false;
    updates.forEach(update => update());
    setUpdates([]);
  }, [updates]);

  return { batchUpdate, startBatch, commitBatch };
} 