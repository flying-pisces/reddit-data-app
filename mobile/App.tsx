/**
 * Reddit Insight Mobile App
 * TikTok-style content discovery with AI-powered insights
 */

import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar, Alert } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import auth, { FirebaseAuthTypes } from '@react-native-firebase/auth';
import { GoogleSignin } from '@react-native-google-signin/google-signin';
import Purchases from 'react-native-purchases';
import HapticFeedback from 'react-native-haptic-feedback';

// Screens
import AuthScreen from './src/screens/AuthScreen';
import OnboardingScreen from './src/screens/OnboardingScreen';
import FeedScreen from './src/screens/FeedScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import SubscriptionScreen from './src/screens/SubscriptionScreen';

// Services
import { PreferencesManager } from './src/services/PreferencesManager';
import { AnalyticsService } from './src/services/AnalyticsService';
import { NotificationService } from './src/services/NotificationService';

// Types
interface UserState {
  user: FirebaseAuthTypes.User | null;
  hasCompletedOnboarding: boolean;
  subscriptionTier: 'FREE' | 'PRO' | 'PREMIUM';
  isLoading: boolean;
}

const Stack = createStackNavigator();

const App: React.FC = () => {
  const [userState, setUserState] = useState<UserState>({
    user: null,
    hasCompletedOnboarding: false,
    subscriptionTier: 'FREE',
    isLoading: true
  });

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Configure Google Sign-In
      GoogleSignin.configure({
        webClientId: 'your-web-client-id.googleusercontent.com',
        offlineAccess: true,
      });

      // Configure RevenueCat for subscriptions
      Purchases.configure({
        apiKey: 'your-revenuecat-api-key',
      });

      // Initialize Firebase Auth listener
      const unsubscribe = auth().onAuthStateChanged(onAuthStateChanged);

      // Initialize services
      await NotificationService.initialize();
      AnalyticsService.initialize();

      return unsubscribe;
    } catch (error) {
      console.error('App initialization error:', error);
      setUserState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const onAuthStateChanged = async (user: FirebaseAuthTypes.User | null) => {
    try {
      if (user) {
        // User is signed in
        const preferences = await PreferencesManager.loadPreferences();
        const hasCompletedOnboarding = preferences.onboarding_completed || false;
        
        // Check subscription status
        const purchaserInfo = await Purchases.getPurchaserInfo();
        const subscriptionTier = getSubscriptionTier(purchaserInfo);
        
        // Track user login
        AnalyticsService.trackEvent('user_login', {
          method: user.providerData[0]?.providerId || 'unknown',
          subscription_tier: subscriptionTier
        });

        setUserState({
          user,
          hasCompletedOnboarding,
          subscriptionTier,
          isLoading: false
        });
      } else {
        // User is signed out
        setUserState({
          user: null,
          hasCompletedOnboarding: false,
          subscriptionTier: 'FREE',
          isLoading: false
        });
      }
    } catch (error) {
      console.error('Auth state change error:', error);
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
      // Save preferences
      await PreferencesManager.savePreferences({
        ...preferences,
        onboarding_completed: true
      });

      // Track onboarding completion
      AnalyticsService.trackEvent('onboarding_completed', {
        interests: preferences.interests,
        total_subreddits: preferences.subreddits?.length || 0
      });

      // Haptic feedback
      HapticFeedback.trigger('notificationSuccess');

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
      const productId = tier === 'PRO' ? 'pro_monthly' : 'premium_monthly';
      const purchaserInfo = await Purchases.purchaseProduct(productId);
      
      // Update subscription state
      const newTier = getSubscriptionTier(purchaserInfo);
      setUserState(prev => ({ ...prev, subscriptionTier: newTier }));

      // Track subscription
      AnalyticsService.trackEvent('subscription_purchased', {
        tier: newTier,
        product_id: productId
      });

      // Haptic feedback
      HapticFeedback.trigger('notificationSuccess');

      Alert.alert('Welcome to ' + tier + '!', 'You now have access to premium features.');
    } catch (error) {
      console.error('Subscription error:', error);
      Alert.alert('Purchase Failed', 'Please try again later.');
    }
  };

  if (userState.isLoading) {
    // Show loading screen
    return null; // You can add a proper loading component here
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
          {!userState.user ? (
            // Authentication flow
            <Stack.Screen name="Auth" component={AuthScreen} />
          ) : !userState.hasCompletedOnboarding ? (
            // Onboarding flow
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
                    user={userState.user}
                    subscriptionTier={userState.subscriptionTier}
                  />
                )}
              </Stack.Screen>
              <Stack.Screen name="Profile">
                {props => (
                  <ProfileScreen
                    {...props}
                    user={userState.user}
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