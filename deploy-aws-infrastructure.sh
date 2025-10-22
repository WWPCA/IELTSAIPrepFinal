#!/bin/bash

# IELTS GenAI Prep - AWS Infrastructure Deployment Script
# This script creates all required AWS resources for production deployment

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
PROJECT_NAME="ielts-genai-prep"
ENVIRONMENT="${ENVIRONMENT:-production}"

echo "🚀 Starting AWS infrastructure deployment for $PROJECT_NAME"
echo "Region: $AWS_REGION"
echo "Environment: $ENVIRONMENT"

# Check AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Create DynamoDB Tables
echo "📊 Creating DynamoDB tables..."

# Users table
aws dynamodb create-table \
    --table-name "${PROJECT_NAME}-users" \
    --attribute-definitions \
        AttributeName=email,AttributeType=S \
    --key-schema \
        AttributeName=email,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region $AWS_REGION \
    --tags Key=Project,Value=$PROJECT_NAME Key=Environment,Value=$ENVIRONMENT \
    || echo "Users table may already exist"

# Sessions table
aws dynamodb create-table \
    --table-name "${PROJECT_NAME}-sessions" \
    --attribute-definitions \
        AttributeName=session_id,AttributeType=S \
    --key-schema \
        AttributeName=session_id,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region $AWS_REGION \
    --tags Key=Project,Value=$PROJECT_NAME Key=Environment,Value=$ENVIRONMENT \
    || echo "Sessions table may already exist"

# Assessment results table
aws dynamodb create-table \
    --table-name "${PROJECT_NAME}-assessments" \
    --attribute-definitions \
        AttributeName=result_id,AttributeType=S \
        AttributeName=user_email,AttributeType=S \
    --key-schema \
        AttributeName=result_id,KeyType=HASH \
    --global-secondary-indexes \
        'IndexName=user_email-index,KeySchema=[{AttributeName=user_email,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}' \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region $AWS_REGION \
    --tags Key=Project,Value=$PROJECT_NAME Key=Environment,Value=$ENVIRONMENT \
    || echo "Assessments table may already exist"

# Assessment rubrics table
aws dynamodb create-table \
    --table-name "${PROJECT_NAME}-rubrics" \
    --attribute-definitions \
        AttributeName=assessment_type,AttributeType=S \
    --key-schema \
        AttributeName=assessment_type,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region $AWS_REGION \
    --tags Key=Project,Value=$PROJECT_NAME Key=Environment,Value=$ENVIRONMENT \
    || echo "Rubrics table may already exist"

echo "⏳ Waiting for DynamoDB tables to be active..."
aws dynamodb wait table-exists --table-name "${PROJECT_NAME}-users" --region $AWS_REGION
aws dynamodb wait table-exists --table-name "${PROJECT_NAME}-sessions" --region $AWS_REGION
aws dynamodb wait table-exists --table-name "${PROJECT_NAME}-assessments" --region $AWS_REGION
aws dynamodb wait table-exists --table-name "${PROJECT_NAME}-rubrics" --region $AWS_REGION

# Enable TTL on sessions table
aws dynamodb update-time-to-live \
    --table-name "${PROJECT_NAME}-sessions" \
    --time-to-live-specification Enabled=true,AttributeName=expires_at \
    --region $AWS_REGION \
    || echo "TTL may already be enabled"

# Create ElastiCache subnet group
echo "🔄 Creating ElastiCache subnet group..."
SUBNET_IDS=$(aws ec2 describe-subnets --query 'Subnets[?AvailabilityZone==`'$AWS_REGION'a` || AvailabilityZone==`'$AWS_REGION'b`].SubnetId' --output text --region $AWS_REGION)
if [ ! -z "$SUBNET_IDS" ]; then
    aws elasticache create-cache-subnet-group \
        --cache-subnet-group-name "${PROJECT_NAME}-subnet-group" \
        --cache-subnet-group-description "Subnet group for $PROJECT_NAME Redis cluster" \
        --subnet-ids $SUBNET_IDS \
        --region $AWS_REGION \
        || echo "Subnet group may already exist"
fi

# Create ElastiCache Redis cluster
echo "🔴 Creating ElastiCache Redis cluster..."
aws elasticache create-cache-cluster \
    --cache-cluster-id "${PROJECT_NAME}-redis" \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1 \
    --cache-subnet-group-name "${PROJECT_NAME}-subnet-group" \
    --region $AWS_REGION \
    --tags Key=Project,Value=$PROJECT_NAME Key=Environment,Value=$ENVIRONMENT \
    || echo "Redis cluster may already exist"

# Create CloudWatch Log Group
echo "📝 Creating CloudWatch log group..."
aws logs create-log-group \
    --log-group-name "/aws/lambda/${PROJECT_NAME}" \
    --region $AWS_REGION \
    || echo "Log group may already exist"

# Create IAM role for Lambda
echo "🔐 Creating IAM role..."
cat > /tmp/trust-policy.json << EOF
{
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
}
EOF

aws iam create-role \
    --role-name "${PROJECT_NAME}-lambda-role" \
    --assume-role-policy-document file:///tmp/trust-policy.json \
    || echo "IAM role may already exist"

# Create IAM policy
cat > /tmp/lambda-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:${AWS_REGION}:*:table/${PROJECT_NAME}-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "elasticache:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:${AWS_REGION}::foundation-model/amazon.nova-sonic-v1:0",
                "arn:aws:bedrock:${AWS_REGION}::foundation-model/amazon.nova-micro-v1:0"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:${AWS_REGION}:*:*"
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name "${PROJECT_NAME}-lambda-role" \
    --policy-name "${PROJECT_NAME}-lambda-policy" \
    --policy-document file:///tmp/lambda-policy.json

# Attach basic Lambda execution role
aws iam attach-role-policy \
    --role-name "${PROJECT_NAME}-lambda-role" \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

echo "✅ Infrastructure deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Wait for ElastiCache cluster to be available (5-10 minutes)"
echo "2. Get the Redis endpoint: aws elasticache describe-cache-clusters --cache-cluster-id ${PROJECT_NAME}-redis --show-cache-node-info --region $AWS_REGION"
echo "3. Update your environment variables with the new endpoints"
echo "4. Deploy your Lambda function using the SAM template"
echo ""
echo "🔧 Environment variables to set:"
echo "DATABASE_URL=https://dynamodb.${AWS_REGION}.amazonaws.com"
echo "AWS_REGION=${AWS_REGION}"
echo "CLOUDWATCH_LOG_GROUP=/aws/lambda/${PROJECT_NAME}"
echo "ELASTICACHE_ENDPOINT=[Get from step 2 above]"

# Clean up temporary files
rm -f /tmp/trust-policy.json /tmp/lambda-policy.json