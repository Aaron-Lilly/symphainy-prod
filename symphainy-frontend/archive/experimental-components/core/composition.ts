/**
 * Component Composition Utilities
 * Advanced composition patterns for React components
 */

import React, { 
  createContext, 
  useContext, 
  useMemo, 
  useCallback,
  ReactNode,
  ComponentType,
  forwardRef,
  useImperativeHandle,
  useRef
} from 'react';

export interface CompositionConfig {
  enableContextComposition: boolean;
  enableRenderProps: boolean;
  enableCompoundComponents: boolean;
  enableHigherOrderComponents: boolean;
}

export interface RenderPropsConfig<T = any> {
  render: (props: T) => ReactNode;
  children?: (props: T) => ReactNode;
}

// Context Composition Hook
export function useContextComposition<T>(
  contexts: Array<React.Context<T>>,
  defaultValue: T
): T {
  return useMemo(() => {
    let result = defaultValue;
    
    for (const context of contexts) {
      const value = useContext(context);
      if (value !== undefined) {
        result = { ...result, ...value };
      }
    }
    
    return result;
  }, [contexts, defaultValue]);
}

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

// Context Provider Composition
export function createContextProvider<T>(
  Context: React.Context<T>,
  defaultValue: T
) {
  return function ContextProvider({ 
    children, 
    value 
  }: { 
    children: ReactNode; 
    value?: Partial<T> 
  }) {
    const contextValue = useMemo(() => ({
      ...defaultValue,
      ...value,
    }), [value]);

    return (
      <Context.Provider value={contextValue}>
        {children}
      </Context.Provider>
    );
  };
}

// Component Registry Hook
export function useComponentRegistry<T extends Record<string, ComponentType<any>>>(
  registry: T
) {
  const registryRef = useRef<T>(registry);

  const registerComponent = useCallback(<K extends keyof T>(
    key: K,
    component: T[K]
  ) => {
    registryRef.current = {
      ...registryRef.current,
      [key]: component,
    };
  }, []);

  const unregisterComponent = useCallback(<K extends keyof T>(key: K) => {
    const { [key]: removed, ...rest } = registryRef.current;
    registryRef.current = rest as T;
  }, []);

  const getComponent = useCallback(<K extends keyof T>(key: K): T[K] | undefined => {
    return registryRef.current[key];
  }, []);

  return {
    registry: registryRef.current,
    registerComponent,
    unregisterComponent,
    getComponent,
  };
}

// Component Factory Hook
export function useComponentFactory<T extends Record<string, any>>(
  factory: (props: T) => ComponentType<any>
) {
  return useCallback((props: T) => {
    return factory(props);
  }, [factory]);
}

// Component Composition with Ref Forwarding
export function createComposedComponent<P extends object>(
  components: Array<ComponentType<P>>,
  config: CompositionConfig = {}
) {
  return forwardRef<any, P>((props, ref) => {
    const composedProps = useComponentComposition(props, []);
    
    let result = <></>;
    
    for (const Component of components) {
      result = <Component {...composedProps} />;
    }
    
    useImperativeHandle(ref, () => ({
      // Expose component methods if needed
    }));
    
    return result;
  });
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
      // This is a simplified pipeline - in practice, you'd need to handle component rendering
      result = { ...result };
    }
    
    return result;
  }, [components, props]);
} 