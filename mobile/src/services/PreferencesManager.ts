import AsyncStorage from '@react-native-async-storage/async-storage';

export interface UserPreferences {
  interests: string[];
  subreddits: string[];
  notifications_enabled: boolean;
  onboarding_completed: boolean;
  onboarding_completed_at?: number;
}

const PREFERENCES_KEY = 'user_preferences';

export class PreferencesManager {
  static async loadPreferences(): Promise<Partial<UserPreferences>> {
    try {
      const stored = await AsyncStorage.getItem(PREFERENCES_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
      return {};
    } catch (error) {
      console.error('Failed to load preferences:', error);
      return {};
    }
  }

  static async savePreferences(preferences: Partial<UserPreferences>): Promise<void> {
    try {
      const existing = await this.loadPreferences();
      const updated = { ...existing, ...preferences };
      await AsyncStorage.setItem(PREFERENCES_KEY, JSON.stringify(updated));
    } catch (error) {
      console.error('Failed to save preferences:', error);
      throw error;
    }
  }

  static async clearPreferences(): Promise<void> {
    try {
      await AsyncStorage.removeItem(PREFERENCES_KEY);
    } catch (error) {
      console.error('Failed to clear preferences:', error);
      throw error;
    }
  }

  static async updateInterests(interests: string[]): Promise<void> {
    await this.savePreferences({ interests });
  }

  static async updateSubreddits(subreddits: string[]): Promise<void> {
    await this.savePreferences({ subreddits });
  }

  static async setNotificationsEnabled(enabled: boolean): Promise<void> {
    await this.savePreferences({ notifications_enabled: enabled });
  }
}