#!/bin/bash

# IELTS GenAI Prep - Production Configuration Script
# Configures environment for AWS production deployment

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-ielts-genai-prep}"
ENVIRONMENT="production"

echo "🔧 Configuring production environment for $STACK_NAME"
echo "Region: $AWS_REGION"

# Check if stack exists
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION &>/dev/null; then
    echo "✅ Stack $STACK_NAME found"
    
    # Get stack outputs
    echo "📋 Retrieving stack outputs..."
    
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text)
    
    WEBSOCKET_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`WebSocketUrl`].OutputValue' \
        --output text)
    
    USERS_TABLE=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`UsersTableName`].OutputValue' \
        --output text)
    
    SESSIONS_TABLE=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`SessionsTableName`].OutputValue' \
        --output text)
    
    echo "🌐 Production endpoints configured:"
    echo "API Gateway URL: $API_URL"
    echo "WebSocket URL: $WEBSOCKET_URL"
    echo "Users Table: $USERS_TABLE"
    echo "Sessions Table: $SESSIONS_TABLE"
    
    # Get ElastiCache endpoint
    echo "🔄 Retrieving ElastiCache endpoint..."
    REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters \
        --cache-cluster-id "${STACK_NAME}-redis" \
        --show-cache-node-info \
        --region $AWS_REGION \
        --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
        --output text 2>/dev/null || echo "")
    
    if [ ! -z "$REDIS_ENDPOINT" ]; then
        echo "✅ Redis endpoint: $REDIS_ENDPOINT"
    else
        echo "⚠️  Redis cluster not found or not ready yet"
    fi
    
    # Create production environment file
    cat > .env.production << EOF
# IELTS GenAI Prep - Production Configuration
# Generated on $(date)

# Environment
ENVIRONMENT=production
AWS_REGION=$AWS_REGION

# API Endpoints
API_GATEWAY_URL=$API_URL
WEBSOCKET_URL=$WEBSOCKET_URL

# DynamoDB Tables
DYNAMODB_USERS_TABLE=$USERS_TABLE
DYNAMODB_SESSIONS_TABLE=$SESSIONS_TABLE
DYNAMODB_ASSESSMENTS_TABLE=${STACK_NAME}-assessments
DYNAMODB_RUBRICS_TABLE=${STACK_NAME}-rubrics

# ElastiCache
ELASTICACHE_ENDPOINT=$REDIS_ENDPOINT

# Logging
CLOUDWATCH_LOG_GROUP=/aws/lambda/$STACK_NAME

# Disable development features
# REPLIT_ENVIRONMENT is unset for production
EOF
    
    echo "✅ Production configuration saved to .env.production"
    
    # Test connectivity
    echo "🧪 Testing production endpoints..."
    
    if curl -s "$API_URL/api/health" | grep -q "success"; then
        echo "✅ API Gateway health check passed"
    else
        echo "❌ API Gateway health check failed"
    fi
    
    # Check DynamoDB tables
    for table in $USERS_TABLE $SESSIONS_TABLE; do
        if aws dynamodb describe-table --table-name $table --region $AWS_REGION &>/dev/null; then
            echo "✅ DynamoDB table $table is active"
        else
            echo "❌ DynamoDB table $table not found"
        fi
    done
    
    echo "🎯 Production configuration complete!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Source the environment file: source .env.production"
    echo "2. Test user registration and login endpoints"
    echo "3. Verify Nova AI model access in Bedrock console"
    echo "4. Configure mobile app with production API URL"
    
else
    echo "❌ Stack $STACK_NAME not found in region $AWS_REGION"
    echo "Please deploy the infrastructure first using:"
    echo "./deploy-aws-infrastructure.sh"
    echo "sam deploy --guided"
    exit 1
fi