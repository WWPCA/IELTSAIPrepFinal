#!/bin/bash

# IELTS GenAI Prep - Production Endpoint Configuration Script
# Automatically configures mobile app and website endpoints after AWS deployment

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-ielts-genai-prep}"

echo "🔧 Configuring production endpoints for $STACK_NAME"

# Check if stack exists and get outputs
if ! aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION &>/dev/null; then
    echo "❌ Stack $STACK_NAME not found. Please deploy infrastructure first:"
    echo "  ./deploy-aws-infrastructure.sh"
    echo "  sam deploy --guided"
    exit 1
fi

echo "📋 Retrieving AWS deployment information..."

# Get API Gateway URL
API_GATEWAY_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
    --output text 2>/dev/null || echo "")

# Get WebSocket URL
WEBSOCKET_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`WebSocketUrl`].OutputValue' \
    --output text 2>/dev/null || echo "")

if [ -z "$API_GATEWAY_URL" ] || [ -z "$WEBSOCKET_URL" ]; then
    echo "❌ Could not retrieve deployment URLs. Please check stack deployment."
    exit 1
fi

echo "✅ Retrieved deployment URLs:"
echo "  API Gateway: $API_GATEWAY_URL"
echo "  WebSocket: $WEBSOCKET_URL"

# Update mobile app configuration
echo "📱 Updating mobile app configuration..."

# Update mobile-app-config.js
sed -i.bak "s|baseURL: 'https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/Prod'|baseURL: '$API_GATEWAY_URL'|g" mobile-app-config.js
sed -i.bak "s|websocketURL: 'wss://your-websocket-id.execute-api.us-east-1.amazonaws.com/Prod'|websocketURL: '$WEBSOCKET_URL'|g" mobile-app-config.js

# Update Capacitor configuration
sed -i.bak "s|https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/Prod|$API_GATEWAY_URL|g" capacitor.config.json

# Update website configuration
echo "🌐 Updating website configuration..."
sed -i.bak "s|apiBaseURL: 'https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/Prod'|apiBaseURL: '$API_GATEWAY_URL'|g" website-config.js
sed -i.bak "s|websocketURL: 'wss://your-websocket-id.execute-api.us-east-1.amazonaws.com/Prod'|websocketURL: '$WEBSOCKET_URL'|g" website-config.js

# Create production environment file
echo "📄 Creating production environment configuration..."
cat > .env.production << EOF
# IELTS GenAI Prep - Production Environment
# Generated on $(date)

# AWS Configuration
AWS_REGION=$AWS_REGION
STACK_NAME=$STACK_NAME

# API Endpoints
API_GATEWAY_URL=$API_GATEWAY_URL
WEBSOCKET_URL=$WEBSOCKET_URL

# DynamoDB Tables
DYNAMODB_USERS_TABLE=${STACK_NAME}-users
DYNAMODB_SESSIONS_TABLE=${STACK_NAME}-sessions
DYNAMODB_ASSESSMENTS_TABLE=${STACK_NAME}-assessments
DYNAMODB_RUBRICS_TABLE=${STACK_NAME}-rubrics

# CloudWatch
CLOUDWATCH_LOG_GROUP=/aws/lambda/${STACK_NAME}

# Environment
ENVIRONMENT=production
EOF

# Test endpoints
echo "🧪 Testing production endpoints..."

# Test health endpoint
if curl -s "$API_GATEWAY_URL/api/health" | grep -q "success"; then
    echo "✅ API Gateway health check passed"
else
    echo "⚠️  API Gateway health check failed - this is normal if Lambda is cold starting"
fi

# Check if assessment data exists
echo "📊 Checking assessment data..."
python3 -c "
import boto3
import sys

try:
    dynamodb = boto3.client('dynamodb', region_name='$AWS_REGION')
    response = dynamodb.scan(
        TableName='${STACK_NAME}-rubrics',
        Select='COUNT'
    )
    count = response.get('Count', 0)
    if count > 0:
        print(f'✅ Found {count} assessment rubrics in database')
    else:
        print('⚠️  No assessment rubrics found. Run: python3 populate-assessment-data.py')
        sys.exit(1)
except Exception as e:
    print(f'❌ Could not check assessment data: {e}')
    sys.exit(1)
" 2>/dev/null || echo "⚠️  Assessment data check failed - run populate-assessment-data.py"

# Clean up backup files
rm -f mobile-app-config.js.bak capacitor.config.json.bak website-config.js.bak

echo "✅ Production endpoint configuration complete!"
echo ""
echo "📱 Mobile App Next Steps:"
echo "1. Build mobile app: npx cap build ios && npx cap build android"
echo "2. Test in-app purchases with production App Store/Google Play"
echo "3. Submit to app stores for review"
echo ""
echo "🌐 Website Next Steps:"
echo "1. Deploy website to CDN or hosting service"
echo "2. Configure custom domain with SSL certificate"
echo "3. Update DNS records to point to production"
echo ""
echo "🔐 Security Checklist:"
echo "1. Enable AWS CloudTrail for audit logging"
echo "2. Configure AWS WAF for API Gateway protection" 
echo "3. Review and rotate IAM access keys"
echo "4. Enable DynamoDB point-in-time recovery"
echo ""
echo "📊 Monitoring Setup:"
echo "1. Create CloudWatch dashboards for key metrics"
echo "2. Set up CloudWatch alarms for errors and latency"
echo "3. Configure SNS notifications for critical alerts"