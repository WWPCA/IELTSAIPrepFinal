# CloudFormation Console Deployment Guide

## Deploy IELTS GenAI Prep Infrastructure via AWS Console

### Step 1: Create New Stack
1. In CloudFormation console, click "Create stack" → "With new resources (standard)"
2. Choose "Upload a template file"
3. Upload: `ielts-genai-prep-cloudformation.yaml`
4. Click "Next"

### Step 2: Stack Configuration
**Stack name:** `ielts-genai-prep-production`

**Parameters:**
- DomainName: `ieltsaiprep.com`
- Environment: `production`
- LambdaS3Bucket: `ielts-genai-prep-deployments-116981806044`
- LambdaS3Key: `lambda/ielts-genai-prep-production.zip`

### Step 3: Stack Options
- Tags:
  - Project: `IELTSGenAIPrep`
  - Environment: `production`
  - ManagedBy: `CloudFormation`
- IAM Capabilities: Check "I acknowledge that AWS CloudFormation might create IAM resources with custom names"

### Step 4: Deploy
Click "Submit" to create the stack

## What This Deploys
- Route 53 hosted zone for ieltsaiprep.com
- SSL certificate with automatic DNS validation
- Lambda function with proper IAM roles
- API Gateway with custom domain
- 4 DynamoDB tables for app data
- Health checks and monitoring
- Complete DNS records pointing to your infrastructure

## Expected Result
Your complete IELTS GenAI Prep infrastructure will be deployed with the professional domain ieltsaiprep.com, ready for mobile app submission to the App Store.