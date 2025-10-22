/**
 * IELTS GenAI Prep - Mobile API Client
 * Production-ready API client for iOS/Android apps
 */

import { API_CONFIG, ENDPOINTS, HTTP_CONFIG, Logger } from './mobile-app-config.js';

class APIClient {
  constructor() {
    this.baseURL = API_CONFIG.baseURL;
    this.timeout = API_CONFIG.timeout;
    this.sessionToken = null;
  }

  // Generic HTTP request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      method: 'GET',
      headers: {
        ...HTTP_CONFIG.headers,
        ...(this.sessionToken && { 'Authorization': `Bearer ${this.sessionToken}` })
      },
      timeout: this.timeout,
      ...options
    };

    Logger.debug('API Request', { url, method: config.method });

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP ${response.status}`);
      }

      Logger.debug('API Response', { status: response.status, data });
      return data;

    } catch (error) {
      Logger.error('API Request Failed', { url, error: error.message });
      throw error;
    }
  }

  // Authentication methods
  async register(userData) {
    const response = await this.request(ENDPOINTS.auth.register, {
      method: 'POST',
      body: JSON.stringify({
        email: userData.email,
        password: userData.password,
        confirm_password: userData.confirmPassword,
        terms_accepted: userData.termsAccepted,
        privacy_accepted: userData.privacyAccepted
      })
    });

    if (response.success && response.session_id) {
      this.sessionToken = response.session_id;
    }

    return response;
  }

  async login(email, password) {
    const response = await this.request(ENDPOINTS.auth.login, {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    if (response.success && response.session_id) {
      this.sessionToken = response.session_id;
    }

    return response;
  }

  async logout() {
    try {
      await this.request(ENDPOINTS.auth.logout, { method: 'POST' });
    } finally {
      this.sessionToken = null;
    }
  }

  // Purchase verification methods
  async verifyApplePurchase(receiptData, productId) {
    return await this.request(ENDPOINTS.purchase.apple, {
      method: 'POST',
      body: JSON.stringify({
        receipt_data: receiptData,
        product_id: productId,
        user_email: this.getCurrentUserEmail()
      })
    });
  }

  async verifyGooglePurchase(purchaseToken, productId) {
    return await this.request(ENDPOINTS.purchase.google, {
      method: 'POST',
      body: JSON.stringify({
        purchase_token: purchaseToken,
        product_id: productId,
        user_email: this.getCurrentUserEmail()
      })
    });
  }

  // Assessment access methods
  async getWritingAssessment(type = 'academic') {
    const endpoint = type === 'academic' 
      ? ENDPOINTS.assessment.writing.academic 
      : ENDPOINTS.assessment.writing.general;
    
    return await this.request(endpoint);
  }

  async getSpeakingAssessment(type = 'academic') {
    const endpoint = type === 'academic'
      ? ENDPOINTS.assessment.speaking.academic
      : ENDPOINTS.assessment.speaking.general;
    
    return await this.request(endpoint);
  }

  // Nova AI assessment methods
  async submitWritingAssessment(essayText, prompt, assessmentType) {
    return await this.request(ENDPOINTS.nova.writing, {
      method: 'POST',
      body: JSON.stringify({
        essay_text: essayText,
        prompt: prompt,
        assessment_type: assessmentType,
        user_email: this.getCurrentUserEmail()
      })
    });
  }

  async startMayaIntroduction(assessmentType) {
    return await this.request(ENDPOINTS.nova.mayaIntroduction, {
      method: 'POST',
      body: JSON.stringify({
        assessment_type: assessmentType,
        user_email: this.getCurrentUserEmail()
      })
    });
  }

  async sendMayaMessage(message, assessmentType) {
    return await this.request(ENDPOINTS.nova.mayaConversation, {
      method: 'POST',
      body: JSON.stringify({
        user_message: message,
        assessment_type: assessmentType,
        user_email: this.getCurrentUserEmail()
      })
    });
  }

  // User management methods
  async getUserProfile() {
    return await this.request(ENDPOINTS.user.profile);
  }

  async getUserAssessments() {
    return await this.request(ENDPOINTS.user.assessments);
  }

  async getUserPurchases() {
    return await this.request(ENDPOINTS.user.purchases);
  }

  // Health check
  async healthCheck() {
    return await this.request(ENDPOINTS.health);
  }

  // Helper methods
  getCurrentUserEmail() {
    // Return stored user email from secure storage
    return this.userEmail || null;
  }

  setUserSession(email, sessionToken) {
    this.userEmail = email;
    this.sessionToken = sessionToken;
  }

  clearSession() {
    this.userEmail = null;
    this.sessionToken = null;
  }
}

// WebSocket client for Nova Sonic streaming
class NovaWebSocketClient {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect(sessionToken) {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${API_CONFIG.websocketURL}?session=${sessionToken}`;
        this.socket = new WebSocket(wsUrl, ['nova-sonic']);

        this.socket.onopen = () => {
          this.isConnected = true;
          this.reconnectAttempts = 0;
          Logger.info('Nova WebSocket connected');
          resolve();
        };

        this.socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        };

        this.socket.onclose = () => {
          this.isConnected = false;
          Logger.info('Nova WebSocket disconnected');
          this.attemptReconnect(sessionToken);
        };

        this.socket.onerror = (error) => {
          Logger.error('Nova WebSocket error', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  sendAudioChunk(audioData) {
    if (this.isConnected && this.socket) {
      this.socket.send(JSON.stringify({
        type: 'audio',
        data: audioData
      }));
    }
  }

  sendMessage(message) {
    if (this.isConnected && this.socket) {
      this.socket.send(JSON.stringify(message));
    }
  }

  handleMessage(data) {
    switch (data.type) {
      case 'maya_response':
        this.onMayaResponse(data);
        break;
      case 'audio_response':
        this.onAudioResponse(data);
        break;
      case 'assessment_result':
        this.onAssessmentResult(data);
        break;
      default:
        Logger.debug('Unknown WebSocket message', data);
    }
  }

  onMayaResponse(data) {
    // Handle Maya's text response
  }

  onAudioResponse(data) {
    // Handle Maya's audio response
  }

  onAssessmentResult(data) {
    // Handle assessment completion
  }

  attemptReconnect(sessionToken) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        Logger.info(`Attempting WebSocket reconnect ${this.reconnectAttempts}`);
        this.connect(sessionToken);
      }, 5000);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
    }
  }
}

// Export singleton instances
export const apiClient = new APIClient();
export const novaWebSocket = new NovaWebSocketClient();

export default apiClient;