# iOS App Store Setup Guide - IELTS GenAI Prep

## Apple Developer Account Configuration

### 1. App Store Connect Setup

#### App Information
- **App Name**: IELTS GenAI Prep
- **Bundle ID**: `com.ieltsaiprep.genai`
- **Primary Language**: English (U.S.)
- **Category**: Education > Language Learning
- **Content Rights**: You own or have licensed all of the content

#### App Privacy
- **Privacy Policy URL**: https://ieltsaiprep.com/privacy
- **Data Collection**: 
  - Personal Data: Email address for account creation
  - Usage Data: Assessment results and progress tracking
  - No sensitive data (health, financial, etc.)

### 2. In-App Purchase Products

#### Product 1: Academic Speaking Assessment
- **Product ID**: `academic_speaking_assessment`
- **Reference Name**: Academic Speaking Assessment
- **Type**: Non-Consumable
- **Price**: $36.00 USD (Tier 36)
- **Display Name**: Academic Speaking Assessment
- **Description**: "Complete IELTS Academic Speaking assessment with AI examiner Maya. Includes real-time conversation practice, detailed feedback, and band score evaluation."

#### Product 2: Academic Writing Assessment  
- **Product ID**: `academic_writing_assessment`
- **Reference Name**: Academic Writing Assessment
- **Type**: Non-Consumable
- **Price**: $36.00 USD (Tier 36)
- **Display Name**: Academic Writing Assessment
- **Description**: "IELTS Academic Writing Tasks 1 & 2 assessment with AI-powered evaluation. Get detailed feedback on task achievement, coherence, lexical resource, and grammatical accuracy."

#### Product 3: General Speaking Assessment
- **Product ID**: `general_speaking_assessment`
- **Reference Name**: General Training Speaking Assessment
- **Type**: Non-Consumable
- **Price**: $36.00 USD (Tier 36)
- **Display Name**: General Training Speaking Assessment
- **Description**: "IELTS General Training Speaking assessment covering everyday topics. Practice with AI examiner Maya and receive comprehensive band score feedback."

#### Product 4: General Writing Assessment
- **Product ID**: `general_writing_assessment`
- **Reference Name**: General Training Writing Assessment
- **Type**: Non-Consumable
- **Price**: $36.00 USD (Tier 36)
- **Display Name**: General Training Writing Assessment
- **Description**: "IELTS General Training Writing Tasks 1 & 2 assessment. Get expert feedback on letter writing and essay composition with detailed scoring."

### 3. App Store Listing

#### App Description
```
Prepare for IELTS success with our AI-powered assessment platform featuring Maya, your personal AI examiner.

🎯 COMPREHENSIVE IELTS PREPARATION
• Academic & General Training modules
• Speaking assessments with real-time AI conversation
• Writing assessments with detailed feedback
• Authentic IELTS test experience

🤖 AI-POWERED ASSESSMENT
• Maya AI Examiner for natural conversation practice
• Instant feedback and band score evaluation
• Personalized improvement recommendations
• Progress tracking and analytics

📱 SEAMLESS EXPERIENCE
• QR code authentication for web platform access
• Cross-platform synchronization
• Offline assessment review
• Global availability with regional optimization

💎 PREMIUM FEATURES
• Individual assessment purchases ($36 each)
• No subscription required
• Lifetime access to purchased assessments
• Regular content updates

🌍 TRUSTED GLOBALLY
• Used by IELTS candidates worldwide
• Developed with IELTS preparation experts
• Continuous AI model improvements
• GDPR compliant and secure

Download now and start your IELTS preparation journey with confidence!
```

#### Keywords
```
IELTS, English test, speaking practice, writing assessment, AI tutor, exam preparation, English learning, band score, Maya examiner, language test
```

#### App Screenshots (Required Sizes)
- **6.7" Display**: 1290 x 2796 pixels
- **6.5" Display**: 1242 x 2688 pixels  
- **5.5" Display**: 1242 x 2208 pixels
- **12.9" iPad Pro**: 2048 x 2732 pixels

### 4. Technical Configuration

#### App Capabilities
```xml
<!-- Required capabilities in Xcode project -->
<key>UIRequiredDeviceCapabilities</key>
<array>
    <string>microphone</string>
    <string>wifi</string>
</array>

<!-- Background modes -->
<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
    <string>background-processing</string>
</array>

<!-- Permissions -->
<key>NSMicrophoneUsageDescription</key>
<string>IELTS GenAI Prep needs microphone access for speaking assessments with AI examiner Maya.</string>

<key>NSCameraUsageDescription</key>
<string>Camera access is needed to scan QR codes for website authentication.</string>
```

#### Capacitor Configuration
```typescript
// capacitor.config.ts
import { CapacitorConfig } from '@capacitor/core';

const config: CapacitorConfig = {
  appId: 'com.ieltsaiprep.genai',
  appName: 'IELTS GenAI Prep',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    cleartext: false
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#667eea',
      showSpinner: false
    },
    StatusBar: {
      style: 'dark',
      backgroundColor: '#667eea'
    },
    CapacitorHttp: {
      enabled: true
    },
    Device: {
      enabled: true
    },
    Network: {
      enabled: true
    },
    Toast: {
      enabled: true
    }
  },
  ios: {
    scheme: 'IELTS GenAI Prep',
    contentInset: 'always'
  }
};

export default config;
```

### 5. In-App Purchase Implementation

#### Purchase Manager Integration
```javascript
// ios-purchase-manager.js
import { CapacitorPurchases } from '@capacitor-community/purchases';

class iOSPurchaseManager {
  constructor() {
    this.products = [
      'academic_speaking_assessment',
      'academic_writing_assessment', 
      'general_speaking_assessment',
      'general_writing_assessment'
    ];
    this.apiClient = new MobileAPIClient();
  }

  async initializePurchases() {
    try {
      await CapacitorPurchases.configure({
        apiKey: 'your_revenuecat_api_key', // Optional: Use RevenueCat
        appUserID: null // Will be set after login
      });
      
      // Load products
      const { products } = await CapacitorPurchases.getProducts({
        productIdentifiers: this.products
      });
      
      return products;
    } catch (error) {
      console.error('Purchase initialization failed:', error);
      throw error;
    }
  }

  async purchaseProduct(productId) {
    try {
      // Show loading state
      await this.showPurchaseLoading();
      
      // Start purchase flow
      const { transaction } = await CapacitorPurchases.purchaseProduct({
        productIdentifier: productId
      });
      
      if (transaction.transactionState === 'purchased') {
        // Verify purchase with backend
        const verification = await this.verifyApplePurchase(
          transaction.transactionReceipt,
          productId
        );
        
        if (verification.success) {
          // Generate QR token for website access
          await this.generateWebsiteQRToken(verification.userEmail);
          await this.showPurchaseSuccess(productId);
          return verification;
        } else {
          throw new Error('Purchase verification failed');
        }
      }
    } catch (error) {
      await this.showPurchaseError(error.message);
      throw error;
    }
  }

  async verifyApplePurchase(receiptData, productId) {
    return await this.apiClient.verifyApplePurchase(receiptData, productId);
  }

  async generateWebsiteQRToken(userEmail) {
    const qrData = await this.apiClient.generateQRToken(userEmail, true);
    await this.displayQRCode(qrData);
    return qrData;
  }

  async displayQRCode(qrData) {
    // Show QR code modal for website authentication
    const modal = document.createElement('div');
    modal.innerHTML = `
      <div class="qr-modal">
        <h3>Scan to Access Website</h3>
        <img src="${qrData.qr_code_image}" alt="QR Code" />
        <p>Scan this code on ieltsaiprep.com to access your assessments</p>
        <p>Code expires in 10 minutes</p>
        <button onclick="this.closest('.qr-modal').remove()">Close</button>
      </div>
    `;
    document.body.appendChild(modal);
  }
}
```

### 6. TestFlight Beta Testing

#### Beta Testing Configuration
- **Internal Testing**: Development team (up to 100 testers)
- **External Testing**: Beta users (up to 10,000 testers)
- **Test Information**:
  - What to Test: QR authentication flow, in-app purchases, speaking assessments
  - Feedback Email: beta@ieltsaiprep.com

#### Beta Test Instructions
```
Welcome to IELTS GenAI Prep Beta!

TEST SCENARIOS:
1. Purchase any assessment module ($36)
2. Complete the QR authentication flow
3. Access your assessment on ieltsaiprep.com
4. Test speaking assessment with Maya AI
5. Review detailed feedback and scoring

FEEDBACK NEEDED:
- Purchase flow smoothness
- QR code scanning reliability  
- Audio quality during speaking tests
- App performance and stability
- User interface clarity

Please report issues to beta@ieltsaiprep.com
```

### 7. App Review Guidelines Compliance

#### Checklist for App Store Review
- ✅ In-app purchases provide clear value
- ✅ QR authentication is clearly explained
- ✅ No external payment methods mentioned
- ✅ Privacy policy covers all data collection
- ✅ Microphone usage clearly justified
- ✅ No references to other platforms
- ✅ Accurate app description and screenshots
- ✅ Proper age rating (4+ for educational content)

#### Review Notes for Apple
```
This app provides IELTS test preparation through AI-powered assessments. 

KEY FEATURES:
- In-app purchases unlock individual assessment modules
- QR code authentication connects mobile purchases to web platform
- Speaking assessments use device microphone for AI conversation
- All purchases are processed through App Store

TECHNICAL NOTES:
- Uses Capacitor framework for native iOS integration
- QR codes connect to secure web platform at ieltsaiprep.com
- Audio processing happens locally, transcripts sent to AWS for AI evaluation
- No external payment processing - all transactions through App Store
```

### 8. Launch Preparation

#### Pre-Launch Checklist
- [ ] Apple Developer account active
- [ ] App Store Connect app created
- [ ] All 4 in-app products configured and approved
- [ ] TestFlight beta testing completed
- [ ] App Store screenshots and metadata finalized
- [ ] Privacy policy updated and published
- [ ] Backend Lambda functions deployed
- [ ] QR authentication system tested
- [ ] Customer support documentation ready

#### Launch Day Actions
1. Submit app for review (typically 24-48 hours)
2. Monitor App Store Connect for review status
3. Prepare launch communications
4. Set up app analytics and monitoring
5. Enable customer support channels

This configuration ensures your iOS app integrates seamlessly with the QR authentication system and provides a smooth purchase-to-assessment flow for global users.