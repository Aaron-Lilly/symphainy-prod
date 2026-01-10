/**
 * State Synchronization Layer
 * Handles real-time state synchronization with Smart City components
 */

import { StateNode, StateChange } from './enhanced_core';
import { EnhancedSmartCityWebSocketClient } from '../websocket/EnhancedSmartCityWebSocketClient';
import { getGlobalConfig } from '../config';

export interface SyncConfig {
  enableRealTimeSync: boolean;
  syncInterval: number;
  batchSize: number;
  retryAttempts: number;
  retryDelay: number;
}

export interface SyncStatus {
  isSyncing: boolean;
  lastSyncTime: number;
  syncErrors: string[];
  pendingChanges: number;
  syncedChanges: number;
}

export class StateSynchronizer {
  private wsClient: EnhancedSmartCityWebSocketClient;
  private config = getGlobalConfig();
  private syncConfig: SyncConfig;
  private syncStatus: SyncStatus;
  private syncInterval: NodeJS.Timeout | null = null;

  constructor(wsClient: EnhancedSmartCityWebSocketClient, config: Partial<SyncConfig> = {}) {
    this.wsClient = wsClient;
    this.syncConfig = {
      enableRealTimeSync: true,
      syncInterval: 3000,
      batchSize: 10,
      retryAttempts: 3,
      retryDelay: 1000,
      ...config,
    };
    this.syncStatus = {
      isSyncing: false,
      lastSyncTime: 0,
      syncErrors: [],
      pendingChanges: 0,
      syncedChanges: 0,
    };
    this.startSync();
  }

  // Synchronize state changes
  async syncChanges(changes: StateChange[]): Promise<void> {
    if (!this.syncConfig.enableRealTimeSync || changes.length === 0) {
      return;
    }

    this.syncStatus.isSyncing = true;
    this.syncStatus.pendingChanges = changes.length;

    try {
      // Batch changes for efficient syncing
      const batches = this.createBatches(changes, this.syncConfig.batchSize);
      
      for (const batch of batches) {
        await this.syncBatch(batch);
      }

      this.syncStatus.lastSyncTime = Date.now();
      this.syncStatus.syncedChanges += changes.length;
      this.syncStatus.pendingChanges = 0;
    } catch (error) {
      this.syncStatus.syncErrors.push(error instanceof Error ? error.message : 'Sync failed');
      throw error;
    } finally {
      this.syncStatus.isSyncing = false;
    }
  }

  // Synchronize individual state node
  async syncNode(node: StateNode): Promise<void> {
    if (!this.syncConfig.enableRealTimeSync) {
      return;
    }

    try {
      // Send to Smart City Archive for persistence
      await this.wsClient.storeSession(node.id, {
        data: node.data,
        version: node.version,
        timestamp: node.timestamp,
        isDirty: node.isDirty,
      });

      // Update sync status
      this.syncStatus.lastSyncTime = Date.now();
      this.syncStatus.syncedChanges++;
    } catch (error) {
      this.syncStatus.syncErrors.push(error instanceof Error ? error.message : 'Node sync failed');
      throw error;
    }
  }

  // Get sync status
  getSyncStatus(): SyncStatus {
    return { ...this.syncStatus };
  }

  // Clear sync errors
  clearSyncErrors(): void {
    this.syncStatus.syncErrors = [];
  }

  // Force sync
  async forceSync(changes: StateChange[]): Promise<void> {
    const originalInterval = this.syncConfig.syncInterval;
    this.syncConfig.syncInterval = 0; // Immediate sync
    
    try {
      await this.syncChanges(changes);
    } finally {
      this.syncConfig.syncInterval = originalInterval;
    }
  }

  // Start automatic sync
  private startSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }

    this.syncInterval = setInterval(() => {
      // This would be called periodically to sync pending changes
      // Implementation depends on how changes are queued
    }, this.syncConfig.syncInterval);
  }

  // Stop automatic sync
  stopSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  // Create batches for efficient syncing
  private createBatches<T>(items: T[], batchSize: number): T[][] {
    const batches: T[][] = [];
    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize));
    }
    return batches;
  }

  // Sync a batch of changes
  private async syncBatch(batch: StateChange[]): Promise<void> {
    let attempts = 0;
    
    while (attempts < this.syncConfig.retryAttempts) {
      try {
        // Send batch to Smart City components
        for (const change of batch) {
          await this.syncChange(change);
        }
        return; // Success
      } catch (error) {
        attempts++;
        if (attempts >= this.syncConfig.retryAttempts) {
          throw error;
        }
        
        // Wait before retry with exponential backoff
        await this.delay(this.syncConfig.retryDelay * Math.pow(2, attempts - 1));
      }
    }
  }

  // Sync individual change
  private async syncChange(change: StateChange): Promise<void> {
    switch (change.type) {
      case 'CREATE':
      case 'UPDATE':
        await this.wsClient.storeSession(change.id, change.data);
        break;
      case 'DELETE':
        await this.wsClient.deleteSession(change.id);
        break;
      case 'SYNC':
        // Handle sync acknowledgment
        break;
      default:
        console.warn('Unknown change type:', change.type);
    }
  }

  // Utility method for delays
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Cleanup
  destroy(): void {
    this.stopSync();
  }
} 