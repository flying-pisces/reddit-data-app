import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { motion, useMotionValue, useTransform, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { 
  TrendingUp, 
  ArrowUp, 
  ArrowDown, 
  ArrowLeft, 
  ArrowRight,
  ExternalLink,
  Settings,
  Bookmark,
  Share2,
  MoreVertical,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

import NewsCard from './NewsCard';
import SwipeIndicators from './SwipeIndicators';
import { generateMockContent } from '../../utils/mockData';

const FeedContainer = styled.div`
  height: 100vh;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 100;
`;

const HeaderTitle = styled.h1`
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(45deg, #ff9a9e, #fecfef);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const IconButton = styled(motion.button)`
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 12px;
  padding: 12px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    color: #ffffff;
  }
`;

const CardStack = styled.div`
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: hidden;
`;

const SwipeArea = styled(motion.div)`
  position: absolute;
  inset: 0;
  cursor: grab;
  
  &:active {
    cursor: grabbing;
  }
`;

const SwipeHints = styled.div`
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 200;
  display: flex;
  gap: 20px;
`;

const SwipeHint = styled(motion.div)`
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  
  ${props => props.active && `
    background: rgba(255, 154, 158, 0.8);
    border-color: #ff9a9e;
    color: #ffffff;
  `}
`;

const LoadingOverlay = styled(motion.div)`
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 300;
  
  .loading-text {
    color: #ffffff;
    font-size: 1.1rem;
    font-weight: 500;
  }
`;

const EmptyState = styled(motion.div)`
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  padding: 40px;
  
  .title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 16px;
    color: rgba(255, 255, 255, 0.9);
  }
  
  .description {
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 24px;
  }
`;

const RefreshButton = styled(motion.button)`
  background: linear-gradient(45deg, #ff9a9e, #fecfef);
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SWIPE_THRESHOLD = 100;
const SWIPE_VELOCITY_THRESHOLD = 500;

const MainFeed = ({ user }) => {
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [cards, setCards] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [swipeDirection, setSwipeDirection] = useState(null);
  const [showHints, setShowHints] = useState(true);
  
  const cardX = useMotionValue(0);
  const cardY = useMotionValue(0);
  const cardRotate = useTransform(cardX, [-300, 300], [-30, 30]);
  const cardOpacity = useTransform(
    cardX, 
    [-300, -150, 0, 150, 300], 
    [0, 0.5, 1, 0.5, 0]
  );

  const constraintsRef = useRef(null);

  useEffect(() => {
    loadInitialContent();
    // Hide hints after 5 seconds
    const timer = setTimeout(() => setShowHints(false), 5000);
    return () => clearTimeout(timer);
  }, []);

  const loadInitialContent = async () => {
    setIsLoading(true);
    try {
      // Simulate API call to fetch personalized content
      await new Promise(resolve => setTimeout(resolve, 1500));
      const mockCards = generateMockContent(user.interests || []);
      setCards(mockCards);
    } catch (error) {
      toast.error('Failed to load content');
    } finally {
      setIsLoading(false);
    }
  };

  const loadMoreContent = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const newCards = generateMockContent(user.interests || []);
      setCards(prev => [...prev, ...newCards]);
    } catch (error) {
      toast.error('Failed to load more content');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSwipe = (direction, velocity = 0) => {
    if (currentCardIndex >= cards.length) return;

    const currentCard = cards[currentCardIndex];
    
    // Record user interaction
    recordUserAction(currentCard.id, direction, velocity);
    
    // Provide haptic feedback (if available)
    if (navigator.vibrate) {
      navigator.vibrate(50);
    }

    // Show appropriate feedback
    switch (direction) {
      case 'right':
        toast.success('Saved for later!', { duration: 1500 });
        break;
      case 'left':
        toast('Not interested', { duration: 1000 });
        break;
      case 'up':
        // Handle expand details
        expandCardDetails(currentCard);
        return; // Don't advance to next card
      case 'down':
        toast('Category filtered', { duration: 1000 });
        break;
    }

    // Advance to next card
    setCurrentCardIndex(prev => prev + 1);
    
    // Load more content when getting low
    if (currentCardIndex >= cards.length - 3) {
      loadMoreContent();
    }
    
    // Reset card position
    cardX.set(0);
    cardY.set(0);
    setSwipeDirection(null);
  };

  const recordUserAction = (cardId, action, velocity) => {
    // TODO: Send to backend for personalization
    console.log('User action recorded:', {
      cardId,
      action,
      velocity,
      timestamp: new Date().toISOString(),
      userId: user.id
    });
  };

  const expandCardDetails = (card) => {
    // TODO: Show detailed view with full content, comments, etc.
    toast.success('Loading full details...', { duration: 1500 });
    console.log('Expanding details for:', card.title);
  };

  const handleDragStart = () => {
    setSwipeDirection(null);
    setShowHints(false);
  };

  const handleDrag = (event, info) => {
    const { offset } = info;
    const absX = Math.abs(offset.x);
    const absY = Math.abs(offset.y);
    
    // Determine primary direction
    if (absX > absY) {
      setSwipeDirection(offset.x > 0 ? 'right' : 'left');
    } else {
      setSwipeDirection(offset.y > 0 ? 'down' : 'up');
    }
  };

  const handleDragEnd = (event, info) => {
    const { offset, velocity } = info;
    const absX = Math.abs(offset.x);
    const absY = Math.abs(offset.y);
    const absVelocityX = Math.abs(velocity.x);
    const absVelocityY = Math.abs(velocity.y);

    // Check if swipe threshold is met
    const shouldSwipe = 
      absX > SWIPE_THRESHOLD || 
      absY > SWIPE_THRESHOLD || 
      absVelocityX > SWIPE_VELOCITY_THRESHOLD ||
      absVelocityY > SWIPE_VELOCITY_THRESHOLD;

    if (shouldSwipe) {
      // Determine final direction
      let direction;
      if (absX > absY) {
        direction = offset.x > 0 ? 'right' : 'left';
      } else {
        direction = offset.y > 0 ? 'down' : 'up';
      }
      
      handleSwipe(direction, Math.max(absVelocityX, absVelocityY));
    } else {
      // Snap back to center
      cardX.set(0);
      cardY.set(0);
      setSwipeDirection(null);
    }
  };

  const currentCard = cards[currentCardIndex];
  const nextCard = cards[currentCardIndex + 1];

  if (isLoading && cards.length === 0) {
    return (
      <FeedContainer>
        <Header>
          <HeaderTitle>Reddit Insight</HeaderTitle>
        </Header>
        <LoadingOverlay
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="loading-text">Loading your personalized feed...</div>
        </LoadingOverlay>
      </FeedContainer>
    );
  }

  if (!currentCard) {
    return (
      <FeedContainer>
        <Header>
          <HeaderTitle>Reddit Insight</HeaderTitle>
          <HeaderActions>
            <IconButton whileTap={{ scale: 0.9 }}>
              <Settings size={20} />
            </IconButton>
          </HeaderActions>
        </Header>
        <CardStack>
          <EmptyState
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="title">You're all caught up!</div>
            <div className="description">
              No new content available right now. Check back later for fresh insights from your favorite communities.
            </div>
            <RefreshButton
              onClick={loadInitialContent}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <TrendingUp size={16} />
              Refresh Feed
            </RefreshButton>
          </EmptyState>
        </CardStack>
      </FeedContainer>
    );
  }

  return (
    <FeedContainer>
      <Header>
        <HeaderTitle>Reddit Insight</HeaderTitle>
        <HeaderActions>
          <IconButton whileTap={{ scale: 0.9 }}>
            <Bookmark size={20} />
          </IconButton>
          <IconButton whileTap={{ scale: 0.9 }}>
            <Settings size={20} />
          </IconButton>
        </HeaderActions>
      </Header>

      <CardStack ref={constraintsRef}>
        <AnimatePresence>
          {/* Next card (background) */}
          {nextCard && (
            <motion.div
              key={`next-${currentCardIndex + 1}`}
              initial={{ scale: 0.9, opacity: 0.5 }}
              animate={{ scale: 0.9, opacity: 0.5 }}
              style={{ position: 'absolute', zIndex: 1 }}
            >
              <NewsCard 
                content={nextCard} 
                isBackground 
              />
            </motion.div>
          )}

          {/* Current card */}
          <SwipeArea
            key={`current-${currentCardIndex}`}
            drag
            dragConstraints={constraintsRef}
            dragElastic={0.1}
            onDragStart={handleDragStart}
            onDrag={handleDrag}
            onDragEnd={handleDragEnd}
            style={{
              x: cardX,
              y: cardY,
              rotate: cardRotate,
              opacity: cardOpacity,
              zIndex: 2
            }}
            animate={{ scale: 1 }}
            exit={{ 
              x: swipeDirection === 'left' ? -500 : swipeDirection === 'right' ? 500 : 0,
              y: swipeDirection === 'up' ? -500 : swipeDirection === 'down' ? 500 : 0,
              opacity: 0,
              scale: 0.8 
            }}
            transition={{ duration: 0.3 }}
          >
            <NewsCard 
              content={currentCard}
              swipeDirection={swipeDirection}
            />
          </SwipeArea>
        </AnimatePresence>

        <SwipeIndicators swipeDirection={swipeDirection} />
      </CardStack>

      {/* Swipe hints */}
      <AnimatePresence>
        {showHints && (
          <SwipeHints>
            <SwipeHint
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ delay: 0 }}
            >
              <ArrowLeft size={14} />
              Not interested
            </SwipeHint>
            <SwipeHint
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ delay: 0.1 }}
            >
              <ArrowRight size={14} />
              Save
            </SwipeHint>
            <SwipeHint
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ delay: 0.2 }}
            >
              <ChevronUp size={14} />
              Details
            </SwipeHint>
            <SwipeHint
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ delay: 0.3 }}
            >
              <ChevronDown size={14} />
              Skip category
            </SwipeHint>
          </SwipeHints>
        )}
      </AnimatePresence>

      {/* Loading overlay for fetching more content */}
      <AnimatePresence>
        {isLoading && cards.length > 0 && (
          <LoadingOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{ 
              background: 'rgba(0, 0, 0, 0.3)',
              backdropFilter: 'blur(2px)'
            }}
          >
            <div className="loading-text">Loading more content...</div>
          </LoadingOverlay>
        )}
      </AnimatePresence>
    </FeedContainer>
  );
};

export default MainFeed;