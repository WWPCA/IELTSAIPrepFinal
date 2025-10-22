#!/bin/bash

# Complete AWS Route 53 Setup for ieltsaiprep.com
# Based on: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/getting-started.html

echo "🌐 Complete AWS Route 53 Deployment for ieltsaiprep.com"
echo "📖 Following AWS Route 53 Getting Started Guide"
echo "=========================================================="

# Configuration
DOMAIN_NAME="ieltsaiprep.com"
REGION="us-east-1"
CALLER_REFERENCE="ieltsaiprep-$(date +%s)"

echo ""
echo "Phase 1: Create Route 53 Hosted Zone"
echo "======================================"

# Create hosted zone
echo "Creating hosted zone for $DOMAIN_NAME..."
HOSTED_ZONE_OUTPUT=$(aws route53 create-hosted-zone \
    --name $DOMAIN_NAME \
    --caller-reference $CALLER_REFERENCE \
    --output json)

if [ $? -eq 0 ]; then
    echo "✅ Hosted zone created successfully"
    
    # Extract hosted zone ID and nameservers
    HOSTED_ZONE_ID=$(echo $HOSTED_ZONE_OUTPUT | jq -r '.HostedZone.Id' | sed 's|/hostedzone/||')
    echo "📋 Hosted Zone ID: $HOSTED_ZONE_ID"
    
    # Get nameservers
    echo ""
    echo "📡 AWS Route 53 Nameservers:"
    echo "============================"
    aws route53 get-hosted-zone --id $HOSTED_ZONE_ID \
        --query 'DelegationSet.NameServers' \
        --output table
    
    echo ""
    echo "📝 ACTION REQUIRED: Update nameservers at Namecheap"
    echo "1. Login to Namecheap domain management"
    echo "2. Go to ieltsaiprep.com domain settings"
    echo "3. Change nameservers to the AWS Route 53 nameservers above"
    echo "4. Wait 24-48 hours for DNS propagation"
    
else
    echo "❌ Failed to create hosted zone"
    exit 1
fi

echo ""
echo "Phase 2: Create DNS Records"
echo "=========================="

# Create A record for apex domain (will point to API Gateway later)
echo "Creating placeholder A record for apex domain..."
cat > /tmp/apex-record.json << EOF
{
    "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
            "Name": "$DOMAIN_NAME",
            "Type": "A",
            "TTL": 300,
            "ResourceRecords": [{
                "Value": "192.0.2.1"
            }]
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/apex-record.json

echo "✅ Placeholder A record created (will update after API Gateway setup)"

# Create CNAME record for www
echo "Creating CNAME record for www subdomain..."
cat > /tmp/www-record.json << EOF
{
    "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
            "Name": "www.$DOMAIN_NAME",
            "Type": "CNAME",
            "TTL": 300,
            "ResourceRecords": [{
                "Value": "$DOMAIN_NAME"
            }]
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/www-record.json

echo "✅ CNAME record created for www subdomain"

echo ""
echo "Phase 3: Request SSL Certificate with Route 53 Validation"
echo "========================================================="

# Delete any existing certificates for the domain
echo "Checking for existing certificates..."
EXISTING_CERTS=$(aws acm list-certificates \
    --region $REGION \
    --query "CertificateSummaryList[?DomainName=='$DOMAIN_NAME' || DomainName=='www.$DOMAIN_NAME'].CertificateArn" \
    --output text)

if [ ! -z "$EXISTING_CERTS" ]; then
    echo "Found existing certificates. Deleting them first..."
    for cert_arn in $EXISTING_CERTS; do
        aws acm delete-certificate --certificate-arn $cert_arn --region $REGION
        echo "🗑️ Deleted certificate: $cert_arn"
    done
fi

# Request new certificate with Route 53 validation
echo "Requesting new SSL certificate with Route 53 DNS validation..."
CERTIFICATE_ARN=$(aws acm request-certificate \
    --domain-name $DOMAIN_NAME \
    --subject-alternative-names "www.$DOMAIN_NAME" \
    --validation-method DNS \
    --region $REGION \
    --output text --query 'CertificateArn')

echo "✅ SSL Certificate requested: $CERTIFICATE_ARN"

echo ""
echo "Phase 4: Automatic DNS Validation Setup"
echo "======================================="

# Wait a moment for certificate details to be available
echo "Waiting for certificate validation records..."
sleep 10

# Get validation records
VALIDATION_RECORDS=$(aws acm describe-certificate \
    --certificate-arn $CERTIFICATE_ARN \
    --region $REGION \
    --query 'Certificate.DomainValidationOptions' \
    --output json)

echo "Creating DNS validation records in Route 53..."

# Process validation records and create them in Route 53
echo $VALIDATION_RECORDS | jq -r '.[] | @base64' | while read record; do
    decoded=$(echo $record | base64 -d)
    validation_name=$(echo $decoded | jq -r '.ResourceRecord.Name')
    validation_value=$(echo $decoded | jq -r '.ResourceRecord.Value')
    
    # Create validation record
    cat > /tmp/validation-record.json << EOF
{
    "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
            "Name": "$validation_name",
            "Type": "CNAME",
            "TTL": 300,
            "ResourceRecords": [{
                "Value": "$validation_value"
            }]
        }
    }]
}
EOF
    
    aws route53 change-resource-record-sets \
        --hosted-zone-id $HOSTED_ZONE_ID \
        --change-batch file:///tmp/validation-record.json
    
    echo "✅ DNS validation record created: $validation_name"
done

echo ""
echo "Phase 5: API Gateway Custom Domain Setup"
echo "========================================"

echo "Waiting for SSL certificate validation (this may take a few minutes)..."

# Function to check certificate status
check_certificate_status() {
    aws acm describe-certificate \
        --certificate-arn $CERTIFICATE_ARN \
        --region $REGION \
        --query 'Certificate.Status' \
        --output text
}

# Wait for certificate to be issued
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    status=$(check_certificate_status)
    echo "Attempt $attempt/$max_attempts: Certificate status: $status"
    
    if [ "$status" = "ISSUED" ]; then
        echo "✅ SSL Certificate successfully validated and issued!"
        break
    elif [ "$status" = "FAILED" ]; then
        echo "❌ SSL Certificate validation failed"
        exit 1
    fi
    
    sleep 30
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "⏰ Certificate validation taking longer than expected"
    echo "Continue manually once certificate shows 'ISSUED' status"
    echo "Certificate ARN: $CERTIFICATE_ARN"
    exit 1
fi

# Create custom domain in API Gateway
echo "Creating custom domain in API Gateway..."
aws apigatewayv2 create-domain-name \
    --domain-name $DOMAIN_NAME \
    --domain-name-configurations CertificateArn=$CERTIFICATE_ARN,EndpointType=REGIONAL,SecurityPolicy=TLS_1_2 \
    --region $REGION

echo "✅ Custom domain created in API Gateway"

# Get the target domain name for the A record
TARGET_DOMAIN=$(aws apigatewayv2 get-domain-name \
    --domain-name $DOMAIN_NAME \
    --region $REGION \
    --query 'DomainNameConfigurations[0].TargetDomainName' \
    --output text)

echo "🎯 API Gateway Target Domain: $TARGET_DOMAIN"

# Update A record to point to API Gateway
echo "Updating A record to point to API Gateway..."
cat > /tmp/update-apex-record.json << EOF
{
    "Changes": [{
        "Action": "UPSERT",
        "ResourceRecordSet": {
            "Name": "$DOMAIN_NAME",
            "Type": "A",
            "AliasTarget": {
                "DNSName": "$TARGET_DOMAIN",
                "EvaluateTargetHealth": false,
                "HostedZoneId": "Z1UJRXOUMOOFQ8"
            }
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/update-apex-record.json

echo "✅ A record updated to point to API Gateway"

# Create API mapping
echo "Creating API mapping..."
API_ID="n0cpf1rmvc"  # Your existing API Gateway ID
STAGE="prod"

aws apigatewayv2 create-api-mapping \
    --domain-name $DOMAIN_NAME \
    --api-id $API_ID \
    --stage $STAGE \
    --region $REGION

echo "✅ API mapping created"

echo ""
echo "Phase 6: Update Mobile App Configuration"
echo "========================================"

# Update Capacitor configuration
cat > capacitor.config.json << EOF
{
  "appId": "com.ieltsgenaiprep.app",
  "appName": "IELTS GenAI Prep",
  "webDir": "www",
  "server": {
    "url": "https://$DOMAIN_NAME",
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

# Update mobile app configuration
cat > mobile-app-config.js << EOF
// IELTS GenAI Prep - Mobile App Configuration
// Production endpoints with Route 53 managed custom domain

const API_CONFIG = {
  // Primary API endpoint
  baseURL: 'https://$DOMAIN_NAME',
  
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
    privacyPolicy: 'https://$DOMAIN_NAME/privacy-policy',
    termsOfService: 'https://$DOMAIN_NAME/terms-of-service'
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

echo "✅ Updated mobile-app-config.js with custom domain"

echo ""
echo "🎉 COMPLETE AWS ROUTE 53 DEPLOYMENT FINISHED!"
echo "=============================================="
echo ""
echo "✅ Route 53 hosted zone created"
echo "✅ DNS records configured"
echo "✅ SSL certificate issued and validated"
echo "✅ API Gateway custom domain configured"
echo "✅ Mobile app configuration updated"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Update nameservers at Namecheap domain registrar"
echo "2. Wait 24-48 hours for DNS propagation"
echo "3. Test: https://$DOMAIN_NAME"
echo "4. Deploy mobile app with new configuration"
echo "5. Submit to App Store with professional domain"
echo ""
echo "📡 AWS Route 53 Nameservers (update at Namecheap):"
aws route53 get-hosted-zone --id $HOSTED_ZONE_ID \
    --query 'DelegationSet.NameServers' \
    --output table
echo ""
echo "🔗 Test URLs after DNS propagation:"
echo "   https://$DOMAIN_NAME"
echo "   https://www.$DOMAIN_NAME"
echo "   https://$DOMAIN_NAME/privacy-policy"
echo "   https://$DOMAIN_NAME/terms-of-service"
echo ""

# Cleanup temporary files
rm -f /tmp/apex-record.json /tmp/www-record.json /tmp/validation-record.json /tmp/update-apex-record.json

echo "🏁 Route 53 deployment script completed successfully!"