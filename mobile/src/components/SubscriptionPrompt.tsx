import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  Dimensions,
} from 'react-native';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';

const { width, height } = Dimensions.get('window');

interface SubscriptionPromptProps {
  visible: boolean;
  onClose: () => void;
  onUpgrade: () => void;
  dailyUsage: number;
  limit: number;
  tier: 'FREE' | 'PRO' | 'PREMIUM';
}

const SubscriptionPrompt: React.FC<SubscriptionPromptProps> = ({
  visible,
  onClose,
  onUpgrade,
  dailyUsage,
  limit,
  tier,
}) => {
  const getProgressPercentage = () => {
    return Math.min((dailyUsage / limit) * 100, 100);
  };

  const getRemainingInsights = () => {
    return Math.max(limit - dailyUsage, 0);
  };

  const getPromptMessage = () => {
    const remaining = getRemainingInsights();
    if (remaining === 0) {
      return "You've reached your daily limit!";
    } else if (remaining <= 5) {
      return `Only ${remaining} insights left today!`;
    } else {
      return `You're doing great! ${remaining} insights remaining.`;
    }
  };

  const getPromptEmoji = () => {
    const remaining = getRemainingInsights();
    if (remaining === 0) return '🚫';
    if (remaining <= 5) return '⚠️';
    return '🎉';
  };

  if (!visible) return null;

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <BlurView intensity={50} style={styles.overlay}>
        <View style={styles.container}>
          <LinearGradient
            colors={['#667eea', '#764ba2']}
            style={styles.promptCard}
          >
            {/* Close Button */}
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>

            {/* Header */}
            <View style={styles.header}>
              <Text style={styles.emoji}>{getPromptEmoji()}</Text>
              <Text style={styles.title}>{getPromptMessage()}</Text>
            </View>

            {/* Usage Progress */}
            <View style={styles.progressContainer}>
              <View style={styles.progressBar}>
                <View
                  style={[
                    styles.progressFill,
                    { width: `${getProgressPercentage()}%` },
                  ]}
                />
              </View>
              <Text style={styles.progressText}>
                {dailyUsage} / {limit} insights used today
              </Text>
            </View>

            {/* Features Comparison */}
            <View style={styles.featuresContainer}>
              <View style={styles.featureRow}>
                <View style={styles.freeColumn}>
                  <Text style={styles.columnTitle}>Free</Text>
                  <Text style={styles.featureText}>20 insights/day</Text>
                  <Text style={styles.featureText}>3 categories</Text>
                  <Text style={styles.featureText}>Basic summaries</Text>
                </View>
                
                <View style={styles.divider} />
                
                <View style={styles.proColumn}>
                  <Text style={styles.columnTitle}>Pro - $4.99</Text>
                  <Text style={styles.featureTextHighlight}>Unlimited insights</Text>
                  <Text style={styles.featureTextHighlight}>All categories</Text>
                  <Text style={styles.featureTextHighlight}>Advanced AI analysis</Text>
                  <Text style={styles.featureTextHighlight}>Priority updates</Text>
                </View>
              </View>
            </View>

            {/* Action Buttons */}
            <View style={styles.buttonsContainer}>
              <TouchableOpacity
                style={styles.upgradeButton}
                onPress={onUpgrade}
              >
                <LinearGradient
                  colors={['#ffffff', '#f1f5f9']}
                  style={styles.upgradeButtonGradient}
                >
                  <Text style={styles.upgradeButtonText}>Upgrade to Pro</Text>
                  <Text style={styles.upgradeButtonSubtext}>Unlock unlimited insights</Text>
                </LinearGradient>
              </TouchableOpacity>

              {getRemainingInsights() > 0 && (
                <TouchableOpacity
                  style={styles.continueButton}
                  onPress={onClose}
                >
                  <Text style={styles.continueButtonText}>
                    Continue with {getRemainingInsights()} left
                  </Text>
                </TouchableOpacity>
              )}
            </View>

            {/* Benefits */}
            <View style={styles.benefitsContainer}>
              <Text style={styles.benefitsTitle}>Why upgrade?</Text>
              <View style={styles.benefitsList}>
                <Text style={styles.benefitItem}>🚀 Never miss trending opportunities</Text>
                <Text style={styles.benefitItem}>📊 Advanced sentiment analysis</Text>
                <Text style={styles.benefitItem}>⚡ Real-time market insights</Text>
                <Text style={styles.benefitItem}>💎 Priority customer support</Text>
              </View>
            </View>

            {/* Footer */}
            <Text style={styles.footerText}>
              Cancel anytime • No commitment • Join 10,000+ users
            </Text>
          </LinearGradient>
        </View>
      </BlurView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  container: {
    width: width * 0.9,
    maxWidth: 400,
    maxHeight: height * 0.85,
  },
  promptCard: {
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 20,
  },
  closeButton: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1,
  },
  closeButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  header: {
    alignItems: 'center',
    marginBottom: 20,
  },
  emoji: {
    fontSize: 48,
    marginBottom: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
  },
  progressContainer: {
    marginBottom: 24,
  },
  progressBar: {
    height: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 4,
  },
  progressText: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 14,
    textAlign: 'center',
  },
  featuresContainer: {
    marginBottom: 24,
  },
  featureRow: {
    flexDirection: 'row',
  },
  freeColumn: {
    flex: 1,
    paddingRight: 12,
  },
  proColumn: {
    flex: 1,
    paddingLeft: 12,
  },
  divider: {
    width: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    marginHorizontal: 8,
  },
  columnTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
    textAlign: 'center',
  },
  featureText: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.7)',
    marginBottom: 4,
    textAlign: 'center',
  },
  featureTextHighlight: {
    fontSize: 12,
    color: '#ffffff',
    marginBottom: 4,
    textAlign: 'center',
    fontWeight: '600',
  },
  buttonsContainer: {
    marginBottom: 20,
  },
  upgradeButton: {
    marginBottom: 12,
  },
  upgradeButtonGradient: {
    borderRadius: 16,
    paddingVertical: 16,
    paddingHorizontal: 24,
    alignItems: 'center',
  },
  upgradeButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 2,
  },
  upgradeButtonSubtext: {
    fontSize: 12,
    color: '#6b7280',
  },
  continueButton: {
    alignItems: 'center',
    paddingVertical: 12,
  },
  continueButtonText: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    textDecorationLine: 'underline',
  },
  benefitsContainer: {
    marginBottom: 16,
  },
  benefitsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 12,
    textAlign: 'center',
  },
  benefitsList: {
    gap: 4,
  },
  benefitItem: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
  },
  footerText: {
    fontSize: 10,
    color: 'rgba(255, 255, 255, 0.6)',
    textAlign: 'center',
    lineHeight: 14,
  },
});

export default SubscriptionPrompt;