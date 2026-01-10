/**
 * Lifecycle Core
 * Core lifecycle management hooks and functionality
 */

import React, { useEffect, useRef, useState } from 'react';
import { LifecycleState, LifecycleConfig, LifecycleEvents } from './types';

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

  return {
    state,
    setState,
    configRef,
    cleanupTimeoutRef,
    observerRef,
    elementRef,
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
      ([entry]) => setIsVisible(entry.isIntersecting),
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
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const updateActivity = () => {
    setIsActive(true);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => setIsActive(false), timeout);
  };

  const checkInactivity = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsActive(false);
  };

  useEffect(() => {
    updateActivity();
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [timeout]);

  return { isActive, updateActivity, checkInactivity };
} 