/**
 * ContentService - Database-less content management
 * Handles content fetching, caching, and personalization
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { AnalyticsService } from './AnalyticsService';

interface ContentItem {
  id: string;
  summary: string;
  category: string;
  sentiment: string;
  relevance_score: number;
  engagement_score: number;
  chart_data?: any;
  key_points: string[];
  tickers: string[];
  original_url: string;
  subreddit: string;
  timestamp: number;
}

interface UserInteraction {
  content_id: string;
  direction: string;
  timestamp: number;
  category: string;
}

export class ContentService {
  private readonly API_BASE = 'https://api.redditinsight.app'; // Your serverless API
  private readonly CACHE_KEY = 'cached_content';
  private readonly INTERACTIONS_KEY = 'user_interactions';
  private readonly SAVED_CONTENT_KEY = 'saved_content';
  
  /**
   * Get personalized feed for user - Database-less approach
   */
  async getPersonalizedFeed(
    userId: string, 
    interests: string[], 
    subscriptionTier: 'FREE' | 'PRO' | 'PREMIUM',
    offset: number = 0
  ): Promise<ContentItem[]> {
    try {
      // Check network connectivity
      const networkState = await NetInfo.fetch();
      
      if (!networkState.isConnected) {
        // Return cached content when offline
        return await this.getCachedContent();
      }

      // Build API request
      const params = new URLSearchParams({
        user_id: userId,
        interests: interests.join(','),
        subscription_tier: subscriptionTier,
        offset: offset.toString(),
        limit: subscriptionTier === 'FREE' ? '20' : '50'
      });

      // Get user's interaction history for personalization
      const interactions = await this.getUserInteractions();
      
      const response = await fetch(`${this.API_BASE}/api/feed?${params}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recent_interactions: interactions.slice(-50), // Last 50 interactions
          timestamp: Date.now()
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      const content: ContentItem[] = data.feed || [];

      // Cache content locally for offline access
      if (offset === 0) { // Only cache initial load
        await this.cacheContent(content);
      }

      // Track content received
      AnalyticsService.trackEvent('content_received', {
        items_count: content.length,
        subscription_tier: subscriptionTier,
        is_refresh: offset === 0
      });

      return content;
    } catch (error) {
      console.error('Failed to fetch personalized feed:', error);
      
      // Fallback to cached content
      const cachedContent = await this.getCachedContent();
      if (cachedContent.length > 0) {
        return cachedContent;
      }
      
      // Last resort: mock data
      return this.getMockContent(interests);
    }
  }

  /**
   * Cache content locally for offline access
   */
  async cacheContent(content: ContentItem[]): Promise<void> {
    try {
      const cacheData = {
        content,
        timestamp: Date.now(),
        expires_at: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
      };
      
      await AsyncStorage.setItem(this.CACHE_KEY, JSON.stringify(cacheData));
    } catch (error) {
      console.error('Failed to cache content:', error);
    }
  }

  /**
   * Get cached content for offline access
   */
  async getCachedContent(): Promise<ContentItem[]> {
    try {
      const cached = await AsyncStorage.getItem(this.CACHE_KEY);
      if (!cached) return [];

      const cacheData = JSON.parse(cached);
      
      // Check if cache is still valid
      if (Date.now() > cacheData.expires_at) {
        await AsyncStorage.removeItem(this.CACHE_KEY);
        return [];
      }

      return cacheData.content || [];
    } catch (error) {
      console.error('Failed to get cached content:', error);
      return [];
    }
  }

  /**
   * Record user swipe for personalization (Database-less)
   */
  async recordSwipe(userId: string, contentId: string, direction: string): Promise<void> {
    try {
      // 1. Store interaction locally
      const interaction: UserInteraction = {
        content_id: contentId,
        direction: direction,
        timestamp: Date.now(),
        category: '' // Will be filled by the calling function
      };

      await this.storeInteractionLocally(interaction);

      // 2. Send to serverless API for real-time personalization
      const networkState = await NetInfo.fetch();
      if (networkState.isConnected) {
        fetch(`${this.API_BASE}/api/swipe`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: userId,
            content_id: contentId,
            direction: direction,
            timestamp: Date.now()
          })
        }).catch(error => {
          console.error('Failed to sync swipe to server:', error);
          // It's OK if this fails - we have local storage
        });
      }
    } catch (error) {
      console.error('Failed to record swipe:', error);
    }
  }

  /**
   * Store user interaction locally
   */
  private async storeInteractionLocally(interaction: UserInteraction): Promise<void> {
    try {
      const existingInteractions = await this.getUserInteractions();
      const updatedInteractions = [...existingInteractions, interaction];
      
      // Keep only last 1000 interactions to manage storage
      const trimmedInteractions = updatedInteractions.slice(-1000);
      
      await AsyncStorage.setItem(
        this.INTERACTIONS_KEY, 
        JSON.stringify(trimmedInteractions)
      );
    } catch (error) {
      console.error('Failed to store interaction locally:', error);
    }
  }

  /**
   * Get user interactions from local storage
   */
  async getUserInteractions(): Promise<UserInteraction[]> {
    try {
      const interactions = await AsyncStorage.getItem(this.INTERACTIONS_KEY);
      return interactions ? JSON.parse(interactions) : [];
    } catch (error) {
      console.error('Failed to get user interactions:', error);
      return [];
    }
  }

  /**
   * Save content for later (local storage)
   */
  async saveContent(contentId: string): Promise<void> {
    try {
      const savedContent = await this.getSavedContent();
      const updatedSaved = [...savedContent, contentId];
      
      await AsyncStorage.setItem(
        this.SAVED_CONTENT_KEY,
        JSON.stringify([...new Set(updatedSaved)]) // Remove duplicates
      );

      AnalyticsService.trackEvent('content_saved', {
        content_id: contentId
      });
    } catch (error) {
      console.error('Failed to save content:', error);
    }
  }

  /**
   * Get saved content IDs
   */
  async getSavedContent(): Promise<string[]> {
    try {
      const saved = await AsyncStorage.getItem(this.SAVED_CONTENT_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch (error) {
      console.error('Failed to get saved content:', error);
      return [];
    }
  }

  /**
   * Mark content as not interested (affects personalization)
   */
  async markNotInterested(contentId: string, category: string): Promise<void> {
    try {
      const interaction: UserInteraction = {
        content_id: contentId,
        direction: 'not_interested',
        timestamp: Date.now(),
        category: category
      };

      await this.storeInteractionLocally(interaction);

      AnalyticsService.trackEvent('content_not_interested', {
        content_id: contentId,
        category: category
      });
    } catch (error) {
      console.error('Failed to mark as not interested:', error);
    }
  }

  /**
   * Skip category temporarily (affects current session)
   */
  async skipCategory(category: string): Promise<void> {
    try {
      // Store category skip preference temporarily
      const skipKey = `skip_category_${category}`;
      const skipUntil = Date.now() + (2 * 60 * 60 * 1000); // Skip for 2 hours
      
      await AsyncStorage.setItem(skipKey, skipUntil.toString());

      AnalyticsService.trackEvent('category_skipped', {
        category: category,
        skip_duration: '2h'
      });
    } catch (error) {
      console.error('Failed to skip category:', error);
    }
  }

  /**
   * Check if category should be skipped
   */
  async shouldSkipCategory(category: string): Promise<boolean> {
    try {
      const skipKey = `skip_category_${category}`;
      const skipUntil = await AsyncStorage.getItem(skipKey);
      
      if (!skipUntil) return false;
      
      const skipUntilTime = parseInt(skipUntil);
      if (Date.now() > skipUntilTime) {
        // Skip period expired, remove the skip
        await AsyncStorage.removeItem(skipKey);
        return false;
      }
      
      return true;
    } catch (error) {
      console.error('Failed to check category skip:', error);
      return false;
    }
  }

  /**
   * Get mock content for development and fallback
   */
  private getMockContent(interests: string[]): ContentItem[] {
    const mockData: ContentItem[] = [
      {
        id: 'mock_1',
        summary: 'Tesla stock surges 15% after strong Q3 delivery numbers exceed analyst expectations.',
        category: 'Finance',
        sentiment: 'BULLISH',
        relevance_score: 92,
        engagement_score: 87,
        key_points: ['Strong Q3', 'Exceeded expectations', 'Stock surge'],
        tickers: ['TSLA'],
        original_url: 'https://reddit.com/r/stocks/example1',
        subreddit: 'stocks',
        timestamp: Date.now() - 3600000,
        chart_data: {
          title: 'TSLA Stock Movement',
          labels: ['6h', '4h', '2h', 'Now'],
          data: [100, 105, 110, 115]
        }
      },
      {
        id: 'mock_2',
        summary: 'OpenAI releases GPT-5 with multimodal capabilities and 10x performance improvement.',
        category: 'Technology',
        sentiment: 'POSITIVE',
        relevance_score: 89,
        engagement_score: 94,
        key_points: ['GPT-5 release', 'Multimodal', '10x faster'],
        tickers: [],
        original_url: 'https://reddit.com/r/technology/example2',
        subreddit: 'technology',
        timestamp: Date.now() - 7200000,
        chart_data: {
          title: 'AI Discussion Trend',
          labels: ['6h', '4h', '2h', 'Now'],
          data: [200, 450, 680, 900]
        }
      }
    ];

    // Filter by user interests
    return mockData.filter(item => 
      interests.some(interest => 
        item.category.toLowerCase().includes(interest.toLowerCase())
      )
    );
  }

  /**
   * Clear all cached data (for logout/reset)
   */
  async clearCache(): Promise<void> {
    try {
      await AsyncStorage.multiRemove([
        this.CACHE_KEY,
        this.INTERACTIONS_KEY,
        this.SAVED_CONTENT_KEY
      ]);
    } catch (error) {
      console.error('Failed to clear cache:', error);
    }
  }

  /**
   * Get usage statistics for subscription management
   */
  async getUsageStats(): Promise<{daily_insights: number, saved_items: number}> {
    try {
      const interactions = await this.getUserInteractions();
      const savedContent = await this.getSavedContent();
      
      // Count today's insights
      const todayStart = new Date().setHours(0, 0, 0, 0);
      const todayInsights = interactions.filter(
        interaction => interaction.timestamp >= todayStart
      ).length;

      return {
        daily_insights: todayInsights,
        saved_items: savedContent.length
      };
    } catch (error) {
      console.error('Failed to get usage stats:', error);
      return { daily_insights: 0, saved_items: 0 };
    }
  }
}