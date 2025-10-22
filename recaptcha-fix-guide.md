# reCAPTCHA Fix Guide - Production Domain Configuration

## Current Issue
The login page shows "ERROR for site owner: Invalid site key" because the reCAPTCHA key is not configured for the production domain www.ieltsaiprep.com.

## Root Cause
The current reCAPTCHA site key `6LdD2VUrAAAAABG_Tt5fFYmWkRB4YFVHPdjggYzQ` is likely configured for a different domain (possibly localhost or development environment) and not authorized for www.ieltsaiprep.com.

## Solution Required

### Step 1: Update reCAPTCHA Domain Configuration
The existing reCAPTCHA key needs to be updated to include the production domain:

1. Go to Google reCAPTCHA Admin Console: https://www.google.com/recaptcha/admin
2. Find the existing reCAPTCHA site configuration
3. Add `www.ieltsaiprep.com` to the authorized domains list
4. Save the configuration

### Step 2: Alternative - Create New reCAPTCHA Key
If the existing key cannot be modified, create a new reCAPTCHA v2 key:

1. Go to Google reCAPTCHA Admin Console
2. Click "+" to create a new site
3. Configure:
   - **Label**: IELTS GenAI Prep Production
   - **reCAPTCHA type**: reCAPTCHA v2 ("I'm not a robot" Checkbox)
   - **Domains**: www.ieltsaiprep.com
4. Copy the new Site Key and Secret Key

### Step 3: Update Lambda Environment Variables
Once the correct keys are obtained, update the Lambda function:

```bash
aws lambda update-function-configuration \
    --function-name ielts-genai-prep-api \
    --environment Variables="{DYNAMODB_TABLE_PREFIX=ielts-genai-prep,ENVIRONMENT=production,RECAPTCHA_V2_SITE_KEY=NEW_SITE_KEY,RECAPTCHA_V2_SECRET_KEY=NEW_SECRET_KEY}"
```

## Current Configuration Status
- **Lambda Function**: ielts-genai-prep-api
- **Current Site Key**: [REDACTED - configured in Lambda environment]
- **Current Secret Key**: [REDACTED - configured in Lambda environment]
- **Production Domain**: www.ieltsaiprep.com
- **Error**: "Invalid site key" on login page

## Verification Steps
After updating the reCAPTCHA configuration:

1. **Test Login Page**: Visit www.ieltsaiprep.com/login
2. **Check reCAPTCHA**: The "I'm not a robot" checkbox should appear without error
3. **Test Login Flow**: Complete login with test credentials
4. **Verify Backend**: reCAPTCHA verification should work in Lambda function

## Test Credentials
- **Email**: test@ieltsgenaiprep.com
- **Password**: Test123!

## Expected Result
After fixing the reCAPTCHA configuration:
- Login page loads without "Invalid site key" error
- reCAPTCHA checkbox functions normally
- Login process works with proper reCAPTCHA validation
- Users can access dashboard after successful login

## Technical Details
The Lambda function code is correctly configured to:
1. Display reCAPTCHA widget on login page
2. Verify reCAPTCHA response with Google's API
3. Validate user IP and response token
4. Handle authentication after successful verification

The only missing piece is the proper domain authorization for the reCAPTCHA keys.