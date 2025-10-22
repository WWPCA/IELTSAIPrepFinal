# Namecheap DNS Cleanup Before Route 53 Setup

## Step 1: Delete Old DNS Records

Delete ALL the existing DNS records shown in your Namecheap dashboard:

**CNAME Records to Delete:**
- bmrktladwvrcqfof
- cbcyordqt58
- etbpe4lycxm6
- ksm6twa2wo2km
- oamrfrymmpjwbm
- ra5ucys6qvf5fqbz
- v4swpc4acyqm6y
- wxfwrqrfpaprvzty

**TXT Records to Delete:**
- _dmarc
- default._domainkey

## Step 2: Verification

After deleting all records, your DNS management should show:
- No CNAME records
- No TXT records
- Clean slate ready for Route 53

## Step 3: Change to Custom DNS

1. **Nameservers section**: Change from "Namecheap BasicDNS" to **"Custom DNS"**
2. Leave nameserver fields empty for now
3. Save changes

## Why This Cleanup is Important

- Old CNAME records can conflict with new DNS setup
- Certificate validation records are no longer needed
- Clean DNS state prevents propagation issues
- Ensures Route 53 has full control

## Next Steps After Cleanup

1. Apply IAM policy to WWP user
2. Create Route 53 hosted zone
3. Add Route 53 nameservers to Namecheap
4. Configure SSL certificate and API Gateway

The cleanup ensures a smooth transition to professional AWS DNS management.