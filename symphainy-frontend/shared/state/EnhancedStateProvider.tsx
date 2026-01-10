/**
 * Enhanced State Provider
 * React context provider for enhanced state management
 */

import React, { createContext, useContext, useRef, useEffect } from 'react';
import { EnhancedStateManager } from './enhanced_core';
import { StatePersistence } from './persistence';
import { StateSynchronizer } from './sync';
import { EnhancedSmartCityWebSocketClient } from '../websocket/EnhancedSmartCityWebSocketClient';
import { getGlobalConfig } from '../config';

interface EnhancedStateContextValue {
  stateManager: EnhancedStateManager | null;
  persistence: StatePersistence | null;
  synchronizer: StateSynchronizer | null;
  wsClient: EnhancedSmartCityWebSocketClient | null;
}

const EnhancedStateContext = createContext<EnhancedStateContextValue>({
  stateManager: null,
  persistence: null,
  synchronizer: null,
  wsClient: null,
});

interface EnhancedStateProviderProps {
  children: React.ReactNode;
  config?: {
    syncInterval?: number;
    enableOfflineMode?: boolean;
    storageKey?: string;
    enableCompression?: boolean;
    enableRealTimeSync?: boolean;
  };
}

export function EnhancedStateProvider({ 
  children, 
  config = {} 
}: EnhancedStateProviderProps) {
  const stateManagerRef = useRef<EnhancedStateManager | null>(null);
  const persistenceRef = useRef<StatePersistence | null>(null);
  const synchronizerRef = useRef<StateSynchronizer | null>(null);
  const wsClientRef = useRef<EnhancedSmartCityWebSocketClient | null>(null);

  useEffect(() => {
    const globalConfig = getGlobalConfig();
    
    // Initialize WebSocket client
    wsClientRef.current = new EnhancedSmartCityWebSocketClient();
    
    // Initialize state manager
    stateManagerRef.current = new EnhancedStateManager({
      syncInterval: config.syncInterval || 5000,
      enableOfflineMode: config.enableOfflineMode ?? true,
    });
    
    // Initialize persistence
    persistenceRef.current = new StatePersistence({
      storageKey: config.storageKey || 'symphainy_enhanced_state',
      enableCompression: config.enableCompression ?? true,
    });
    
    // Initialize synchronizer
    synchronizerRef.current = new StateSynchronizer(wsClientRef.current, {
      enableRealTimeSync: config.enableRealTimeSync ?? true,
      syncInterval: config.syncInterval || 3000,
    });

    // Connect WebSocket if Smart City is enabled
    if (globalConfig.getSection('smartCity').enabled) {
      wsClientRef.current.connect().catch(console.error);
    }

    return () => {
      stateManagerRef.current?.destroy();
      synchronizerRef.current?.destroy();
      wsClientRef.current?.shutdown();
    };
  }, [config]);

  const contextValue: EnhancedStateContextValue = {
    stateManager: stateManagerRef.current,
    persistence: persistenceRef.current,
    synchronizer: synchronizerRef.current,
    wsClient: wsClientRef.current,
  };

  return (
    <EnhancedStateContext.Provider value={contextValue}>
      {children}
    </EnhancedStateContext.Provider>
  );
}

// Hook to use enhanced state context
export function useEnhancedStateContext() {
  const context = useContext(EnhancedStateContext);
  if (!context) {
    throw new Error('useEnhancedStateContext must be used within EnhancedStateProvider');
  }
  return context;
} 