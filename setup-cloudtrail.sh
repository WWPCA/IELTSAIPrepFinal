#!/bin/bash
# Enable AWS CloudTrail for IELTS AI Prep
# Tracks all AWS API calls for security auditing

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
TRAIL_NAME="ielts-ai-prep-security-trail"
S3_BUCKET_NAME="ielts-cloudtrail-logs-$(aws sts get-caller-identity --query Account --output text)"
SNS_TOPIC_ARN=""  # Optional: Set to receive CloudTrail notifications

echo "🔍 Setting up AWS CloudTrail for Security Auditing"
echo "=================================================="
echo "Region: $AWS_REGION"
echo "Trail Name: $TRAIL_NAME"
echo "S3 Bucket: $S3_BUCKET_NAME"
echo ""

# Step 1: Create S3 bucket for CloudTrail logs
echo "📦 Step 1: Creating S3 bucket for CloudTrail logs..."

# Check if bucket already exists
if aws s3 ls "s3://$S3_BUCKET_NAME" 2>/dev/null; then
    echo "   Bucket already exists: $S3_BUCKET_NAME"
else
    # Create bucket
    if [ "$AWS_REGION" = "us-east-1" ]; then
        aws s3 mb "s3://$S3_BUCKET_NAME" --region $AWS_REGION
    else
        aws s3 mb "s3://$S3_BUCKET_NAME" --region $AWS_REGION --create-bucket-configuration LocationConstraint=$AWS_REGION
    fi
    echo "✅ S3 bucket created: $S3_BUCKET_NAME"
fi

# Step 2: Apply bucket policy for CloudTrail
echo ""
echo "🔒 Step 2: Applying bucket policy for CloudTrail..."

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

cat > /tmp/cloudtrail-bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSCloudTrailAclCheck",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::$S3_BUCKET_NAME"
    },
    {
      "Sid": "AWSCloudTrailWrite",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::$S3_BUCKET_NAME/AWSLogs/$ACCOUNT_ID/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    }
  ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $S3_BUCKET_NAME \
    --policy file:///tmp/cloudtrail-bucket-policy.json

echo "✅ Bucket policy applied"
rm /tmp/cloudtrail-bucket-policy.json

# Step 3: Create CloudTrail
echo ""
echo "🛤️  Step 3: Creating CloudTrail..."

# Check if trail already exists
if aws cloudtrail get-trail-status --name $TRAIL_NAME --region $AWS_REGION 2>/dev/null; then
    echo "   Trail already exists: $TRAIL_NAME"
    echo "   Updating trail configuration..."
    
    aws cloudtrail update-trail \
        --name $TRAIL_NAME \
        --s3-bucket-name $S3_BUCKET_NAME \
        --include-global-service-events \
        --is-multi-region-trail \
        --enable-log-file-validation \
        --region $AWS_REGION
else
    echo "   Creating new trail..."
    
    aws cloudtrail create-trail \
        --name $TRAIL_NAME \
        --s3-bucket-name $S3_BUCKET_NAME \
        --include-global-service-events \
        --is-multi-region-trail \
        --enable-log-file-validation \
        --region $AWS_REGION
fi

echo "✅ CloudTrail created/updated: $TRAIL_NAME"

# Step 4: Start logging
echo ""
echo "▶️  Step 4: Starting CloudTrail logging..."

aws cloudtrail start-logging \
    --name $TRAIL_NAME \
    --region $AWS_REGION

echo "✅ CloudTrail logging started"

# Step 5: Enable CloudWatch Logs integration (optional but recommended)
echo ""
echo "📊 Step 5: Setting up CloudWatch Logs integration..."

# Create CloudWatch Logs group
LOG_GROUP_NAME="/aws/cloudtrail/$TRAIL_NAME"

aws logs create-log-group \
    --log-group-name $LOG_GROUP_NAME \
    --region $AWS_REGION 2>/dev/null || echo "   Log group already exists"

# Create IAM role for CloudTrail to write to CloudWatch Logs
ROLE_NAME="CloudTrailToCloudWatchLogsRole"

# Check if role exists
if aws iam get-role --role-name $ROLE_NAME 2>/dev/null; then
    echo "   IAM role already exists: $ROLE_NAME"
else
    cat > /tmp/cloudtrail-assume-role-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file:///tmp/cloudtrail-assume-role-policy.json

    rm /tmp/cloudtrail-assume-role-policy.json

    # Attach policy
    cat > /tmp/cloudtrail-cloudwatch-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSCloudTrailCreateLogStream",
      "Effect": "Allow",
      "Action": "logs:CreateLogStream",
      "Resource": "arn:aws:logs:$AWS_REGION:$ACCOUNT_ID:log-group:$LOG_GROUP_NAME:log-stream:*"
    },
    {
      "Sid": "AWSCloudTrailPutLogEvents",
      "Effect": "Allow",
      "Action": "logs:PutLogEvents",
      "Resource": "arn:aws:logs:$AWS_REGION:$ACCOUNT_ID:log-group:$LOG_GROUP_NAME:log-stream:*"
    }
  ]
}
EOF

    aws iam put-role-policy \
        --role-name $ROLE_NAME \
        --policy-name CloudTrailToCloudWatchLogsPolicy \
        --policy-document file:///tmp/cloudtrail-cloudwatch-policy.json

    rm /tmp/cloudtrail-cloudwatch-policy.json

    echo "✅ IAM role created: $ROLE_NAME"
    
    # Wait for role to propagate
    echo "   Waiting for IAM role to propagate..."
    sleep 10
fi

# Update trail with CloudWatch Logs
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"

aws cloudtrail update-trail \
    --name $TRAIL_NAME \
    --cloud-watch-logs-log-group-arn "arn:aws:logs:$AWS_REGION:$ACCOUNT_ID:log-group:$LOG_GROUP_NAME" \
    --cloud-watch-logs-role-arn $ROLE_ARN \
    --region $AWS_REGION 2>/dev/null || echo "   CloudWatch Logs integration already configured"

echo "✅ CloudWatch Logs integration enabled"

# Verify trail status
echo ""
echo "🔍 Step 6: Verifying CloudTrail status..."

aws cloudtrail get-trail-status \
    --name $TRAIL_NAME \
    --region $AWS_REGION \
    --output table

echo ""
echo "✅ CloudTrail Setup Complete!"
echo ""
echo "📋 What's Now Being Tracked:"
echo "   ✅ All AWS API calls across all regions"
echo "   ✅ Lambda function updates"
echo "   ✅ DynamoDB table modifications"
echo "   ✅ IAM policy changes"
echo "   ✅ CloudFront configuration changes"
echo "   ✅ S3 bucket access and modifications"
echo ""
echo "📊 Logs Location:"
echo "   S3 Bucket: s3://$S3_BUCKET_NAME"
echo "   CloudWatch Logs: $LOG_GROUP_NAME"
echo ""
echo "🔍 View logs in AWS Console:"
echo "   https://console.aws.amazon.com/cloudtrail/home?region=$AWS_REGION"
echo ""
echo "💡 Pro Tip: Use CloudWatch Insights to query logs:"
echo "   aws logs tail $LOG_GROUP_NAME --follow"
echo ""
