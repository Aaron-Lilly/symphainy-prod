/**
 * State Persistence Layer
 * Handles offline storage and state persistence
 */

import { StateNode, StateChange } from './enhanced_core';

export interface PersistenceConfig {
  storageKey: string;
  maxStorageSize: number;
  enableCompression: boolean;
  syncToCloud: boolean;
}

export interface StorageStats {
  usedSpace: number;
  maxSpace: number;
  itemCount: number;
  lastBackup: number;
}

export class StatePersistence {
  private config: PersistenceConfig;
  private storage: Storage;

  constructor(config: Partial<PersistenceConfig> = {}) {
    this.config = {
      storageKey: 'symphainy_state',
      maxStorageSize: 50 * 1024 * 1024, // 50MB
      enableCompression: true,
      syncToCloud: false,
      ...config,
    };
    this.storage = this.getStorage();
  }

  // Save state to storage
  async saveState(id: string, node: StateNode): Promise<void> {
    try {
      const data = this.config.enableCompression 
        ? this.compress(JSON.stringify(node))
        : JSON.stringify(node);
      
      this.storage.setItem(`${this.config.storageKey}_${id}`, data);
      this.updateStats();
    } catch (error) {
      console.error('Failed to save state:', error);
      throw error;
    }
  }

  // Load state from storage
  async loadState<T>(id: string): Promise<StateNode<T> | null> {
    try {
      const data = this.storage.getItem(`${this.config.storageKey}_${id}`);
      if (!data) return null;

      const decompressed = this.config.enableCompression 
        ? this.decompress(data)
        : data;
      
      return JSON.parse(decompressed);
    } catch (error) {
      console.error('Failed to load state:', error);
      return null;
    }
  }

  // Save changes to storage
  async saveChanges(changes: StateChange[]): Promise<void> {
    try {
      const data = this.config.enableCompression 
        ? this.compress(JSON.stringify(changes))
        : JSON.stringify(changes);
      
      this.storage.setItem(`${this.config.storageKey}_changes`, data);
      this.updateStats();
    } catch (error) {
      console.error('Failed to save changes:', error);
      throw error;
    }
  }

  // Load changes from storage
  async loadChanges(): Promise<StateChange[]> {
    try {
      const data = this.storage.getItem(`${this.config.storageKey}_changes`);
      if (!data) return [];

      const decompressed = this.config.enableCompression 
        ? this.decompress(data)
        : data;
      
      return JSON.parse(decompressed);
    } catch (error) {
      console.error('Failed to load changes:', error);
      return [];
    }
  }

  // Clear storage
  async clearStorage(): Promise<void> {
    try {
      const keys = Object.keys(this.storage);
      const stateKeys = keys.filter(key => key.startsWith(this.config.storageKey));
      
      stateKeys.forEach(key => {
        this.storage.removeItem(key);
      });
      
      this.updateStats();
    } catch (error) {
      console.error('Failed to clear storage:', error);
      throw error;
    }
  }

  // Get storage statistics
  getStorageStats(): StorageStats {
    try {
      const statsData = this.storage.getItem(`${this.config.storageKey}_stats`);
      if (statsData) {
        return JSON.parse(statsData);
      }
    } catch (error) {
      console.error('Failed to load storage stats:', error);
    }

    return {
      usedSpace: 0,
      maxSpace: this.config.maxStorageSize,
      itemCount: 0,
      lastBackup: 0,
    };
  }

  // Check if storage is available
  isStorageAvailable(): boolean {
    try {
      const testKey = `${this.config.storageKey}_test`;
      this.storage.setItem(testKey, 'test');
      this.storage.removeItem(testKey);
      return true;
    } catch (error) {
      return false;
    }
  }

  // Check storage space
  hasStorageSpace(dataSize: number): boolean {
    const stats = this.getStorageStats();
    return (stats.usedSpace + dataSize) <= stats.maxSpace;
  }

  // Private methods
  private getStorage(): Storage {
    if (typeof window !== 'undefined' && window.localStorage) {
      return window.localStorage;
    }
    
    // Fallback to sessionStorage or memory storage
    if (typeof window !== 'undefined' && window.sessionStorage) {
      return window.sessionStorage;
    }
    
    // Memory storage fallback
    return new MemoryStorage();
  }

  private compress(data: string): string {
    // Simple compression - in production, use a proper compression library
    return btoa(data);
  }

  private decompress(data: string): string {
    // Simple decompression - in production, use a proper compression library
    return atob(data);
  }

  private updateStats(): void {
    try {
      const keys = Object.keys(this.storage);
      const stateKeys = keys.filter(key => key.startsWith(this.config.storageKey));
      
      let usedSpace = 0;
      stateKeys.forEach(key => {
        const data = this.storage.getItem(key);
        if (data) {
          usedSpace += new Blob([data]).size;
        }
      });

      const stats: StorageStats = {
        usedSpace,
        maxSpace: this.config.maxStorageSize,
        itemCount: stateKeys.length,
        lastBackup: Date.now(),
      };

      this.storage.setItem(`${this.config.storageKey}_stats`, JSON.stringify(stats));
    } catch (error) {
      console.error('Failed to update storage stats:', error);
    }
  }
}

// Memory storage fallback
class MemoryStorage implements Storage {
  private data: Map<string, string> = new Map();

  get length(): number {
    return this.data.size;
  }

  clear(): void {
    this.data.clear();
  }

  getItem(key: string): string | null {
    return this.data.get(key) || null;
  }

  key(index: number): string | null {
    const keys = Array.from(this.data.keys());
    return keys[index] || null;
  }

  removeItem(key: string): void {
    this.data.delete(key);
  }

  setItem(key: string, value: string): void {
    this.data.set(key, value);
  }
} 