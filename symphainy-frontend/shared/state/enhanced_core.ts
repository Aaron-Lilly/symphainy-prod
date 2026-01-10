/**
 * Enhanced State Management Core
 * Real-time state synchronization with offline support
 */

import { getGlobalConfig } from '../config';

export interface StateNode<T = any> {
  id: string;
  data: T;
  version: number;
  timestamp: number;
  lastSync: number;
  isDirty: boolean;
  isOffline: boolean;
}

export interface StateChange<T = any> {
  id: string;
  type: 'CREATE' | 'UPDATE' | 'DELETE' | 'SYNC';
  data?: T;
  version: number;
  timestamp: number;
  source: 'local' | 'remote' | 'sync';
}

export interface StateConfig {
  syncInterval: number;
  maxOfflineTime: number;
  conflictResolution: 'local' | 'remote' | 'manual';
  enableOfflineMode: boolean;
}

export class EnhancedStateManager {
  private state: Map<string, StateNode> = new Map();
  private changes: StateChange[] = [];
  private listeners: Map<string, ((node: StateNode) => void)[]> = new Map();
  private config = getGlobalConfig();
  private stateConfig: StateConfig;
  private syncInterval: NodeJS.Timeout | null = null;

  constructor(config: Partial<StateConfig> = {}) {
    this.stateConfig = {
      syncInterval: 5000,
      maxOfflineTime: 300000,
      conflictResolution: 'local',
      enableOfflineMode: true,
      ...config,
    };
    this.startSync();
  }

  setState<T>(id: string, data: T): void {
    const existing = this.state.get(id);
    const version = existing ? existing.version + 1 : 1;
    
    const node: StateNode<T> = {
      id,
      data,
      version,
      timestamp: Date.now(),
      lastSync: existing?.lastSync || 0,
      isDirty: true,
      isOffline: !navigator.onLine,
    };

    this.state.set(id, node);
    this.recordChange('UPDATE', id, data, version);
    this.notifyListeners(id, node);
  }

  getState<T>(id: string): T | null {
    const node = this.state.get(id);
    return node ? node.data : null;
  }

  deleteState(id: string): void {
    const node = this.state.get(id);
    if (node) {
      this.recordChange('DELETE', id, undefined, node.version + 1);
      this.state.delete(id);
      this.notifyListeners(id, node);
    }
  }

  private recordChange<T>(
    type: StateChange['type'],
    id: string,
    data?: T,
    version?: number
  ): void {
    const change: StateChange<T> = {
      id,
      type,
      data,
      version: version || 1,
      timestamp: Date.now(),
      source: 'local',
    };
    this.changes.push(change);
  }

  subscribe(id: string, callback: (node: StateNode) => void): () => void {
    if (!this.listeners.has(id)) {
      this.listeners.set(id, []);
    }
    this.listeners.get(id)!.push(callback);
    return () => {
      const callbacks = this.listeners.get(id);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  private notifyListeners(id: string, node: StateNode): void {
    const callbacks = this.listeners.get(id);
    if (callbacks) {
      callbacks.forEach(callback => callback(node));
    }
  }

  private startSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
    this.syncInterval = setInterval(() => {
      this.performSync();
    }, this.stateConfig.syncInterval);
  }

  private async performSync(): Promise<void> {
    if (!navigator.onLine) {
      this.markAllOffline();
      return;
    }
    const dirtyNodes = Array.from(this.state.values()).filter(node => node.isDirty);
    for (const node of dirtyNodes) {
      try {
        await this.syncNode(node);
      } catch (error) {
        console.error(`Failed to sync node ${node.id}:`, error);
      }
    }
  }

  private async syncNode(node: StateNode): Promise<void> {
    const syncChange: StateChange = {
      id: node.id,
      type: 'SYNC',
      data: node.data,
      version: node.version,
      timestamp: Date.now(),
      source: 'remote',
    };
    node.lastSync = Date.now();
    node.isDirty = false;
    node.isOffline = false;
    this.changes.push(syncChange);
    this.notifyListeners(node.id, node);
  }

  private markAllOffline(): void {
    for (const node of Array.from(this.state.values())) {
      node.isOffline = true;
      this.notifyListeners(node.id, node);
    }
  }

  getChanges(): StateChange[] {
    return [...this.changes];
  }

  clearChanges(): void {
    this.changes = [];
  }

  getStats() {
    return {
      totalNodes: this.state.size,
      dirtyNodes: Array.from(this.state.values()).filter(n => n.isDirty).length,
      offlineNodes: Array.from(this.state.values()).filter(n => n.isOffline).length,
      pendingChanges: this.changes.length,
    };
  }

  destroy(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
    this.state.clear();
    this.changes = [];
    this.listeners.clear();
  }
} 