/**
 * FeedScreen - TikTok-style swipe interface for Reddit content
 */

import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  Dimensions,
  Animated,
  PanResponder,
  StyleSheet,
  Alert,
  RefreshControl,
  ScrollView
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { FirebaseAuthTypes } from '@react-native-firebase/auth';
import HapticFeedback from 'react-native-haptic-feedback';
import NetInfo from '@react-native-community/netinfo';

// Components
import ContentCard from '../components/ContentCard';
import SwipeIndicators from '../components/SwipeIndicators';
import SubscriptionPrompt from '../components/SubscriptionPrompt';

// Services
import { ContentService } from '../services/ContentService';
import { AnalyticsService } from '../services/AnalyticsService';
import { PreferencesManager } from '../services/PreferencesManager';

// Types
interface ContentItem {
  id: string;
  summary: string;
  category: string;
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL' | 'POSITIVE' | 'NEGATIVE';
  relevance_score: number;
  engagement_score: number;
  chart_data?: any;
  key_points: string[];
  tickers: string[];
  original_url: string;
  subreddit: string;
  timestamp: number;
}

interface Props {
  user: FirebaseAuthTypes.User;
  subscriptionTier: 'FREE' | 'PRO' | 'PREMIUM';
  navigation: any;
}

const { width, height } = Dimensions.get('window');
const SWIPE_THRESHOLD = 120;
const SWIPE_OUT_DURATION = 300;

const FeedScreen: React.FC<Props> = ({ user, subscriptionTier, navigation }) => {
  const [content, setContent] = useState<ContentItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [swipeDirection, setSwipeDirection] = useState<string | null>(null);
  const [dailyInsights, setDailyInsights] = useState(0);
  const [isConnected, setIsConnected] = useState(true);

  // Animation values
  const position = useRef(new Animated.ValueXY()).current;
  const rotate = useRef(new Animated.Value(0)).current;
  const opacity = useRef(new Animated.Value(1)).current;

  // Content service
  const contentService = useRef(new ContentService()).current;

  useEffect(() => {
    initializeFeed();
    setupNetworkListener();
  }, []);

  const setupNetworkListener = () => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsConnected(state.isConnected || false);
      if (state.isConnected && content.length === 0) {
        loadContent();
      }
    });

    return unsubscribe;
  };

  const initializeFeed = async () => {
    try {
      // Load cached content first (instant loading)
      const cachedContent = await contentService.getCachedContent();
      if (cachedContent.length > 0) {
        setContent(cachedContent);
        setIsLoading(false);
      }

      // Then load fresh content
      await loadContent();
    } catch (error) {
      console.error('Feed initialization error:', error);
      setIsLoading(false);
    }
  };

  const loadContent = async () => {
    try {
      const userPreferences = await PreferencesManager.loadPreferences();
      const newContent = await contentService.getPersonalizedFeed(
        user.uid,
        userPreferences.interests,
        subscriptionTier
      );

      setContent(newContent);
      setIsLoading(false);
      setIsRefreshing(false);

      // Track content loading
      AnalyticsService.trackEvent('content_loaded', {
        items_count: newContent.length,
        subscription_tier: subscriptionTier,
        user_interests: userPreferences.interests
      });
    } catch (error) {
      console.error('Content loading error:', error);
      setIsLoading(false);
      setIsRefreshing(false);
      
      if (!isConnected) {
        Alert.alert('Offline', 'Showing cached content. Connect to internet for fresh insights.');
      }
    }
  };

  const onRefresh = () => {
    setIsRefreshing(true);
    loadContent();
  };

  // Pan responder for swipe gestures
  const panResponder = PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onMoveShouldSetPanResponder: (_, gesture) => {
      return Math.abs(gesture.dx) > 5 || Math.abs(gesture.dy) > 5;
    },

    onPanResponderMove: (_, gesture) => {
      position.setValue({ x: gesture.dx, y: gesture.dy });

      // Update rotation based on horizontal movement
      const rotateValue = gesture.dx * 0.1;
      rotate.setValue(rotateValue);

      // Determine swipe direction for visual feedback
      const absX = Math.abs(gesture.dx);
      const absY = Math.abs(gesture.dy);

      if (absX > absY) {
        setSwipeDirection(gesture.dx > 0 ? 'right' : 'left');
      } else {
        setSwipeDirection(gesture.dy > 0 ? 'down' : 'up');
      }

      // Haptic feedback on strong swipe
      if (absX > SWIPE_THRESHOLD || absY > SWIPE_THRESHOLD) {
        HapticFeedback.trigger('impactLight');
      }
    },

    onPanResponderRelease: (_, gesture) => {
      const absX = Math.abs(gesture.dx);
      const absY = Math.abs(gesture.dy);

      if (absX > SWIPE_THRESHOLD || absY > SWIPE_THRESHOLD) {
        // Determine final swipe direction
        let direction: string;
        if (absX > absY) {
          direction = gesture.dx > 0 ? 'right' : 'left';
        } else {
          direction = gesture.dy > 0 ? 'down' : 'up';
        }

        handleSwipe(direction);
      } else {
        // Snap back to center
        resetPosition();
        setSwipeDirection(null);
      }
    }
  });

  const handleSwipe = async (direction: string) => {
    if (currentIndex >= content.length) return;

    const currentContent = content[currentIndex];
    
    // Check subscription limits
    if (subscriptionTier === 'FREE' && dailyInsights >= 20) {
      showSubscriptionPrompt();
      resetPosition();
      return;
    }

    // Animate card out
    const x = direction === 'left' ? -width : direction === 'right' ? width : 0;
    const y = direction === 'up' ? -height : direction === 'down' ? height : 0;

    Animated.parallel([
      Animated.timing(position, {
        toValue: { x, y },
        duration: SWIPE_OUT_DURATION,
        useNativeDriver: false
      }),
      Animated.timing(opacity, {
        toValue: 0,
        duration: SWIPE_OUT_DURATION,
        useNativeDriver: false
      })
    ]).start(() => {
      // Move to next content
      setCurrentIndex(prev => prev + 1);
      resetPosition();
      setSwipeDirection(null);
    });

    // Record user interaction
    await recordSwipe(currentContent.id, direction, currentContent.category);

    // Handle different swipe actions
    switch (direction) {
      case 'right':
        // Save content
        await contentService.saveContent(currentContent.id);
        HapticFeedback.trigger('notificationSuccess');
        break;
      case 'left':
        // Not interested
        await contentService.markNotInterested(currentContent.id, currentContent.category);
        HapticFeedback.trigger('impactMedium');
        break;
      case 'up':
        // Show details or open original
        showContentDetails(currentContent);
        break;
      case 'down':
        // Skip category
        await contentService.skipCategory(currentContent.category);
        HapticFeedback.trigger('impactLight');
        break;
    }

    // Update daily insights counter
    if (subscriptionTier === 'FREE') {
      setDailyInsights(prev => prev + 1);
    }

    // Preload more content if running low
    if (currentIndex >= content.length - 3) {
      loadMoreContent();
    }
  };

  const resetPosition = () => {
    position.setValue({ x: 0, y: 0 });
    rotate.setValue(0);
    opacity.setValue(1);
  };

  const recordSwipe = async (contentId: string, direction: string, category: string) => {
    try {
      // Record swipe for personalization
      await contentService.recordSwipe(user.uid, contentId, direction);

      // Track analytics
      AnalyticsService.trackEvent('content_swipe', {
        content_id: contentId,
        direction: direction,
        category: category,
        subscription_tier: subscriptionTier
      });
    } catch (error) {
      console.error('Failed to record swipe:', error);
    }
  };

  const showContentDetails = (contentItem: ContentItem) => {
    // Navigate to content details or open original URL
    AnalyticsService.trackEvent('content_details_viewed', {
      content_id: contentItem.id,
      category: contentItem.category
    });
    
    // For now, we'll just reset position - in full implementation, 
    // you'd navigate to a details screen
    resetPosition();
    setSwipeDirection(null);
  };

  const loadMoreContent = async () => {
    try {
      const userPreferences = await PreferencesManager.loadPreferences();
      const moreContent = await contentService.getPersonalizedFeed(
        user.uid,
        userPreferences.interests,
        subscriptionTier,
        content.length // offset
      );

      setContent(prev => [...prev, ...moreContent]);
    } catch (error) {
      console.error('Failed to load more content:', error);
    }
  };

  const showSubscriptionPrompt = () => {
    Alert.alert(
      'Daily Limit Reached',
      'You\'ve reached your daily limit of 20 insights. Upgrade to Pro for unlimited access!',
      [
        { text: 'Maybe Later', style: 'cancel' },
        { 
          text: 'Upgrade Now', 
          onPress: () => navigation.navigate('Subscription')
        }
      ]
    );
  };

  const renderCurrentCard = () => {
    if (currentIndex >= content.length) {
      return (
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateText}>You're all caught up!</Text>
          <Text style={styles.emptyStateSubtext}>Pull down to refresh for new content</Text>
        </View>
      );
    }

    const currentContent = content[currentIndex];
    const nextContent = content[currentIndex + 1];

    const animatedStyle = {
      transform: [
        { translateX: position.x },
        { translateY: position.y },
        { 
          rotate: rotate.interpolate({
            inputRange: [-200, 0, 200],
            outputRange: ['-15deg', '0deg', '15deg']
          })
        }
      ],
      opacity
    };

    return (
      <View style={styles.cardContainer}>
        {/* Next card (background) */}
        {nextContent && (
          <View style={[styles.card, styles.nextCard]}>
            <ContentCard content={nextContent} isBackground />
          </View>
        )}

        {/* Current card */}
        <Animated.View
          style={[styles.card, animatedStyle]}
          {...panResponder.panHandlers}
        >
          <ContentCard 
            content={currentContent} 
            subscriptionTier={subscriptionTier}
          />
          <SwipeIndicators direction={swipeDirection} />
        </Animated.View>
      </View>
    );
  };

  if (isLoading && content.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading your personalized feed...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Reddit Insight</Text>
        <View style={styles.headerRight}>
          {subscriptionTier === 'FREE' && (
            <Text style={styles.insightsCounter}>
              {dailyInsights}/20 today
            </Text>
          )}
          <Text 
            style={styles.profileButton}
            onPress={() => navigation.navigate('Profile')}
          >
            Profile
          </Text>
        </View>
      </View>

      {/* Content Feed */}
      <ScrollView
        style={styles.feedContainer}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={onRefresh}
            tintColor="#ffffff"
          />
        }
        scrollEnabled={false} // Disable scroll for swipe interface
      >
        {renderCurrentCard()}
      </ScrollView>

      {/* Subscription prompt for free users */}
      {subscriptionTier === 'FREE' && dailyInsights >= 15 && (
        <SubscriptionPrompt 
          onUpgrade={() => navigation.navigate('Subscription')}
          remainingInsights={20 - dailyInsights}
        />
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#667eea',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 15,
  },
  insightsCounter: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  profileButton: {
    fontSize: 16,
    color: '#ffffff',
    fontWeight: '500',
  },
  feedContainer: {
    flex: 1,
  },
  cardContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  card: {
    width: width - 40,
    height: height * 0.7,
    position: 'absolute',
  },
  nextCard: {
    opacity: 0.5,
    transform: [{ scale: 0.95 }],
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 18,
    color: '#ffffff',
    fontWeight: '500',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyStateText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 10,
    textAlign: 'center',
  },
  emptyStateSubtext: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
  },
});

export default FeedScreen;