'use client';

/**
 * Authentication context provider
 */

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { authAPI } from '@/lib/auth';
import { 
  AuthState, 
  AuthContextType, 
  LoginRequest, 
  RegisterRequest, 
  User,
  ApiKeyResponse
} from '@/types/auth';

// Auth actions
type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_TOKENS'; payload: { accessToken: string; refreshToken: string } }
  | { type: 'CLEAR_AUTH' }
  | { type: 'SET_AUTHENTICATED'; payload: boolean };

// Initial state
const initialState: AuthState = {
  user: null,
  isLoading: true,
  isAuthenticated: false,
  accessToken: null,
  refreshToken: null,
};

// Auth reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    
    case 'SET_USER':
      return { 
        ...state, 
        user: action.payload,
        isAuthenticated: !!action.payload,
        isLoading: false
      };
    
    case 'SET_TOKENS':
      return {
        ...state,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
        isAuthenticated: true,
      };
    
    case 'CLEAR_AUTH':
      return {
        ...initialState,
        isLoading: false,
      };
    
    case 'SET_AUTHENTICATED':
      return { ...state, isAuthenticated: action.payload };
    
    default:
      return state;
  }
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize authentication state
  useEffect(() => {
    const initAuth = async () => {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      try {
        if (authAPI.isAuthenticated()) {
          const user = await authAPI.getCurrentUser();
          dispatch({ type: 'SET_USER', payload: user });
        } else {
          dispatch({ type: 'SET_LOADING', payload: false });
        }
      } catch (error) {
        console.warn('Authentication initialization failed:', error);
        dispatch({ type: 'CLEAR_AUTH' });
      }
    };

    initAuth();
  }, []);

  // Login function
  const login = async (credentials: LoginRequest): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const response = await authAPI.login(credentials);
      dispatch({ 
        type: 'SET_TOKENS', 
        payload: { 
          accessToken: response.access_token, 
          refreshToken: response.refresh_token 
        } 
      });
      dispatch({ type: 'SET_USER', payload: response.user });
    } catch (error) {
      dispatch({ type: 'SET_LOADING', payload: false });
      throw error;
    }
  };

  // Register function
  const register = async (data: RegisterRequest): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const response = await authAPI.register(data);
      dispatch({ 
        type: 'SET_TOKENS', 
        payload: { 
          accessToken: response.access_token, 
          refreshToken: response.refresh_token 
        } 
      });
      dispatch({ type: 'SET_USER', payload: response.user });
    } catch (error) {
      dispatch({ type: 'SET_LOADING', payload: false });
      throw error;
    }
  };

  // Logout function
  const logout = async (): Promise<void> => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.warn('Logout failed:', error);
    } finally {
      dispatch({ type: 'CLEAR_AUTH' });
    }
  };

  // Refresh access token
  const refreshAccessToken = async (): Promise<void> => {
    try {
      const response = await authAPI.refreshToken();
      dispatch({ 
        type: 'SET_TOKENS', 
        payload: { 
          accessToken: response.access_token, 
          refreshToken: response.refresh_token 
        } 
      });
      dispatch({ type: 'SET_USER', payload: response.user });
    } catch (error) {
      dispatch({ type: 'CLEAR_AUTH' });
      throw error;
    }
  };

  // Generate API key
  const generateApiKey = async (name: string): Promise<ApiKeyResponse> => {
    const response = await authAPI.generateApiKey({ name });
    
    // Refresh user data to get updated api_key_name
    if (state.user) {
      const updatedUser = await authAPI.getCurrentUser();
      dispatch({ type: 'SET_USER', payload: updatedUser });
    }
    
    return response;
  };

  // Revoke API key
  const revokeApiKey = async (): Promise<void> => {
    await authAPI.revokeApiKey();
    
    // Refresh user data to remove api_key_name
    if (state.user) {
      const updatedUser = await authAPI.getCurrentUser();
      dispatch({ type: 'SET_USER', payload: updatedUser });
    }
  };

  // Update profile
  const updateProfile = async (data: Partial<User>): Promise<void> => {
    const updatedUser = await authAPI.updateProfile(data);
    dispatch({ type: 'SET_USER', payload: updatedUser });
  };

  const contextValue: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshAccessToken,
    generateApiKey,
    revokeApiKey,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}