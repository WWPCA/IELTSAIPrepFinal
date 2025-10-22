#!/bin/bash

# Custom Domain Setup for ieltsaiprep.com
# Maps custom domain to AWS Lambda API Gateway

echo "🌐 Setting up custom domain: ieltsaiprep.com"
echo "📍 Current backend: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod"

# Configuration
DOMAIN_NAME="ieltsaiprep.com"
API_ID="n0cpf1rmvc"
REGION="us-east-1"
STAGE="prod"

echo ""
echo "Step 1: Creating SSL Certificate in AWS Certificate Manager..."

# Request SSL certificate
CERTIFICATE_ARN=$(aws acm request-certificate \
    --domain-name $DOMAIN_NAME \
    --subject-alternative-names "www.$DOMAIN_NAME" \
    --validation-method DNS \
    --region $REGION \
    --output text --query 'CertificateArn')

echo "✅ SSL Certificate requested: $CERTIFICATE_ARN"
echo ""

echo "Step 2: Creating Custom Domain in API Gateway..."

# Create custom domain name
aws apigatewayv2 create-domain-name \
    --domain-name $DOMAIN_NAME \
    --domain-name-configurations CertificateArn=$CERTIFICATE_ARN,EndpointType=REGIONAL,SecurityPolicy=TLS_1_2 \
    --region $REGION

echo "✅ Custom domain created in API Gateway"
echo ""

echo "Step 3: Creating API Mapping..."

# Create API mapping
aws apigatewayv2 create-api-mapping \
    --domain-name $DOMAIN_NAME \
    --api-id $API_ID \
    --stage $STAGE \
    --region $REGION

echo "✅ API mapping created"
echo ""

echo "Step 4: Getting domain configuration details..."

# Get domain name configuration
DOMAIN_INFO=$(aws apigatewayv2 get-domain-name \
    --domain-name $DOMAIN_NAME \
    --region $REGION \
    --output json)

TARGET_DOMAIN=$(echo $DOMAIN_INFO | jq -r '.DomainNameConfigurations[0].TargetDomainName')
HOSTED_ZONE_ID=$(echo $DOMAIN_INFO | jq -r '.DomainNameConfigurations[0].HostedZoneId')

echo "🎯 Target Domain Name: $TARGET_DOMAIN"
echo "🏠 Hosted Zone ID: $HOSTED_ZONE_ID"
echo ""

echo "Step 5: DNS Configuration Required"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Add these DNS records to your domain registrar for ieltsaiprep.com:"
echo ""
echo "📍 A Record:"
echo "   Type: A"
echo "   Name: @"
echo "   Value: $TARGET_DOMAIN"
echo "   TTL: 300"
echo ""
echo "📍 CNAME Record:"
echo "   Type: CNAME" 
echo "   Name: www"
echo "   Value: ieltsaiprep.com"
echo "   TTL: 300"
echo ""
echo "🔐 SSL Certificate Validation"
echo "   Check AWS Certificate Manager console for DNS validation records"
echo "   Add the CNAME validation records to your DNS"
echo ""

echo "Step 6: Updating mobile app configuration..."

# Update Capacitor configuration
cat > capacitor.config.json << EOF
{
  "appId": "com.ieltsgenaiprep.app",
  "appName": "IELTS GenAI Prep",
  "webDir": "www",
  "server": {
    "url": "https://ieltsaiprep.com",
    "cleartext": false
  },
  "plugins": {
    "CapacitorHttp": {
      "enabled": true
    }
  }
}
EOF

echo "✅ Updated capacitor.config.json with custom domain"
echo ""

echo "Step 7: Creating mobile app configuration files..."

# Update mobile API configuration
cat > mobile-app-config.js << EOF
// IELTS GenAI Prep - Mobile App Configuration
// Production endpoints with custom domain

const API_CONFIG = {
  // Primary API endpoint
  baseURL: 'https://ieltsaiprep.com',
  
  // API endpoints
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
    }
  },
  
  // App Store Connect configuration
  appStore: {
    products: {
      academicWriting: 'com.ieltsgenaiprep.academic.writing',
      generalWriting: 'com.ieltsgenaiprep.general.writing',
      academicSpeaking: 'com.ieltsgenaiprep.academic.speaking',
      generalSpeaking: 'com.ieltsgenaiprep.general.speaking'
    },
    prices: {
      cad: 36.00
    }
  },
  
  // Legal pages
  legal: {
    privacyPolicy: 'https://ieltsaiprep.com/privacy-policy',
    termsOfService: 'https://ieltsaiprep.com/terms-of-service'
  }
};

// Export for use in mobile app
if (typeof module !== 'undefined' && module.exports) {
  module.exports = API_CONFIG;
}

// Global window object for web usage
if (typeof window !== 'undefined') {
  window.API_CONFIG = API_CONFIG;
}
EOF

echo "✅ Created mobile-app-config.js with custom domain endpoints"
echo ""

echo "🎉 Custom Domain Setup Complete!"
echo ""
echo "Next Steps:"
echo "1. Add DNS records to your domain registrar"
echo "2. Validate SSL certificate in AWS Console"
echo "3. Wait 24-48 hours for DNS propagation"
echo "4. Test: https://ieltsaiprep.com"
echo "5. Rebuild mobile app with new configuration"
echo ""
echo "Commands to test after DNS propagation:"
echo "curl -I https://ieltsaiprep.com"
echo "curl -I https://ieltsaiprep.com/privacy-policy"
echo ""