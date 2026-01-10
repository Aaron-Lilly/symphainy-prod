/**
 * Composition Patterns
 * Design patterns for component composition
 */

import React, { 
  useMemo, 
  forwardRef,
  ComponentType,
  ReactNode,
  useState,
  useEffect,
  useCallback,
  useContext
} from 'react';
import { RenderPropsConfig } from './types';

// Render Props Hook
export function useRenderProps<T>(
  config: RenderPropsConfig<T>,
  props: T
): ReactNode {
  return useMemo(() => {
    if (config.render) {
      return config.render(props);
    }
    if (config.children) {
      return config.children(props);
    }
    return null;
  }, [config, props]);
}

// Compound Component Hook
export function useCompoundComponent<T extends Record<string, ComponentType<any>>>(
  components: T,
  props: Record<string, any> = {}
) {
  return useMemo(() => {
    const compoundComponents: Record<string, ComponentType<any>> = {};
    
    Object.entries(components).forEach(([key, Component]) => {
      compoundComponents[key] = forwardRef<any, any>((componentProps, ref) => {
        const mergedProps = { ...props, ...componentProps };
        return <Component {...mergedProps} ref={ref} />;
      });
    });
    
    return compoundComponents;
  }, [components, props]);
}

// Higher Order Component Factory
export function createHOC<P extends object>(
  WrappedComponent: ComponentType<P>,
  enhancer: (Component: ComponentType<P>) => ComponentType<P>
) {
  return enhancer(WrappedComponent);
}

// Component Composition Hook
export function useComponentComposition<T extends Record<string, any>>(
  baseProps: T,
  compositions: Array<(props: T) => T> = []
): T {
  return useMemo(() => {
    let result = baseProps;
    
    for (const composition of compositions) {
      result = composition(result);
    }
    
    return result;
  }, [baseProps, compositions]);
}

// Component Factory Hook
export function useComponentFactory<T extends Record<string, any>>(
  factory: (props: T) => ComponentType<any>
) {
  return useMemo(() => factory, [factory]);
}

// Conditional Component Hook
export function useConditionalComponent<P extends object>(
  condition: boolean,
  Component: ComponentType<P>,
  fallback?: ComponentType<P>
) {
  return useMemo(() => {
    if (condition) {
      return Component;
    }
    return fallback || (() => null);
  }, [condition, Component, fallback]);
}

// Component Pipeline Hook
export function useComponentPipeline<P extends object>(
  components: Array<ComponentType<P>>,
  props: P
) {
  return useMemo(() => {
    let result = props;
    
    for (const Component of components) {
      result = { ...result, ...Component.defaultProps };
    }
    
    return result;
  }, [components, props]);
}

// State-based composition hook
export function useStateComposition<T>(initialState: T) {
  const [state, setState] = useState<T>(initialState);
  
  const updateState = useCallback((updates: Partial<T>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);
  
  return { state, setState, updateState };
}

// Effect-based composition hook
export function useEffectComposition(effects: Array<() => void | (() => void)>) {
  useEffect(() => {
    const cleanupFns: Array<(() => void) | void> = [];
    
    effects.forEach(effect => {
      const cleanup = effect();
      if (cleanup) {
        cleanupFns.push(cleanup);
      }
    });
    
    return () => {
      cleanupFns.forEach(cleanup => {
        if (typeof cleanup === 'function') {
          cleanup();
        }
      });
    };
  }, [effects]);
} 