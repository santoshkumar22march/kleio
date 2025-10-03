/**
 * Axios API client for backend communication
 * Automatically includes Firebase token in all requests
 */

import axios from 'axios';
import { auth } from './firebase';

// Base URL from environment variable
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds (AI endpoints can be slow)
});

// Request interceptor to add Firebase token
api.interceptors.request.use(
  async (config) => {
    // Get current user
    const user = auth.currentUser;
    
    if (user) {
      try {
        // Get fresh token
        const token = await user.getIdToken();
        
        // Add to Authorization header
        config.headers.Authorization = `Bearer ${token}`;
      } catch (error) {
        console.error('Failed to get Firebase token:', error);
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      if (status === 401) {
        // Unauthorized - token expired or invalid
        console.error('Unauthorized. Please log in again.');
        // You might want to redirect to login here
        // window.location.href = '/login';
      } else if (status === 403) {
        console.error('Forbidden. You do not have access.');
      } else if (status === 404) {
        console.error('Resource not found.');
      } else if (status >= 500) {
        console.error('Server error. Please try again later.');
      }
      
      // Include error details
      error.message = data?.detail || error.message;
    } else if (error.request) {
      // Request made but no response
      console.error('No response from server. Check your connection.');
      error.message = 'Network error. Please check your internet connection.';
    }
    
    return Promise.reject(error);
  }
);

export default api;

