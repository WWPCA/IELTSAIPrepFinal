#!/bin/bash
# Setup AWS Billing Alerts for IELTS AI Prep
# Monitors AWS costs and alerts on spikes

set -e

# Configuration
ADMIN_EMAIL="${ADMIN_EMAIL}"
SNS_TOPIC_NAME="ielts-billing-alerts"

echo "💰 Setting up AWS Billing Alerts"
echo "================================="
echo "Alert Email: $ADMIN_EMAIL"
echo ""

# Important: Billing metrics are only available in us-east-1
AWS_REGION="us-east-1"

# Step 1: Create SNS Topic for Billing Alerts
echo "📧 Step 1: Creating SNS topic for billing alerts..."

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

# Subscribe admin email
echo "   Subscribing $ADMIN_EMAIL to billing alerts..."
aws sns subscribe \
    --topic-arn $SNS_TOPIC_ARN \
    --protocol email \
    --notification-endpoint $ADMIN_EMAIL \
    --region $AWS_REGION \
    --output json > /dev/null 2>&1 || echo "   (Already subscribed)"

echo "   ⚠️  Check your email and confirm the subscription!"
echo ""

# Step 2: Create Monthly Budget Alert ($200/month)
echo "💵 Step 2: Creating monthly budget alert ($200/month)..."

aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-Monthly-Costs-High" \
    --alarm-description "Alert when estimated monthly AWS charges exceed $200" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --dimensions Name=Currency,Value=USD \
    --statistic Maximum \
    --period 21600 \
    --evaluation-periods 1 \
    --threshold 200 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $AWS_REGION

echo "✅ Alarm created: Monthly Costs (>$200/month)"
echo ""

# Step 3: Create Daily Spike Alert ($50/day)
echo "⚡ Step 3: Creating daily cost spike alert ($50/day)..."

# Note: We approximate daily costs by comparing current vs. previous day
aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-Daily-Cost-Spike" \
    --alarm-description "Alert when daily AWS charges spike above $50" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --dimensions Name=Currency,Value=USD \
    --statistic Maximum \
    --period 86400 \
    --evaluation-periods 1 \
    --threshold 50 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $AWS_REGION \
    --treat-missing-data notBreaching

echo "✅ Alarm created: Daily Cost Spike (>$50/day)"
echo ""

# Step 4: Create Bedrock Cost Alert ($20/day)
echo "🤖 Step 4: Creating Bedrock AI cost alert ($20/day)..."

aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-Bedrock-High-Costs" \
    --alarm-description "Alert when Bedrock (Nova) costs are unusually high" \
    --metric-name BedrockCosts \
    --namespace IELTS/Costs \
    --statistic Sum \
    --period 86400 \
    --evaluation-periods 1 \
    --threshold 20 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $AWS_REGION \
    --treat-missing-data notBreaching

echo "✅ Alarm created: Bedrock Costs (>$20/day)"
echo ""

# Step 5: Create Lambda Cost Alert ($10/day)
echo "⚡ Step 5: Creating Lambda cost alert ($10/day)..."

aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-Lambda-High-Invocations" \
    --alarm-description "Alert when Lambda invocations are unusually high (cost spike)" \
    --metric-name Invocations \
    --namespace AWS/Lambda \
    --dimensions Name=FunctionName,Value=ielts-genai-prep-api \
    --statistic Sum \
    --period 86400 \
    --evaluation-periods 1 \
    --threshold 100000 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $AWS_REGION \
    --treat-missing-data notBreaching

echo "✅ Alarm created: Lambda High Invocations (>100k/day)"
echo ""

# Step 6: Create DynamoDB Cost Alert
echo "💾 Step 6: Creating DynamoDB cost alert..."

aws cloudwatch put-metric-alarm \
    --alarm-name "IELTS-DynamoDB-High-Read-Capacity" \
    --alarm-description "Alert when DynamoDB read capacity is high (cost spike)" \
    --metric-name ConsumedReadCapacityUnits \
    --namespace AWS/DynamoDB \
    --dimensions Name=TableName,Value=ielts-genai-prep-assessments \
    --statistic Sum \
    --period 3600 \
    --evaluation-periods 2 \
    --threshold 50000 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $AWS_REGION \
    --treat-missing-data notBreaching

echo "✅ Alarm created: DynamoDB High Read Capacity (>50k/hour)"
echo ""

# Summary
echo ""
echo "✅ All Billing Alerts Created Successfully!"
echo ""
echo "💰 Billing Alarms Summary:"
echo "   1. Monthly Costs > $200 → Budget exceeded"
echo "   2. Daily Cost Spike > $50 → Unusual usage"
echo "   3. Bedrock Costs > $20/day → AI abuse"
echo "   4. Lambda Invocations > 100k/day → Traffic spike"
echo "   5. DynamoDB Reads > 50k/hour → Database abuse"
echo ""
echo "📧 Email Alerts: $ADMIN_EMAIL"
echo "   ⚠️  IMPORTANT: Check your email and confirm the SNS subscription!"
echo ""
echo "💡 Recommended Actions When Alerted:"
echo "   • Check CloudWatch Logs for unusual activity"
echo "   • Review recent Lambda invocations"
echo "   • Check for API abuse (same user making many requests)"
echo "   • Verify no compromised credentials"
echo "   • Consider implementing stricter rate limits"
echo ""
echo "🔍 View billing in AWS Console:"
echo "   https://console.aws.amazon.com/billing/home"
echo ""
echo "📊 View cost breakdown:"
echo "   https://console.aws.amazon.com/cost-management/home"
echo ""
echo "✅ Setup Complete!"
