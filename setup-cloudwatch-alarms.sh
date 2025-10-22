#!/bin/bash
# Setup CloudWatch Alarms for IELTS AI Prep Security Monitoring
# Run this script to create all security and cost monitoring alarms

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
LAMBDA_FUNCTION_NAME="ielts-genai-prep-api"
ADMIN_EMAIL="${ADMIN_EMAIL}"
SNS_TOPIC_NAME="ielts-security-alerts"

echo "🚨 Setting up CloudWatch Alarms for Security Monitoring"
echo "========================================================"
echo "Region: $AWS_REGION"
echo "Lambda: $LAMBDA_FUNCTION_NAME"
echo "Alert Email: $ADMIN_EMAIL"
echo ""

# Step 1: Create SNS Topic for Alerts
echo "📧 Step 1: Creating SNS topic for email alerts..."

SNS_TOPIC_ARN=$(aws sns create-topic \
    --name $SNS_TOPIC_NAME \
    --region $AWS_REGION \
    --output text \
    --query 'TopicArn' 2>/dev/null || \
aws sns list-topics \
    --region $AWS_REGION \
    --output text \
    --query "Topics[?contains(TopicArn, '$SNS_TOPIC_NAME')].TopicArn | [0]")

echo "✅ SNS Topic: $SNS_TOPIC_ARN"

# Subscribe admin email to SNS topic
echo "   Subscribing $ADMIN_EMAIL to alerts..."
aws sns subscribe \
    --topic-arn $SNS_TOPIC_ARN \
    --protocol email \
    --notification-endpoint $ADMIN_EMAIL \
    --region $AWS_REGION \
    --output json > /dev/null 2>&1 || echo "   (Already subscribed)"

echo "   ⚠️  Check your email and confirm the subscription!"
echo ""

# Step 2: Create Alarm for Failed Login Attempts
echo "🔐 Step 2: Creating alarm for failed login attempts..."

aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-Failed-Login-Attempts" \
    --alarm-description "Alert when failed login attempts exceed threshold (brute force attack)" \
    --metric-name "FailedLoginAttempts" \
    --namespace "IELTS/Security" \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $AWS_REGION

echo "✅ Alarm created: Failed Login Attempts (>10 in 5 minutes)"
echo ""

# Step 3: Create Alarm for Lambda Errors
echo "⚠️  Step 3: Creating alarm for Lambda errors..."

aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-Lambda-High-Error-Rate" \
    --alarm-description "Alert when Lambda error rate exceeds 5%" \
    --metric-name "Errors" \
    --namespace "AWS/Lambda" \
    --dimensions Name=FunctionName,Value=$LAMBDA_FUNCTION_NAME \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 0.05 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $AWS_REGION \
    --treat-missing-data notBreaching

echo "✅ Alarm created: Lambda Error Rate (>5%)"
echo ""

# Step 4: Create Alarm for Lambda Throttling
echo "🚦 Step 4: Creating alarm for Lambda throttling..."

aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-Lambda-Throttling" \
    --alarm-description "Alert when Lambda function is being throttled" \
    --metric-name "Throttles" \
    --namespace "AWS/Lambda" \
    --dimensions Name=FunctionName,Value=$LAMBDA_FUNCTION_NAME \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $AWS_REGION \
    --treat-missing-data notBreaching

echo "✅ Alarm created: Lambda Throttling (>5 throttles in 5 minutes)"
echo ""

# Step 5: Create Alarm for Rate Limit Violations
echo "🚨 Step 5: Creating alarm for rate limit violations..."

aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-Rate-Limit-Violations" \
    --alarm-description "Alert when users exceed daily assessment limits frequently" \
    --metric-name "RateLimitViolations" \
    --namespace "IELTS/Security" \
    --statistic Sum \
    --period 3600 \
    --evaluation-periods 1 \
    --threshold 20 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $AWS_REGION \
    --treat-missing-data notBreaching

echo "✅ Alarm created: Rate Limit Violations (>20 per hour)"
echo ""

# Step 6: Create Alarm for Lambda Duration (Timeout Risk)
echo "⏱️  Step 6: Creating alarm for Lambda timeout risk..."

aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-Lambda-Long-Duration" \
    --alarm-description "Alert when Lambda executions take too long (timeout risk)" \
    --metric-name "Duration" \
    --namespace "AWS/Lambda" \
    --dimensions Name=FunctionName,Value=$LAMBDA_FUNCTION_NAME \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 25000 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $AWS_REGION \
    --treat-missing-data notBreaching

echo "✅ Alarm created: Lambda Long Duration (>25 seconds average)"
echo ""

# Step 7: Create Alarm for CloudFront 4xx Errors
echo "🌐 Step 7: Creating alarm for CloudFront client errors..."

CLOUDFRONT_DISTRIBUTION_ID="E1EPXAU67877FR"

aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-CloudFront-High-4xx-Errors" \
    --alarm-description "Alert when CloudFront 4xx error rate is high" \
    --metric-name "4xxErrorRate" \
    --namespace "AWS/CloudFront" \
    --dimensions Name=DistributionId,Value=$CLOUDFRONT_DISTRIBUTION_ID Name=Region,Value=Global \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region us-east-1 \
    --treat-missing-data notBreaching

echo "✅ Alarm created: CloudFront 4xx Error Rate (>5%)"
echo ""

# Step 8: Create Alarm for CloudFront 5xx Errors
echo "🔥 Step 8: Creating alarm for CloudFront server errors..."

aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-CloudFront-High-5xx-Errors" \
    --alarm-description "Alert when CloudFront 5xx error rate is high (server issues)" \
    --metric-name "5xxErrorRate" \
    --namespace "AWS/CloudFront" \
    --dimensions Name=DistributionId,Value=$CLOUDFRONT_DISTRIBUTION_ID Name=Region,Value=Global \
    --statistic Average \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 1 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region us-east-1 \
    --treat-missing-data notBreaching

echo "✅ Alarm created: CloudFront 5xx Error Rate (>1%)"
echo ""

# Summary
echo ""
echo "✅ All CloudWatch Alarms Created Successfully!"
echo ""
echo "📊 Alarms Summary:"
echo "   1. Failed Login Attempts (>10 in 5 min) → Brute force detection"
echo "   2. Lambda High Error Rate (>5%) → Application issues"
echo "   3. Lambda Throttling (>5 throttles) → Capacity issues"
echo "   4. Rate Limit Violations (>20/hour) → Abuse detection"
echo "   5. Lambda Long Duration (>25s avg) → Timeout risk"
echo "   6. CloudFront 4xx Errors (>5%) → Client errors"
echo "   7. CloudFront 5xx Errors (>1%) → Server errors"
echo ""
echo "📧 Email Alerts: $ADMIN_EMAIL"
echo "   ⚠️  IMPORTANT: Check your email and confirm the SNS subscription!"
echo ""
echo "🔍 View alarms in AWS Console:"
echo "   https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#alarmsV2:"
echo ""
echo "✅ Setup Complete!"
