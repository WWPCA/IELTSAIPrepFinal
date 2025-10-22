#!/bin/bash

# IELTS AI Prep - GitHub Export Script
# Pushes complete updated codebase to GitHub repository
# Repository: https://github.com/WWPCA/IELTSAIPrepFinal

set -e  # Exit on error

echo "=================================="
echo "IELTS AI Prep - GitHub Export"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Git not initialized. Initializing...${NC}"
    git init
    git branch -M main
    echo -e "${GREEN}✓ Git initialized${NC}"
else
    echo -e "${GREEN}✓ Git already initialized${NC}"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo -e "${YELLOW}Creating .gitignore...${NC}"
    cat > .gitignore << 'EOF'
# Build outputs
.aws-sam/
android/build/
android/app/build/
ios/build/
ios/Pods/
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg-info/
dist/
build/

# Archives
*.zip
*.tar.gz
*.rar

# Environment files
.env
.env.local
.env.production
*.key
*.pem

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Logs
*.log
access_logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Temporary files
attached_assets/
github_backup/
archive/
.replit
.config/

# Duplicates and status docs (keep important ones)
*FIXES_COMPLETE.md
*SUMMARY.md
*AUDIT.md
*-FIX-*.md
LOGIN-FIX-COMPLETE.md
RECAPTCHA-*.md
TABLE_MAPPING_*.md
TEST-CREDENTIALS-*.md
ULTIMATE-*.md
URGENT-*.md
VERIFICATION*.md
COMPREHENSIVE-*.md
MOBILE_INTEGRATION_COMPLETE.md
MOBILE_APP_STATUS_AND_PLAN.md
FINAL_STATUS_REPORT.md
EMAIL_TEMPLATES_COMPLETE.md
EMAIL_TEMPLATE_AUDIT.md
EMAIL_AND_AI_UPDATES_SUMMARY.md
NOVA_PRO_ESCALATION_DESIGN.md

# Keep these important docs
!README.md
!replit.md
!DEPLOYMENT_COMPLETE.md
!GITHUB_EXPORT_READY.md
!API_ENDPOINT_AUDIT.md
!DYNAMODB_TABLE_AUDIT.md
!LAMBDA_ARCHITECTURE_EXPLAINED.md
!app-store-setup-steps.md
EOF
    echo -e "${GREEN}✓ .gitignore created${NC}"
else
    echo -e "${GREEN}✓ .gitignore exists${NC}"
fi

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo -e "${YELLOW}Creating .env.example...${NC}"
    cat > .env.example << 'EOF'
# IELTS AI Prep - Environment Variables Template
# Copy this file to .env and fill in your actual values

# Session & Security
SESSION_SECRET=your_session_secret_here_min_32_chars

# Google reCAPTCHA v2
RECAPTCHA_V2_SECRET_KEY=your_recaptcha_secret_key_here
RECAPTCHA_V2_SITE_KEY=your_recaptcha_site_key_here

# Admin Credentials
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD_HASH=your_bcrypt_hash_here

# AWS Configuration (auto-configured in Lambda)
AWS_REGION=us-east-1
DATABASE_URL=auto_configured_by_lambda

# Domain Configuration
DOMAIN_URL=https://www.ieltsaiprep.com

# Email Configuration (using AWS SES)
# No configuration needed - handled automatically by boto3

# AI Models (configured in Lambda environment)
# Nova Micro: amazon.nova-micro-v1:0
# Nova Pro: amazon.nova-pro-v1:0
# Gemini: Google GenAI SDK handles configuration
EOF
    echo -e "${GREEN}✓ .env.example created${NC}"
else
    echo -e "${GREEN}✓ .env.example exists${NC}"
fi

echo ""
echo "=================================="
echo "Adding files to git..."
echo "=================================="

# Add all files (respecting .gitignore)
git add .

# Show what will be committed
echo ""
echo -e "${YELLOW}Files staged for commit:${NC}"
git status --short | head -20
if [ $(git status --short | wc -l) -gt 20 ]; then
    echo "... and $(( $(git status --short | wc -l) - 20 )) more files"
fi

echo ""
echo "=================================="
echo "Creating commit..."
echo "=================================="

# Commit with comprehensive message
git commit -m "Complete IELTS AI Prep codebase - Production ready

Updates included:
- Mobile API client: Updated to use www.ieltsaiprep.com (CloudFront)
- WebSocket endpoints: Configured for production
- Email templates: Updated with info@ieltsaiprep.com
- Nova Pro escalation: Customer support with 70% cost savings
- Capacitor apps: iOS and Android production-ready
- AWS deployment: Lambda, DynamoDB, CloudFront, API Gateway
- AI support system: Nova Micro → Pro → Human escalation

Architecture:
- Hybrid AWS-Google Cloud (AWS primary, Gemini for speech)
- Serverless Lambda with automatic scaling
- CloudFront CDN with custom domain
- DynamoDB for user data and assessments
- Mobile-first in-app purchases

Mobile Apps:
- iOS: com.ieltsaiprep.genai
- Android: com.ieltsaiprep.app
- Capacitor 7.x with native plugins
- Production server: https://www.ieltsaiprep.com

AI Models:
- Amazon Nova Micro: Text assessments (~\$0.003 each)
- Amazon Nova Pro: Complex support questions (~\$0.01 each)
- Google Gemini 2.5 Flash Lite/Flash: Speech assessments with DSQ

Deployment:
- Primary Lambda: ielts-genai-prep-api
- API Gateway: n0cpf1rmvc (prod stage)
- CloudFront: E1EPXAU67877FR
- Custom domain: www.ieltsaiprep.com

Date: October 22, 2025
Status: Production deployed and verified" || {
    echo -e "${YELLOW}No changes to commit (already committed)${NC}"
}

echo ""
echo "=================================="
echo "Checking remote configuration..."
echo "=================================="

# Check if remote exists
if git remote | grep -q "origin"; then
    echo -e "${GREEN}✓ Remote 'origin' already configured${NC}"
    git remote -v
else
    echo -e "${YELLOW}Adding remote 'origin'...${NC}"
    git remote add origin https://github.com/WWPCA/IELTSAIPrepFinal.git
    echo -e "${GREEN}✓ Remote added${NC}"
    git remote -v
fi

echo ""
echo "=================================="
echo "Ready to push to GitHub!"
echo "=================================="
echo ""
echo -e "${YELLOW}Repository:${NC} https://github.com/WWPCA/IELTSAIPrepFinal"
echo -e "${YELLOW}Branch:${NC} main"
echo ""
echo -e "${GREEN}Run the following command to push:${NC}"
echo ""
echo -e "${YELLOW}git push -u origin main${NC}"
echo ""
echo "Or if the repository already has commits:"
echo -e "${YELLOW}git push -u origin main --force${NC}"
echo ""
echo "=================================="
echo -e "${GREEN}✓ Export preparation complete!${NC}"
echo "=================================="
