/**
 * Verity Mobile - Offline Queue Manager
 * Handles offline storage and syncing of verification requests
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo, { NetInfoState } from '@react-native-community/netinfo';
import { showNotification } from './notifications';

// Queue item status
export type QueueItemStatus = 'pending' | 'syncing' | 'completed' | 'failed' | 'retrying';

// Queue item types
export interface OfflineQueueItem {
  id: string;
  type: 'text' | 'image' | 'url';
  claim: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  status: QueueItemStatus;
  retryCount: number;
  maxRetries: number;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  result?: VerificationResult;
  error?: string;
  metadata?: Record<string, unknown>;
}

export interface VerificationResult {
  verdict: string;
  confidence: number;
  explanation: string;
  sources: Array<{ name: string; url: string; reliability: number }>;
  providers: string[];
  processingTime: number;
}

// Sync status
export interface SyncStatus {
  isOnline: boolean;
  isSyncing: boolean;
  lastSyncTime?: string;
  pendingCount: number;
  failedCount: number;
  completedCount: number;
}

// API configuration
const API_URL = 'https://veritysystems-production.up.railway.app';

class OfflineQueueManager {
  private queue: OfflineQueueItem[] = [];
  private isOnline: boolean = true;
  private isSyncing: boolean = false;
  private syncInterval: NodeJS.Timeout | null = null;
  private networkUnsubscribe: (() => void) | null = null;
  private listeners: Set<(status: SyncStatus) => void> = new Set();

  /**
   * Initialize queue manager
   */
  async initialize(): Promise<void> {
    // Load persisted queue
    await this.loadQueue();
    
    // Monitor network status
    this.networkUnsubscribe = NetInfo.addEventListener(this.handleNetworkChange.bind(this));
    
    // Check initial network state
    const state = await NetInfo.fetch();
    this.isOnline = state.isConnected ?? false;
    
    // Start sync interval (every 30 seconds when online)
    this.startSyncInterval();
    
    // Process queue if online
    if (this.isOnline) {
      this.processQueue();
    }
  }

  /**
   * Handle network state changes
   */
  private handleNetworkChange(state: NetInfoState): void {
    const wasOnline = this.isOnline;
    this.isOnline = state.isConnected ?? false;
    
    if (!wasOnline && this.isOnline) {
      console.log('Network restored, processing queue...');
      this.processQueue();
      
      // Notify user
      const pending = this.getPendingCount();
      if (pending > 0) {
        showNotification({
          type: 'sync_complete',
          title: 'Back Online',
          body: `Syncing ${pending} pending verifications...`,
        });
      }
    }
    
    this.notifyListeners();
  }

  /**
   * Add item to queue
   */
  async addToQueue(
    claim: string,
    type: 'text' | 'image' | 'url' = 'text',
    priority: 'low' | 'normal' | 'high' | 'urgent' = 'normal',
    metadata?: Record<string, unknown>
  ): Promise<OfflineQueueItem> {
    const item: OfflineQueueItem = {
      id: this.generateId(),
      type,
      claim,
      priority,
      status: 'pending',
      retryCount: 0,
      maxRetries: 3,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      metadata,
    };
    
    // Add to queue (respect priority)
    this.insertByPriority(item);
    await this.saveQueue();
    
    // Try to process immediately if online
    if (this.isOnline && !this.isSyncing) {
      this.processQueue();
    }
    
    this.notifyListeners();
    return item;
  }

  /**
   * Insert item by priority
   */
  private insertByPriority(item: OfflineQueueItem): void {
    const priorityOrder = { urgent: 0, high: 1, normal: 2, low: 3 };
    const itemPriority = priorityOrder[item.priority];
    
    const insertIndex = this.queue.findIndex(
      (existing) => priorityOrder[existing.priority] > itemPriority
    );
    
    if (insertIndex === -1) {
      this.queue.push(item);
    } else {
      this.queue.splice(insertIndex, 0, item);
    }
  }

  /**
   * Process queue items
   */
  async processQueue(): Promise<void> {
    if (this.isSyncing || !this.isOnline) return;
    
    const pendingItems = this.queue.filter(
      (item) => item.status === 'pending' || item.status === 'retrying'
    );
    
    if (pendingItems.length === 0) return;
    
    this.isSyncing = true;
    this.notifyListeners();
    
    console.log(`Processing ${pendingItems.length} items...`);
    
    for (const item of pendingItems) {
      if (!this.isOnline) break;
      
      try {
        item.status = 'syncing';
        item.updatedAt = new Date().toISOString();
        this.notifyListeners();
        
        const result = await this.verifyItem(item);
        
        item.status = 'completed';
        item.result = result;
        item.completedAt = new Date().toISOString();
        item.updatedAt = new Date().toISOString();
        
      } catch (error) {
        item.retryCount++;
        item.error = error instanceof Error ? error.message : 'Unknown error';
        item.updatedAt = new Date().toISOString();
        
        if (item.retryCount >= item.maxRetries) {
          item.status = 'failed';
        } else {
          item.status = 'retrying';
        }
      }
      
      await this.saveQueue();
      this.notifyListeners();
    }
    
    this.isSyncing = false;
    
    // Show completion notification
    const completed = this.getCompletedCount();
    const failed = this.getFailedCount();
    
    if (completed > 0 || failed > 0) {
      showNotification({
        type: 'queue_update',
        title: 'Queue Processed',
        body: `${completed} completed, ${failed} failed`,
      });
    }
    
    this.notifyListeners();
  }

  /**
   * Verify a single item via API
   */
  private async verifyItem(item: OfflineQueueItem): Promise<VerificationResult> {
    const response = await fetch(`${API_URL}/api/v1/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        claim: item.claim,
        options: {
          include_sources: true,
          include_evidence: true,
          model: 'standard',
        },
      }),
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    return {
      verdict: data.verdict || 'unknown',
      confidence: data.confidence || 0,
      explanation: data.explanation || '',
      sources: data.sources || [],
      providers: data.providers || [],
      processingTime: data.processing_time || 0,
    };
  }

  /**
   * Retry failed items
   */
  async retryFailed(): Promise<void> {
    const failedItems = this.queue.filter((item) => item.status === 'failed');
    
    for (const item of failedItems) {
      item.status = 'retrying';
      item.retryCount = 0;
      item.error = undefined;
      item.updatedAt = new Date().toISOString();
    }
    
    await this.saveQueue();
    this.processQueue();
  }

  /**
   * Remove item from queue
   */
  async removeItem(id: string): Promise<boolean> {
    const index = this.queue.findIndex((item) => item.id === id);
    if (index === -1) return false;
    
    this.queue.splice(index, 1);
    await this.saveQueue();
    this.notifyListeners();
    
    return true;
  }

  /**
   * Clear completed items
   */
  async clearCompleted(): Promise<number> {
    const completedCount = this.queue.filter((item) => item.status === 'completed').length;
    this.queue = this.queue.filter((item) => item.status !== 'completed');
    await this.saveQueue();
    this.notifyListeners();
    return completedCount;
  }

  /**
   * Clear all items
   */
  async clearAll(): Promise<void> {
    this.queue = [];
    await this.saveQueue();
    this.notifyListeners();
  }

  /**
   * Get queue items
   */
  getQueue(): OfflineQueueItem[] {
    return [...this.queue];
  }

  /**
   * Get item by ID
   */
  getItem(id: string): OfflineQueueItem | undefined {
    return this.queue.find((item) => item.id === id);
  }

  /**
   * Get sync status
   */
  getSyncStatus(): SyncStatus {
    return {
      isOnline: this.isOnline,
      isSyncing: this.isSyncing,
      pendingCount: this.getPendingCount(),
      failedCount: this.getFailedCount(),
      completedCount: this.getCompletedCount(),
    };
  }

  /**
   * Get counts
   */
  getPendingCount(): number {
    return this.queue.filter(
      (item) => item.status === 'pending' || item.status === 'retrying'
    ).length;
  }

  getFailedCount(): number {
    return this.queue.filter((item) => item.status === 'failed').length;
  }

  getCompletedCount(): number {
    return this.queue.filter((item) => item.status === 'completed').length;
  }

  /**
   * Subscribe to status changes
   */
  subscribe(listener: (status: SyncStatus) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * Notify all listeners
   */
  private notifyListeners(): void {
    const status = this.getSyncStatus();
    this.listeners.forEach((listener) => listener(status));
  }

  /**
   * Start sync interval
   */
  private startSyncInterval(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
    
    // Process queue every 30 seconds
    this.syncInterval = setInterval(() => {
      if (this.isOnline && !this.isSyncing) {
        this.processQueue();
      }
    }, 30000);
  }

  /**
   * Load queue from storage
   */
  private async loadQueue(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem('verity_offline_queue');
      if (stored) {
        this.queue = JSON.parse(stored);
        console.log(`Loaded ${this.queue.length} items from queue`);
      }
    } catch (error) {
      console.error('Failed to load queue:', error);
    }
  }

  /**
   * Save queue to storage
   */
  private async saveQueue(): Promise<void> {
    try {
      await AsyncStorage.setItem('verity_offline_queue', JSON.stringify(this.queue));
    } catch (error) {
      console.error('Failed to save queue:', error);
    }
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Cleanup
   */
  cleanup(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
    if (this.networkUnsubscribe) {
      this.networkUnsubscribe();
    }
    this.listeners.clear();
  }
}

// Export singleton instance
export const offlineQueue = new OfflineQueueManager();

// Export convenience functions
export const initializeOfflineQueue = () => offlineQueue.initialize();
export const addToOfflineQueue = (
  claim: string,
  type?: 'text' | 'image' | 'url',
  priority?: 'low' | 'normal' | 'high' | 'urgent'
) => offlineQueue.addToQueue(claim, type, priority);
export const getQueueStatus = () => offlineQueue.getSyncStatus();
