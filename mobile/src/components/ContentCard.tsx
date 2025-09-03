import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

const { width, height } = Dimensions.get('window');

export interface ContentItem {
  id: string;
  summary: string;
  category: string;
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL' | 'POSITIVE' | 'NEGATIVE';
  keyPoints: string[];
  subreddit: string;
  upvotes?: number;
  comments?: number;
  timestamp?: number;
  stock_ticker?: string;
  confidence?: number;
}

interface ContentCardProps {
  content: ContentItem;
  onPress?: () => void;
}

const ContentCard: React.FC<ContentCardProps> = ({ content, onPress }) => {
  const getSentimentColor = () => {
    switch (content.sentiment) {
      case 'BULLISH':
      case 'POSITIVE':
        return ['#10B981', '#059669'];
      case 'BEARISH':
      case 'NEGATIVE':
        return ['#EF4444', '#DC2626'];
      default:
        return ['#6B7280', '#4B5563'];
    }
  };

  const getSentimentEmoji = () => {
    switch (content.sentiment) {
      case 'BULLISH':
      case 'POSITIVE':
        return '📈';
      case 'BEARISH':
      case 'NEGATIVE':
        return '📉';
      default:
        return '📊';
    }
  };

  const getCategoryEmoji = () => {
    switch (content.category.toLowerCase()) {
      case 'finance':
      case 'stocks':
        return '💰';
      case 'technology':
        return '💻';
      case 'crypto':
      case 'cryptocurrency':
        return '₿';
      case 'trading':
        return '📊';
      default:
        return '📱';
    }
  };

  return (
    <TouchableOpacity
      style={styles.container}
      onPress={onPress}
      activeOpacity={0.95}
    >
      <LinearGradient
        colors={['#ffffff', '#f8fafc']}
        style={styles.card}
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.categoryContainer}>
            <Text style={styles.categoryEmoji}>{getCategoryEmoji()}</Text>
            <Text style={styles.category}>{content.category}</Text>
          </View>
          
          <View style={[styles.sentimentBadge, { backgroundColor: getSentimentColor()[0] }]}>
            <Text style={styles.sentimentEmoji}>{getSentimentEmoji()}</Text>
            <Text style={styles.sentimentText}>{content.sentiment}</Text>
          </View>
        </View>

        {/* Stock Ticker */}
        {content.stock_ticker && (
          <View style={styles.tickerContainer}>
            <Text style={styles.tickerSymbol}>${content.stock_ticker}</Text>
            {content.confidence && (
              <Text style={styles.confidence}>{Math.round(content.confidence * 100)}% confidence</Text>
            )}
          </View>
        )}

        {/* Summary */}
        <Text style={styles.summary}>{content.summary}</Text>

        {/* Key Points */}
        <View style={styles.keyPointsContainer}>
          {content.keyPoints.slice(0, 3).map((point, index) => (
            <View key={index} style={styles.keyPointRow}>
              <Text style={styles.bullet}>•</Text>
              <Text style={styles.keyPoint}>{point}</Text>
            </View>
          ))}
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <View style={styles.subredditContainer}>
            <Text style={styles.subredditPrefix}>r/</Text>
            <Text style={styles.subreddit}>{content.subreddit}</Text>
          </View>
          
          <View style={styles.stats}>
            {content.upvotes && (
              <Text style={styles.statText}>↑ {content.upvotes}</Text>
            )}
            {content.comments && (
              <Text style={styles.statText}>💬 {content.comments}</Text>
            )}
          </View>
        </View>

        {/* Timestamp */}
        {content.timestamp && (
          <Text style={styles.timestamp}>
            {new Date(content.timestamp).toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </Text>
        )}
      </LinearGradient>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    width: width - 40,
    height: height * 0.65,
    alignSelf: 'center',
  },
  card: {
    flex: 1,
    borderRadius: 20,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 10,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  categoryContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  categoryEmoji: {
    fontSize: 18,
    marginRight: 8,
  },
  category: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
  sentimentBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  sentimentEmoji: {
    fontSize: 12,
    marginRight: 4,
  },
  sentimentText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  tickerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#f1f5f9',
    borderRadius: 8,
  },
  tickerSymbol: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1e40af',
  },
  confidence: {
    fontSize: 12,
    color: '#64748b',
    fontWeight: '500',
  },
  summary: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    lineHeight: 26,
    marginBottom: 20,
  },
  keyPointsContainer: {
    marginBottom: 24,
  },
  keyPointRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  bullet: {
    fontSize: 16,
    color: '#6366f1',
    marginRight: 8,
    marginTop: 2,
  },
  keyPoint: {
    flex: 1,
    fontSize: 14,
    color: '#4b5563',
    lineHeight: 20,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 'auto',
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  subredditContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  subredditPrefix: {
    fontSize: 14,
    color: '#9ca3af',
    fontWeight: '500',
  },
  subreddit: {
    fontSize: 14,
    color: '#6366f1',
    fontWeight: '600',
  },
  stats: {
    flexDirection: 'row',
    gap: 12,
  },
  statText: {
    fontSize: 12,
    color: '#9ca3af',
    fontWeight: '500',
  },
  timestamp: {
    position: 'absolute',
    top: 12,
    right: 20,
    fontSize: 10,
    color: '#9ca3af',
  },
});

export default ContentCard;