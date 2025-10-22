# IELTS AI Prep - Email Configuration

## SES Verified Email Addresses

Based on your AWS SES configuration, the platform uses two verified email addresses:

### 1. donotreply@ieltsaiprep.com
**Purpose:** Automated system emails  
**Use Cases:**
- Welcome emails to new users
- Password reset requests
- Email confirmation links
- Account verification emails
- System notifications

**Configuration:**
```python
FROM_EMAIL = 'donotreply@ieltsaiprep.com'
```

**Example Usage:**
```python
# Welcome email
ses.send_email(
    Source='donotreply@ieltsaiprep.com',
    Destination={'ToAddresses': [user_email]},
    Message={
        'Subject': {'Data': 'Welcome to IELTS AI Prep'},
        'Body': {'Html': {'Data': welcome_html}}
    }
)
```

---

### 2. info@ieltsaiprep.com
**Purpose:** Customer support and technical assistance  
**Use Cases:**
- AI Support Agent inbox (receives customer inquiries)
- Support ticket responses
- Technical assistance replies
- General customer communication

**Configuration:**
```python
SUPPORT_EMAIL = 'info@ieltsaiprep.com'
```

**AI Agent Integration:**
```python
# Customer Support Lambda environment variable
SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'info@ieltsaiprep.com')

# DevOps Agent uses same for sending technical updates
SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'info@ieltsaiprep.com')
```

---

## SES Configuration Commands

### Verify Email Addresses
```bash
# Already verified - just confirming
aws ses verify-email-identity \
  --email-address donotreply@ieltsaiprep.com \
  --region us-east-1

aws ses verify-email-identity \
  --email-address info@ieltsaiprep.com \
  --region us-east-1
```

### Check Verification Status
```bash
aws ses get-identity-verification-attributes \
  --identities donotreply@ieltsaiprep.com info@ieltsaiprep.com \
  --region us-east-1
```

---

## Email Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   IELTS AI Prep Platform                     │
└─────────────────────────────────────────────────────────────┘
                          │
         ┌────────────────┴────────────────┐
         │                                 │
         ▼                                 ▼
┌──────────────────────┐         ┌──────────────────────┐
│ donotreply@          │         │ info@                │
│ ieltsaiprep.com      │         │ ieltsaiprep.com      │
├──────────────────────┤         ├──────────────────────┤
│ • Welcome emails     │         │ • Support inbox      │
│ • Password resets    │         │ • AI agent replies   │
│ • Confirmations      │         │ • Technical help     │
│ • Verifications      │         │ • Customer comm      │
└──────────────────────┘         └──────────────────────┘
                                           │
                                           ▼
                                 ┌──────────────────────┐
                                 │ AI Support Agent     │
                                 │ (Nova Micro Lambda)  │
                                 ├──────────────────────┤
                                 │ 1. Classify issue    │
                                 │ 2. Retrieve FAQ      │
                                 │ 3. Generate response │
                                 │ 4. Escalate if needed│
                                 └──────────────────────┘
```

---

## SES Receipt Rules for AI Support

### Create Receipt Rule Set
```bash
aws ses create-receipt-rule-set \
  --rule-set-name ielts-support-email-rules \
  --region us-east-1
```

### Add Receipt Rule (Future Enhancement)
When ready to enable full email parsing:

```bash
aws ses create-receipt-rule \
  --rule-set-name ielts-support-email-rules \
  --rule '{
    "Name": "customer-support-to-lambda",
    "Enabled": true,
    "Recipients": ["info@ieltsaiprep.com"],
    "Actions": [
      {
        "S3Action": {
          "BucketName": "ielts-email-storage",
          "ObjectKeyPrefix": "incoming/"
        }
      },
      {
        "LambdaAction": {
          "FunctionArn": "arn:aws:lambda:us-east-1:ACCOUNT_ID:function:ielts-customer-support-agent",
          "InvocationType": "Event"
        }
      }
    ]
  }' \
  --region us-east-1
```

---

## Important Notes

### Current Implementation
- **donotreply@ieltsaiprep.com:** Fully configured for sending automated emails
- **info@ieltsaiprep.com:** Configured as support email, AI agent ready to respond

### Known Limitation
The AI Support Agent currently uses a placeholder for email body extraction. For production use with real incoming emails:

1. Configure SES to store emails in S3
2. Add MIME email parsing to Lambda
3. Extract plain text/HTML body
4. Sanitize content before AI processing

See `DEPLOYMENT_GUIDE.md` for full implementation details.

---

## Cost Optimization

### SES Pricing (us-east-1)
- **Outbound emails:** $0.10 per 1,000 emails
- **Inbound emails:** FREE (up to 1,000 emails/month)
- **S3 storage:** $0.023 per GB

### Monthly Cost Estimate (15,000 users)
- Welcome emails: 500/month × $0.0001 = $0.05
- Password resets: 100/month × $0.0001 = $0.01
- Support responses: 750/month × $0.0001 = $0.08
- **Total SES:** ~$0.14/month

---

## Testing Commands

### Test Automated Email (donotreply)
```bash
aws ses send-email \
  --from donotreply@ieltsaiprep.com \
  --destination ToAddresses=your-test@example.com \
  --message \
    Subject={Data="Welcome to IELTS AI Prep"},\
    Body={Text={Data="Thank you for signing up!"}} \
  --region us-east-1
```

### Test Support Email (info)
```bash
aws ses send-email \
  --from your-verified@example.com \
  --destination ToAddresses=info@ieltsaiprep.com \
  --message \
    Subject={Data="Test Support Request"},\
    Body={Text={Data="My QR code expired, please help."}} \
  --region us-east-1
```

### Test Lambda Directly (Bypass SES)
```bash
aws lambda invoke \
  --function-name ielts-customer-support-agent \
  --payload '{
    "from": "customer@example.com",
    "subject": "QR code help",
    "body": "My QR code expired",
    "timestamp": "2025-10-18T10:00:00Z"
  }' \
  response.json
```

---

## Security Best Practices

### Email Sending
- ✅ Use verified email addresses only
- ✅ Enable DKIM signing for authentication
- ✅ Set up SPF records in DNS
- ✅ Monitor bounce and complaint rates
- ✅ Use SES sending quotas to prevent abuse

### Email Receiving
- ✅ Validate incoming email headers
- ✅ Sanitize email body before AI processing
- ✅ Store emails encrypted in S3
- ✅ Set TTL for email retention (90 days)
- ✅ Monitor for spam/phishing attempts

### Compliance
- ✅ Include unsubscribe links (automated emails)
- ✅ Honor opt-out requests
- ✅ GDPR-compliant data retention
- ✅ CAN-SPAM Act compliance

---

## Troubleshooting

### Email Not Sending
```bash
# Check verification status
aws ses get-identity-verification-attributes \
  --identities donotreply@ieltsaiprep.com \
  --region us-east-1

# Check sending statistics
aws ses get-send-statistics --region us-east-1

# Check account status (sandbox vs production)
aws ses get-account-sending-enabled --region us-east-1
```

### Email Not Receiving
```bash
# Check active receipt rule set
aws ses describe-active-receipt-rule-set --region us-east-1

# Check MX records
dig MX ieltsaiprep.com

# Test email delivery
aws ses send-email \
  --from test@example.com \
  --destination ToAddresses=info@ieltsaiprep.com \
  --message Subject={Data="Test"},Body={Text={Data="Test"}} \
  --region us-east-1
```

---

## Summary

| Email Address | Purpose | Direction | AI Agent |
|---------------|---------|-----------|----------|
| donotreply@ieltsaiprep.com | System emails | Outbound | No |
| info@ieltsaiprep.com | Customer support | Both | Yes (Nova Micro) |

**Key Point:** All AI Support Agent configuration now correctly uses `info@ieltsaiprep.com` instead of the previously incorrect `helpdesk@ieltsaiprep.com`.

---

For deployment instructions, see `DEPLOYMENT_GUIDE.md`  
For AI agent details, see `IMPLEMENTATION_SUMMARY.md`
