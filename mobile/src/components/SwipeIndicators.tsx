import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
} from 'react-native';

const { width, height } = Dimensions.get('window');

interface SwipeIndicatorsProps {
  swipeDirection?: 'left' | 'right' | 'up' | 'down' | null;
  opacity?: Animated.Value;
}

const SwipeIndicators: React.FC<SwipeIndicatorsProps> = ({
  swipeDirection,
  opacity = new Animated.Value(1),
}) => {
  const getIndicatorStyle = (direction: string) => ({
    opacity: swipeDirection === direction ? 1 : 0.3,
    transform: [
      {
        scale: swipeDirection === direction ? 1.2 : 1,
      },
    ],
  });

  return (
    <Animated.View style={[styles.container, { opacity }]}>
      {/* Left - Not Interested */}
      <Animated.View style={[styles.leftIndicator, getIndicatorStyle('left')]}>
        <View style={[styles.indicator, styles.notInterestedIndicator]}>
          <Text style={styles.indicatorEmoji}>👎</Text>
          <Text style={styles.indicatorText}>Not Interested</Text>
        </View>
      </Animated.View>

      {/* Right - Save */}
      <Animated.View style={[styles.rightIndicator, getIndicatorStyle('right')]}>
        <View style={[styles.indicator, styles.saveIndicator]}>
          <Text style={styles.indicatorEmoji}>❤️</Text>
          <Text style={styles.indicatorText}>Save</Text>
        </View>
      </Animated.View>

      {/* Top - Details */}
      <Animated.View style={[styles.topIndicator, getIndicatorStyle('up')]}>
        <View style={[styles.indicator, styles.detailsIndicator]}>
          <Text style={styles.indicatorEmoji}>📊</Text>
          <Text style={styles.indicatorText}>View Details</Text>
        </View>
      </Animated.View>

      {/* Bottom - Skip Category */}
      <Animated.View style={[styles.bottomIndicator, getIndicatorStyle('down')]}>
        <View style={[styles.indicator, styles.skipIndicator]}>
          <Text style={styles.indicatorEmoji}>⏭️</Text>
          <Text style={styles.indicatorText}>Skip Category</Text>
        </View>
      </Animated.View>

      {/* Corner hints when no swipe is active */}
      {!swipeDirection && (
        <>
          <View style={styles.cornerHint}>
            <View style={styles.cornerLeftHint}>
              <Text style={styles.cornerHintText}>👎</Text>
            </View>
            <View style={styles.cornerRightHint}>
              <Text style={styles.cornerHintText}>❤️</Text>
            </View>
          </View>
          
          <View style={styles.verticalHints}>
            <View style={styles.cornerTopHint}>
              <Text style={styles.cornerHintText}>📊</Text>
            </View>
            <View style={styles.cornerBottomHint}>
              <Text style={styles.cornerHintText}>⏭️</Text>
            </View>
          </View>
        </>
      )}
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    pointerEvents: 'none',
  },
  indicator: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
    minWidth: 120,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 10,
  },
  indicatorEmoji: {
    fontSize: 24,
    marginBottom: 4,
  },
  indicatorText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    textAlign: 'center',
  },
  leftIndicator: {
    position: 'absolute',
    left: 30,
    top: height * 0.4,
    transform: [{ translateY: -50 }],
  },
  rightIndicator: {
    position: 'absolute',
    right: 30,
    top: height * 0.4,
    transform: [{ translateY: -50 }],
  },
  topIndicator: {
    position: 'absolute',
    top: 100,
    left: width / 2,
    transform: [{ translateX: -60 }],
  },
  bottomIndicator: {
    position: 'absolute',
    bottom: 150,
    left: width / 2,
    transform: [{ translateX: -60 }],
  },
  notInterestedIndicator: {
    backgroundColor: 'rgba(239, 68, 68, 0.9)',
  },
  saveIndicator: {
    backgroundColor: 'rgba(16, 185, 129, 0.9)',
  },
  detailsIndicator: {
    backgroundColor: 'rgba(99, 102, 241, 0.9)',
  },
  skipIndicator: {
    backgroundColor: 'rgba(156, 163, 175, 0.9)',
  },
  cornerHint: {
    position: 'absolute',
    top: height * 0.3,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 40,
  },
  cornerLeftHint: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(239, 68, 68, 0.3)',
  },
  cornerRightHint: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(16, 185, 129, 0.3)',
  },
  verticalHints: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: width / 2,
    transform: [{ translateX: -20 }],
    justifyContent: 'space-between',
    paddingVertical: 120,
  },
  cornerTopHint: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(99, 102, 241, 0.3)',
  },
  cornerBottomHint: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(156, 163, 175, 0.3)',
  },
  cornerHintText: {
    fontSize: 20,
  },
});

export default SwipeIndicators;