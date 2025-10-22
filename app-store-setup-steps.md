# App Store Connect Setup - Next Steps

## Step 1: App Information (Required)
Click on **"App Information"** in the left sidebar and fill out:

- **Category:** Education
- **Subcategory:** Language Learning  
- **Content Rights:** No, this app does not use third-party content
- **Age Rating:** Click "Edit" and answer the questionnaire (should result in 4+ rating)

## Step 2: Pricing and Availability
Click **"Pricing and Availability"** in the left sidebar:

- **Price:** Free
- **Availability:** All countries and regions
- **App Store Distribution:** Make available on the App Store

## Step 3: App Privacy (Critical)
Click **"App Privacy"** in the left sidebar:

- **Privacy Policy URL:** https://ieltsaiprep.com/privacy-policy
- **Data Collection:** Answer privacy questionnaire based on your app's data usage

## Step 4: Create In-App Purchases
Click **"In-App Purchases"** in the left sidebar, then create these 4 products:

### Product 1: Academic Writing Assessment
- **Type:** Non-Consumable
- **Reference Name:** Academic Writing Assessment
- **Product ID:** com.ieltsgenaiprep.academic.writing
- **Price:** $36.00 USD

### Product 2: General Writing Assessment  
- **Type:** Non-Consumable
- **Reference Name:** General Writing Assessment
- **Product ID:** com.ieltsgenaiprep.general.writing
- **Price:** $36.00 USD

### Product 3: Academic Speaking Assessment
- **Type:** Non-Consumable
- **Reference Name:** Academic Speaking Assessment
- **Product ID:** com.ieltsgenaiprep.academic.speaking
- **Price:** $36.00 USD

### Product 4: General Speaking Assessment
- **Type:** Non-Consumable
- **Reference Name:** General Speaking Assessment
- **Product ID:** com.ieltsgenaiprep.general.speaking
- **Price:** $36.00 USD

## Step 5: Upload App Screenshots
Currently showing: "0 of 3 App Previews | 0 of 10 Screenshots"

You need to upload iPhone screenshots (at least 3 required).

## Step 6: Fill App Description
Add your app description in the "Promotional Text" section using the content from APP_STORE_SUBMISSION_CHECKLIST.md

## Step 7: Build and Upload App
After completing the above, run:
```bash
./deploy-mobile-app.sh
```

This will open Xcode where you can build and upload your app.

## Current Status
✅ App created in App Store Connect
➡️ Complete Steps 1-6 above
➡️ Then build and upload app binary