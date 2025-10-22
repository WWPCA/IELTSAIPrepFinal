#!/bin/bash
# IELTS GenAI Prep - Mobile App Deployment Script

echo "🚀 Deploying IELTS GenAI Prep Mobile App..."

# Build and sync mobile assets
echo "📱 Building mobile app assets..."
npx cap copy
npx cap sync

# Open iOS project for App Store submission
echo "📱 Opening iOS project in Xcode..."
npx cap open ios

echo "✅ iOS project opened in Xcode"
echo ""
echo "Next Steps for iOS App Store:"
echo "1. In Xcode, select 'Any iOS Device' as build target"
echo "2. Go to Product > Archive"
echo "3. Once archived, click 'Distribute App'"
echo "4. Select 'App Store Connect'"
echo "5. Upload to App Store Connect"
echo ""
echo "📱 To open Android project for Google Play:"
echo "Run: npx cap open android"
echo ""
echo "Next Steps for Google Play Store:"
echo "1. In Android Studio, go to Build > Generate Signed Bundle/APK"
echo "2. Select 'Android App Bundle'"
echo "3. Create or use existing keystore"
echo "4. Build release AAB file"
echo "5. Upload to Google Play Console"
echo ""
echo "🔗 Production Backend: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod"
echo "📖 Full deployment guide: See MOBILE_APP_DEPLOYMENT_GUIDE.md"