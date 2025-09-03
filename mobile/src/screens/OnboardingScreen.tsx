import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const { width } = Dimensions.get('window');

interface OnboardingScreenProps {
  navigation: any;
  onComplete: (preferences: any) => void;
}

const INTERESTS = [
  { id: 'finance', name: 'Finance & Investing', emoji: '💰' },
  { id: 'technology', name: 'Technology', emoji: '💻' },
  { id: 'crypto', name: 'Cryptocurrency', emoji: '₿' },
  { id: 'stocks', name: 'Stock Market', emoji: '📈' },
  { id: 'startups', name: 'Startups', emoji: '🚀' },
  { id: 'trading', name: 'Day Trading', emoji: '📊' },
  { id: 'economics', name: 'Economics', emoji: '🏦' },
  { id: 'business', name: 'Business News', emoji: '💼' },
];

const POPULAR_SUBREDDITS = [
  'wallstreetbets',
  'stocks',
  'investing',
  'cryptocurrency',
  'Bitcoin',
  'ethereum',
  'SecurityAnalysis',
  'ValueInvesting',
  'pennystocks',
  'options',
  'StockMarket',
  'financialindependence',
  'personalfinance',
  'technology',
  'startups',
  'entrepreneur',
];

const OnboardingScreen: React.FC<OnboardingScreenProps> = ({ navigation, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [selectedSubreddits, setSelectedSubreddits] = useState<string[]>([]);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  const steps = [
    'Welcome',
    'Select Interests',
    'Choose Subreddits',
    'Notifications',
    'Complete',
  ];

  const toggleInterest = (interestId: string) => {
    setSelectedInterests(prev => 
      prev.includes(interestId) 
        ? prev.filter(id => id !== interestId)
        : [...prev, interestId]
    );
  };

  const toggleSubreddit = (subreddit: string) => {
    setSelectedSubreddits(prev => 
      prev.includes(subreddit) 
        ? prev.filter(sub => sub !== subreddit)
        : [...prev, subreddit]
    );
  };

  const handleNext = () => {
    if (currentStep === 1 && selectedInterests.length === 0) {
      Alert.alert('Select Interests', 'Please select at least one interest to continue');
      return;
    }
    
    if (currentStep === 2 && selectedSubreddits.length === 0) {
      Alert.alert('Choose Subreddits', 'Please select at least one subreddit to continue');
      return;
    }

    if (currentStep === steps.length - 1) {
      handleComplete();
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handleComplete = () => {
    const preferences = {
      interests: selectedInterests,
      subreddits: selectedSubreddits,
      notifications_enabled: notificationsEnabled,
      onboarding_completed_at: Date.now(),
    };

    onComplete(preferences);
  };

  const renderWelcome = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.welcomeTitle}>Welcome to Reddit Insight!</Text>
      <Text style={styles.welcomeSubtitle}>
        Get AI-powered insights from Reddit's financial communities in a TikTok-style feed
      </Text>
      
      <View style={styles.featuresList}>
        <Text style={styles.featureItem}>📱 Swipe through bite-sized insights</Text>
        <Text style={styles.featureItem}>🤖 AI-powered summaries</Text>
        <Text style={styles.featureItem}>📈 Real-time market sentiment</Text>
        <Text style={styles.featureItem}>🎯 Personalized content</Text>
      </View>
    </View>
  );

  const renderInterests = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>What interests you?</Text>
      <Text style={styles.stepSubtitle}>Select your areas of interest to personalize your feed</Text>
      
      <View style={styles.interestsGrid}>
        {INTERESTS.map(interest => (
          <TouchableOpacity
            key={interest.id}
            style={[
              styles.interestCard,
              selectedInterests.includes(interest.id) && styles.selectedInterestCard
            ]}
            onPress={() => toggleInterest(interest.id)}
          >
            <Text style={styles.interestEmoji}>{interest.emoji}</Text>
            <Text style={[
              styles.interestName,
              selectedInterests.includes(interest.id) && styles.selectedInterestName
            ]}>
              {interest.name}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const renderSubreddits = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Choose Subreddits</Text>
      <Text style={styles.stepSubtitle}>Select communities you want insights from</Text>
      
      <ScrollView style={styles.subredditsContainer} showsVerticalScrollIndicator={false}>
        {POPULAR_SUBREDDITS.map(subreddit => (
          <TouchableOpacity
            key={subreddit}
            style={[
              styles.subredditItem,
              selectedSubreddits.includes(subreddit) && styles.selectedSubredditItem
            ]}
            onPress={() => toggleSubreddit(subreddit)}
          >
            <Text style={styles.subredditPrefix}>r/</Text>
            <Text style={[
              styles.subredditName,
              selectedSubreddits.includes(subreddit) && styles.selectedSubredditName
            ]}>
              {subreddit}
            </Text>
            {selectedSubreddits.includes(subreddit) && (
              <Text style={styles.checkmark}>✓</Text>
            )}
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );

  const renderNotifications = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Stay Updated</Text>
      <Text style={styles.stepSubtitle}>Get notifications for trending insights</Text>
      
      <View style={styles.notificationOptions}>
        <TouchableOpacity
          style={[
            styles.notificationOption,
            notificationsEnabled && styles.selectedNotificationOption
          ]}
          onPress={() => setNotificationsEnabled(true)}
        >
          <Text style={styles.notificationEmoji}>🔔</Text>
          <Text style={styles.notificationTitle}>Enable Notifications</Text>
          <Text style={styles.notificationDescription}>
            Get alerts for breaking market insights and trending discussions
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[
            styles.notificationOption,
            !notificationsEnabled && styles.selectedNotificationOption
          ]}
          onPress={() => setNotificationsEnabled(false)}
        >
          <Text style={styles.notificationEmoji}>🔕</Text>
          <Text style={styles.notificationTitle}>Skip for Now</Text>
          <Text style={styles.notificationDescription}>
            You can enable notifications later in settings
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return renderWelcome();
      case 1:
        return renderInterests();
      case 2:
        return renderSubreddits();
      case 3:
        return renderNotifications();
      default:
        return renderWelcome();
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Progress Bar */}
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View style={[
            styles.progressFill,
            { width: `${((currentStep + 1) / steps.length) * 100}%` }
          ]} />
        </View>
        <Text style={styles.progressText}>
          {currentStep + 1} of {steps.length}
        </Text>
      </View>

      {/* Content */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {renderStep()}
      </ScrollView>

      {/* Bottom Navigation */}
      <View style={styles.bottomContainer}>
        {currentStep > 0 && (
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => setCurrentStep(prev => prev - 1)}
          >
            <Text style={styles.backButtonText}>Back</Text>
          </TouchableOpacity>
        )}
        
        <TouchableOpacity
          style={styles.nextButton}
          onPress={handleNext}
        >
          <Text style={styles.nextButtonText}>
            {currentStep === steps.length - 1 ? 'Get Started' : 'Next'}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#667eea',
  },
  progressContainer: {
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  progressBar: {
    height: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 2,
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 2,
  },
  progressText: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 12,
    textAlign: 'center',
  },
  content: {
    flex: 1,
  },
  stepContainer: {
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  welcomeTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 12,
  },
  welcomeSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  featuresList: {
    marginTop: 20,
  },
  featureItem: {
    fontSize: 16,
    color: '#ffffff',
    marginBottom: 12,
    paddingLeft: 8,
  },
  stepTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 8,
  },
  stepSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    marginBottom: 24,
  },
  interestsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  interestCard: {
    width: (width - 50) / 2,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedInterestCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderColor: '#ffffff',
  },
  interestEmoji: {
    fontSize: 24,
    marginBottom: 8,
  },
  interestName: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
  },
  selectedInterestName: {
    color: '#ffffff',
    fontWeight: '600',
  },
  subredditsContainer: {
    maxHeight: 400,
  },
  subredditItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  selectedSubredditItem: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderColor: '#ffffff',
  },
  subredditPrefix: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: 14,
    marginRight: 4,
  },
  subredditName: {
    flex: 1,
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 14,
  },
  selectedSubredditName: {
    color: '#ffffff',
    fontWeight: '500',
  },
  checkmark: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  notificationOptions: {
    marginTop: 20,
  },
  notificationOption: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedNotificationOption: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderColor: '#ffffff',
  },
  notificationEmoji: {
    fontSize: 32,
    marginBottom: 8,
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 4,
  },
  notificationDescription: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
    lineHeight: 18,
  },
  bottomContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 20,
    gap: 12,
  },
  backButton: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  backButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '500',
  },
  nextButton: {
    flex: 2,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
  },
  nextButtonText: {
    color: '#667eea',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default OnboardingScreen;