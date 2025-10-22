/**
 * IELTS GenAI Prep - Mobile App Integration
 * Complete iOS/Android implementation with QR authentication and in-app purchases
 */

import { CapacitorConfig } from '@capacitor/core';
import { Device } from '@capacitor/device';
import { Network } from '@capacitor/network';
import { Toast } from '@capacitor/toast';
import { App } from '@capacitor/app';

// Regional API configuration for global deployment
class MobileAPIClient {
  private baseURL: string;
  private region: string;
  private sessionToken: string | null = null;
  private qrAuthToken: string | null = null;

  constructor() {
    this.detectRegionAndInitialize();
  }

  private async detectRegionAndInitialize() {
    try {
      const deviceInfo = await Device.getInfo();
      const networkInfo = await Network.getStatus();
      
      // Determine optimal region based on device location
      this.region = await this.detectOptimalRegion();
      this.baseURL = this.getRegionalEndpoint(this.region);
      
      console.log(`Initialized for region: ${this.region}`);
    } catch (error) {
      console.error('Failed to initialize API client:', error);
      // Fallback to US East
      this.region = 'us-east-1';
      this.baseURL = 'https://api-us.ieltsaiprep.com';
    }
  }

  private async detectOptimalRegion(): Promise<string> {
    const deviceInfo = await Device.getInfo();
    const locale = deviceInfo.locale || 'en-US';
    
    // Regional mapping based on device locale
    const regionMap: { [key: string]: string } = {
      'en-GB': 'eu-west-1',
      'de': 'eu-west-1',
      'fr': 'eu-west-1',
      'es': 'eu-west-1',
      'it': 'eu-west-1',
      'ja': 'ap-southeast-1',
      'ko': 'ap-southeast-1',
      'zh': 'ap-southeast-1',
      'th': 'ap-southeast-1',
      'vi': 'ap-southeast-1'
    };

    return regionMap[locale.split('-')[0]] || 'us-east-1';
  }

  private getRegionalEndpoint(region: string): string {
    const endpoints = {
      'us-east-1': 'https://api-us.ieltsaiprep.com',
      'eu-west-1': 'https://api-eu.ieltsaiprep.com',
      'ap-southeast-1': 'https://api-ap.ieltsaiprep.com'
    };
    return endpoints[region] || endpoints['us-east-1'];
  }

  async makeAPICall(endpoint: string, method = 'POST', data: any = null): Promise<any> {
    const url = `${this.baseURL}${endpoint}`;
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'IELTSGenAIPrepMobile/2.0.0',
        ...(this.sessionToken && { 'Authorization': `Bearer ${this.sessionToken}` })
      },
      ...(data && { body: JSON.stringify(data) })
    };

    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`API call to ${endpoint} failed:`, error);
      throw error;
    }
  }

  async registerUser(email: string, password: string): Promise<any> {
    return this.makeAPICall('/auth/register', 'POST', { email, password });
  }

  async loginUser(email: string, password: string): Promise<any> {
    const result = await this.makeAPICall('/auth/login', 'POST', { email, password });
    if (result.success) {
      this.sessionToken = result.token;
    }
    return result;
  }

  async generateQRTokenAfterPurchase(userEmail: string, productId: string): Promise<any> {
    return this.makeAPICall('/auth/generate-qr', 'POST', {
      user_email: userEmail,
      product_id: productId,
      purchase_verified: true
    });
  }

  async verifyApplePurchase(receiptData: string, productId: string): Promise<any> {
    return this.makeAPICall('/purchase/verify/apple', 'POST', {
      receipt_data: receiptData,
      product_id: productId
    });
  }

  async verifyGooglePurchase(purchaseToken: string, productId: string): Promise<any> {
    return this.makeAPICall('/purchase/verify/google', 'POST', {
      purchase_token: purchaseToken,
      product_id: productId
    });
  }

  async submitSpeechAssessment(audioData: Blob, assessmentType: string): Promise<any> {
    // Nova Sonic streaming always routes to us-east-1
    const novaSonicURL = 'https://api-us.ieltsaiprep.com/nova-sonic/stream';
    const formData = new FormData();
    formData.append('audio', audioData);
    formData.append('assessment_type', assessmentType);

    const response = await fetch(novaSonicURL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.sessionToken}`
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Speech assessment failed: ${response.statusText}`);
    }

    return response.json();
  }

  async submitWritingAssessment(essayText: string, prompt: string, assessmentType: string): Promise<any> {
    return this.makeAPICall('/assess-writing', 'POST', {
      essay_text: essayText,
      prompt,
      assessment_type: assessmentType
    });
  }
}

// iOS In-App Purchase Manager
class iOSPurchaseManager {
  private apiClient: MobileAPIClient;
  private products: string[] = [
    'academic_speaking_assessment',
    'academic_writing_assessment',
    'general_speaking_assessment',
    'general_writing_assessment',
    'academic_mock_test',
    'general_mock_test'
  ];

  constructor(apiClient: MobileAPIClient) {
    this.apiClient = apiClient;
  }

  async initializePurchases(): Promise<void> {
    try {
      // Initialize StoreKit for iOS
      if (window.StoreKit) {
        await window.StoreKit.initialize();
        console.log('StoreKit initialized successfully');
      }
    } catch (error) {
      console.error('Failed to initialize purchases:', error);
      throw error;
    }
  }

  async loadProducts(): Promise<any[]> {
    try {
      if (!window.StoreKit) {
        throw new Error('StoreKit not available');
      }

      const products = await window.StoreKit.loadProducts(this.products);
      return products;
    } catch (error) {
      console.error('Failed to load products:', error);
      throw error;
    }
  }

  async purchaseProduct(productId: string, userEmail: string): Promise<any> {
    try {
      await this.showToast('Processing purchase...', 'bottom');

      // Start iOS purchase flow
      const transaction = await window.StoreKit.purchaseProduct(productId);

      if (transaction.transactionState === 'purchased') {
        // Verify purchase with backend
        const verification = await this.apiClient.verifyApplePurchase(
          transaction.transactionReceipt,
          productId
        );

        if (verification.success) {
          // Generate QR token for website access
          const qrData = await this.apiClient.generateQRTokenAfterPurchase(
            userEmail,
            productId
          );

          // Add purchased product to user data through main app
          const appInstance = (window as any).appInstance;
          if (appInstance) {
            await appInstance.addPurchasedProduct(userEmail, productId);
          }
          
          await this.showPurchaseSuccessWithQR(productId, qrData);
          return { success: true, qrData, verification };
        } else {
          throw new Error('Purchase verification failed');
        }
      } else {
        throw new Error('Purchase was not completed');
      }
    } catch (error) {
      await this.showToast(`Purchase failed: ${error.message}`, 'bottom');
      throw error;
    }
  }

  private async showPurchaseSuccessWithQR(productId: string, qrData: any): Promise<void> {
    const productNames = {
      'academic_speaking_assessment': 'Academic Speaking Assessment',
      'academic_writing_assessment': 'Academic Writing Assessment',
      'general_speaking_assessment': 'General Speaking Assessment',
      'general_writing_assessment': 'General Writing Assessment',
      'academic_mock_test': 'Academic Mock Test',
      'general_mock_test': 'General Training Mock Test'
    };

    const productName = productNames[productId] || 'Assessment';

    // Create modal with QR code
    const modal = document.createElement('div');
    modal.className = 'purchase-success-modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="success-header">
          <i class="fas fa-check-circle"></i>
          <h2>Purchase Successful!</h2>
          <p>${productName} is now available</p>
        </div>
        
        <div class="qr-section">
          <h3>Access on Website</h3>
          <div class="qr-container">
            <img src="${qrData.qr_code_image}" alt="QR Code" class="qr-image">
          </div>
          <p class="qr-instructions">
            Scan this QR code on <strong>ieltsaiprep.com</strong> to access your assessment
          </p>
          <p class="qr-expiry">Code expires in 10 minutes</p>
        </div>
        
        <div class="mobile-access-section">
          <h3>Start Assessment Now</h3>
          <p>Your assessment is ready! Choose how you'd like to begin:</p>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
            <button class="btn-start-mobile" data-product="${productId}">
              Start in App
            </button>
            <button class="btn-use-web" data-product="${productId}">
              Use on Desktop
            </button>
          </div>
        </div>
        
        <div class="qr-section" style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
          <h4 style="font-size: 16px; margin-bottom: 12px;">Desktop Access</h4>
          <div class="qr-container">
            <img src="${qrData.qr_code_image}" alt="QR Code" class="qr-image">
          </div>
          <p class="qr-instructions">
            Scan this QR code on <strong>ieltsaiprep.com</strong> to access your assessment
          </p>
          <p class="qr-expiry">Code expires in 10 minutes</p>
        </div>
        
        <div class="modal-actions">
          <button class="btn-primary" onclick="this.closest('.purchase-success-modal').remove()">
            Got It!
          </button>
        </div>
      </div>
    `;

    // Add modal styles
    const styles = `
      <style>
        .purchase-success-modal {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0,0,0,0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10000;
        }
        .modal-content {
          background: white;
          border-radius: 16px;
          padding: 24px;
          max-width: 350px;
          width: 90%;
          text-align: center;
        }
        .success-header i {
          font-size: 48px;
          color: #28a745;
          margin-bottom: 16px;
        }
        .qr-container {
          background: #f8f9fa;
          padding: 16px;
          border-radius: 12px;
          margin: 16px 0;
        }
        .qr-image {
          width: 200px;
          height: 200px;
          border-radius: 8px;
        }
        .qr-instructions {
          font-size: 14px;
          color: #6c757d;
          margin: 8px 0;
        }
        .qr-expiry {
          font-size: 12px;
          color: #dc3545;
          font-weight: 500;
        }
        .modal-actions {
          margin-top: 24px;
        }
        .btn-primary, .btn-secondary {
          padding: 12px 24px;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          margin: 4px;
          cursor: pointer;
        }
        .btn-primary {
          background: #007bff;
          color: white;
        }
        .btn-secondary {
          background: #6c757d;
          color: white;
        }
      </style>
    `;

    document.head.insertAdjacentHTML('beforeend', styles);
    document.body.appendChild(modal);

    // Set up event listeners for the new modal buttons
    const startMobileBtn = modal.querySelector('.btn-start-mobile');
    const useWebBtn = modal.querySelector('.btn-use-web');

    if (startMobileBtn) {
      startMobileBtn.addEventListener('click', async () => {
        modal.remove();
        const assessmentType = productId.includes('speaking') ? 'speaking' : 'writing';
        
        // Get the main app instance and start assessment
        const appInstance = (window as any).appInstance;
        if (appInstance) {
          await appInstance.startAssessmentInApp(productId, assessmentType);
        }
      });
    }

    if (useWebBtn) {
      useWebBtn.addEventListener('click', () => {
        modal.remove();
        // Show web access guide
        const appInstance = (window as any).appInstance;
        if (appInstance) {
          appInstance.showWebAccessGuide(productId);
        }
      });
    }

    // Auto-close after 5 minutes
    setTimeout(() => {
      if (modal.parentNode) {
        modal.remove();
      }
    }, 300000);
  }

  async restorePurchases(): Promise<any[]> {
    try {
      if (!window.StoreKit) {
        throw new Error('StoreKit not available');
      }

      const transactions = await window.StoreKit.restoreTransactions();
      return transactions;
    } catch (error) {
      console.error('Failed to restore purchases:', error);
      throw error;
    }
  }

  private async showToast(message: string, position: 'top' | 'center' | 'bottom' = 'bottom'): Promise<void> {
    try {
      await Toast.show({
        text: message,
        duration: 'short',
        position
      });
    } catch (error) {
      console.log(message); // Fallback to console
    }
  }
}

// QR Code Scanner for website authentication
class QRCodeScanner {
  private apiClient: MobileAPIClient;
  private isScanning = false;

  constructor(apiClient: MobileAPIClient) {
    this.apiClient = apiClient;
  }

  async startScanning(): Promise<string> {
    if (this.isScanning) {
      throw new Error('Already scanning');
    }

    this.isScanning = true;

    try {
      // Use Capacitor Camera plugin for QR scanning
      if (!window.BarcodeScanner) {
        throw new Error('QR Scanner not available');
      }

      const result = await window.BarcodeScanner.startScan();
      
      if (result.hasContent) {
        return result.content; // Return raw QR content for processing
      } else {
        throw new Error('No QR code detected');
      }
    } finally {
      this.isScanning = false;
    }
  }

  async authenticateWithWebsite(qrData: string, userEmail: string, userProducts: string[]): Promise<boolean> {
    try {
      const response = await this.apiClient.makeAPICall('/api/mobile/scan-qr', 'POST', {
        qr_data: qrData,
        user_email: userEmail,
        user_products: userProducts
      });

      if (response.success) {
        await this.showToast(`Website authenticated for ${userEmail}`, 'center');
        return true;
      } else {
        await this.showToast(response.error || 'Authentication failed', 'center');
        return false;
      }
    } catch (error) {
      console.error('Website authentication failed:', error);
      await this.showToast('Network error during authentication', 'center');
      return false;
    }
  }

  private async showToast(message: string, position: 'top' | 'center' | 'bottom' = 'bottom'): Promise<void> {
    try {
      if (window.Capacitor && window.Capacitor.Plugins.Toast) {
        await window.Capacitor.Plugins.Toast.show({
          text: message,
          duration: 'short',
          position: position
        });
      } else {
        console.log(`Toast: ${message}`);
      }
    } catch (error) {
      console.log(`Toast fallback: ${message}`);
    }
  }
}

// Main Application Class
class IELTSGenAIPrepApp {
  private apiClient: MobileAPIClient;
  private purchaseManager: iOSPurchaseManager;
  private qrScanner: QRCodeScanner;
  private currentUser: any = null;

  constructor() {
    this.apiClient = new MobileAPIClient();
    this.purchaseManager = new iOSPurchaseManager(this.apiClient);
    this.qrScanner = new QRCodeScanner(this.apiClient);
  }

  async initialize(): Promise<void> {
    try {
      // Initialize all components
      await this.purchaseManager.initializePurchases();
      
      // Set up the home screen UI
      this.setupHomeScreen();
      
      // Set up app state listeners
      App.addListener('appStateChange', ({ isActive }) => {
        if (isActive) {
          this.handleAppResume();
        }
      });

      // Set up network listeners
      Network.addListener('networkStatusChange', (status) => {
        if (!status.connected) {
          this.showOfflineMessage();
        }
      });

      console.log('IELTS GenAI Prep app initialized successfully');
    } catch (error) {
      console.error('App initialization failed:', error);
      throw error;
    }
  }

  private setupHomeScreen(): void {
    const homeContainer = document.getElementById('home-screen') || document.body;
    
    const homeScreenHTML = `
      <div id="ielts-home-screen" style="padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <!-- Top Half: Web Version Access Information -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 16px; margin-bottom: 20px; text-align: center;">
          <div style="font-size: 24px; font-weight: bold; margin-bottom: 12px;">
            📱 ➜ 💻 Access Anywhere
          </div>
          <div style="font-size: 16px; line-height: 1.5; margin-bottom: 16px;">
            Use your mobile purchases on desktop and laptop too!
          </div>
          <div style="background: rgba(255,255,255,0.2); padding: 16px; border-radius: 12px; margin-bottom: 16px;">
            <div style="font-size: 14px; margin-bottom: 8px;">
              <strong>After purchasing assessments:</strong>
            </div>
            <div style="font-size: 14px; line-height: 1.4;">
              1. Get your QR code from the purchase confirmation<br>
              2. Visit <strong>ieltsaiprep.com</strong> on your computer<br>
              3. Scan the QR code to access your assessments
            </div>
          </div>
          <button id="learn-more-web-access" style="background: white; color: #667eea; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; font-size: 14px;">
            Learn More About Web Access
          </button>
        </div>

        <!-- My Assessments Section -->
        <div id="my-assessments-section" style="margin-bottom: 20px; display: none;">
          <h2 style="font-size: 20px; font-weight: bold; color: #333; margin-bottom: 16px;">
            My Assessments
          </h2>
          <div id="purchased-assessments" style="display: grid; gap: 12px;">
            <!-- Purchased assessments will be loaded here -->
          </div>
        </div>

        <!-- Assessment Products Section -->
        <div id="products-section" style="margin-bottom: 20px;">
          <h2 style="font-size: 20px; font-weight: bold; color: #333; margin-bottom: 16px;">
            IELTS Assessment Products
          </h2>
          <div style="display: grid; gap: 12px;">
            ${this.generateProductCards()}
          </div>
        </div>

        <!-- QR Scanner Section -->
        <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; text-align: center;">
          <h3 style="font-size: 18px; color: #333; margin-bottom: 12px;">
            Already have web access?
          </h3>
          <p style="font-size: 14px; color: #666; margin-bottom: 16px;">
            Scan QR codes from ieltsaiprep.com to authenticate
          </p>
          <button id="qr-scan-button" style="background: #28a745; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">
            Scan QR Code
          </button>
        </div>
      </div>
    `;
    
    homeContainer.innerHTML = homeScreenHTML;
    
    // Set up event listeners
    this.setupHomeScreenListeners();
    
    // Load and display purchased assessments
    this.loadPurchasedAssessments();
  }

  private generateProductCards(): string {
    const products = [
      {
        id: 'academic_speaking_assessment',
        title: 'Academic Speaking',
        description: 'AI-powered speaking assessment with Maya examiner',
        price: '$25.00',
        note: '2 assessments'
      },
      {
        id: 'academic_writing_assessment', 
        title: 'Academic Writing',
        description: 'Comprehensive writing evaluation and feedback',
        price: '$25.00',
        note: '2 assessments'
      },
      {
        id: 'general_speaking_assessment',
        title: 'General Speaking',
        description: 'General IELTS speaking practice and assessment',
        price: '$25.00',
        note: '2 assessments'
      },
      {
        id: 'general_writing_assessment',
        title: 'General Writing',
        description: 'General IELTS writing tasks and evaluation',
        price: '$25.00',
        note: '2 assessments'
      },
      {
        id: 'academic_mock_test',
        title: 'Academic Mock Test',
        description: 'Complete IELTS Academic simulation with all 4 skills',
        price: '$99.00',
        note: '2 full tests'
      },
      {
        id: 'general_mock_test',
        title: 'General Mock Test',
        description: 'Complete IELTS General simulation with all 4 skills',
        price: '$99.00',
        note: '2 full tests'
      }
    ];

    return products.map(product => `
      <div style="background: white; border: 1px solid #e9ecef; border-radius: 12px; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <div style="flex: 1;">
            <h4 style="font-size: 16px; font-weight: 600; color: #333; margin: 0 0 8px 0;">
              ${product.title}
            </h4>
            <p style="font-size: 14px; color: #666; margin: 0 0 12px 0;">
              ${product.description}
            </p>
            <div style="font-size: 18px; font-weight: bold; color: #007bff;">
              ${product.price}
            </div>
            <div style="font-size: 12px; color: #888; margin-top: 4px;">
              ${product.note}
            </div>
          </div>
          <button class="purchase-btn" data-product="${product.id}" style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 14px; font-weight: 500; margin-left: 12px;">
            Purchase
          </button>
        </div>
      </div>
    `).join('');
  }

  private setupHomeScreenListeners(): void {
    // Learn more about web access
    const learnMoreBtn = document.getElementById('learn-more-web-access');
    if (learnMoreBtn) {
      learnMoreBtn.addEventListener('click', () => {
        this.showWebAccessInfo();
      });
    }

    // QR scanner button
    const qrScanBtn = document.getElementById('qr-scan-button');
    if (qrScanBtn) {
      qrScanBtn.addEventListener('click', () => {
        this.handleQRScan();
      });
    }

    // Purchase buttons
    const purchaseBtns = document.querySelectorAll('.purchase-btn');
    purchaseBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const productId = (e.target as HTMLElement).getAttribute('data-product');
        if (productId) {
          this.handlePurchase(productId);
        }
      });
    });
  }

  private async showWebAccessInfo(): Promise<void> {
    const modal = document.createElement('div');
    modal.innerHTML = `
      <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 20px;">
        <div style="background: white; border-radius: 16px; padding: 24px; max-width: 400px; width: 100%; max-height: 80vh; overflow-y: auto;">
          <h3 style="font-size: 20px; font-weight: bold; color: #333; margin: 0 0 16px 0; text-align: center;">
            🖥️ Web Access Guide
          </h3>
          
          <div style="margin-bottom: 20px;">
            <h4 style="font-size: 16px; font-weight: 600; color: #333; margin: 0 0 8px 0;">
              How it works:
            </h4>
            <ol style="font-size: 14px; line-height: 1.6; color: #666; padding-left: 20px;">
              <li>Purchase any assessment product in this mobile app</li>
              <li>After successful purchase, you'll receive a QR code</li>
              <li>Go to <strong>ieltsaiprep.com</strong> on your desktop or laptop</li>
              <li>Scan the QR code with this mobile app</li>
              <li>Access your purchased assessments on the web platform</li>
            </ol>
          </div>

          <div style="background: #e3f2fd; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
            <h4 style="font-size: 14px; font-weight: 600; color: #1976d2; margin: 0 0 8px 0;">
              ✨ Benefits of Web Access:
            </h4>
            <ul style="font-size: 13px; line-height: 1.5; color: #1976d2; margin: 0; padding-left: 16px;">
              <li>Larger screen for writing assessments</li>
              <li>Full keyboard support</li>
              <li>Better audio quality for speaking tests</li>
              <li>Seamless sync between mobile and web</li>
            </ul>
          </div>

          <div style="text-align: center;">
            <button id="close-web-info" style="background: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">
              Got it!
            </button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    const closeBtn = modal.querySelector('#close-web-info');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        modal.remove();
      });
    }

    // Close on backdrop click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
  }

  async handlePurchase(productId: string): Promise<void> {
    if (!this.currentUser) {
      throw new Error('User must be logged in to make purchases');
    }

    try {
      const result = await this.purchaseManager.purchaseProduct(
        productId,
        this.currentUser.email
      );

      if (result.success) {
        // Update user's purchased products
        this.currentUser.purchasedProducts = this.currentUser.purchasedProducts || [];
        this.currentUser.purchasedProducts.push(productId);
        
        // Store updated user data
        await this.saveUserData();
      }
    } catch (error) {
      console.error('Purchase handling failed:', error);
      throw error;
    }
  }

  async handleQRScan(): Promise<void> {
    try {
      // Check if user is logged in and has purchases
      if (!this.currentUser?.email) {
        await Toast.show({
          text: 'Please log in first to authenticate with website',
          duration: 'long',
          position: 'center'
        });
        return;
      }

      // Get user's purchased products
      const userProducts = this.currentUser.products || [];
      if (userProducts.length === 0) {
        await Toast.show({
          text: 'No purchased products found. Please make a purchase first.',
          duration: 'long',
          position: 'center'
        });
        return;
      }

      // Start scanning
      const qrData = await this.qrScanner.startScanning();
      
      // Authenticate with website using user's products
      const success = await this.qrScanner.authenticateWithWebsite(
        qrData,
        this.currentUser.email,
        userProducts
      );

      if (success) {
        await Toast.show({
          text: 'Website authenticated! You can now access your assessments on ieltsaiprep.com',
          duration: 'long',
          position: 'center'
        });
      } else {
        throw new Error('Authentication failed');
      }
    } catch (error) {
      await Toast.show({
        text: `QR authentication failed: ${error.message}`,
        duration: 'long',
        position: 'center'
      });
    }
  }

  private async handleAppResume(): Promise<void> {
    // Check for restored purchases
    try {
      const restoredTransactions = await this.purchaseManager.restorePurchases();
      if (restoredTransactions.length > 0) {
        console.log(`Restored ${restoredTransactions.length} purchases`);
      }
    } catch (error) {
      console.error('Failed to restore purchases:', error);
    }
  }

  private async showOfflineMessage(): Promise<void> {
    await Toast.show({
      text: 'You are offline. Some features may not be available.',
      duration: 'long',
      position: 'top'
    });
  }

  private async saveUserData(): Promise<void> {
    try {
      localStorage.setItem('ielts_user_data', JSON.stringify(this.currentUser));
    } catch (error) {
      console.error('Failed to save user data:', error);
    }
  }

  async loadUserData(): Promise<void> {
    try {
      const userData = localStorage.getItem('ielts_user_data');
      if (userData) {
        this.currentUser = JSON.parse(userData);
      }
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  }

  async addPurchasedProduct(userEmail: string, productId: string): Promise<void> {
    try {
      if (!this.currentUser) {
        this.currentUser = { email: userEmail, products: [] };
      }
      if (!this.currentUser.products) {
        this.currentUser.products = [];
      }
      if (!this.currentUser.products.includes(productId)) {
        this.currentUser.products.push(productId);
      }
      
      await this.saveUserData();
      
      // Refresh the home screen to show purchased assessments
      this.setupHomeScreen();
    } catch (error) {
      console.error('Failed to add purchased product:', error);
    }
  }

  private async loadPurchasedAssessments(): Promise<void> {
    try {
      // Load user data first
      await this.loadUserData();
      
      if (!this.currentUser?.email) {
        // No user logged in, hide purchased assessments section
        return;
      }

      const purchasedProducts = this.currentUser.products || [];
      
      if (purchasedProducts.length === 0) {
        // No purchased products, hide section
        return;
      }

      // Show purchased assessments section
      const myAssessmentsSection = document.getElementById('my-assessments-section');
      if (myAssessmentsSection) {
        myAssessmentsSection.style.display = 'block';
      }

      // Generate assessment cards for purchased products
      const purchasedContainer = document.getElementById('purchased-assessments');
      if (purchasedContainer) {
        purchasedContainer.innerHTML = this.generatePurchasedAssessmentCards(purchasedProducts);
        this.setupPurchasedAssessmentListeners();
      }

    } catch (error) {
      console.error('Failed to load purchased assessments:', error);
    }
  }

  private generatePurchasedAssessmentCards(purchasedProducts: string[]): string {
    const assessmentMap = {
      'academic_speaking_assessment': {
        title: 'ClearScore® GenAI Speaking',
        subtitle: 'Academic Training',
        icon: '🗣️',
        type: 'speaking',
        color: '#007bff'
      },
      'academic_writing_assessment': {
        title: 'TrueScore® GenAI Writing',
        subtitle: 'Academic Training', 
        icon: '✍️',
        type: 'writing',
        color: '#28a745'
      },
      'general_speaking_assessment': {
        title: 'ClearScore® GenAI Speaking',
        subtitle: 'General Training',
        icon: '🗣️',
        type: 'speaking',
        color: '#007bff'
      },
      'general_writing_assessment': {
        title: 'TrueScore® GenAI Writing',
        subtitle: 'General Training',
        icon: '✍️', 
        type: 'writing',
        color: '#28a745'
      }
    };

    return purchasedProducts.map(productId => {
      const assessment = assessmentMap[productId];
      if (!assessment) return '';

      return `
        <div style="background: white; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <div style="font-size: 24px; margin-right: 12px;">${assessment.icon}</div>
            <div style="flex: 1;">
              <div style="font-size: 16px; font-weight: bold; color: #333;">${assessment.title}</div>
              <div style="font-size: 14px; color: #666;">${assessment.subtitle}</div>
            </div>
          </div>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
            <button class="start-assessment-btn" data-product="${productId}" data-type="${assessment.type}" 
                    style="background: ${assessment.color}; color: white; border: none; padding: 10px 16px; border-radius: 8px; font-size: 14px; font-weight: 500;">
              Start in App
            </button>
            <button class="web-access-btn" data-product="${productId}" 
                    style="background: white; color: ${assessment.color}; border: 2px solid ${assessment.color}; padding: 10px 16px; border-radius: 8px; font-size: 14px; font-weight: 500;">
              Use on Web
            </button>
          </div>
        </div>
      `;
    }).join('');
  }

  private setupPurchasedAssessmentListeners(): void {
    // Start assessment in app buttons
    const startBtns = document.querySelectorAll('.start-assessment-btn');
    startBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const productId = (e.target as HTMLElement).getAttribute('data-product');
        const assessmentType = (e.target as HTMLElement).getAttribute('data-type');
        if (productId && assessmentType) {
          this.startAssessmentInApp(productId, assessmentType);
        }
      });
    });

    // Web access buttons
    const webBtns = document.querySelectorAll('.web-access-btn');
    webBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const productId = (e.target as HTMLElement).getAttribute('data-product');
        if (productId) {
          this.showWebAccessGuide(productId);
        }
      });
    });
  }

  private async startAssessmentInApp(productId: string, assessmentType: string): Promise<void> {
    try {
      if (assessmentType === 'speaking') {
        await this.startSpeakingAssessment(productId);
      } else if (assessmentType === 'writing') {
        await this.startWritingAssessment(productId);
      }
    } catch (error) {
      console.error('Failed to start assessment:', error);
      await Toast.show({
        text: `Failed to start assessment: ${error.message}`,
        duration: 'long',
        position: 'center'
      });
    }
  }

  private async startSpeakingAssessment(productId: string): Promise<void> {
    // Show speaking assessment interface
    const modal = document.createElement('div');
    modal.innerHTML = `
      <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 10000; display: flex; flex-direction: column;">
        <div style="background: #007bff; color: white; padding: 16px; display: flex; align-items: center; justify-content: space-between;">
          <h3 style="margin: 0; font-size: 18px;">Speaking Assessment</h3>
          <button id="close-speaking" style="background: none; border: none; color: white; font-size: 24px;">&times;</button>
        </div>
        
        <div style="flex: 1; padding: 20px; color: white; text-align: center; display: flex; flex-direction: column; justify-content: center;">
          <div style="font-size: 48px; margin-bottom: 20px;">🗣️</div>
          <h2 style="margin-bottom: 16px;">AI Conversation with Maya</h2>
          <p style="margin-bottom: 30px; line-height: 1.5;">
            Start a natural conversation with Maya, your AI IELTS examiner. 
            She'll assess your speaking skills in real-time.
          </p>
          
          <button id="start-speaking-btn" style="background: #28a745; color: white; border: none; padding: 16px 32px; border-radius: 12px; font-size: 18px; font-weight: bold; margin-bottom: 16px;">
            Start Conversation
          </button>
          
          <p style="font-size: 14px; opacity: 0.8;">
            Make sure you're in a quiet environment with good microphone access
          </p>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Set up event listeners
    document.getElementById('close-speaking')?.addEventListener('click', () => {
      modal.remove();
    });

    document.getElementById('start-speaking-btn')?.addEventListener('click', async () => {
      try {
        // Start Nova Sonic conversation
        await this.apiClient.submitSpeechAssessment(new Blob(), productId);
        await Toast.show({
          text: 'Speaking assessment started! Continue conversation with Maya.',
          duration: 'long',
          position: 'center'
        });
      } catch (error) {
        await Toast.show({
          text: 'Failed to start conversation. Please try again.',
          duration: 'long',
          position: 'center'
        });
      }
    });
  }

  private async startWritingAssessment(productId: string): Promise<void> {
    // Show writing assessment interface
    const modal = document.createElement('div');
    modal.innerHTML = `
      <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: white; z-index: 10000; display: flex; flex-direction: column;">
        <div style="background: #28a745; color: white; padding: 16px; display: flex; align-items: center; justify-content: space-between;">
          <h3 style="margin: 0; font-size: 18px;">Writing Assessment</h3>
          <button id="close-writing" style="background: none; border: none; color: white; font-size: 24px;">&times;</button>
        </div>
        
        <div style="flex: 1; padding: 20px; overflow-y: auto;">
          <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
            <h4 style="margin: 0 0 12px 0; color: #333;">Writing Task</h4>
            <p style="margin: 0; line-height: 1.5; color: #555;">
              Write an essay of at least 250 words discussing the advantages and disadvantages of social media in modern society.
              You should provide specific examples and express your own opinion.
            </p>
          </div>
          
          <textarea id="essay-text" placeholder="Start writing your essay here..." 
                    style="width: 100%; height: 300px; padding: 16px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; line-height: 1.5; resize: vertical;"></textarea>
          
          <div style="margin-top: 16px; display: flex; justify-content: space-between; align-items: center;">
            <div id="word-count" style="color: #666; font-size: 14px;">0 words</div>
            <button id="submit-essay" style="background: #28a745; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">
              Submit for Assessment
            </button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    const essayTextarea = document.getElementById('essay-text') as HTMLTextAreaElement;
    const wordCountDiv = document.getElementById('word-count');

    // Word count functionality
    essayTextarea?.addEventListener('input', () => {
      const wordCount = essayTextarea.value.trim().split(/\s+/).filter(word => word.length > 0).length;
      if (wordCountDiv) {
        wordCountDiv.textContent = `${wordCount} words`;
      }
    });

    // Set up event listeners
    document.getElementById('close-writing')?.addEventListener('click', () => {
      modal.remove();
    });

    document.getElementById('submit-essay')?.addEventListener('click', async () => {
      const essayText = essayTextarea?.value.trim();
      if (!essayText || essayText.length < 50) {
        await Toast.show({
          text: 'Please write at least 50 characters before submitting.',
          duration: 'long',
          position: 'center'
        });
        return;
      }

      try {
        await this.apiClient.submitWritingAssessment(
          essayText, 
          'Social media advantages and disadvantages essay',
          productId
        );
        
        modal.remove();
        await Toast.show({
          text: 'Essay submitted successfully! You will receive detailed feedback shortly.',
          duration: 'long',
          position: 'center'
        });
      } catch (error) {
        await Toast.show({
          text: 'Failed to submit essay. Please try again.',
          duration: 'long', 
          position: 'center'
        });
      }
    });
  }

  private async showWebAccessGuide(productId: string): Promise<void> {
    const modal = document.createElement('div');
    modal.innerHTML = `
      <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; display: flex; align-items: center; justify-content: center; padding: 20px;">
        <div style="background: white; border-radius: 16px; padding: 24px; max-width: 400px; width: 100%; text-align: center;">
          <h3 style="margin: 0 0 16px 0; color: #333;">Access on Web Platform</h3>
          
          <div style="font-size: 48px; margin-bottom: 16px;">🖥️</div>
          
          <p style="margin-bottom: 20px; line-height: 1.5; color: #555;">
            For the best assessment experience with full screen and keyboard support:
          </p>
          
          <ol style="text-align: left; margin-bottom: 20px; padding-left: 20px; line-height: 1.6; color: #555;">
            <li>Visit <strong>ieltsaiprep.com</strong> on your computer</li>
            <li>The website will display a QR code</li>
            <li>Return to this app and tap "Scan QR Code"</li>
            <li>Point your camera at the QR code</li>
            <li>You'll be logged into the web platform automatically</li>
          </ol>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <button id="open-qr-scanner" style="background: #007bff; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: 600;">
              Scan QR Code
            </button>
            <button id="close-web-guide" style="background: #f8f9fa; color: #333; border: none; padding: 12px; border-radius: 8px; font-weight: 600;">
              Got It
            </button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    document.getElementById('close-web-guide')?.addEventListener('click', () => {
      modal.remove();
    });

    document.getElementById('open-qr-scanner')?.addEventListener('click', () => {
      modal.remove();
      this.handleQRScan();
    });
  }
}

// Export for global use
declare global {
  interface Window {
    IELTSGenAIPrepApp: typeof IELTSGenAIPrepApp;
    StoreKit: any;
    BarcodeScanner: any;
  }
}

window.IELTSGenAIPrepApp = IELTSGenAIPrepApp;

export { IELTSGenAIPrepApp, MobileAPIClient, iOSPurchaseManager, QRCodeScanner };