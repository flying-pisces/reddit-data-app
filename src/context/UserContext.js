import React, { createContext, useContext, useReducer } from 'react';

const UserContext = createContext();

const userReducer = (state, action) => {
  switch (action.type) {
    case 'SET_PREFERENCES':
      return {
        ...state,
        preferences: action.payload
      };
    case 'UPDATE_INTERESTS':
      return {
        ...state,
        preferences: {
          ...state.preferences,
          interests: action.payload
        }
      };
    case 'RECORD_INTERACTION':
      return {
        ...state,
        interactions: [
          ...state.interactions,
          {
            ...action.payload,
            timestamp: new Date().toISOString()
          }
        ]
      };
    case 'UPDATE_PERSONALIZATION':
      return {
        ...state,
        personalization: {
          ...state.personalization,
          ...action.payload
        }
      };
    default:
      return state;
  }
};

const initialState = {
  preferences: {
    interests: [],
    subreddits: [],
    notificationSettings: {
      pushEnabled: true,
      emailEnabled: false
    }
  },
  interactions: [],
  personalization: {
    contentScores: {},
    categoryPreferences: {},
    timePreferences: {}
  }
};

export const UserProvider = ({ children }) => {
  const [state, dispatch] = useReducer(userReducer, initialState);

  const updatePreferences = (preferences) => {
    dispatch({ type: 'SET_PREFERENCES', payload: preferences });
  };

  const updateInterests = (interests) => {
    dispatch({ type: 'UPDATE_INTERESTS', payload: interests });
  };

  const recordInteraction = (interaction) => {
    dispatch({ type: 'RECORD_INTERACTION', payload: interaction });
  };

  const updatePersonalization = (data) => {
    dispatch({ type: 'UPDATE_PERSONALIZATION', payload: data });
  };

  const value = {
    ...state,
    updatePreferences,
    updateInterests,
    recordInteraction,
    updatePersonalization
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export default UserContext;