import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

interface User {
  id: string;
  username: string;
  is_admin: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (accessToken: string, refreshToken: string) => void;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        // Decode token to get user info
        const tokenPayload = JSON.parse(atob(token.split('.')[1]));
        
        // Check if token is expired
        if (tokenPayload.exp * 1000 > Date.now()) {
          setUser({
            id: tokenPayload.sub,
            username: tokenPayload.username,
            is_admin: tokenPayload.is_admin,
          });
          setIsAuthenticated(true);
        } else {
          // Token expired, try to refresh
          refreshToken();
        }
      } catch (error) {
        console.error('Invalid token:', error);
        logout();
      }
    }
  }, []);

  const login = (accessToken: string, refreshToken: string) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    
    try {
      const tokenPayload = JSON.parse(atob(accessToken.split('.')[1]));
      setUser({
        id: tokenPayload.sub,
        username: tokenPayload.username,
        is_admin: tokenPayload.is_admin,
      });
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Invalid token:', error);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
    navigate('/login');
  };

  const refreshToken = async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) {
      logout();
      return;
    }

    try {
      // Use apiClient for consistent API calls
      const response = await apiClient.post('/auth/refresh', { refresh_token: refresh });
      const data = response.data;

      login(data.access_token, data.refresh_token);
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
    }
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
};