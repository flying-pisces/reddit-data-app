import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { 
  TrendingUp, 
  Heart, 
  Briefcase, 
  Music, 
  Gamepad2, 
  Lightbulb,
  ChevronRight,
  ChevronLeft,
  Check,
  ArrowRight
} from 'lucide-react';

const OnboardingContainer = styled.div`
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const OnboardingCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 600px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
  border: 1px solid rgba(255, 255, 255, 0.18);
  text-align: center;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  margin-bottom: 30px;
  overflow: hidden;
`;

const Progress = styled(motion.div)`
  height: 100%;
  background: linear-gradient(90deg, #ff9a9e, #fecfef);
  border-radius: 2px;
`;

const StepContent = styled(motion.div)`
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;

const StepTitle = styled.h2`
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 16px;
  background: linear-gradient(45deg, #ff9a9e, #fecfef);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const StepDescription = styled.p`
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin-bottom: 40px;
  max-width: 400px;
`;

const InterestGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  width: 100%;
  max-width: 500px;
  margin-bottom: 40px;
`;

const InterestCard = styled(motion.div)`
  background: rgba(255, 255, 255, ${props => props.selected ? '0.25' : '0.1'});
  border: 2px solid ${props => props.selected ? '#ff9a9e' : 'rgba(255, 255, 255, 0.2)'};
  border-radius: 16px;
  padding: 24px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.4);
    transform: translateY(-2px);
  }

  .icon {
    color: ${props => props.selected ? '#ff9a9e' : 'rgba(255, 255, 255, 0.8)'};
  }
  
  .title {
    font-weight: 600;
    color: ${props => props.selected ? '#ffffff' : 'rgba(255, 255, 255, 0.9)'};
    font-size: 0.95rem;
  }
  
  .description {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.6);
    text-align: center;
    line-height: 1.3;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: space-between;
  gap: 20px;
  width: 100%;
  max-width: 400px;
  margin-top: auto;
`;

const Button = styled(motion.button)`
  flex: 1;
  padding: 16px 24px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const BackButton = styled(Button)`
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  
  &:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.2);
  }
`;

const NextButton = styled(Button)`
  background: linear-gradient(45deg, #ff9a9e, #fecfef);
  color: #ffffff;
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(255, 154, 158, 0.4);
  }
`;

const WelcomeAnimation = styled(motion.div)`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
`;

const INTEREST_CATEGORIES = [
  {
    id: 'finance',
    title: 'Finance & Investing',
    description: 'Stocks, crypto, personal finance',
    icon: TrendingUp,
    subreddits: ['stocks', 'investing', 'personalfinance', 'wallstreetbets', 'cryptocurrency']
  },
  {
    id: 'lifestyle',
    title: 'Life & Health',
    description: 'Tips, motivation, wellness',
    icon: Heart,
    subreddits: ['lifeprotips', 'getmotivated', 'fitness', 'nutrition', 'productivity']
  },
  {
    id: 'technology',
    title: 'Technology',
    description: 'Tech news, programming, gadgets',
    icon: Lightbulb,
    subreddits: ['technology', 'programming', 'gadgets', 'MachineLearning', 'startups']
  },
  {
    id: 'business',
    title: 'Business & Career',
    description: 'Entrepreneurship, career advice',
    icon: Briefcase,
    subreddits: ['entrepreneur', 'smallbusiness', 'careerguidance', 'jobs', 'marketing']
  },
  {
    id: 'entertainment',
    title: 'Entertainment',
    description: 'Movies, music, gaming',
    icon: Music,
    subreddits: ['movies', 'music', 'gaming', 'television', 'books']
  },
  {
    id: 'gaming',
    title: 'Gaming',
    description: 'Video games, reviews, news',
    icon: Gamepad2,
    subreddits: ['gaming', 'pcgaming', 'nintendo', 'playstation', 'xbox']
  }
];

const OnboardingFlow = ({ user, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedInterests, setSelectedInterests] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const totalSteps = 3;
  const progress = ((currentStep + 1) / totalSteps) * 100;

  const toggleInterest = (interestId) => {
    setSelectedInterests(prev => 
      prev.includes(interestId)
        ? prev.filter(id => id !== interestId)
        : [...prev, interestId]
    );
  };

  const handleNext = () => {
    if (currentStep === totalSteps - 1) {
      handleComplete();
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    setCurrentStep(prev => Math.max(0, prev - 1));
  };

  const handleComplete = async () => {
    if (selectedInterests.length === 0) {
      toast.error('Please select at least one interest to continue');
      return;
    }

    setIsLoading(true);
    
    try {
      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Prepare user preferences
      const selectedCategories = INTEREST_CATEGORIES.filter(cat => 
        selectedInterests.includes(cat.id)
      );
      
      const subreddits = selectedCategories.reduce((acc, category) => {
        return [...acc, ...category.subreddits];
      }, []);

      const userPreferences = {
        interests: selectedInterests,
        selectedCategories: selectedCategories.map(cat => ({
          id: cat.id,
          title: cat.title,
          subreddits: cat.subreddits
        })),
        monitoredSubreddits: [...new Set(subreddits)], // Remove duplicates
        onboardingCompletedAt: new Date().toISOString()
      };

      toast.success('Setup complete! Welcome to Reddit Insight!');
      onComplete(userPreferences);
    } catch (error) {
      toast.error('Setup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <StepContent
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <WelcomeAnimation>
              <motion.div
                animate={{ 
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <TrendingUp size={80} color="#ff9a9e" />
              </motion.div>
              <StepTitle>Welcome, {user.name}!</StepTitle>
              <StepDescription>
                Let's personalize your Reddit experience. We'll help you discover the most relevant and interesting content from across Reddit's communities.
              </StepDescription>
            </WelcomeAnimation>
          </StepContent>
        );

      case 1:
        return (
          <StepContent
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <StepTitle>What interests you?</StepTitle>
            <StepDescription>
              Select the topics you'd like to stay updated on. We'll curate content from the best Reddit communities in these areas.
            </StepDescription>
            <InterestGrid>
              {INTEREST_CATEGORIES.map((interest) => (
                <InterestCard
                  key={interest.id}
                  selected={selectedInterests.includes(interest.id)}
                  onClick={() => toggleInterest(interest.id)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <interest.icon size={32} className="icon" />
                  <div className="title">{interest.title}</div>
                  <div className="description">{interest.description}</div>
                  {selectedInterests.includes(interest.id) && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="checkmark"
                    >
                      <Check size={16} color="#ff9a9e" />
                    </motion.div>
                  )}
                </InterestCard>
              ))}
            </InterestGrid>
            {selectedInterests.length > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{ 
                  color: 'rgba(255, 255, 255, 0.7)', 
                  fontSize: '0.9rem',
                  marginTop: '10px'
                }}
              >
                {selectedInterests.length} interest{selectedInterests.length !== 1 ? 's' : ''} selected
              </motion.div>
            )}
          </StepContent>
        );

      case 2:
        const selectedCategories = INTEREST_CATEGORIES.filter(cat => 
          selectedInterests.includes(cat.id)
        );
        
        return (
          <StepContent
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <StepTitle>You're all set!</StepTitle>
            <StepDescription>
              We'll monitor {selectedCategories.reduce((acc, cat) => acc + cat.subreddits.length, 0)} Reddit communities based on your interests and deliver personalized insights.
            </StepDescription>
            
            <div style={{ 
              background: 'rgba(255, 255, 255, 0.1)', 
              borderRadius: '16px', 
              padding: '24px', 
              marginBottom: '30px',
              maxWidth: '400px',
              width: '100%'
            }}>
              <h4 style={{ 
                color: '#ff9a9e', 
                marginBottom: '16px',
                fontSize: '1.1rem'
              }}>
                Your Selected Interests:
              </h4>
              <div style={{ 
                display: 'flex', 
                flexWrap: 'wrap', 
                gap: '8px' 
              }}>
                {selectedCategories.map(category => (
                  <span
                    key={category.id}
                    style={{
                      background: 'linear-gradient(45deg, #ff9a9e, #fecfef)',
                      color: '#ffffff',
                      padding: '6px 12px',
                      borderRadius: '20px',
                      fontSize: '0.85rem',
                      fontWeight: '500'
                    }}
                  >
                    {category.title}
                  </span>
                ))}
              </div>
            </div>
            
            <StepDescription style={{ fontSize: '0.95rem', opacity: 0.8 }}>
              You can always adjust your preferences later in the settings.
            </StepDescription>
          </StepContent>
        );

      default:
        return null;
    }
  };

  return (
    <OnboardingContainer>
      <OnboardingCard
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <ProgressBar>
          <Progress
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </ProgressBar>

        <AnimatePresence mode="wait">
          {renderStep()}
        </AnimatePresence>

        <ButtonContainer>
          <BackButton
            onClick={handleBack}
            disabled={currentStep === 0 || isLoading}
            whileHover={{ scale: currentStep === 0 ? 1 : 1.02 }}
            whileTap={{ scale: currentStep === 0 ? 1 : 0.98 }}
          >
            <ChevronLeft size={16} />
            Back
          </BackButton>

          <NextButton
            onClick={handleNext}
            disabled={
              isLoading || 
              (currentStep === 1 && selectedInterests.length === 0)
            }
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? (
              'Setting up...'
            ) : currentStep === totalSteps - 1 ? (
              <>
                Get Started
                <ArrowRight size={16} />
              </>
            ) : (
              <>
                Next
                <ChevronRight size={16} />
              </>
            )}
          </NextButton>
        </ButtonContainer>
      </OnboardingCard>
    </OnboardingContainer>
  );
};

export default OnboardingFlow;