/**
 * IELTS GenAI Prep - Mobile Purchase Integration
 * Handles Apple App Store and Google Play Store in-app purchases
 */

import { Capacitor } from '@capacitor/core';
import { apiClient } from './mobile-api-client.js';
import { ASSESSMENT_PRODUCTS, Logger } from './mobile-app-config.js';

class PurchaseManager {
  constructor() {
    this.platform = Capacitor.getPlatform();
    this.isInitialized = false;
  }

  async initialize() {
    if (this.isInitialized) return;

    try {
      if (this.platform === 'ios') {
        await this.initializeAppleStore();
      } else if (this.platform === 'android') {
        await this.initializeGooglePlay();
      }
      
      this.isInitialized = true;
      Logger.info('Purchase manager initialized', { platform: this.platform });
    } catch (error) {
      Logger.error('Failed to initialize purchase manager', error);
      throw error;
    }
  }

  async initializeAppleStore() {
    // Initialize Apple StoreKit
    const { StoreKit } = await import('@capacitor/store-kit');
    
    await StoreKit.initialize({
      products: Object.values(ASSESSMENT_PRODUCTS).map(p => p.appleProductId)
    });

    // Set up purchase listener
    StoreKit.addListener('purchaseCompleted', (purchase) => {
      this.handleApplePurchase(purchase);
    });

    StoreKit.addListener('purchaseFailed', (error) => {
      this.handlePurchaseError(error);
    });
  }

  async initializeGooglePlay() {
    // Initialize Google Play Billing
    const { GooglePlayBilling } = await import('@capacitor/google-play-billing');
    
    await GooglePlayBilling.initialize();

    // Set up purchase listener
    GooglePlayBilling.addListener('purchaseCompleted', (purchase) => {
      this.handleGooglePurchase(purchase);
    });

    GooglePlayBilling.addListener('purchaseFailed', (error) => {
      this.handlePurchaseError(error);
    });
  }

  async getAvailableProducts() {
    await this.initialize();

    try {
      if (this.platform === 'ios') {
        const { StoreKit } = await import('@capacitor/store-kit');
        const products = await StoreKit.getProducts({
          productIds: Object.values(ASSESSMENT_PRODUCTS).map(p => p.appleProductId)
        });
        return this.formatAppleProducts(products.products);
        
      } else if (this.platform === 'android') {
        const { GooglePlayBilling } = await import('@capacitor/google-play-billing');
        const products = await GooglePlayBilling.getSkuDetails({
          skuList: Object.values(ASSESSMENT_PRODUCTS).map(p => p.googleProductId),
          type: 'inapp'
        });
        return this.formatGoogleProducts(products.skuDetails);
      }
      
      return [];
    } catch (error) {
      Logger.error('Failed to get available products', error);
      return [];
    }
  }

  async purchaseProduct(assessmentType) {
    await this.initialize();

    const product = ASSESSMENT_PRODUCTS[assessmentType];
    if (!product) {
      throw new Error(`Invalid assessment type: ${assessmentType}`);
    }

    try {
      if (this.platform === 'ios') {
        return await this.purchaseAppleProduct(product);
      } else if (this.platform === 'android') {
        return await this.purchaseGoogleProduct(product);
      } else {
        throw new Error('Purchases not supported on this platform');
      }
    } catch (error) {
      Logger.error('Purchase failed', { assessmentType, error });
      throw error;
    }
  }

  async purchaseAppleProduct(product) {
    const { StoreKit } = await import('@capacitor/store-kit');
    
    const result = await StoreKit.purchase({
      productId: product.appleProductId
    });

    if (result.success) {
      Logger.info('Apple purchase initiated', { productId: product.appleProductId });
      return result;
    } else {
      throw new Error(result.error || 'Purchase failed');
    }
  }

  async purchaseGoogleProduct(product) {
    const { GooglePlayBilling } = await import('@capacitor/google-play-billing');
    
    const result = await GooglePlayBilling.purchaseProduct({
      sku: product.googleProductId,
      type: 'inapp'
    });

    if (result.success) {
      Logger.info('Google purchase initiated', { sku: product.googleProductId });
      return result;
    } else {
      throw new Error(result.error || 'Purchase failed');
    }
  }

  async handleApplePurchase(purchase) {
    try {
      Logger.info('Processing Apple purchase', { transactionId: purchase.transactionId });

      // Get receipt data
      const { StoreKit } = await import('@capacitor/store-kit');
      const receipt = await StoreKit.getReceiptData();

      // Verify purchase with backend
      const verificationResult = await apiClient.verifyApplePurchase(
        receipt.receiptData,
        purchase.productId
      );

      if (verificationResult.success) {
        Logger.info('Apple purchase verified successfully');
        await this.onPurchaseSuccess(purchase.productId, 'apple');
        
        // Finish transaction
        await StoreKit.finishTransaction({
          transactionId: purchase.transactionId
        });
      } else {
        throw new Error('Purchase verification failed');
      }

    } catch (error) {
      Logger.error('Failed to process Apple purchase', error);
      await this.onPurchaseError(error);
    }
  }

  async handleGooglePurchase(purchase) {
    try {
      Logger.info('Processing Google purchase', { purchaseToken: purchase.purchaseToken });

      // Verify purchase with backend
      const verificationResult = await apiClient.verifyGooglePurchase(
        purchase.purchaseToken,
        purchase.sku
      );

      if (verificationResult.success) {
        Logger.info('Google purchase verified successfully');
        await this.onPurchaseSuccess(purchase.sku, 'google');
        
        // Acknowledge purchase
        const { GooglePlayBilling } = await import('@capacitor/google-play-billing');
        await GooglePlayBilling.acknowledgePurchase({
          purchaseToken: purchase.purchaseToken
        });
      } else {
        throw new Error('Purchase verification failed');
      }

    } catch (error) {
      Logger.error('Failed to process Google purchase', error);
      await this.onPurchaseError(error);
    }
  }

  async onPurchaseSuccess(productId, platform) {
    // Find assessment type from product ID
    const assessmentType = this.getAssessmentTypeFromProductId(productId, platform);
    
    if (assessmentType) {
      // Store purchase locally
      await this.storePurchaseLocally(assessmentType, platform);
      
      // Trigger purchase success callback
      if (this.onPurchaseSuccessCallback) {
        this.onPurchaseSuccessCallback(assessmentType);
      }
      
      // Show success message
      this.showPurchaseSuccess(assessmentType);
    }
  }

  async onPurchaseError(error) {
    Logger.error('Purchase error', error);
    
    if (this.onPurchaseErrorCallback) {
      this.onPurchaseErrorCallback(error);
    }
    
    // Show error message
    this.showPurchaseError(error.message);
  }

  getAssessmentTypeFromProductId(productId, platform) {
    const productKey = platform === 'apple' ? 'appleProductId' : 'googleProductId';
    
    for (const [type, product] of Object.entries(ASSESSMENT_PRODUCTS)) {
      if (product[productKey] === productId) {
        return type;
      }
    }
    
    return null;
  }

  async storePurchaseLocally(assessmentType, platform) {
    try {
      const purchases = await this.getStoredPurchases();
      purchases[assessmentType] = {
        platform,
        purchaseDate: new Date().toISOString(),
        verified: true
      };
      
      await this.setPurchases(purchases);
      Logger.info('Purchase stored locally', { assessmentType, platform });
    } catch (error) {
      Logger.error('Failed to store purchase locally', error);
    }
  }

  async getStoredPurchases() {
    try {
      const { Storage } = await import('@capacitor/storage');
      const result = await Storage.get({ key: 'ielts_purchases' });
      return result.value ? JSON.parse(result.value) : {};
    } catch (error) {
      Logger.error('Failed to get stored purchases', error);
      return {};
    }
  }

  async setPurchases(purchases) {
    try {
      const { Storage } = await import('@capacitor/storage');
      await Storage.set({
        key: 'ielts_purchases',
        value: JSON.stringify(purchases)
      });
    } catch (error) {
      Logger.error('Failed to store purchases', error);
    }
  }

  async hasPurchased(assessmentType) {
    const purchases = await this.getStoredPurchases();
    return !!purchases[assessmentType]?.verified;
  }

  formatAppleProducts(products) {
    return products.map(product => ({
      id: product.productId,
      name: product.displayName,
      description: product.description,
      price: product.price,
      currency: product.currency,
      platform: 'apple'
    }));
  }

  formatGoogleProducts(skuDetails) {
    return skuDetails.map(sku => ({
      id: sku.sku,
      name: sku.title,
      description: sku.description,
      price: sku.price,
      currency: sku.priceCurrencyCode,
      platform: 'google'
    }));
  }

  showPurchaseSuccess(assessmentType) {
    const product = ASSESSMENT_PRODUCTS[assessmentType];
    if (product && window.showToast) {
      window.showToast(`${product.name} purchased successfully!`, 'success');
    }
  }

  showPurchaseError(message) {
    if (window.showToast) {
      window.showToast(`Purchase failed: ${message}`, 'error');
    }
  }

  handlePurchaseError(error) {
    Logger.error('Purchase failed', error);
    this.onPurchaseError(error);
  }

  // Callback setters
  setPurchaseSuccessCallback(callback) {
    this.onPurchaseSuccessCallback = callback;
  }

  setPurchaseErrorCallback(callback) {
    this.onPurchaseErrorCallback = callback;
  }

  // Restore purchases
  async restorePurchases() {
    await this.initialize();

    try {
      if (this.platform === 'ios') {
        const { StoreKit } = await import('@capacitor/store-kit');
        const result = await StoreKit.restorePurchases();
        return result.purchases || [];
        
      } else if (this.platform === 'android') {
        const { GooglePlayBilling } = await import('@capacitor/google-play-billing');
        const result = await GooglePlayBilling.getPurchases({
          type: 'inapp'
        });
        return result.purchases || [];
      }
      
      return [];
    } catch (error) {
      Logger.error('Failed to restore purchases', error);
      return [];
    }
  }
}

// Export singleton instance
export const purchaseManager = new PurchaseManager();
export default purchaseManager;