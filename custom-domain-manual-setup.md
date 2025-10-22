# Custom Domain Setup - ieltsaiprep.com
## Manual AWS Console Configuration

Your current backend: `https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod`
Target domain: `https://ieltsaiprep.com`

## Step 1: Request SSL Certificate

1. Go to **AWS Certificate Manager** (ACM) Console
   - Region: **us-east-1** (must match your API Gateway)
   - Click "Request a certificate"

2. **Certificate Details:**
   - Certificate type: Request public certificate
   - Domain names: 
     - `ieltsaiprep.com`
     - `www.ieltsaiprep.com`
   - Validation method: **DNS validation**
   - Key algorithm: RSA 2048

3. **DNS Validation Records:**
   - AWS will provide CNAME records
   - Add these to your domain registrar's DNS

## Step 2: Create Custom Domain in API Gateway

1. Go to **API Gateway Console**
   - Click "Custom domain names"
   - Click "Create domain name"

2. **Domain Configuration:**
   - Domain name: `ieltsaiprep.com`
   - Certificate: Select your validated certificate
   - Endpoint type: **Regional**
   - Security policy: TLS 1.2

3. **API Mappings:**
   - Click "Add mapping"
   - API: Select your existing API (`n0cpf1rmvc`)
   - Stage: `prod`
   - Path: (leave empty for root)

## Step 3: DNS Configuration

Add these records to your domain registrar:

### Main Domain Record
```
Type: A
Name: @
Value: [Target Domain from API Gateway - will be provided]
TTL: 300
```

### WWW Subdomain
```
Type: CNAME
Name: www
Value: ieltsaiprep.com
TTL: 300
```

## Step 4: Get Target Domain Name

After creating the custom domain in API Gateway:
1. Click on your domain name `ieltsaiprep.com`
2. Copy the **Target domain name** (looks like: `d-xxxxxxxxx.execute-api.us-east-1.amazonaws.com`)
3. Use this as the A record value in your DNS

## Step 5: Test Configuration

After DNS propagation (24-48 hours):
- https://ieltsaiprep.com
- https://ieltsaiprep.com/login
- https://ieltsaiprep.com/privacy-policy

## Expected Results

✅ Professional domain for all users
✅ SSL certificate for security
✅ Same backend functionality
✅ Mobile app uses ieltsaiprep.com
✅ Ready for App Store submission

## Timeline
- SSL certificate validation: 5-10 minutes
- Custom domain creation: 2-3 minutes
- DNS propagation: 24-48 hours
- Total setup time: 2-3 days

## Next Steps After Domain is Live
1. Update mobile app configuration
2. Test all endpoints
3. Submit to App Store with professional domain