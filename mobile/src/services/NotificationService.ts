import { Alert } from 'react-native';

export interface NotificationPermissions {
  granted: boolean;
  canRequest: boolean;
}

export class NotificationService {
  private static isInitialized = false;

  static async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      console.log('🔔 Notification Service initialized');
      this.isInitialized = true;
    } catch (error) {
      console.error('Failed to initialize notifications:', error);
    }
  }

  static async requestPermissions(): Promise<NotificationPermissions> {
    try {
      // In a real app, you would use @react-native-firebase/messaging
      // or expo-notifications to request permissions
      console.log('🔔 Requesting notification permissions');
      
      // For demo purposes, simulate permission granted
      return {
        granted: true,
        canRequest: true,
      };
    } catch (error) {
      console.error('Failed to request notification permissions:', error);
      return {
        granted: false,
        canRequest: false,
      };
    }
  }

  static async getPermissionStatus(): Promise<NotificationPermissions> {
    try {
      // Check current permission status
      // This would typically use the native notification APIs
      return {
        granted: true, // Simulate granted for demo
        canRequest: true,
      };
    } catch (error) {
      console.error('Failed to get permission status:', error);
      return {
        granted: false,
        canRequest: true,
      };
    }
  }

  static async scheduleNotification(title: string, body: string, data?: Record<string, any>) {
    try {
      console.log('🔔 Scheduling notification:', { title, body, data });
      
      // In a real app, you would schedule the notification
      // For demo purposes, show an alert
      setTimeout(() => {
        Alert.alert(title, body);
      }, 2000);
    } catch (error) {
      console.error('Failed to schedule notification:', error);
    }
  }

  static async cancelAllNotifications() {
    try {
      console.log('🔔 Cancelling all notifications');
      // Cancel all scheduled notifications
    } catch (error) {
      console.error('Failed to cancel notifications:', error);
    }
  }

  static async sendInsightNotification(insight: {
    title: string;
    summary: string;
    category: string;
    sentiment: string;
  }) {
    await this.scheduleNotification(
      `🚀 New ${insight.category} Insight`,
      insight.summary,
      {
        type: 'insight',
        category: insight.category,
        sentiment: insight.sentiment,
      }
    );
  }

  static async sendTrendingNotification(stock: string, trend: 'up' | 'down') {
    const emoji = trend === 'up' ? '📈' : '📉';
    const direction = trend === 'up' ? 'rising' : 'falling';
    
    await this.scheduleNotification(
      `${emoji} ${stock} Trending`,
      `${stock} is ${direction} in Reddit discussions`,
      {
        type: 'trending',
        stock,
        trend,
      }
    );
  }

  static async sendDailyDigest(insightCount: number) {
    await this.scheduleNotification(
      '📊 Your Daily Reddit Insight Digest',
      `${insightCount} new insights available for you to explore`,
      {
        type: 'daily_digest',
        insight_count: insightCount,
      }
    );
  }
}