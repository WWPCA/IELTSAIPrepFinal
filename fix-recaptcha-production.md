# Fix reCAPTCHA for Production Domain

## Issue
The login page shows "ERROR for site owner: Invalid site key" because the reCAPTCHA is not configured for www.ieltsaiprep.com.

## Root Cause
The current reCAPTCHA keys are configured for a different domain (likely localhost or development) and need to be updated for the production domain.

## Solution Steps

### 1. Update reCAPTCHA Domain Configuration
- Go to Google reCAPTCHA Admin Console
- Find the existing reCAPTCHA site configuration
- Add `www.ieltsaiprep.com` to the authorized domains list
- Save the configuration

### 2. Alternative: Create New Production Keys
If the existing keys cannot be modified:
- Create a new reCAPTCHA v2 site for www.ieltsaiprep.com
- Configure the new site with the production domain
- Update the Lambda environment variables with the new keys

### 3. Update Lambda Function
Once the correct keys are obtained, I can update the Lambda function environment variables.

## Current Status
- The Lambda function code is correctly implementing reCAPTCHA
- The issue is purely domain authorization for the keys
- All other login functionality is working properly

## Next Steps
After you update the reCAPTCHA configuration for www.ieltsaiprep.com, I can update the Lambda function with the correct keys and test the login flow.