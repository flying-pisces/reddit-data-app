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

interface SubscriptionScreenProps {
  navigation: any;
  currentTier: 'FREE' | 'PRO' | 'PREMIUM';
  onUpgrade: (tier: 'PRO' | 'PREMIUM') => Promise<void>;
}

const SUBSCRIPTION_TIERS = [
  {
    id: 'FREE',
    name: 'Free',
    price: 0,
    priceLabel: 'Free Forever',
    features: [
      '20 insights per day',
      'Basic AI summaries',
      '3 categories only',
      'Community support',
    ],
    limitations: ['Daily limit', 'Limited categories', 'Basic features'],
    color: '#999',
    popular: false,
  },
  {
    id: 'PRO',
    name: 'Pro',
    price: 4.99,
    priceLabel: '$4.99/month',
    features: [
      'Unlimited insights',
      'All categories',
      'Priority updates',
      'No advertisements',
      'Advanced AI analysis',
      'Save unlimited posts',
    ],
    limitations: [],
    color: '#667eea',
    popular: true,
  },
  {
    id: 'PREMIUM',
    name: 'Premium',
    price: 9.99,
    priceLabel: '$9.99/month',
    features: [
      'Everything in Pro',
      'AI-powered predictions',
      'Portfolio tracking',
      'API access',
      'Custom alerts',
      'Advanced analytics',
      'Priority support',
      'Early access to features',
    ],
    limitations: [],
    color: '#FFD700',
    popular: false,
  },
];

const SubscriptionScreen: React.FC<SubscriptionScreenProps> = ({
  navigation,
  currentTier,
  onUpgrade,
}) => {
  const [selectedTier, setSelectedTier] = useState<'FREE' | 'PRO' | 'PREMIUM'>(currentTier);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubscribe = async () => {
    if (selectedTier === 'FREE' || selectedTier === currentTier) {
      navigation.goBack();
      return;
    }

    setIsProcessing(true);
    try {
      await onUpgrade(selectedTier as 'PRO' | 'PREMIUM');
      navigation.goBack();
    } catch (error) {
      console.error('Subscription error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRestorePurchases = () => {
    Alert.alert('Restore Purchases', 'Checking for previous purchases...');
    // Implement restore purchases logic
  };

  const renderTierCard = (tier: typeof SUBSCRIPTION_TIERS[0]) => {
    const isSelected = selectedTier === tier.id;
    const isCurrent = currentTier === tier.id;

    return (
      <TouchableOpacity
        key={tier.id}
        style={[
          styles.tierCard,
          isSelected && styles.selectedTierCard,
          { borderColor: tier.color },
        ]}
        onPress={() => setSelectedTier(tier.id as any)}
        disabled={isCurrent}
      >
        {tier.popular && (
          <View style={[styles.popularBadge, { backgroundColor: tier.color }]}>
            <Text style={styles.popularText}>Most Popular</Text>
          </View>
        )}

        {isCurrent && (
          <View style={styles.currentBadge}>
            <Text style={styles.currentText}>Current Plan</Text>
          </View>
        )}

        <View style={styles.tierHeader}>
          <Text style={[styles.tierName, { color: tier.color }]}>{tier.name}</Text>
          <Text style={styles.tierPrice}>{tier.priceLabel}</Text>
        </View>

        <View style={styles.featuresContainer}>
          {tier.features.map((feature, index) => (
            <View key={index} style={styles.featureRow}>
              <Text style={styles.featureCheck}>✓</Text>
              <Text style={styles.featureText}>{feature}</Text>
            </View>
          ))}
          
          {tier.limitations.map((limitation, index) => (
            <View key={`limitation-${index}`} style={styles.featureRow}>
              <Text style={styles.limitationX}>✗</Text>
              <Text style={styles.limitationText}>{limitation}</Text>
            </View>
          ))}
        </View>

        {isSelected && !isCurrent && (
          <View style={styles.selectedIndicator}>
            <Text style={styles.selectedText}>Selected</Text>
          </View>
        )}
      </TouchableOpacity>
    );
  };

  const getButtonText = () => {
    if (selectedTier === currentTier) {
      return 'Current Plan';
    }
    if (selectedTier === 'FREE') {
      return 'Continue with Free';
    }
    return `Upgrade to ${selectedTier}`;
  };

  const getButtonStyle = () => {
    const selectedTierData = SUBSCRIPTION_TIERS.find(t => t.id === selectedTier);
    return {
      backgroundColor: selectedTier === currentTier ? '#999' : selectedTierData?.color || '#667eea',
    };
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.closeButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.closeButtonText}>✕</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Choose Your Plan</Text>
        <TouchableOpacity
          style={styles.restoreButton}
          onPress={handleRestorePurchases}
        >
          <Text style={styles.restoreButtonText}>Restore</Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.introSection}>
          <Text style={styles.introTitle}>Unlock Premium Features</Text>
          <Text style={styles.introSubtitle}>
            Get unlimited access to AI-powered Reddit insights and advanced features
          </Text>
        </View>

        {/* Subscription Tiers */}
        <View style={styles.tiersContainer}>
          {SUBSCRIPTION_TIERS.map(renderTierCard)}
        </View>

        {/* Benefits Section */}
        <View style={styles.benefitsSection}>
          <Text style={styles.benefitsTitle}>Why Upgrade?</Text>
          
          <View style={styles.benefitItem}>
            <Text style={styles.benefitEmoji}>🚀</Text>
            <View style={styles.benefitContent}>
              <Text style={styles.benefitTitle}>Unlimited Insights</Text>
              <Text style={styles.benefitDescription}>
                No daily limits - get insights whenever you want
              </Text>
            </View>
          </View>

          <View style={styles.benefitItem}>
            <Text style={styles.benefitEmoji}>🤖</Text>
            <View style={styles.benefitContent}>
              <Text style={styles.benefitTitle}>Advanced AI Analysis</Text>
              <Text style={styles.benefitDescription}>
                Deeper insights with sentiment analysis and predictions
              </Text>
            </View>
          </View>

          <View style={styles.benefitItem}>
            <Text style={styles.benefitEmoji}>💰</Text>
            <View style={styles.benefitContent}>
              <Text style={styles.benefitTitle}>Portfolio Tracking</Text>
              <Text style={styles.benefitDescription}>
                Track your investments with Reddit sentiment data
              </Text>
            </View>
          </View>

          <View style={styles.benefitItem}>
            <Text style={styles.benefitEmoji}>🔔</Text>
            <View style={styles.benefitContent}>
              <Text style={styles.benefitTitle}>Custom Alerts</Text>
              <Text style={styles.benefitDescription}>
                Get notified about trending stocks and opportunities
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.bottomSpace} />
      </ScrollView>

      {/* Bottom Action */}
      <View style={styles.bottomContainer}>
        <TouchableOpacity
          style={[styles.subscribeButton, getButtonStyle()]}
          onPress={handleSubscribe}
          disabled={isProcessing || selectedTier === currentTier}
        >
          <Text style={styles.subscribeButtonText}>
            {isProcessing ? 'Processing...' : getButtonText()}
          </Text>
        </TouchableOpacity>

        <Text style={styles.disclaimerText}>
          Cancel anytime. No commitment. Terms and conditions apply.
        </Text>
      </View>
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
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  headerTitle: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  restoreButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  restoreButtonText: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 14,
  },
  content: {
    flex: 1,
  },
  introSection: {
    paddingHorizontal: 20,
    paddingVertical: 20,
    alignItems: 'center',
  },
  introTitle: {
    color: '#ffffff',
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  introSubtitle: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
  },
  tiersContainer: {
    paddingHorizontal: 20,
  },
  tierCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: 'transparent',
    position: 'relative',
  },
  selectedTierCard: {
    backgroundColor: '#ffffff',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  popularBadge: {
    position: 'absolute',
    top: -8,
    left: 20,
    right: 20,
    paddingVertical: 4,
    borderRadius: 12,
    alignItems: 'center',
  },
  popularText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  currentBadge: {
    position: 'absolute',
    top: -8,
    left: 20,
    right: 20,
    backgroundColor: '#10B981',
    paddingVertical: 4,
    borderRadius: 12,
    alignItems: 'center',
  },
  currentText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  tierHeader: {
    alignItems: 'center',
    marginBottom: 16,
    marginTop: 8,
  },
  tierName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  tierPrice: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  featuresContainer: {
    marginBottom: 16,
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  featureCheck: {
    color: '#10B981',
    fontSize: 16,
    fontWeight: 'bold',
    width: 24,
  },
  featureText: {
    color: '#333',
    fontSize: 14,
    flex: 1,
  },
  limitationX: {
    color: '#EF4444',
    fontSize: 16,
    fontWeight: 'bold',
    width: 24,
  },
  limitationText: {
    color: '#666',
    fontSize: 14,
    flex: 1,
  },
  selectedIndicator: {
    backgroundColor: '#667eea',
    borderRadius: 8,
    paddingVertical: 8,
    alignItems: 'center',
  },
  selectedText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  benefitsSection: {
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  benefitsTitle: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
  },
  benefitItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 12,
    padding: 16,
  },
  benefitEmoji: {
    fontSize: 24,
    marginRight: 12,
  },
  benefitContent: {
    flex: 1,
  },
  benefitTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  benefitDescription: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 14,
    lineHeight: 20,
  },
  bottomSpace: {
    height: 20,
  },
  bottomContainer: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    paddingBottom: 32,
  },
  subscribeButton: {
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 8,
  },
  subscribeButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  disclaimerText: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: 12,
    textAlign: 'center',
    lineHeight: 16,
  },
});

export default SubscriptionScreen;