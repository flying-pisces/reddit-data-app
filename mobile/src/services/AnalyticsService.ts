export interface AnalyticsEvent {
  event_name: string;
  properties: Record<string, any>;
  timestamp?: number;
}

export class AnalyticsService {
  private static isInitialized = false;

  static initialize() {
    if (this.isInitialized) return;
    
    console.log('📊 Analytics Service initialized');
    this.isInitialized = true;
  }

  static trackEvent(eventName: string, properties: Record<string, any> = {}) {
    if (!this.isInitialized) {
      console.warn('Analytics not initialized, skipping event:', eventName);
      return;
    }

    const event: AnalyticsEvent = {
      event_name: eventName,
      properties: {
        ...properties,
        platform: 'mobile',
        app_version: '1.0.0',
      },
      timestamp: Date.now(),
    };

    // In a real app, you would send this to your analytics service
    // For now, we'll just log it
    console.log('📊 Analytics Event:', event);

    // Example integrations you might add:
    // - Firebase Analytics
    // - Mixpanel
    // - Amplitude
    // - Custom backend analytics
  }

  static trackScreenView(screenName: string, properties: Record<string, any> = {}) {
    this.trackEvent('screen_view', {
      screen_name: screenName,
      ...properties,
    });
  }

  static trackUserAction(action: string, properties: Record<string, any> = {}) {
    this.trackEvent('user_action', {
      action,
      ...properties,
    });
  }

  static trackContentInteraction(type: 'swipe' | 'tap' | 'save' | 'share', properties: Record<string, any> = {}) {
    this.trackEvent('content_interaction', {
      interaction_type: type,
      ...properties,
    });
  }

  static trackSubscriptionEvent(event: 'upgrade_prompt' | 'purchase_started' | 'purchase_completed' | 'purchase_failed', properties: Record<string, any> = {}) {
    this.trackEvent('subscription_event', {
      subscription_event: event,
      ...properties,
    });
  }

  static setUserProperties(properties: Record<string, any>) {
    console.log('📊 User Properties Updated:', properties);
    // In a real app, you would update user properties in your analytics service
  }

  static identifyUser(userId: string, properties: Record<string, any> = {}) {
    console.log('📊 User Identified:', userId, properties);
    // In a real app, you would identify the user in your analytics service
  }
}