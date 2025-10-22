// IELTS GenAI Prep - Production Configuration with Custom Domain
// Ready for ieltsaiprep.com professional domain deployment

const PRODUCTION_CONFIG = {
  // Professional custom domain (after Route 53 setup)
  baseURL: 'https://ieltsaiprep.com',
  
  // API endpoints for Lambda backend
  endpoints: {
    auth: {
      register: '/api/register',
      login: '/api/login',
      verify: '/api/verify-session'
    },
    assessments: {
      speaking: '/api/nova-sonic',
      writing: '/api/nova-micro',
      access: '/assessment'
    },
    purchases: {
      apple: '/api/verify-apple-purchase',
      google: '/api/verify-google-purchase',
      unlock: '/api/unlock-module'
    },
    health: '/health'
  },
  
  // App Store product identifiers
  appStore: {
    products: {
      academicWriting: 'com.ieltsgenaiprep.academic.writing',
      generalWriting: 'com.ieltsgenaiprep.general.writing',
      academicSpeaking: 'com.ieltsgenaiprep.academic.speaking',
      generalSpeaking: 'com.ieltsgenaiprep.general.speaking'
    },
    prices: {
      cad: 36.00,
      usd: 27.00
    }
  },
  
  // Legal pages for App Store compliance
  legal: {
    privacyPolicy: 'https://ieltsaiprep.com/privacy-policy',
    termsOfService: 'https://ieltsaiprep.com/terms-of-service',
    support: 'https://ieltsaiprep.com/support'
  },
  
  // AWS configuration
  aws: {
    region: 'us-east-1',
    apiGatewayId: 'n0cpf1rmvc',
    lambdaFunction: 'ielts-genai-prep-api'
  },
  
  // Feature flags
  features: {
    novaSONIC: true,
    novaMICRO: true,
    mobilePurchases: true,
    webAccess: true
  }
};

// Fallback to Lambda URL during domain setup
const FALLBACK_CONFIG = {
  baseURL: 'https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod',
  legal: {
    privacyPolicy: 'https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/privacy-policy',
    termsOfService: 'https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/terms-of-service',
    support: 'https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/support'
  }
};

// Export configuration based on environment
const API_CONFIG = process.env.NODE_ENV === 'production' ? PRODUCTION_CONFIG : FALLBACK_CONFIG;

// Module exports for different environments
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    API_CONFIG,
    PRODUCTION_CONFIG,
    FALLBACK_CONFIG
  };
}

// Browser global
if (typeof window !== 'undefined') {
  window.API_CONFIG = API_CONFIG;
  window.PRODUCTION_CONFIG = PRODUCTION_CONFIG;
}

// Capacitor configuration
if (typeof global !== 'undefined') {
  global.IELTS_API_CONFIG = API_CONFIG;
}