/**
 * Advanced Component Core
 * Core advanced component functionality
 */

import React, { Component, ReactNode, useState, useEffect, useCallback } from 'react';
import { getGlobalConfig } from '../../../config';
import { ComponentConfig, ComponentState } from './types';

// Base Advanced Component
export class AdvancedComponent<P = {}, S = {}> extends Component<P, S & ComponentState> {
  protected config: ComponentConfig;

  constructor(props: P) {
    super(props);
    
    const globalConfig = getGlobalConfig();
    this.config = {
      enableLazyLoading: true,
      enableErrorBoundary: true,
      enablePerformanceMonitoring: true,
      enableCaching: true,
      cacheTimeout: 300000,
      ...globalConfig.getSection('components'),
    };

    this.state = {
      ...this.state,
      isLoading: false,
      hasError: false,
      error: null,
      lastRender: Date.now(),
      renderCount: 0,
    } as S & ComponentState;
  }

  componentDidMount() {
    this.setState(prevState => ({
      ...prevState,
      lastRender: Date.now(),
      renderCount: (prevState as ComponentState).renderCount + 1,
    }));
  }

  componentDidUpdate() {
    this.setState(prevState => ({
      ...prevState,
      lastRender: Date.now(),
      renderCount: (prevState as ComponentState).renderCount + 1,
    }));
  }

  protected setLoading(loading: boolean) {
    this.setState(prevState => ({
      ...prevState,
      isLoading: loading,
    }));
  }

  protected setError(error: Error | null) {
    this.setState(prevState => ({
      ...prevState,
      hasError: !!error,
      error,
    }));
  }

  render(): ReactNode {
    return null; // Override in subclasses
  }
}

// Functional component hook for advanced features
export function useAdvancedComponent(config: Partial<ComponentConfig> = {}) {
  const [state, setState] = useState<ComponentState>({
    isLoading: false,
    hasError: false,
    error: null,
    lastRender: Date.now(),
    renderCount: 0,
  });

  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoading: loading }));
  }, []);

  const setError = useCallback((error: Error | null) => {
    setState(prev => ({ ...prev, hasError: !!error, error }));
  }, []);

  const updateRenderCount = useCallback(() => {
    setState(prev => ({
      ...prev,
      lastRender: Date.now(),
      renderCount: prev.renderCount + 1,
    }));
  }, []);

  useEffect(() => {
    updateRenderCount();
  });

  return {
    state,
    setLoading,
    setError,
    updateRenderCount,
  };
} 