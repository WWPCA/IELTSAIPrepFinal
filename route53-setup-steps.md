# Route 53 DNS Setup for ieltsaiprep.com (Keep Namecheap as Registrar)

## Recommended Approach: DNS Management Only

Since you own ieltsaiprep.com at Namecheap, we'll use Route 53 for DNS management while keeping Namecheap as the registrar. This avoids the $14 USD transfer fee and complexity.

## Step 1: Create Route 53 Hosted Zone

1. Go to **AWS Route 53 Console**
2. Click **"Create hosted zone"**
3. **Domain name**: `ieltsaiprep.com`
4. **Type**: Public hosted zone
5. Click **"Create hosted zone"**
6. **IMPORTANT**: Copy the 4 nameservers shown in the NS record

## Step 2: Update Nameservers at Namecheap

1. **Close the AWS Route 53 transfer page** (we're not transferring)
2. Go to **Namecheap Domain List**
3. Find **ieltsaiprep.com** → Click **"Manage"**
4. **Nameservers**: Change from "Namecheap BasicDNS" to **"Custom DNS"**
5. Enter the 4 Route 53 nameservers from Step 1:
   - ns-xxxx.awsdns-xx.com
   - ns-xxxx.awsdns-xx.co.uk
   - ns-xxxx.awsdns-xx.net
   - ns-xxxx.awsdns-xx.org
6. Click **"Save Changes"**

## Step 3: Request SSL Certificate in AWS

1. Go to **AWS Certificate Manager**
2. Click **"Request certificate"**
3. **Domain names**:
   - `ieltsaiprep.com`
   - `www.ieltsaiprep.com`
4. **Validation method**: DNS validation
5. Click **"Request"**
6. Click **"Create records in Route 53"** for both domains
7. Wait 5-30 minutes for validation

## Step 4: Create API Gateway Custom Domain

1. Go to **AWS API Gateway Console**
2. Click **"Custom domain names"** → **"Create"**
3. **Domain name**: `ieltsaiprep.com`
4. **Certificate**: Select your validated certificate
5. Click **"Create custom domain name"**
6. **Configure API mappings**:
   - **API**: `ielts-genai-prep-production` (n0cpf1rmvc)
   - **Stage**: `prod`
   - **Path**: (leave empty)
7. **Save**

## Step 5: Create DNS Records

1. Return to **Route 53 hosted zone**
2. Click **"Create record"**
3. **Root domain record**:
   - **Name**: (leave empty)
   - **Type**: A
   - **Alias**: Yes
   - **Route traffic to**: API Gateway
   - **Region**: us-east-1
   - **Endpoint**: Select your custom domain
4. **WWW record**:
   - **Name**: www
   - **Type**: A
   - **Alias**: Yes
   - **Route traffic to**: API Gateway
   - **Region**: us-east-1
   - **Endpoint**: Select your custom domain

## Expected Timeline

- Route 53 hosted zone: 2 minutes
- Nameserver update: 15 minutes
- SSL certificate: 5-30 minutes
- DNS propagation: 24-48 hours

## Benefits of This Approach

- Keep existing Namecheap registration
- No $14 transfer fee
- Professional AWS DNS management
- Same end result for your mobile app

## Test After Setup

```bash
curl -I https://ieltsaiprep.com
curl -I https://ieltsaiprep.com/health
```

Your mobile app will use the professional ieltsaiprep.com domain for App Store submission.