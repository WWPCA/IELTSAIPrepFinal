# IELTS AI Prep - AI Agents Deployment Guide

Complete deployment guide for Customer Support and DevOps AI agents.

---

## Prerequisites

### AWS Account Setup
- ✅ AWS CLI configured with deployment credentials
- ✅ IAM permissions for:
  - Lambda, DynamoDB, S3, SNS, SES
  - Bedrock (Nova Micro, Nova Pro)
  - CodeCommit (read access to ielts-* repos)
- ✅ AWS SAM CLI installed

### Required Services
- Amazon Bedrock (enabled in us-east-1)
- Amazon SES (verified domain or email)
- CodeCommit repositories: `ielts-ai-prep`, `ielts-deployment`

---

## Step 1: Create Bedrock Knowledge Bases

### 1.1 Create S3 Bucket for Knowledge Base
```bash
aws s3 mb s3://ielts-knowledge-base-$(aws sts get-caller-identity --query Account --output text) \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ielts-knowledge-base-$(aws sts get-caller-identity --query Account --output text) \
  --versioning-configuration Status=Enabled
```

### 1.2 Upload Knowledge Base Files
```bash
cd ai-agents/knowledge-base

aws s3 sync . s3://ielts-knowledge-base-$(aws sts get-caller-identity --query Account --output text)/ \
  --region us-east-1 \
  --exclude ".DS_Store" \
  --exclude "*.pyc"
```

### 1.3 Create Knowledge Base #1 (Customer Support)

**Via AWS Console:**
1. Go to Amazon Bedrock → Knowledge Bases
2. Click "Create knowledge base"
3. Name: `ielts-customer-support-kb`
4. IAM role: Create new service role
5. Data source: S3
   - Bucket: `s3://ielts-knowledge-base-{account-id}/customer-support/`
   - Chunking: Fixed-size, 500 tokens, 50 overlap
6. Embeddings model: Titan Embeddings G1
7. Vector store: Create new (or use existing OpenSearch Serverless)
8. Create knowledge base

**Note the Knowledge Base ID** (format: `XXXXX`)

### 1.4 Create Knowledge Base #2 (DevOps)

Repeat above steps:
- Name: `ielts-devops-architecture-kb`
- Data source #1: `s3://ielts-knowledge-base-{account-id}/internal-devops/`
- Data source #2: CodeCommit repository `ielts-ai-prep` (main branch)
- Data source #3: CodeCommit repository `ielts-deployment` (main branch)
- Chunking: Fixed-size, 1000 tokens, 100 overlap

**Note the Knowledge Base ID**

---

## Step 2: Configure SES Email Receiving

### 2.1 Verify Email Domain (or Email Address)

**Option A: Verify Domain (Recommended)**
```bash
aws ses verify-domain-identity \
  --domain ieltsaiprep.com \
  --region us-east-1
```

Add the verification TXT record to your DNS.

**Option B: Verify Email Address (Testing)**
```bash
aws ses verify-email-identity \
  --email-address info@ieltsaiprep.com \
  --region us-east-1
```

Check email and click verification link.

### 2.2 Set Up MX Records

Add MX record to DNS:
```
Priority: 10
Value: inbound-smtp.us-east-1.amazonaws.com
```

### 2.3 Test Email Receiving
```bash
# Send test email
aws ses send-email \
  --from your-verified-email@example.com \
  --destination ToAddresses=info@ieltsaiprep.com \
  --message Subject={Data="Test"},Body={Text={Data="Test message"}} \
  --region us-east-1
```

---

## Step 3: Deploy Infrastructure with CloudFormation

### 3.1 Package Lambda Functions
```bash
cd ai-agents

# Install dependencies (if not using Lambda layers)
pip install boto3 -t ./package
cp lambda_customer_support.py ./package/
cp lambda_devops_agent.py ./package/

cd package
zip -r ../customer-support.zip .
cd ..

# Same for devops agent
```

### 3.2 Deploy with SAM
```bash
sam deploy \
  --template-file cloudformation-agents.yaml \
  --stack-name ielts-ai-agents \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    EscalationEmail=your-email@example.com \
    SupportEmail=info@ieltsaiprep.com \
    BedrockKBIdCustomerSupport=XXXXX \
    BedrockKBIdDevOps=YYYYY \
  --region us-east-1
```

### 3.3 Verify Deployment
```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name ielts-ai-agents \
  --query 'Stacks[0].StackStatus' \
  --region us-east-1

# Should return: CREATE_COMPLETE
```

---

## Step 4: Activate SES Receipt Rule

### 4.1 Set Active Receipt Rule Set
```bash
aws ses set-active-receipt-rule-set \
  --rule-set-name ielts-support-email-rules \
  --region us-east-1
```

### 4.2 Verify Rule
```bash
aws ses describe-receipt-rule \
  --rule-set-name ielts-support-email-rules \
  --rule-name forward-to-lambda \
  --region us-east-1
```

---

## Step 5: Test End-to-End Flow

### 5.1 Test Customer Support Agent

Send test email:
```bash
aws ses send-email \
  --from your-verified-email@example.com \
  --destination ToAddresses=info@ieltsaiprep.com \
  --message \
    Subject={Data="Test: Maya disconnecting in Part 2"},\
    Body={Text={Data="I keep getting disconnected during Part 2 of the speaking test. Maya stops responding."}} \
  --region us-east-1
```

**Expected Flow:**
1. Email received by SES
2. Triggers Customer Support Lambda
3. Classifies as "audio" category, "technical" issue
4. Queries Knowledge Base for FAQs
5. Sends acknowledgment email to sender
6. Triggers DevOps Agent via SNS (technical escalation)
7. DevOps Agent analyzes gemini_live_audio_service_smart.py
8. Creates DevOps action in DynamoDB
9. Sends notification to your escalation email

### 5.2 Check DynamoDB Tables

```bash
# Check support tickets
aws dynamodb scan \
  --table-name ielts-support-tickets \
  --limit 5 \
  --region us-east-1

# Check DevOps actions
aws dynamodb scan \
  --table-name ielts-devops-actions \
  --limit 5 \
  --region us-east-1
```

### 5.3 View Dashboard

Navigate to: `https://your-domain.com/dashboard/support/tickets`

You should see:
- Recent support ticket
- Status: "escalated"
- Category: "audio"
- Priority: Based on keywords
- AI response generated
- Link to DevOps action

---

## Step 6: Monitor and Optimize

### 6.1 CloudWatch Metrics

Key metrics to monitor:
```bash
# Customer Support Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=ielts-customer-support-agent \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --region us-east-1
```

**Metrics to track:**
- Lambda invocations
- Lambda duration
- Lambda errors
- DynamoDB read/write capacity
- Bedrock model invocations
- SNS messages published

### 6.2 Set Up Alarms

```bash
# Alert on Lambda errors
aws cloudwatch put-metric-alarm \
  --alarm-name ielts-customer-support-errors \
  --alarm-description "Alert on Customer Support Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=ielts-customer-support-agent \
  --evaluation-periods 1 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:ielts-alerts \
  --region us-east-1
```

### 6.3 Cost Monitoring

**Expected Monthly Costs (1,000 support emails):**
- Customer Support Lambda: $0.20
- DevOps Agent Lambda: $0.50
- DynamoDB (on-demand): $1.00
- Bedrock Nova Micro: $0.75
- Bedrock Nova Pro: $0.50
- Knowledge Base queries: $0.002
- S3 storage: $0.03
- SNS: $0.01

**Total: ~$3.00/month** ✅

---

## Step 7: Integrate Dashboard with Main App

### 7.1 Add Blueprint to Main App

Edit `deployment/app.py`:

```python
# Add at the end of imports section
try:
    from dashboard_routes import dashboard_bp
    app.register_blueprint(dashboard_bp)
    print("[INFO] AI Agents Dashboard registered at /dashboard/*")
except ImportError:
    print("[WARNING] Dashboard routes not available")
```

### 7.2 Create Dashboard Templates

Create `templates/dashboard/` directory with templates:
- `support_tickets.html`
- `ticket_detail.html`
- `devops_actions.html`
- `action_detail.html`

### 7.3 Add Navigation Link

Add to your main navigation:
```html
<a href="{{ url_for('dashboard.support_tickets') }}">Support Dashboard</a>
```

---

## Troubleshooting

### Issue: Lambda not receiving SES events

**Check:**
1. SES receipt rule is active: `aws ses describe-active-receipt-rule-set`
2. Lambda has SES invoke permission
3. Email domain is verified
4. MX record is correct

**Fix:**
```bash
aws lambda add-permission \
  --function-name ielts-customer-support-agent \
  --statement-id AllowSES \
  --action lambda:InvokeFunction \
  --principal ses.amazonaws.com \
  --source-account $(aws sts get-caller-identity --query Account --output text) \
  --region us-east-1
```

### Issue: Bedrock Knowledge Base not returning results

**Check:**
1. KB has completed indexing: Check KB console
2. S3 data source is accessible
3. IAM role has s3:GetObject permission

**Fix - Trigger manual sync:**
```bash
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id XXXXX \
  --data-source-id YYYYY \
  --region us-east-1
```

### Issue: DevOps Agent cannot read CodeCommit

**Check:**
1. Lambda execution role has codecommit:GetFile permission
2. Repository names match environment variable
3. Branch "main" exists

**Test CodeCommit access:**
```bash
aws codecommit get-file \
  --repository-name ielts-ai-prep \
  --file-path gemini_live_audio_service_smart.py \
  --commit-specifier main \
  --region us-east-1
```

### Issue: High Bedrock costs

**Optimize:**
1. Reduce Knowledge Base chunk overlap (50 → 25 tokens)
2. Limit KB results (5 → 3 max)
3. Add caching for common queries
4. Use Nova Micro instead of Pro where possible

---

## Security Checklist

- [ ] S3 bucket has public access blocked
- [ ] IAM roles follow least privilege
- [ ] DynamoDB tables have encryption enabled
- [ ] Lambda functions have timeout limits
- [ ] SES has DKIM configured
- [ ] CloudWatch Logs retention set (30 days recommended)
- [ ] Escalation email secured with MFA
- [ ] Dashboard requires authentication
- [ ] Environment variables use AWS Secrets Manager

---

## Known Limitations & Next Steps

### ⚠️ Important: SES Email Body Parsing

**Current Status:**
The Customer Support Lambda has a placeholder for email body extraction. For production use, you need to:

1. **Configure SES to Store Emails in S3:**
```bash
aws ses set-receipt-rule \
  --rule-set-name ielts-support-email-rules \
  --rule '{
    "Name": "store-in-s3",
    "Enabled": true,
    "Actions": [{
      "S3Action": {
        "BucketName": "ielts-email-storage",
        "ObjectKeyPrefix": "incoming/"
      }
    }, {
      "LambdaAction": {
        "FunctionArn": "arn:aws:lambda:...:ielts-customer-support-agent"
      }
    }]
  }'
```

2. **Implement MIME Email Parsing:**
Add to `lambda_customer_support.py`:
```python
import email
from email import policy

def parse_email_from_s3(bucket, key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)
    msg = email.message_from_bytes(
        response['Body'].read(),
        policy=policy.default
    )
    return {
        'subject': msg['subject'],
        'from': msg['from'],
        'body': msg.get_body(preferencelist=('plain', 'html')).get_content()
    }
```

**Testing Workaround:**
For now, test by directly invoking Lambda with test events:
```json
{
  "from": "customer@example.com",
  "subject": "Maya keeps disconnecting",
  "body": "I keep getting disconnected during Part 2 of the speaking test.",
  "timestamp": "2025-10-18T10:00:00Z"
}
```

### Future Enhancements

1. **Add More FAQs:** Expand knowledge-base/customer-support/faqs/
2. **Tune Confidence Thresholds:** Adjust escalation logic
3. **Create PR Automation:** Auto-create PRs for approved DevOps fixes
4. **Add Slack Integration:** Notify team of urgent tickets
5. **Build Analytics Dashboard:** Track resolution times, AI accuracy
6. **Implement Feedback Loop:** Let users rate AI responses
7. **Complete SES Email Parsing:** Production-ready MIME email handling

---

## Support

For issues or questions:
- Check CloudWatch Logs: `/aws/lambda/ielts-customer-support-agent`
- Review DynamoDB tables for data
- Email: devops@ieltsaiprep.com
