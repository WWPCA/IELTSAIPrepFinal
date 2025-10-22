# Update Existing CloudFormation Stack with Resource Import

## Step-by-Step Console Process

### Step 1: Prepare Resource Import
In the CloudFormation console for stack `aws-sam-cli-managed-default`:

1. Click **"Update stack"**
2. Select **"Replace current template"** 
3. Choose **"Upload a template file"**
4. Upload: `import-template.yaml`
5. Click **"Next"**

### Step 2: Configure Import Parameters
**Parameters:**
- DomainName: `ieltsaiprep.com`
- Environment: `production`

Click **"Next"**

### Step 3: Import Existing Resources
On the "Configure stack options" page:
1. Scroll down to **"Import resources into stack"**
2. Check the box: **"Import resources into stack"**
3. Click **"Next"**

### Step 4: Specify Resource Identifiers
You'll see a table to map CloudFormation resources to existing AWS resources:

**Resource Mappings:**
- **IELTSGenAIPrepFunction**: 
  - Identifier Type: `Function Name`
  - Identifier Value: `ielts-genai-prep-api`

- **IELTSGenAIPrepAPI**:
  - Identifier Type: `REST API ID`  
  - Identifier Value: `n0cpf1rmvc`

Click **"Next"**

### Step 5: Review and Import
1. Review the changes summary
2. Check **"I acknowledge that AWS CloudFormation might create IAM resources"**
3. Click **"Submit"**

### Step 6: Monitor Progress
The import process will:
1. Import existing Lambda function and API Gateway (2-3 minutes)
2. Create Route 53 hosted zone (1-2 minutes)
3. Request SSL certificate with DNS validation (5-10 minutes)
4. Create custom domain and DNS records (3-5 minutes)

**Total time: 10-20 minutes**

## Expected Results

After successful import and update:

### New Infrastructure Added:
- Route 53 hosted zone for ieltsaiprep.com
- SSL certificate with automatic DNS validation
- Custom domain configuration for API Gateway
- DNS records pointing to your API
- Health checks for monitoring

### Outputs Available:
- **CustomDomainUrl**: https://ieltsaiprep.com
- **HostedZoneNameServers**: Nameservers for Namecheap update
- **SSLCertificateArn**: Certificate for mobile app references

## Final Step: Update Nameservers
Once the stack update completes, you'll get the Route 53 nameservers from the Outputs tab. Update these at Namecheap to complete the professional domain setup.

Your mobile app will then use the professional ieltsaiprep.com domain for all API calls and legal page references.