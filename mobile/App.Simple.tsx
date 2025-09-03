/**
 * Reddit Insight Mobile App - Ultra Lean Version
 * No Firebase, No Database, Maximum Simplicity
 */

import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar, Alert } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import Purchases from 'react-native-purchases';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Screens
import AuthScreen from './src/screens/AuthScreen';
import OnboardingScreen from './src/screens/OnboardingScreen';
import FeedScreen from './src/screens/FeedScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import SubscriptionScreen from './src/screens/SubscriptionScreen';

// Services
import { PreferencesManager } from './src/services/PreferencesManager';
import { AnalyticsService } from './src/services/AnalyticsService';

// Simplified user state (no Firebase)
interface UserState {
  hasCompletedOnboarding: boolean;
  subscriptionTier: 'FREE' | 'PRO' | 'PREMIUM';
  isLoading: boolean;
  anonymousId: string; // Simple anonymous identifier
}

const Stack = createStackNavigator();

const App: React.FC = () => {
  const [userState, setUserState] = useState<UserState>({
    hasCompletedOnboarding: false,
    subscriptionTier: 'FREE',
    isLoading: true,
    anonymousId: '',
  });

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Generate or load anonymous user ID
      let anonymousId = await AsyncStorage.getItem('anonymous_user_id');
      if (!anonymousId) {
        anonymousId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        await AsyncStorage.setItem('anonymous_user_id', anonymousId);
      }

      // Configure RevenueCat for subscriptions (only required API key)
      Purchases.configure({
        apiKey: 'your-revenuecat-api-key', // Replace with actual key
      });

      // Check subscription status
      const purchaserInfo = await Purchases.getPurchaserInfo();
      const subscriptionTier = getSubscriptionTier(purchaserInfo);

      // Load user preferences
      const preferences = await PreferencesManager.loadPreferences();
      const hasCompletedOnboarding = preferences.onboarding_completed || false;

      // Initialize analytics (local only)
      AnalyticsService.initialize();

      setUserState({
        hasCompletedOnboarding,
        subscriptionTier,
        isLoading: false,
        anonymousId,
      });

    } catch (error) {
      console.error('App initialization error:', error);
      setUserState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const getSubscriptionTier = (purchaserInfo: any): 'FREE' | 'PRO' | 'PREMIUM' => {
    if (purchaserInfo.entitlements.active['premium']) return 'PREMIUM';
    if (purchaserInfo.entitlements.active['pro']) return 'PRO';
    return 'FREE';
  };

  const handleOnboardingComplete = async (preferences: any) => {
    try {
      // Save preferences locally (no backend)
      await PreferencesManager.savePreferences({
        ...preferences,
        onboarding_completed: true
      });

      // Track onboarding completion locally
      AnalyticsService.trackEvent('onboarding_completed', {
        interests: preferences.interests,
        total_subreddits: preferences.subreddits?.length || 0,
        anonymous_id: userState.anonymousId,
      });

      setUserState(prev => ({
        ...prev,
        hasCompletedOnboarding: true
      }));

    } catch (error) {
      console.error('Onboarding completion error:', error);
      Alert.alert('Error', 'Failed to save preferences. Please try again.');
    }
  };

  const handleSubscriptionUpgrade = async (tier: 'PRO' | 'PREMIUM') => {
    try {
      const productId = tier === 'PRO' ? 'reddit_insight_pro_monthly' : 'reddit_insight_premium_monthly';
      const purchaserInfo = await Purchases.purchaseProduct(productId);
      
      // Update subscription state
      const newTier = getSubscriptionTier(purchaserInfo);
      setUserState(prev => ({ ...prev, subscriptionTier: newTier }));

      // Track subscription locally
      AnalyticsService.trackEvent('subscription_purchased', {
        tier: newTier,
        product_id: productId,
        anonymous_id: userState.anonymousId,
      });

      Alert.alert('Welcome to ' + tier + '!', 'You now have access to premium features.');
      
    } catch (error) {
      console.error('Subscription error:', error);
      Alert.alert('Purchase Failed', 'Please try again later.');
    }
  };

  if (userState.isLoading) {
    // Show loading screen - you can add a proper loading component here
    return null; 
  }

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <StatusBar barStyle="light-content" backgroundColor="#667eea" />
      <NavigationContainer>
        <Stack.Navigator
          screenOptions={{
            headerShown: false,
            gestureEnabled: true,
            animationEnabled: true
          }}
        >
          {!userState.hasCompletedOnboarding ? (
            // Skip auth, go straight to onboarding
            <Stack.Screen name="Onboarding">
              {props => (
                <OnboardingScreen
                  {...props}
                  onComplete={handleOnboardingComplete}
                />
              )}
            </Stack.Screen>
          ) : (
            // Main app flow
            <>
              <Stack.Screen name="Feed">
                {props => (
                  <FeedScreen
                    {...props}
                    anonymousId={userState.anonymousId}
                    subscriptionTier={userState.subscriptionTier}
                  />
                )}
              </Stack.Screen>
              <Stack.Screen name="Profile">
                {props => (
                  <ProfileScreen
                    {...props}
                    anonymousId={userState.anonymousId}
                    subscriptionTier={userState.subscriptionTier}
                  />
                )}
              </Stack.Screen>
              <Stack.Screen name="Subscription">
                {props => (
                  <SubscriptionScreen
                    {...props}
                    currentTier={userState.subscriptionTier}
                    onUpgrade={handleSubscriptionUpgrade}
                  />
                )}
              </Stack.Screen>
            </>
          )}
        </Stack.Navigator>
      </NavigationContainer>
    </GestureHandlerRootView>
  );
};

export default App;