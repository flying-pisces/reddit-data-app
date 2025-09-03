import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { TrendingUp } from 'lucide-react';

const LoadingContainer = styled.div`
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
`;

const LogoContainer = styled(motion.div)`
  margin-bottom: 40px;
`;

const Logo = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(45deg, #ff9a9e, #fecfef);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const LoadingAnimation = styled(motion.div)`
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
`;

const LoadingDot = styled(motion.div)`
  width: 12px;
  height: 12px;
  background: linear-gradient(45deg, #ff9a9e, #fecfef);
  border-radius: 50%;
`;

const LoadingText = styled(motion.p)`
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
`;

const LoadingScreen = () => {
  const dotVariants = {
    start: {
      scale: 0.5,
      opacity: 0.5
    },
    end: {
      scale: 1,
      opacity: 1
    }
  };

  const dotTransition = {
    duration: 0.6,
    repeat: Infinity,
    repeatType: "reverse",
    ease: "easeInOut"
  };

  return (
    <LoadingContainer>
      <LogoContainer
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Logo>
          <motion.div
            animate={{ 
              rotate: [0, 360]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "linear"
            }}
          >
            <TrendingUp size={48} />
          </motion.div>
          Reddit Insight
        </Logo>
      </LogoContainer>

      <LoadingAnimation>
        {[0, 1, 2].map((index) => (
          <LoadingDot
            key={index}
            variants={dotVariants}
            initial="start"
            animate="end"
            transition={{
              ...dotTransition,
              delay: index * 0.2
            }}
          />
        ))}
      </LoadingAnimation>

      <LoadingText
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.5 }}
      >
        Initializing your personalized feed...
      </LoadingText>
    </LoadingContainer>
  );
};

export default LoadingScreen;