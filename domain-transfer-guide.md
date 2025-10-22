# Domain Transfer Guide: ieltsaiprep.com from Namecheap to AWS Route 53

## Prerequisites
- Domain transfer authorization from Namecheap (✅ Already requested)
- AWS Account with Route 53 access
- Domain must be unlocked and transfer-ready at Namecheap

## Step-by-Step Transfer Process

### Step 1: Prepare Domain at Namecheap
1. **Unlock Domain**: Ensure domain is unlocked in Namecheap dashboard
2. **Get Auth Code**: Obtain the EPP/Authorization code from Namecheap
3. **Update Contact Info**: Ensure all contact information is accurate
4. **Disable Privacy Protection**: Temporarily disable WHOIS privacy protection

### Step 2: Initiate Transfer in AWS Route 53
1. **Create Hosted Zone**: Set up hosted zone for ieltsaiprep.com in Route 53
2. **Request Transfer**: Use AWS Route 53 domain transfer service
3. **Provide Auth Code**: Enter the EPP code from Namecheap
4. **Pay Transfer Fee**: AWS charges ~$12-14 for .com domain transfer

### Step 3: DNS Configuration (Critical)
1. **Backup Current DNS**: Document all existing DNS records from Namecheap
2. **Create DNS Records**: Replicate all records in Route 53 hosted zone
3. **Test DNS**: Verify all records work correctly before transfer completion

### Step 4: Transfer Completion
1. **Monitor Transfer**: Transfer typically takes 5-7 days
2. **Approve Transfer**: Respond to approval emails from both registrars
3. **Update Name Servers**: Route 53 will automatically update name servers
4. **Verify Functionality**: Test website and email functionality

## Important Notes
- **No Downtime**: DNS records must be configured in Route 53 before transfer
- **Email Services**: Ensure MX records are properly configured
- **SSL Certificates**: Verify SSL certificates continue to work
- **Transfer Lock**: Domain will be locked for 60 days after transfer

## DNS Records to Migrate
Based on current ieltsaiprep.com configuration:
- A record: www.ieltsaiprep.com → CloudFront distribution
- CNAME records: Any subdomains
- MX records: Email services (if any)
- TXT records: Domain verification, SPF, DKIM

## Cost Implications
- AWS Route 53 hosted zone: $0.50/month
- Domain transfer fee: ~$12-14 (includes 1 year renewal)
- DNS queries: $0.40 per million queries

## Rollback Plan
If issues arise:
1. Keep Namecheap DNS active during transfer
2. Can cancel transfer within first 5 days
3. Revert name servers if needed