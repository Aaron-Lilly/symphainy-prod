/**
 * Experience Dimension Context
 * 
 * Legacy context - functionality moved to specialized providers.
 */

"use client";

import React, { createContext, useContext, ReactNode } from 'react';

interface ExperienceDimensionContextType {
  dimensions: any[];
  setDimensions: (dimensions: any[]) => void;
  setUserContext: (context: any) => void;
  isConnected: boolean;
  connectionError: string | null;
}

const ExperienceDimensionContext = createContext<ExperienceDimensionContextType | undefined>(undefined);

export function ExperienceDimensionProvider({ children }: { children: ReactNode }) {
  const [dimensions, setDimensions] = React.useState<any[]>([]);
  const [isConnected] = React.useState(false);
  const [connectionError] = React.useState<string | null>(null);
  
  const setUserContext = React.useCallback((context: any) => {
    console.warn('[ExperienceDimensionContext] setUserContext - stub implementation');
  }, []);
  
  return (
    <ExperienceDimensionContext.Provider value={{ 
      dimensions, 
      setDimensions, 
      setUserContext, 
      isConnected,
      connectionError 
    }}>
      {children}
    </ExperienceDimensionContext.Provider>
  );
}

export function useExperienceDimension() {
  const context = useContext(ExperienceDimensionContext);
  if (context === undefined) {
    // Return default values instead of throwing for SSR compatibility
    return { 
      dimensions: [], 
      setDimensions: () => {}, 
      setUserContext: () => {},
      isConnected: false,
      connectionError: null
    };
  }
  return context;
}

// Alias for backward compatibility
export const useExperienceDimensionContext = useExperienceDimension;

export default ExperienceDimensionContext;
