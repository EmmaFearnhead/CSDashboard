import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  // Check if user is already authenticated on app load
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      verifyToken(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async (tokenToVerify) => {
    try {
      const response = await axios.post(
        `${API}/auth/verify`,
        {},
        {
          headers: {
            Authorization: `Bearer ${tokenToVerify}`
          }
        }
      );
      
      if (response.status === 200) {
        setToken(tokenToVerify);
        setIsAuthenticated(true);
        localStorage.setItem('auth_token', tokenToVerify);
        
        // Set default authorization header for all future requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${tokenToVerify}`;
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('auth_token');
      delete axios.defaults.headers.common['Authorization'];
      setToken(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (password) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/auth/login`, {
        password: password
      });

      if (response.status === 200) {
        const { access_token } = response.data;
        setToken(access_token);
        setIsAuthenticated(true);
        localStorage.setItem('auth_token', access_token);
        
        // Set default authorization header for all future requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        
        return { success: true };
      }
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setIsAuthenticated(false);
    localStorage.removeItem('auth_token');
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    isAuthenticated,
    loading,
    token,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};