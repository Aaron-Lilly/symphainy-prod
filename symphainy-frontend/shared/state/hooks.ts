/**
 * React Hooks for Enhanced State Management
 * Provides React hooks for state management functionality
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { EnhancedStateManager, StateNode } from './enhanced_core';
import { StatePersistence } from './persistence';
import { StateSynchronizer } from './sync';
import { EnhancedSmartCityWebSocketClient } from '../websocket/EnhancedSmartCityWebSocketClient';
import { getGlobalConfig } from '../config';

// Hook for enhanced state management
export function useEnhancedState<T = any>(id: string, initialData?: T) {
  const [state, setState] = useState<T | null>(initialData || null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState(false);
  
  const stateManagerRef = useRef<EnhancedStateManager | null>(null);
  const persistenceRef = useRef<StatePersistence | null>(null);
  const synchronizerRef = useRef<StateSynchronizer | null>(null);
  const wsClientRef = useRef<EnhancedSmartCityWebSocketClient | null>(null);

  // Initialize state management
  useEffect(() => {
    const config = getGlobalConfig();
    
    // Initialize WebSocket client
    wsClientRef.current = new EnhancedSmartCityWebSocketClient();
    
    // Initialize state manager
    stateManagerRef.current = new EnhancedStateManager({
      syncInterval: 5000,
      enableOfflineMode: true,
    });
    
    // Initialize persistence
    persistenceRef.current = new StatePersistence({
      storageKey: 'symphainy_enhanced_state',
      enableCompression: true,
    });
    
    // Initialize synchronizer
    synchronizerRef.current = new StateSynchronizer(wsClientRef.current, {
      enableRealTimeSync: true,
      syncInterval: 3000,
    });

    // Load initial state
    loadState();

    return () => {
      stateManagerRef.current?.destroy();
      synchronizerRef.current?.destroy();
    };
  }, [id]);

  // Load state from storage and manager
  const loadState = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Try to load from state manager first
      const managerState = stateManagerRef.current?.getState<T>(id);
      if (managerState) {
        setState(managerState);
        setIsLoading(false);
        return;
      }

      // Try to load from persistence
      if (persistenceRef.current) {
        const persistedState = await persistenceRef.current.loadState<T>(id);
        if (persistedState) {
          setState(persistedState.data);
          // Restore to state manager
          stateManagerRef.current?.setState(id, persistedState.data);
        }
      }

      setIsLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load state');
      setIsLoading(false);
    }
  }, [id]);

  // Update state
  const updateState = useCallback(async (newData: T) => {
    try {
      setError(null);
      setState(newData);

      // Update state manager
      stateManagerRef.current?.setState(id, newData);

      // Persist to storage
      if (persistenceRef.current) {
        const node: StateNode<T> = {
          id,
          data: newData,
          version: 1,
          timestamp: Date.now(),
          lastSync: Date.now(),
          isDirty: true,
          isOffline: !navigator.onLine,
        };
        await persistenceRef.current.saveState(id, node);
      }

      // Sync to remote
      if (synchronizerRef.current) {
        const changes = stateManagerRef.current?.getChanges() || [];
        await synchronizerRef.current.syncChanges(changes);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update state');
    }
  }, [id]);

  // Subscribe to state changes
  useEffect(() => {
    if (!stateManagerRef.current) return;

    const unsubscribe = stateManagerRef.current.subscribe(id, (node: StateNode) => {
      setState(node.data);
      setIsOffline(node.isOffline);
    });

    return unsubscribe;
  }, [id]);

  return {
    state,
    isLoading,
    error,
    isOffline,
    updateState,
    reload: loadState,
  };
}

// Hook for state synchronization
export function useStateSync() {
  const [syncStatus, setSyncStatus] = useState({
    isSyncing: false,
    lastSyncTime: 0,
    syncErrors: [],
    pendingChanges: 0,
    syncedChanges: 0,
  });

  const synchronizerRef = useRef<StateSynchronizer | null>(null);

  useEffect(() => {
    const wsClient = new EnhancedSmartCityWebSocketClient();
    synchronizerRef.current = new StateSynchronizer(wsClient);

    const interval = setInterval(() => {
      if (synchronizerRef.current) {
        setSyncStatus(synchronizerRef.current.getSyncStatus());
      }
    }, 1000);

    return () => {
      clearInterval(interval);
      synchronizerRef.current?.destroy();
    };
  }, []);

  const forceSync = useCallback(async (changes: any[]) => {
    if (synchronizerRef.current) {
      await synchronizerRef.current.forceSync(changes);
    }
  }, []);

  const clearErrors = useCallback(() => {
    synchronizerRef.current?.clearSyncErrors();
  }, []);

  return {
    syncStatus,
    forceSync,
    clearErrors,
  };
}

// Hook for state persistence
export function useStatePersistence() {
  const [storageStats, setStorageStats] = useState({
    usedSpace: 0,
    maxSpace: 50 * 1024 * 1024,
    itemCount: 0,
    lastBackup: 0,
  });

  const persistenceRef = useRef<StatePersistence | null>(null);

  useEffect(() => {
    persistenceRef.current = new StatePersistence();

    const interval = setInterval(() => {
      if (persistenceRef.current) {
        setStorageStats(persistenceRef.current.getStorageStats());
      }
    }, 5000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  const clearStorage = useCallback(async () => {
    if (persistenceRef.current) {
      await persistenceRef.current.clearStorage();
    }
  }, []);

  const isStorageAvailable = useCallback(() => {
    return persistenceRef.current?.isStorageAvailable() || false;
  }, []);

  return {
    storageStats,
    clearStorage,
    isStorageAvailable,
  };
} 