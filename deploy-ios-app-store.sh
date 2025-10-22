#!/bin/bash

# Deploy iOS App to Apple App Store
# IELTS GenAI Prep - App Store Deployment Script

echo "🚀 IELTS GenAI Prep - iOS App Store Deployment"
echo "=============================================="

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: iOS development requires macOS"
    echo "📋 Please run this script on a macOS system with Xcode installed"
    exit 1
fi

# Check for Xcode
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Error: Xcode not found"
    echo "📋 Please install Xcode from the Mac App Store"
    exit 1
fi

# Check for Capacitor CLI
if ! command -v npx &> /dev/null; then
    echo "❌ Error: Node.js/npm not found"
    echo "📋 Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Environment checks passed"
echo ""

# Sync Capacitor project
echo "🔄 Syncing Capacitor project..."
npx cap sync ios

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to sync Capacitor project"
    exit 1
fi

echo "✅ Capacitor sync completed"
echo ""

# Validate iOS project
echo "🔍 Validating iOS project..."
if [ ! -d "ios/App/App.xcworkspace" ]; then
    echo "❌ Error: iOS workspace not found"
    echo "📋 Please ensure the iOS platform has been added correctly"
    exit 1
fi

echo "✅ iOS project validation passed"
echo ""

# Display configuration
echo "📱 App Configuration:"
echo "   • App ID: com.ieltsgenaiprep.app"
echo "   • App Name: IELTS GenAI Prep"
echo "   • Server URL: https://www.ieltsaiprep.com"
echo "   • Bundle Version: 1.0.0"
echo ""

# Next steps instructions
echo "🎯 Next Steps for App Store Deployment:"
echo ""
echo "1. APPLE DEVELOPER ACCOUNT"
echo "   • Ensure you have an active Apple Developer Program membership (\$99/year)"
echo "   • Login to https://developer.apple.com/"
echo ""
echo "2. OPEN XCODE PROJECT"
echo "   • Run: npx cap open ios"
echo "   • Or manually open: ios/App/App.xcworkspace"
echo ""
echo "3. CONFIGURE CODE SIGNING"
echo "   • Select your development team in Xcode"
echo "   • Create iOS Distribution Certificate"
echo "   • Create App Store Provisioning Profile"
echo ""
echo "4. APP STORE CONNECT SETUP"
echo "   • Login to https://appstoreconnect.apple.com/"
echo "   • Create new app with Bundle ID: com.ieltsgenaiprep.app"
echo "   • Configure in-app purchases (4 products at \$36 each)"
echo ""
echo "5. BUILD AND UPLOAD"
echo "   • In Xcode: Select 'Any iOS Device' as target"
echo "   • Product > Archive"
echo "   • Upload to App Store Connect"
echo ""
echo "6. APP REVIEW SUBMISSION"
echo "   • Complete app metadata in App Store Connect"
echo "   • Upload screenshots and app icon"
echo "   • Submit for review"
echo ""

# Open Xcode if requested
read -p "🔧 Would you like to open the Xcode project now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Opening Xcode project..."
    npx cap open ios
else
    echo "📋 To open later, run: npx cap open ios"
fi

echo ""
echo "✅ iOS App Store deployment preparation complete!"
echo "📖 For detailed instructions, see: APPLE_APP_STORE_DEPLOYMENT.md"