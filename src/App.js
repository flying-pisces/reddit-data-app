import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import styled from 'styled-components';

// Components
import AuthScreen from './components/Auth/AuthScreen';
import OnboardingFlow from './components/Onboarding/OnboardingFlow';
import MainFeed from './components/Feed/MainFeed';
import LoadingScreen from './components/Common/LoadingScreen';

// Context
import { AuthProvider } from './context/AuthContext';
import { UserProvider } from './context/UserContext';

// Global Styles
const AppContainer = styled.div`
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  overflow: hidden;
`;

const GlobalStyle = styled.div`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
`;

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(false);

  useEffect(() => {
    // Initialize app and check authentication status
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Check for existing user session
      const savedUser = localStorage.getItem('reddit_insight_user');
      if (savedUser) {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setHasCompletedOnboarding(userData.hasCompletedOnboarding || false);
      }
      
      // Simulate initialization delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      setIsLoading(false);
    } catch (error) {
      console.error('App initialization error:', error);
      setIsLoading(false);
    }
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    localStorage.setItem('reddit_insight_user', JSON.stringify(userData));
  };

  const handleOnboardingComplete = (userPreferences) => {
    const updatedUser = { 
      ...user, 
      ...userPreferences, 
      hasCompletedOnboarding: true 
    };
    setUser(updatedUser);
    setHasCompletedOnboarding(true);
    localStorage.setItem('reddit_insight_user', JSON.stringify(updatedUser));
  };

  if (isLoading) {
    return (
      <AppContainer>
        <LoadingScreen />
      </AppContainer>
    );
  }

  return (
    <AppContainer>
      <GlobalStyle />
      <AuthProvider>
        <UserProvider>
          <Router>
            <Routes>
              {!user && (
                <Route 
                  path="*" 
                  element={<AuthScreen onAuthSuccess={handleAuthSuccess} />} 
                />
              )}
              
              {user && !hasCompletedOnboarding && (
                <Route 
                  path="*" 
                  element={
                    <OnboardingFlow 
                      user={user}
                      onComplete={handleOnboardingComplete} 
                    />
                  } 
                />
              )}
              
              {user && hasCompletedOnboarding && (
                <Route 
                  path="*" 
                  element={<MainFeed user={user} />} 
                />
              )}
            </Routes>
          </Router>
          <Toaster
            position="top-center"
            toastOptions={{
              duration: 3000,
              style: {
                background: '#333',
                color: '#fff',
              },
            }}
          />
        </UserProvider>
      </AuthProvider>
    </AppContainer>
  );
}

export default App;