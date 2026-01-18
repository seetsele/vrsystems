/**
 * Verity Mobile - Push Notification Utility
 * Handles local and push notifications for verification updates
 */

import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configure notification handling
Notifications.setNotificationHandler({
  handleNotification: async (notification: Notifications.Notification) => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

// Notification types
export type NotificationType = 
  | 'verification_complete'
  | 'queue_update'
  | 'sync_complete'
  | 'daily_digest'
  | 'trending_claim'
  | 'system_alert';

export interface NotificationPayload {
  type: NotificationType;
  title: string;
  body: string;
  data?: Record<string, unknown>;
}

// Notification settings
interface NotificationSettings {
  enabled: boolean;
  verificationAlerts: boolean;
  queueUpdates: boolean;
  dailyDigest: boolean;
  trendingClaims: boolean;
  quietHoursStart?: number; // 0-23
  quietHoursEnd?: number;   // 0-23
}

const DEFAULT_SETTINGS: NotificationSettings = {
  enabled: true,
  verificationAlerts: true,
  queueUpdates: true,
  dailyDigest: false,
  trendingClaims: true,
};

class NotificationService {
  private expoPushToken: string | null = null;
  private settings: NotificationSettings = DEFAULT_SETTINGS;
  private notificationListener: Notifications.Subscription | null = null;
  private responseListener: Notifications.Subscription | null = null;

  /**
   * Initialize notification service
   */
  async initialize(): Promise<void> {
    await this.loadSettings();
    
    // Register for push notifications
    this.expoPushToken = await this.registerForPushNotifications();
    
    // Set up notification listeners
    this.setupListeners();
  }

  /**
   * Register for push notifications
   */
  async registerForPushNotifications(): Promise<string | null> {
    if (!Device.isDevice) {
      console.debug('Push notifications only work on physical devices');
      return null;
    }

    try {
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.debug('Notification permission not granted');
        return null;
      }

      // Get push token
      const projectId = Constants.expoConfig?.extra?.eas?.projectId;
      const token = await Notifications.getExpoPushTokenAsync({
        projectId: projectId || undefined,
      });

      // Save token for server-side push
      await this.savePushToken(token.data);
      
      // Android-specific channel setup
      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('verification', {
          name: 'Verification Alerts',
          importance: Notifications.AndroidImportance.HIGH,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#4F46E5',
        });
        
        await Notifications.setNotificationChannelAsync('queue', {
          name: 'Queue Updates',
          importance: Notifications.AndroidImportance.DEFAULT,
        });
        
        await Notifications.setNotificationChannelAsync('digest', {
          name: 'Daily Digest',
          importance: Notifications.AndroidImportance.LOW,
        });
      }

      return token.data;
    } catch (error) {
      console.error('Failed to register for push notifications:', error);
      return null;
    }
  }

  /**
   * Set up notification listeners
   */
  private setupListeners(): void {
    // Handle received notifications
    this.notificationListener = Notifications.addNotificationReceivedListener(
      (notification: Notifications.Notification) => {
        console.debug('Notification received:', notification);
        this.handleNotification(notification);
      }
    );

    // Handle notification taps
    this.responseListener = Notifications.addNotificationResponseReceivedListener(
      (response: Notifications.NotificationResponse) => {
        console.debug('Notification tapped:', response);
        this.handleNotificationTap(response);
      }
    );
  }

  /**
   * Handle incoming notification
   */
  private handleNotification(notification: Notifications.Notification): void {
    const data = notification.request.content.data as unknown as NotificationPayload;
    
    // Custom handling based on type
    switch (data?.type) {
      case 'verification_complete':
        // Could update app state here
        break;
      case 'queue_update':
        // Refresh queue
        break;
      case 'sync_complete':
        // Update sync status
        break;
    }
  }

  /**
   * Handle notification tap
   */
  private handleNotificationTap(response: Notifications.NotificationResponse): void {
    const data = response.notification.request.content.data as unknown as NotificationPayload;
    
    // Navigate based on notification type
    // This would typically use navigation ref
    console.debug('Navigate to:', data?.type);
  }

  /**
   * Show local notification
   */
  async showNotification(payload: NotificationPayload): Promise<string | null> {
    // Check if notifications are enabled
    if (!this.settings.enabled) return null;
    
    // Check quiet hours
    if (this.isQuietHours()) return null;
    
    // Check type-specific settings
    if (!this.shouldShowNotificationType(payload.type)) return null;

    try {
      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title: payload.title,
          body: payload.body,
          data: { ...payload.data, type: payload.type },
          sound: true,
        },
        trigger: null, // Immediate
      });
      
      return notificationId;
    } catch (error) {
      console.error('Failed to show notification:', error);
      return null;
    }
  }

  /**
   * Show verification complete notification
   */
  async showVerificationComplete(claim: string, verdict: string, confidence: number): Promise<void> {
    const verdictEmoji = this.getVerdictEmoji(verdict);
    
    await this.showNotification({
      type: 'verification_complete',
      title: `${verdictEmoji} Verification Complete`,
      body: `"${claim.substring(0, 50)}..." is ${verdict.toUpperCase()} (${confidence}% confidence)`,
      data: { claim, verdict, confidence },
    });
  }

  /**
   * Show queue update notification
   */
  async showQueueUpdate(count: number, completed: number): Promise<void> {
    await this.showNotification({
      type: 'queue_update',
      title: 'Queue Updated',
      body: `${completed} verifications completed. ${count - completed} remaining.`,
      data: { count, completed },
    });
  }

  /**
   * Show sync complete notification
   */
  async showSyncComplete(itemsSynced: number): Promise<void> {
    await this.showNotification({
      type: 'sync_complete',
      title: 'Sync Complete',
      body: `${itemsSynced} items synced with Verity Cloud.`,
      data: { itemsSynced },
    });
  }

  /**
   * Schedule daily digest notification
   */
  async scheduleDailyDigest(hour: number = 9): Promise<void> {
    if (!this.settings.dailyDigest) return;

    await Notifications.cancelScheduledNotificationAsync('daily-digest');
    
    await Notifications.scheduleNotificationAsync({
      identifier: 'daily-digest',
      content: {
        title: '📊 Your Daily Verity Digest',
        body: 'Check your verification stats and trending claims.',
        data: { type: 'daily_digest' },
      },
      trigger: {
        type: Notifications.SchedulableTriggerInputTypes.CALENDAR,
        hour,
        minute: 0,
        repeats: true,
      },
    });
  }

  /**
   * Get emoji for verdict
   */
  private getVerdictEmoji(verdict: string): string {
    const emojis: Record<string, string> = {
      'true': '✅',
      'mostly_true': '🟢',
      'mixed': '🟡',
      'mostly_false': '🟠',
      'false': '❌',
      'unverifiable': '❓',
    };
    return emojis[verdict] || '🔍';
  }

  /**
   * Check if currently in quiet hours
   */
  private isQuietHours(): boolean {
    if (!this.settings.quietHoursStart || !this.settings.quietHoursEnd) {
      return false;
    }

    const now = new Date().getHours();
    const start = this.settings.quietHoursStart;
    const end = this.settings.quietHoursEnd;

    if (start < end) {
      return now >= start && now < end;
    } else {
      // Quiet hours span midnight
      return now >= start || now < end;
    }
  }

  /**
   * Check if should show notification type
   */
  private shouldShowNotificationType(type: NotificationType): boolean {
    switch (type) {
      case 'verification_complete':
        return this.settings.verificationAlerts;
      case 'queue_update':
        return this.settings.queueUpdates;
      case 'daily_digest':
        return this.settings.dailyDigest;
      case 'trending_claim':
        return this.settings.trendingClaims;
      default:
        return true;
    }
  }

  /**
   * Save push token to server
   */
  private async savePushToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem('verity_push_token', token);
      // Would also send to server here for push notifications
    } catch (error) {
      console.error('Failed to save push token:', error);
    }
  }

  /**
   * Load notification settings
   */
  private async loadSettings(): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem('verity_notification_settings');
      if (stored) {
        this.settings = { ...DEFAULT_SETTINGS, ...JSON.parse(stored) };
      }
    } catch (error) {
      console.error('Failed to load notification settings:', error);
    }
  }

  /**
   * Save notification settings
   */
  async saveSettings(settings: Partial<NotificationSettings>): Promise<void> {
    this.settings = { ...this.settings, ...settings };
    try {
      await AsyncStorage.setItem('verity_notification_settings', JSON.stringify(this.settings));
    } catch (error) {
      console.error('Failed to save notification settings:', error);
    }
  }

  /**
   * Get current settings
   */
  getSettings(): NotificationSettings {
    return { ...this.settings };
  }

  /**
   * Get push token
   */
  getPushToken(): string | null {
    return this.expoPushToken;
  }

  /**
   * Clear all notifications
   */
  async clearAll(): Promise<void> {
    await Notifications.dismissAllNotificationsAsync();
    await Notifications.setBadgeCountAsync(0);
  }

  /**
   * Cleanup listeners
   */
  cleanup(): void {
    if (this.notificationListener && typeof this.notificationListener.remove === 'function') {
      this.notificationListener.remove();
    }
    if (this.responseListener && typeof this.responseListener.remove === 'function') {
      this.responseListener.remove();
    }
  }
}

// Export singleton instance
export const notificationService = new NotificationService();

// Export convenience functions
export const initializeNotifications = () => notificationService.initialize();
export const showNotification = (payload: NotificationPayload) => notificationService.showNotification(payload);
export const showVerificationComplete = (claim: string, verdict: string, confidence: number) => 
  notificationService.showVerificationComplete(claim, verdict, confidence);
export const showQueueUpdate = (count: number, completed: number) => 
  notificationService.showQueueUpdate(count, completed);
