#!/bin/bash
# Script to create IELTS main web application Lambda function

set -e

# Configuration
FUNCTION_NAME="ielts-genai-prep-lambda"
RUNTIME="python3.11"
HANDLER="lambda_handler.handler"
ROLE_NAME="ielts-lambda-execution-role"
REGION="us-east-1"
ZIP_FILE="ielts-lambda-deployment.zip"

echo "🚀 Creating Lambda function for IELTS AI Prep..."
echo ""

# Step 1: Create IAM role if it doesn't exist
echo "📋 Step 1: Creating Lambda execution role..."

TRUST_POLICY='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'

# Try to create the role
aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document "$TRUST_POLICY" \
  --description "Execution role for IELTS Lambda function" \
  2>/dev/null || echo "Role may already exist, continuing..."

# Attach basic Lambda execution policy
aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Attach DynamoDB access
aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

# Attach SES access
aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonSESFullAccess

# Attach Bedrock access
aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# Get the role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
echo "✅ Role ARN: $ROLE_ARN"
echo ""

# Wait for role to propagate
echo "⏳ Waiting for IAM role to propagate (10 seconds)..."
sleep 10

# Step 2: Create Lambda function
echo "📦 Step 2: Creating Lambda function..."

aws lambda create-function \
  --function-name $FUNCTION_NAME \
  --runtime $RUNTIME \
  --role $ROLE_ARN \
  --handler $HANDLER \
  --zip-file fileb://$ZIP_FILE \
  --timeout 30 \
  --memory-size 1024 \
  --region $REGION \
  --description "IELTS AI Prep - Main Flask Application" \
  --environment Variables={
    AWS_REGION=$REGION,
    ENVIRONMENT=production,
    SESSION_SECRET=CHANGE_THIS_TO_SECURE_SECRET
  }

echo ""
echo "✅ Lambda function created successfully!"
echo ""
echo "Next steps:"
echo "1. Update environment variables in Lambda console"
echo "2. Add SESSION_SECRET with a secure value"
echo "3. Configure API Gateway or Application Load Balancer"
echo "4. Test the function"
echo ""
echo "Test command:"
echo "  aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"httpMethod\":\"GET\",\"path\":\"/health\"}' response.json"
