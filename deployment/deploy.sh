#!/bin/bash
# Deploy IELTS Speaking Assessment WebSocket to AWS Lambda

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-production}"
AWS_REGION="${2:-us-east-1}"
GCP_CREDENTIALS_FILE="${3:-gcp-service-account.json}"

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}IELTS Speaking Assessment Deployment${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Environment: $ENVIRONMENT"
echo "AWS Region: $AWS_REGION"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI not installed${NC}"
    exit 1
fi

if ! command -v sam &> /dev/null; then
    echo -e "${RED}Error: AWS SAM CLI not installed${NC}"
    echo "Install: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"

# Step 1: Store GCP credentials in AWS Secrets Manager
echo ""
echo -e "${YELLOW}Step 1: Storing GCP credentials in AWS Secrets Manager...${NC}"

SECRET_NAME="gemini-vertex-ai-credentials"

if [ ! -f "$GCP_CREDENTIALS_FILE" ]; then
    echo -e "${RED}Error: GCP credentials file not found: $GCP_CREDENTIALS_FILE${NC}"
    echo "Please provide your GCP service account JSON file"
    exit 1
fi

# Check if secret already exists
if aws secretsmanager describe-secret --secret-id $SECRET_NAME --region $AWS_REGION &> /dev/null; then
    echo "Secret already exists. Updating..."
    aws secretsmanager update-secret \
        --secret-id $SECRET_NAME \
        --secret-string file://$GCP_CREDENTIALS_FILE \
        --region $AWS_REGION
else
    echo "Creating new secret..."
    aws secretsmanager create-secret \
        --name $SECRET_NAME \
        --description "GCP service account for Vertex AI Gemini" \
        --secret-string file://$GCP_CREDENTIALS_FILE \
        --region $AWS_REGION
fi

echo -e "${GREEN}✓ GCP credentials stored${NC}"

# Step 2: Install Python dependencies
echo ""
echo -e "${YELLOW}Step 2: Installing Python dependencies...${NC}"

pip install -r requirements.txt -t . --upgrade

# Install Google Cloud libraries
pip install google-cloud-aiplatform google-auth google-genai -t . --upgrade

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Copy necessary files to deployment directory
echo ""
echo -e "${YELLOW}Step 3: Copying project files...${NC}"

# Copy core services
cp ../gemini_live_audio_service_aws.py .
cp ../gemini_regional_router.py .
cp ../personalized_improvement_service.py .
cp ../ielts_workflow_manager.py .

echo -e "${GREEN}✓ Files copied${NC}"

# Step 4: Build SAM application
echo ""
echo -e "${YELLOW}Step 4: Building SAM application...${NC}"

sam build --use-container --region $AWS_REGION

echo -e "${GREEN}✓ Build complete${NC}"

# Step 5: Deploy to AWS
echo ""
echo -e "${YELLOW}Step 5: Deploying to AWS...${NC}"

sam deploy \
    --stack-name ielts-speaking-$ENVIRONMENT \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        GCPCredentialsSecretName=$SECRET_NAME \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION \
    --no-confirm-changeset \
    --resolve-s3

echo -e "${GREEN}✓ Deployment complete${NC}"

# Step 6: Get WebSocket URL
echo ""
echo -e "${YELLOW}Step 6: Retrieving WebSocket endpoint...${NC}"

WEBSOCKET_URL=$(aws cloudformation describe-stacks \
    --stack-name ielts-speaking-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`WebSocketURL`].OutputValue' \
    --output text \
    --region $AWS_REGION)

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Deployment Successful!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${GREEN}WebSocket URL:${NC} $WEBSOCKET_URL"
echo ""
echo "Next steps:"
echo "1. Update your frontend to use this WebSocket URL"
echo "2. Test the connection with a speaking assessment"
echo "3. Monitor CloudWatch logs for errors"
echo ""
echo "CloudWatch Logs:"
echo "  aws logs tail /aws/lambda/${ENVIRONMENT}-ielts-speaking-websocket --follow"
echo ""
