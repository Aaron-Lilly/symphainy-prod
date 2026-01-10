/**
 * Composition Context
 * Context composition utilities
 */

import React, { 
  createContext, 
  useContext, 
  useMemo,
  ReactNode
} from 'react';

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

// Context Provider Creator
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
      ...value
    }), [value]);
    
    return (
      <Context.Provider value={contextValue}>
        {children}
      </Context.Provider>
    );
  };
}

// Component Registry Hook
export function useComponentRegistry<T extends Record<string, React.ComponentType<any>>>(
  registry: T
) {
  return useMemo(() => {
    const enhancedRegistry: Record<string, React.ComponentType<any>> = {};
    
    Object.entries(registry).forEach(([key, Component]) => {
      enhancedRegistry[key] = React.memo(Component);
    });
    
    return enhancedRegistry;
  }, [registry]);
}

// Composed Component Creator
export function createComposedComponent<P extends object>(
  components: Array<React.ComponentType<P>>,
  config: { enableMemoization?: boolean } = {}
) {
  return React.forwardRef<any, P>((props, ref) => {
    let result = <div ref={ref} />;
    
    for (let i = components.length - 1; i >= 0; i--) {
      const Component = components[i];
      result = <Component {...props}>{result}</Component>;
    }
    
    return config.enableMemoization ? React.memo(() => result)() : result;
  });
} 