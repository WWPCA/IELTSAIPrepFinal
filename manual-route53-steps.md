# Manual Route 53 Custom Domain Setup

## Setup Professional Domain for IELTS GenAI Prep

### Step 1: Create Route 53 Hosted Zone
1. Open AWS Route 53 console
2. Click "Create hosted zone"
3. Domain name: `ieltsaiprep.com`
4. Type: Public hosted zone
5. Click "Create"
6. **Save the 4 nameservers** from the NS record

### Step 2: Request SSL Certificate
1. Open AWS Certificate Manager console
2. Click "Request certificate"
3. Domain names:
   - `ieltsaiprep.com`
   - `www.ieltsaiprep.com`
4. Validation method: DNS validation
5. Click "Request"
6. Click "Create records in Route 53" for both domains
7. Wait for certificate validation (5-30 minutes)

### Step 3: Create API Gateway Custom Domain
1. Open API Gateway console
2. Click "Custom domain names"
3. Click "Create"
4. Domain name: `ieltsaiprep.com`
5. Certificate: Select your validated certificate
6. Click "Create"
7. Note the **Target domain name** (looks like d-xyz.execute-api.us-east-1.amazonaws.com)

### Step 4: Configure Base Path Mapping
1. In the custom domain you just created
2. Click "API mappings"
3. Click "Configure API mappings"
4. Add mapping:
   - API: `ielts-genai-prep-production` (ID: n0cpf1rmvc)
   - Stage: `prod`
   - Path: (leave empty)
5. Click "Save"

### Step 5: Create DNS Records in Route 53
1. Return to Route 53 hosted zone for ieltsaiprep.com
2. Click "Create record"
3. Record 1:
   - Name: (leave empty for root domain)
   - Type: A
   - Alias: Yes
   - Route traffic to: API Gateway
   - Region: us-east-1
   - API Gateway: Select your custom domain
4. Click "Create records"
5. Create second record:
   - Name: `www`
   - Type: A
   - Alias: Yes
   - Route traffic to: API Gateway
   - Region: us-east-1
   - API Gateway: Select your custom domain

### Step 6: Update Nameservers at Namecheap
1. Login to Namecheap
2. Go to Domain List → ieltsaiprep.com
3. Click "Manage"
4. Change nameservers to "Custom DNS"
5. Add the 4 Route 53 nameservers from Step 1
6. Save changes

### Expected Timeline
- SSL certificate validation: 5-30 minutes
- DNS propagation after nameserver update: 24-48 hours
- Total setup time: 15-20 minutes active work

### Test Commands (after DNS propagation)
```bash
curl -I https://ieltsaiprep.com
curl -I https://ieltsaiprep.com/health
```

### Mobile App Configuration Update
After DNS propagation, your mobile app will use:
- Base URL: `https://ieltsaiprep.com`
- Privacy Policy: `https://ieltsaiprep.com/privacy-policy`
- Terms of Service: `https://ieltsaiprep.com/terms-of-service`

This gives you the professional domain needed for App Store submission.