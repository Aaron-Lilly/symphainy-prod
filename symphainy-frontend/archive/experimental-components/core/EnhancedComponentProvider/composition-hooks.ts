/**
 * Enhanced Component Provider Composition Hooks
 * Composition utilities and hooks for enhanced component functionality
 */

import React, { useContext, useRef, useCallback } from 'react';

// Context Composition Hook
export function useContextComposition<T>(context: React.Context<T>, defaultValue: T) {
  const value = useContext(context);
  return value !== null ? value : defaultValue;
}

// Render Props Hook
export function useRenderProps<T>(
  render: (props: T) => React.ReactNode,
  props: T
) {
  return render(props);
}

// Compound Component Hook
export function useCompoundComponent<T extends Record<string, any>>(
  components: T,
  props: any
) {
  return Object.keys(components).reduce((acc, key) => {
    acc[key] = React.cloneElement(components[key], props);
    return acc;
  }, {} as T);
}

// Higher Order Component Creator
export function createHOC<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  enhancer: (props: P) => P
) {
  return React.forwardRef<any, P>((props, ref) => {
    const enhancedProps = enhancer(props);
    return <WrappedComponent {...enhancedProps} ref={ref} />;
  });
}

// Component Composition Hook
export function useComponentComposition<T extends Record<string, any>>(
  baseProps: T,
  compositions: Array<(props: T) => T>
) {
  return compositions.reduce((props, composition) => composition(props), baseProps);
}

// Context Provider Creator
export function createContextProvider<T>(
  defaultValue: T,
  reducer?: (state: T, action: any) => T
) {
  const Context = createContext<T>(defaultValue);
  
  const Provider: React.FC<{ children: React.ReactNode; value?: T }> = ({ 
    children, 
    value = defaultValue 
  }) => {
    const [state, dispatch] = React.useReducer(
      reducer || ((state: T) => state),
      value
    );
    
    return (
      <Context.Provider value={state}>
        {children}
      </Context.Provider>
    );
  };
  
  return { Context, Provider };
}

// Component Registry Hook
export function useComponentRegistry() {
  const registry = useRef<Map<string, React.ComponentType<any>>>(new Map());
  
  const register = useCallback((name: string, component: React.ComponentType<any>) => {
    registry.current.set(name, component);
  }, []);
  
  const get = useCallback((name: string) => {
    return registry.current.get(name);
  }, []);
  
  const unregister = useCallback((name: string) => {
    registry.current.delete(name);
  }, []);
  
  return { register, get, unregister };
} 