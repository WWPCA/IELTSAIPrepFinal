/**
 * IELTS GenAI Prep - Website Production Configuration
 * Configures frontend JavaScript for production AWS endpoints
 */

// Environment detection
const isProduction = window.location.hostname !== 'localhost' && 
                    !window.location.hostname.includes('replit');

// Production configuration
const PRODUCTION_CONFIG = {
  apiBaseURL: 'https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/Prod',
  websocketURL: 'wss://your-websocket-id.execute-api.us-east-1.amazonaws.com/Prod',
  region: 'us-east-1'
};

// Development configuration
const DEVELOPMENT_CONFIG = {
  apiBaseURL: window.location.origin,
  websocketURL: `ws://${window.location.host}/ws`,
  region: 'us-east-1'
};

// Select configuration
const CONFIG = isProduction ? PRODUCTION_CONFIG : DEVELOPMENT_CONFIG;

// Global API configuration
window.IELTS_CONFIG = {
  ...CONFIG,
  
  // API endpoints
  endpoints: {
    auth: {
      login: '/api/auth/login',
      register: '/api/auth/register',
      logout: '/api/auth/logout'
    },
    assessment: {
      academicWriting: '/assessment/academic_writing',
      generalWriting: '/assessment/general_writing',
      academicSpeaking: '/assessment/academic_speaking',
      generalSpeaking: '/assessment/general_speaking'
    },
    nova: {
      writing: '/api/nova-micro/writing',
      mayaIntroduction: '/api/maya/introduction',
      mayaConversation: '/api/maya/conversation'
    },
    user: {
      profile: '/api/user/profile',
      assessments: '/api/user/assessments'
    },
    health: '/api/health'
  },
  
  // HTTP configuration
  timeout: 30000,
  retryAttempts: 3,
  
  // Session management
  sessionKey: 'ielts_session',
  sessionTimeout: 3600000, // 1 hour
  
  // Assessment configuration
  assessmentTypes: {
    academic_writing: {
      name: 'TrueScore® GenAI Writing Assessment (Academic)',
      description: '4 Assessment Attempts • Task 1 & Task 2 • TrueScore® GenAI Evaluation',
      assessmentCount: 4,
      price: 36.00
    },
    general_writing: {
      name: 'TrueScore® GenAI Writing Assessment (General)', 
      description: '4 Assessment Attempts • Letter & Essay Assessment • TrueScore® GenAI Evaluation',
      assessmentCount: 4,
      price: 36.00
    },
    academic_speaking: {
      name: 'ClearScore® GenAI Speaking Assessment (Academic)',
      description: '4 Assessment Attempts • 3-Part Speaking Test • Maya AI Examiner',
      assessmentCount: 4,
      price: 36.00
    },
    general_speaking: {
      name: 'ClearScore® GenAI Speaking Assessment (General)',
      description: '4 Assessment Attempts • 3-Part Speaking Test • Maya AI Examiner', 
      assessmentCount: 4,
      price: 36.00
    }
  }
};

// HTTP client utility
class WebAPIClient {
  constructor() {
    this.baseURL = CONFIG.apiBaseURL;
    this.sessionId = this.getStoredSession();
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(this.sessionId && { 'Cookie': `web_session_id=${this.sessionId}` })
      },
      credentials: 'include',
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      // Handle session cookies
      const setCookie = response.headers.get('Set-Cookie');
      if (setCookie && setCookie.includes('web_session_id')) {
        const sessionMatch = setCookie.match(/web_session_id=([^;]+)/);
        if (sessionMatch) {
          this.sessionId = sessionMatch[1];
          this.storeSession(this.sessionId);
        }
      }

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401) {
          this.clearSession();
          window.location.href = '/login';
        }
        throw new Error(data.message || `HTTP ${response.status}`);
      }

      return data;

    } catch (error) {
      console.error('API Request Failed:', { url, error: error.message });
      throw error;
    }
  }

  // Authentication methods
  async login(email, password) {
    const response = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    if (response.success && response.redirect_url) {
      window.location.href = response.redirect_url;
    }

    return response;
  }

  async getUserProfile() {
    return await this.request('/api/user/profile');
  }

  async getUserAssessments() {
    return await this.request('/api/user/assessments');
  }

  // Assessment methods
  async getAssessment(type) {
    return await this.request(`/assessment/${type}`);
  }

  async submitWriting(essayText, prompt, assessmentType) {
    return await this.request('/api/nova-micro/writing', {
      method: 'POST',
      body: JSON.stringify({
        essay_text: essayText,
        prompt: prompt,
        assessment_type: assessmentType
      })
    });
  }

  async startMayaConversation(assessmentType) {
    return await this.request('/api/maya/introduction', {
      method: 'POST',
      body: JSON.stringify({ assessment_type: assessmentType })
    });
  }

  async sendMayaMessage(message, assessmentType) {
    return await this.request('/api/maya/conversation', {
      method: 'POST',
      body: JSON.stringify({
        user_message: message,
        assessment_type: assessmentType
      })
    });
  }

  // Session management
  getStoredSession() {
    return localStorage.getItem('ielts_session_id');
  }

  storeSession(sessionId) {
    localStorage.setItem('ielts_session_id', sessionId);
  }

  clearSession() {
    localStorage.removeItem('ielts_session_id');
    this.sessionId = null;
  }
}

// Nova Sonic WebSocket client for website
class NovaWebSocketClient {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.messageHandlers = new Map();
  }

  connect() {
    return new Promise((resolve, reject) => {
      const wsUrl = `${CONFIG.websocketURL}?session=${this.getSessionId()}`;
      
      try {
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
          this.isConnected = true;
          console.log('Nova WebSocket connected');
          resolve();
        };

        this.socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        };

        this.socket.onclose = () => {
          this.isConnected = false;
          console.log('Nova WebSocket disconnected');
        };

        this.socket.onerror = (error) => {
          console.error('Nova WebSocket error:', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  sendMessage(message) {
    if (this.isConnected && this.socket) {
      this.socket.send(JSON.stringify(message));
    }
  }

  handleMessage(data) {
    const handler = this.messageHandlers.get(data.type);
    if (handler) {
      handler(data);
    }
  }

  onMessage(type, handler) {
    this.messageHandlers.set(type, handler);
  }

  getSessionId() {
    return localStorage.getItem('ielts_session_id');
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
    }
  }
}

// Global instances
window.apiClient = new WebAPIClient();
window.novaWebSocket = new NovaWebSocketClient();

// Utility functions
window.showToast = function(message, type = 'info') {
  // Create toast notification
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    border-radius: 4px;
    color: white;
    font-weight: 500;
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
    background-color: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
  `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => document.body.removeChild(toast), 300);
  }, 3000);
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  console.log('IELTS GenAI Prep initialized for:', isProduction ? 'Production' : 'Development');
  console.log('API Base URL:', CONFIG.apiBaseURL);
});

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CONFIG, WebAPIClient, NovaWebSocketClient };
}