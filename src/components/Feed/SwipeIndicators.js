import React from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart, Bookmark, ExternalLink, X } from 'lucide-react';

const IndicatorsContainer = styled.div`
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 10;
`;

const Indicator = styled(motion.div)`
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.2rem;
  border-radius: 16px;
  padding: 12px 20px;
  backdrop-filter: blur(10px);
  border: 2px solid;
  gap: 8px;
`;

const LeftIndicator = styled(Indicator)`
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(239, 68, 68, 0.9);
  border-color: #ef4444;
  color: white;
`;

const RightIndicator = styled(Indicator)`
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(34, 197, 94, 0.9);
  border-color: #22c55e;
  color: white;
`;

const TopIndicator = styled(Indicator)`
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(59, 130, 246, 0.9);
  border-color: #3b82f6;
  color: white;
`;

const BottomIndicator = styled(Indicator)`
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(156, 163, 175, 0.9);
  border-color: #9ca3af;
  color: white;
`;

const SwipeIndicators = ({ swipeDirection }) => {
  const indicatorVariants = {
    hidden: { 
      opacity: 0, 
      scale: 0.8 
    },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 20
      }
    },
    exit: { 
      opacity: 0, 
      scale: 0.8,
      transition: {
        duration: 0.2
      }
    }
  };

  return (
    <IndicatorsContainer>
      <AnimatePresence>
        {swipeDirection === 'left' && (
          <LeftIndicator
            variants={indicatorVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <X size={20} />
            Not Interested
          </LeftIndicator>
        )}
        
        {swipeDirection === 'right' && (
          <RightIndicator
            variants={indicatorVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <Bookmark size={20} />
            Saved
          </RightIndicator>
        )}
        
        {swipeDirection === 'up' && (
          <TopIndicator
            variants={indicatorVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <ExternalLink size={20} />
            More Details
          </TopIndicator>
        )}
        
        {swipeDirection === 'down' && (
          <BottomIndicator
            variants={indicatorVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <Heart size={20} />
            Skip Category
          </BottomIndicator>
        )}
      </AnimatePresence>
    </IndicatorsContainer>
  );
};

export default SwipeIndicators;