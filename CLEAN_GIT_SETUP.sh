#!/bin/bash
# Clean Git Repository Setup - Removes all large files from history

echo "=== IELTS AI Prep - Clean Git Setup ==="
echo "This will create a fresh git repository without large files"
echo ""

# Step 1: Backup current .git directory
echo "Step 1: Backing up current git history..."
mv .git .git.backup.$(date +%s) 2>/dev/null || true
echo "✓ Backup created"

# Step 2: Initialize fresh repository
echo ""
echo "Step 2: Creating fresh git repository..."
git init
echo "✓ Fresh repository initialized"

# Step 3: Add all files (respecting .gitignore)
echo ""
echo "Step 3: Staging files (respecting .gitignore)..."
git add .
echo "✓ Files staged"

# Step 4: Show what will be committed
echo ""
echo "Step 4: Checking repository size..."
STAGED_SIZE=$(git ls-files | xargs -I{} du -b "{}" 2>/dev/null | awk '{sum+=$1} END {print sum/1024/1024}')
echo "Total staged files: ${STAGED_SIZE}MB (should be <500MB)"

# Step 5: Verify no large files
echo ""
echo "Step 5: Checking for files >50MB..."
LARGE_FILES=$(git ls-files | xargs -I{} sh -c 'size=$(stat -c%s "{}" 2>/dev/null || stat -f%z "{}" 2>/dev/null); if [ "$size" -gt 52428800 ]; then echo "$(echo "scale=2; $size/1048576" | bc)MB {}" ; fi')

if [ -n "$LARGE_FILES" ]; then
    echo "⚠️  WARNING: Large files detected:"
    echo "$LARGE_FILES"
    echo ""
    echo "Add these to .gitignore and run: git reset"
    exit 1
else
    echo "✓ No files over 50MB"
fi

# Step 6: Create initial commit
echo ""
echo "Step 6: Creating initial commit..."
git commit -m "Initial commit: IELTS AI Prep with production CI/CD

Production-ready platform with:
- AWS Lambda deployment (ielts-genai-prep-api)
- Mobile apps (iOS/Android) with Capacitor
- GitHub Actions CI/CD workflows
- Unit tests, security scanning, mobile builds
- DynamoDB data layer, Bedrock AI integration
- Gemini Live Audio for speaking assessments

Domain: www.ieltsaiprep.com
CloudFront: E1EPXAU67877FR
API Gateway: n0cpf1rmvc/prod"

echo "✓ Initial commit created"

# Step 7: Add remote
echo ""
echo "Step 7: Setting up GitHub remote..."
git remote add origin https://github.com/WWPCA/IELTSAIPrepFinal.git
echo "✓ Remote configured"

# Step 8: Ready to push
echo ""
echo "=== READY TO PUSH ==="
echo "Run this command to push to GitHub:"
echo ""
echo "  git push -u origin main --force"
echo ""
echo "This will upload your clean repository without large files."
