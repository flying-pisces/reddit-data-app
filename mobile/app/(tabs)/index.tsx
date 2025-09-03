/**
 * Reddit Insight Mobile App - TikTok Style Feed Demo
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  PanResponder,
  Alert,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const { width, height } = Dimensions.get('window');
const SWIPE_THRESHOLD = 80;

// Mock content data
const mockContent = [
  {
    id: '1',
    summary: 'Tesla stock surges 15% after strong Q3 delivery numbers exceed analyst expectations.',
    category: 'Finance',
    sentiment: 'BULLISH',
    keyPoints: ['Strong Q3', 'Exceeded expectations', 'Stock surge'],
    subreddit: 'stocks',
  },
  {
    id: '2', 
    summary: 'OpenAI releases GPT-5 with multimodal capabilities and 10x performance improvement.',
    category: 'Technology',
    sentiment: 'POSITIVE',
    keyPoints: ['GPT-5 release', 'Multimodal', '10x faster'],
    subreddit: 'technology',
  },
  {
    id: '3',
    summary: 'Apple announces new iPhone 16 with revolutionary AI chip and enhanced camera system.',
    category: 'Technology',
    sentiment: 'POSITIVE',
    keyPoints: ['iPhone 16', 'AI chip', 'Camera upgrade'],
    subreddit: 'apple',
  }
];

export default function HomeScreen() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [dailyInsights, setDailyInsights] = useState(0);
  const subscriptionTier = 'FREE'; // Demo subscription tier

  const handleSwipe = (direction: string) => {
    if (currentIndex >= mockContent.length) {
      Alert.alert('All caught up!', 'Pull to refresh for new content');
      return;
    }

    // Check subscription limits
    if (subscriptionTier === 'FREE' && dailyInsights >= 20) {
      Alert.alert(
        'Daily Limit Reached',
        'You\'ve reached your daily limit of 20 insights. Upgrade to Pro for unlimited access!'
      );
      return;
    }

    const currentContent = mockContent[currentIndex];
    
    // Handle different swipe actions
    switch (direction) {
      case 'right':
        Alert.alert('Saved!', `Saved: ${currentContent.summary.substring(0, 50)}...`);
        break;
      case 'left':
        Alert.alert('Not Interested', 'Content marked as not interested');
        break;
      case 'up':
        Alert.alert('Details', `Opening details for: ${currentContent.category}`);
        break;
      case 'down':
        Alert.alert('Skip Category', `Skipping ${currentContent.category} for 2 hours`);
        break;
    }

    // Move to next content
    setCurrentIndex(prev => prev + 1);
    setDailyInsights(prev => prev + 1);
  };

  const panResponder = PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onMoveShouldSetPanResponder: (_, gesture) => {
      return Math.abs(gesture.dx) > 5 || Math.abs(gesture.dy) > 5;
    },
    onPanResponderRelease: (_, gesture) => {
      const absX = Math.abs(gesture.dx);
      const absY = Math.abs(gesture.dy);

      if (absX > SWIPE_THRESHOLD || absY > SWIPE_THRESHOLD) {
        let direction: string;
        if (absX > absY) {
          direction = gesture.dx > 0 ? 'right' : 'left';
        } else {
          direction = gesture.dy > 0 ? 'down' : 'up';
        }
        handleSwipe(direction);
      }
    }
  });

  const currentContent = mockContent[currentIndex] || null;

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Reddit Insight</Text>
        <Text style={styles.insightsCounter}>{dailyInsights}/20 today</Text>
      </View>

      {/* Content Card */}
      {currentContent ? (
        <View style={styles.cardContainer} {...panResponder.panHandlers}>
          <View style={styles.card}>
            <Text style={styles.category}>{currentContent.category}</Text>
            <Text style={styles.summary}>{currentContent.summary}</Text>
            
            <View style={styles.keyPoints}>
              {currentContent.keyPoints.map((point, index) => (
                <Text key={index} style={styles.keyPoint}>• {point}</Text>
              ))}
            </View>
            
            <View style={styles.footer}>
              <Text style={styles.subreddit}>r/{currentContent.subreddit}</Text>
              <Text style={styles.sentiment}>{currentContent.sentiment}</Text>
            </View>
          </View>
          
          <View style={styles.swipeInstructions}>
            <Text style={styles.instructionText}>← Not Interested | Save →</Text>
            <Text style={styles.instructionText}>↑ Details | Skip Category ↓</Text>
          </View>
        </View>
      ) : (
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateText}>You're all caught up! 🎉</Text>
          <TouchableOpacity 
            style={styles.refreshButton}
            onPress={() => {
              setCurrentIndex(0);
              setDailyInsights(0);
            }}
          >
            <Text style={styles.refreshButtonText}>Reset Demo</Text>
          </TouchableOpacity>
        </View>
      )}
    </SafeAreaView>
  );
}

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
  insightsCounter: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  cardContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  card: {
    width: width - 40,
    height: height * 0.6,
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 10,
  },
  category: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 15,
  },
  summary: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    lineHeight: 28,
    marginBottom: 20,
  },
  keyPoints: {
    marginBottom: 30,
  },
  keyPoint: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
    lineHeight: 22,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 'auto',
  },
  subreddit: {
    fontSize: 14,
    color: '#888',
    fontWeight: '500',
  },
  sentiment: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#667eea',
  },
  swipeInstructions: {
    alignItems: 'center',
    marginTop: 20,
  },
  instructionText: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 4,
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
    marginBottom: 30,
    textAlign: 'center',
  },
  refreshButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  refreshButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});
