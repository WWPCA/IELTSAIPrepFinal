#!/bin/bash

# Deploy IELTS GenAI Prep Infrastructure with CloudFormation
# Complete AWS infrastructure deployment using Infrastructure as Code

set -e

echo "🚀 IELTS GenAI Prep - CloudFormation Infrastructure Deployment"
echo "=============================================================="

# Configuration
STACK_NAME="ielts-genai-prep-production"
TEMPLATE_FILE="ielts-genai-prep-cloudformation.yaml"
REGION="us-east-1"
DOMAIN_NAME="ieltsaiprep.com"
ENVIRONMENT="production"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Run 'aws configure' first."
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account: $ACCOUNT_ID"
echo "Region: $REGION"
echo "Stack Name: $STACK_NAME"
echo "Domain: $DOMAIN_NAME"

echo ""
echo "Step 1: Package Lambda Function for Deployment"
echo "=============================================="

# Create deployment package
echo "Creating Lambda deployment package..."
mkdir -p deployment
cp app.py deployment/
cp aws_mock_config.py deployment/

# Create requirements.txt for Lambda
cat > deployment/requirements.txt << EOF
anthropic
bcrypt
boto3
botocore
email-validator
openai
pillow
psycopg2-binary
pyjwt
qrcode
requests
structlog
tenacity
trafilatura
EOF

# Package Lambda function
cd deployment
zip -r ../ielts-genai-prep-lambda.zip . -x "*.pyc" "__pycache__/*"
cd ..

echo "✅ Lambda package created: ielts-genai-prep-lambda.zip"

echo ""
echo "Step 2: Create S3 Bucket for Deployment Artifacts"
echo "================================================"

S3_BUCKET="ielts-genai-prep-deployments-$ACCOUNT_ID"

# Create S3 bucket if it doesn't exist
if ! aws s3 ls "s3://$S3_BUCKET" >/dev/null 2>&1; then
    echo "Creating S3 bucket for deployments..."
    aws s3 mb "s3://$S3_BUCKET" --region $REGION
    
    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket $S3_BUCKET \
        --versioning-configuration Status=Enabled
    
    echo "✅ S3 bucket created: $S3_BUCKET"
else
    echo "✅ S3 bucket exists: $S3_BUCKET"
fi

# Upload Lambda package
echo "Uploading Lambda package to S3..."
aws s3 cp ielts-genai-prep-lambda.zip "s3://$S3_BUCKET/lambda/ielts-genai-prep-production.zip"
echo "✅ Lambda package uploaded"

echo ""
echo "Step 3: Validate CloudFormation Template"
echo "========================================"

echo "Validating CloudFormation template..."
aws cloudformation validate-template \
    --template-body file://$TEMPLATE_FILE \
    --region $REGION

echo "✅ CloudFormation template is valid"

echo ""
echo "Step 4: Deploy CloudFormation Stack"
echo "==================================="

echo "Deploying infrastructure stack..."

# Deploy the stack
aws cloudformation deploy \
    --template-file $TEMPLATE_FILE \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        DomainName=$DOMAIN_NAME \
        Environment=$ENVIRONMENT \
        LambdaS3Bucket=$S3_BUCKET \
        LambdaS3Key=lambda/ielts-genai-prep-production.zip \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION \
    --tags \
        Project=IELTSGenAIPrep \
        Environment=$ENVIRONMENT \
        ManagedBy=CloudFormation \
        DeployedBy=$(whoami) \
        DeploymentDate=$(date -u +%Y-%m-%dT%H:%M:%SZ)

if [ $? -eq 0 ]; then
    echo "✅ CloudFormation stack deployed successfully!"
else
    echo "❌ CloudFormation deployment failed"
    exit 1
fi

echo ""
echo "Step 5: Retrieve Stack Outputs"
echo "=============================="

echo "Getting stack outputs..."

# Get stack outputs
OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output json)

echo "Stack Outputs:"
echo "=============="
echo $OUTPUTS | jq -r '.[] | "\(.OutputKey): \(.OutputValue)"'

# Extract specific outputs
HOSTED_ZONE_ID=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="HostedZoneId") | .OutputValue')
NAMESERVERS=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="HostedZoneNameServers") | .OutputValue')
CUSTOM_DOMAIN_URL=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="CustomDomainUrl") | .OutputValue')
SSL_CERTIFICATE_ARN=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="SSLCertificateArn") | .OutputValue')

echo ""
echo "Step 6: Save Configuration"
echo "========================="

# Save deployment summary
cat > cloudformation-deployment-summary.json << EOF
{
  "stackName": "$STACK_NAME",
  "region": "$REGION",
  "domainName": "$DOMAIN_NAME",
  "environment": "$ENVIRONMENT",
  "deploymentDate": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "awsAccount": "$ACCOUNT_ID",
  "hostedZoneId": "$HOSTED_ZONE_ID",
  "nameservers": "$NAMESERVERS",
  "customDomainUrl": "$CUSTOM_DOMAIN_URL",
  "sslCertificateArn": "$SSL_CERTIFICATE_ARN",
  "s3Bucket": "$S3_BUCKET"
}
EOF

echo "✅ Deployment summary saved to cloudformation-deployment-summary.json"

# Update mobile app configuration
echo "Updating mobile app configuration..."
cat > mobile-app-config.js << EOF
// IELTS GenAI Prep - CloudFormation Deployed Configuration
const API_CONFIG = {
  baseURL: '$CUSTOM_DOMAIN_URL',
  
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
  
  legal: {
    privacyPolicy: '$CUSTOM_DOMAIN_URL/privacy-policy',
    termsOfService: '$CUSTOM_DOMAIN_URL/terms-of-service'
  }
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = API_CONFIG;
}

if (typeof window !== 'undefined') {
  window.API_CONFIG = API_CONFIG;
}
EOF

echo "✅ Mobile app configuration updated"

echo ""
echo "🎉 CLOUDFORMATION DEPLOYMENT COMPLETE!"
echo "====================================="
echo ""
echo "✅ Complete AWS infrastructure deployed via CloudFormation"
echo "✅ Route 53 hosted zone created"
echo "✅ SSL certificate issued and validated automatically"
echo "✅ API Gateway with custom domain configured"
echo "✅ Lambda function deployed"
echo "✅ DynamoDB tables created"
echo "✅ Health checks configured"
echo "✅ Mobile app configuration updated"
echo ""
echo "🚨 FINAL STEP - Update Nameservers at Namecheap:"
echo "==============================================="
echo ""
echo "Nameservers to add at Namecheap:"
IFS=', ' read -ra NS_ARRAY <<< "$NAMESERVERS"
for ns in "${NS_ARRAY[@]}"; do
    echo "   $ns"
done
echo ""
echo "🔗 Your app will be live at: $CUSTOM_DOMAIN_URL"
echo "⏱️  DNS propagation: 24-48 hours after nameserver update"
echo "📱 Mobile app ready for App Store submission"
echo ""
echo "🧪 Test commands (after DNS propagation):"
echo "   curl -I $CUSTOM_DOMAIN_URL"
echo "   curl -I $CUSTOM_DOMAIN_URL/health"
echo ""

# Cleanup
rm -rf deployment/
rm -f ielts-genai-prep-lambda.zip

echo "🏁 Infrastructure deployment completed successfully!"