import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('expensesense_token');
      if (token) {
        try {
          const res = await api.get('/auth/me');
          setUser(res.data);
        } catch (err) {
          console.error("Auth check failed:", err);
          localStorage.removeItem('expensesense_token');
        }
      }
      setLoading(false);
    };
    fetchUser();
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { access_token, user } = res.data;
    localStorage.setItem('expensesense_token', access_token);
    setUser(user);
    return user;
  };

  const register = async (userData) => {
    const res = await api.post('/auth/register', userData);
    const { access_token, user } = res.data;
    localStorage.setItem('expensesense_token', access_token);
    setUser(user);
    return user;
  };

  const logout = () => {
    localStorage.removeItem('expensesense_token');
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
