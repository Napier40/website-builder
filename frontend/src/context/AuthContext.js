import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

export const AuthContext = createContext();

/**
 * Custom hook for consuming the auth context.
 * Usage:   const { user, login, logout, isAuthenticated } = useAuth();
 */
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an <AuthProvider>');
  }
  return ctx;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Keep axios Authorization header in sync with the token. This runs
  // as an effect (not during render) so we don't violate React's
  // no-side-effects-in-render rule, and so it re-runs whenever the
  // token changes (login / logout / token-refresh).
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Load user
  const loadUser = useCallback(async () => {
    try {
      if (token) {
        const res = await axios.get('/api/auth/me');
        setUser(res.data.data.user);
        setIsAuthenticated(true);
      }
    } catch (err) {
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      setError(err.response?.data?.message || 'Authentication error');
    }
    setLoading(false);
  }, [token]);

  // Register user
  const register = async (formData) => {
    try {
      const res = await axios.post('/api/auth/register', formData);
      const token = res.data.data.token;
      localStorage.setItem('token', token);
      setToken(token);
      // loadUser will run automatically via useEffect when token changes
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
      return { success: false, error: err.response?.data?.message || 'Registration failed' };
    }
  };

  // Login user
  const login = async (formData) => {
    try {
      const res = await axios.post('/api/auth/login', formData);
      const token = res.data.data.token;
      const user  = res.data.data.user;
      if (!token) {
        throw new Error('Login response did not include a token');
      }
      localStorage.setItem('token', token);
      // Set axios header immediately so the next /api/auth/me call authenticates
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Optimistically set the user so the UI can flip before loadUser confirms
      setUser(user);
      setIsAuthenticated(true);
      setToken(token);  // also triggers loadUser via useEffect
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Login failed');
      return { success: false, error: err.response?.data?.message || err.message || 'Login failed' };
    }
  };

  // Logout user
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  // Update profile
  const updateProfile = async (formData) => {
    try {
      const res = await axios.put('/api/auth/profile', formData);
      setUser(res.data.data.user);
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.message || 'Update failed');
      return { success: false, error: err.response?.data?.message || 'Update failed' };
    }
  };

  // Change password
  const changePassword = async (formData) => {
    try {
      await axios.put('/api/auth/change-password', formData);
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.message || 'Password change failed');
      return { success: false, error: err.response?.data?.message || 'Password change failed' };
    }
  };

  // Clear errors
  const clearError = () => {
    setError(null);
  };

  // Load user on initial render (and whenever the token changes)
  useEffect(() => {
    loadUser();
  }, [loadUser]);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        loading,
        error,
        register,
        login,
        logout,
        updateProfile,
        changePassword,
        clearError
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};