/**
 * IELTS GenAI Prep - Mobile App Production Configuration
 * Configures API endpoints and authentication for iOS/Android apps
 */

// Environment detection
const isDevelopment = __DEV__ || process.env.NODE_ENV === 'development';
const isStaging = process.env.ENVIRONMENT === 'staging';

// Production API configuration
const PRODUCTION_CONFIG = {
  // Primary API Gateway endpoint - LIVE PRODUCTION DEPLOYMENT
  baseURL: 'https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod',
  
  // WebSocket endpoint for Nova Sonic streaming
  websocketURL: 'wss://your-websocket-id.execute-api.us-east-1.amazonaws.com/Prod',
  
  // AWS region for all services
  region: 'us-east-1',
  
  // Timeout configurations
  timeout: 30000,
  uploadTimeout: 60000,
  
  // Retry configuration
  retryAttempts: 3,
  retryDelay: 1000
};

// Staging configuration
const STAGING_CONFIG = {
  baseURL: 'https://staging-api-gateway-id.execute-api.us-east-1.amazonaws.com/Prod',
  websocketURL: 'wss://staging-websocket-id.execute-api.us-east-1.amazonaws.com/Prod',
  region: 'us-east-1',
  timeout: 30000,
  uploadTimeout: 60000,
  retryAttempts: 3,
  retryDelay: 1000
};

// Development configuration (Replit environment)
const DEVELOPMENT_CONFIG = {
  baseURL: 'http://localhost:5000',
  websocketURL: 'ws://localhost:5000/ws',
  region: 'us-east-1',
  timeout: 30000,
  uploadTimeout: 60000,
  retryAttempts: 3,
  retryDelay: 1000
};

// Select configuration based on environment
export const API_CONFIG = isDevelopment 
  ? DEVELOPMENT_CONFIG 
  : isStaging 
    ? STAGING_CONFIG 
    : PRODUCTION_CONFIG;

// API Endpoints
export const ENDPOINTS = {
  // Authentication
  auth: {
    register: '/api/auth/register',
    login: '/api/auth/login',
    logout: '/api/auth/logout'
  },
  
  // Purchase verification
  purchase: {
    apple: '/api/purchase/apple/verify',
    google: '/api/purchase/google/verify'
  },
  
  // Assessment access
  assessment: {
    writing: {
      academic: '/assessment/academic_writing',
      general: '/assessment/general_writing'
    },
    speaking: {
      academic: '/assessment/academic_speaking',
      general: '/assessment/general_speaking'
    }
  },
  
  // Nova AI services
  nova: {
    writing: '/api/nova-micro/writing',
    writingSubmit: '/api/nova-micro/submit',
    mayaIntroduction: '/api/maya/introduction',
    mayaConversation: '/api/maya/conversation'
  },
  
  // User management
  user: {
    profile: '/api/user/profile',
    assessments: '/api/user/assessments',
    purchases: '/api/user/purchases'
  },
  
  // System
  health: '/api/health'
};

// Assessment product configuration
export const ASSESSMENT_PRODUCTS = {
  academic_writing: {
    id: 'academic_writing_assessment',
    name: 'TrueScore® GenAI Writing Assessment (Academic)',
    description: '4 Assessment Attempts • Task 1 & Task 2 • TrueScore® GenAI Evaluation • Official IELTS Criteria • Detailed Band Score Feedback • Writing Improvement Recommendations',
    price: 36.00,
    currency: 'USD',
    assessmentCount: 4,
    appleProductId: 'com.ieltsgenaiprep.academic.writing',
    googleProductId: 'academic_writing_assessment'
  },
  general_writing: {
    id: 'general_writing_assessment',
    name: 'TrueScore® GenAI Writing Assessment (General)',
    description: '4 Assessment Attempts • Letter & Essay Assessment • TrueScore® GenAI Evaluation • Official IELTS Criteria • Detailed Band Score Feedback • Writing Improvement Recommendations',
    price: 36.00,
    currency: 'USD',
    assessmentCount: 4,
    appleProductId: 'com.ieltsgenaiprep.general.writing',
    googleProductId: 'general_writing_assessment'
  },
  academic_speaking: {
    id: 'academic_speaking_assessment',
    name: 'ClearScore® GenAI Speaking Assessment (Academic)',
    description: '4 Assessment Attempts • 3-Part Speaking Test • Maya AI Examiner • Real-Time Conversation • Official IELTS Criteria • Detailed Band Score Feedback • Speaking Improvement Recommendations',
    price: 36.00,
    currency: 'USD',
    assessmentCount: 4,
    appleProductId: 'com.ieltsgenaiprep.academic.speaking',
    googleProductId: 'academic_speaking_assessment'
  },
  general_speaking: {
    id: 'general_speaking_assessment',
    name: 'ClearScore® GenAI Speaking Assessment (General)',
    description: '4 Assessment Attempts • 3-Part Speaking Test • Maya AI Examiner • Real-Time Conversation • Official IELTS Criteria • Detailed Band Score Feedback • Speaking Improvement Recommendations',
    price: 36.00,
    currency: 'USD',
    assessmentCount: 4,
    appleProductId: 'com.ieltsgenaiprep.general.speaking',
    googleProductId: 'general_speaking_assessment'
  }
};

// HTTP client configuration
export const HTTP_CONFIG = {
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'IELTSGenAIPrep-Mobile/1.0'
  },
  
  // Request interceptor for adding authentication
  interceptors: {
    request: (config) => {
      // Add session token if available
      const sessionToken = getStoredSessionToken();
      if (sessionToken) {
        config.headers['Authorization'] = `Bearer ${sessionToken}`;
      }
      return config;
    },
    
    response: (response) => {
      // Handle session expiration
      if (response.status === 401) {
        clearStoredSession();
        // Redirect to login
      }
      return response;
    }
  }
};

// WebSocket configuration for Nova Sonic
export const WEBSOCKET_CONFIG = {
  protocols: ['nova-sonic'],
  heartbeatInterval: 30000,
  reconnectInterval: 5000,
  maxReconnectAttempts: 5,
  
  // Audio configuration for Nova Sonic streaming
  audio: {
    sampleRate: 16000,
    channels: 1,
    bitsPerSample: 16,
    format: 'pcm'
  }
};

// Helper functions for session management
export const getStoredSessionToken = () => {
  // Implementation depends on platform (AsyncStorage, SecureStore, etc.)
  return null; // Placeholder
};

export const clearStoredSession = () => {
  // Clear stored session data
};

// Environment-specific logging
export const Logger = {
  debug: (message, data) => {
    if (isDevelopment) {
      console.log(`[DEBUG] ${message}`, data);
    }
  },
  
  info: (message, data) => {
    console.log(`[INFO] ${message}`, data);
  },
  
  error: (message, error) => {
    console.error(`[ERROR] ${message}`, error);
    // In production, send to crash reporting service
  }
};

// Export default configuration
export default {
  API_CONFIG,
  ENDPOINTS,
  ASSESSMENT_PRODUCTS,
  HTTP_CONFIG,
  WEBSOCKET_CONFIG,
  Logger
};