# AWS Lambda Deployment Instructions - IELTS AI Prep

## 📦 Deployment Package Ready

This deployment package contains:
- ✅ All updated email templates with Roboto font
- ✅ Latest application code with all functionality
- ✅ All Python dependencies pre-installed
- ✅ AWS service integrations (Bedrock, DynamoDB, SES)
- ✅ Gemini API integration for speaking assessments

---

## 🚀 Deployment Steps

### Option 1: Direct AWS Lambda Upload (Recommended for Quick Deploy)

1. **Create ZIP Package**
```bash
cd deployment
zip -r ../ielts-lambda-deployment.zip . -x "*.git*" -x "*__pycache__*" -x "*.pyc"
```

2. **Upload to AWS Lambda Console**
   - Go to AWS Lambda Console: https://console.aws.amazon.com/lambda
   - Select your function: `ielts-genai-prep-lambda`
   - Click "Upload from" → ".zip file"
   - Upload `ielts-lambda-deployment.zip`
   - Click "Save"

3. **Environment Variables (Already Set)**
   - `AWS_REGION` - AWS region for services
   - `SESSION_SECRET` - Flask session secret
   - `DATABASE_URL` - DynamoDB configuration
   - `SES_SENDER_EMAIL` - Email sender address
   - `GOOGLE_APPLICATION_CREDENTIALS` - Gemini API credentials

---

### Option 2: AWS CLI Upload

```bash
# Create deployment package
cd deployment
zip -r ../ielts-lambda-deployment.zip . -x "*.git*" -x "*__pycache__*" -x "*.pyc"
cd ..

# Upload to Lambda
aws lambda update-function-code \
  --function-name ielts-genai-prep-lambda \
  --zip-file fileb://ielts-lambda-deployment.zip \
  --region us-east-1
```

---

### Option 3: S3 Upload (For Large Packages >50MB)

```bash
# Upload to S3 first
aws s3 cp ielts-lambda-deployment.zip s3://ielts-deployment-bucket/

# Update Lambda from S3
aws lambda update-function-code \
  --function-name ielts-genai-prep-lambda \
  --s3-bucket ielts-deployment-bucket \
  --s3-key ielts-lambda-deployment.zip \
  --region us-east-1
```

---

## 🔧 Post-Deployment Verification

### 1. Check Lambda Deployment Status
```bash
aws lambda get-function \
  --function-name ielts-genai-prep-lambda \
  --region us-east-1
```

### 2. Test Lambda Function
```bash
# Test basic health check
aws lambda invoke \
  --function-name ielts-genai-prep-lambda \
  --payload '{"httpMethod":"GET","path":"/health"}' \
  response.json
  
cat response.json
```

### 3. Verify CloudFront Distribution
- Access: https://www.ieltsaiprep.com
- Check homepage loads correctly
- Verify Roboto font renders in browser

### 4. Test Email Templates
- Trigger password reset email
- Check Roboto font in email client
- Verify brand colors (#2c3e50, #3498db)

---

## 📋 What's New in This Deployment

### Email Templates (16 Updated)
✅ All emails now use Roboto font  
✅ Brand gradient headers (#2c3e50 → #3498db)  
✅ Professional styling with brand colors  
✅ New customer support response template  

### Templates Added
✅ listening_test.html  
✅ reading_test.html  
✅ speaking_assessment_with_fallback.html  

### Services Updated
✅ ses_email_service.py - Roboto font emails  
✅ gemini_live_audio_service_smart.py - Regional routing  
✅ ielts_workflow_manager.py - Workflow orchestration  

---

## ⚙️ Lambda Configuration

### Recommended Settings
- **Runtime**: Python 3.11
- **Memory**: 512 MB (minimum), 1024 MB (recommended)
- **Timeout**: 30 seconds (API), 300 seconds (WebSocket)
- **Handler**: `lambda_handler.handler`

### Environment Variables Required
```
AWS_REGION=us-east-1
SESSION_SECRET=<your-secret>
DATABASE_URL=<dynamodb-config>
SES_SENDER_EMAIL=donotreply@ieltsaiprep.com
DOMAIN_URL=https://www.ieltsaiprep.com
```

---

## 🔐 Security Checklist

✅ All secrets stored in AWS Secrets Manager  
✅ CloudFront distribution uses HTTPS  
✅ Lambda execution role has minimum permissions  
✅ DynamoDB tables encrypted at rest  
✅ SES email sending verified  

---

## 🧪 Testing Endpoints

### Health Check
```
GET https://www.ieltsaiprep.com/health
Expected: 200 OK
```

### Homepage
```
GET https://www.ieltsaiprep.com/
Expected: Homepage with Roboto font
```

### Email Test (Password Reset)
```
POST https://www.ieltsaiprep.com/api/request-password-reset
Body: {"email": "test@example.com"}
Expected: Email with Roboto font
```

---

## 📊 Monitoring

### CloudWatch Logs
```bash
# View recent logs
aws logs tail /aws/lambda/ielts-genai-prep-lambda --follow
```

### Metrics to Monitor
- Lambda invocations
- Lambda errors
- DynamoDB read/write capacity
- SES email delivery rate
- API Gateway 4xx/5xx errors

---

## 🆘 Troubleshooting

### Issue: Lambda package too large
**Solution**: Use Lambda layers for large dependencies
```bash
# Create layer for dependencies
cd deployment
zip -r layer.zip python/
aws lambda publish-layer-version --layer-name ielts-dependencies --zip-file fileb://layer.zip
```

### Issue: Email templates not rendering correctly
**Solution**: Verify Google Fonts import in email HTML
- Check: `@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');`

### Issue: Gemini API errors
**Solution**: Check regional endpoint configuration
- Verify `gemini_live_audio_service_smart.py` is deployed
- Check GOOGLE_APPLICATION_CREDENTIALS

---

## 📅 Deployment Checklist

- [ ] Create ZIP package from deployment folder
- [ ] Upload to AWS Lambda via console or CLI
- [ ] Verify Lambda deployment status
- [ ] Test homepage at www.ieltsaiprep.com
- [ ] Test email sending (password reset)
- [ ] Verify Roboto font in emails
- [ ] Check CloudWatch logs for errors
- [ ] Test speaking assessment flow
- [ ] Test writing assessment flow
- [ ] Verify QR code authentication
- [ ] Monitor CloudWatch metrics

---

## 🎯 Rollback Plan

If issues occur:
1. Go to Lambda Console → Versions
2. Find previous working version
3. Update alias to point to previous version
4. Verify application works
5. Investigate issues in new version

---

**Deployment Package Size**: ~25-50 MB (with dependencies)  
**Lambda Handler**: `lambda_handler.handler`  
**Runtime**: Python 3.11  
**Last Updated**: October 18, 2025  
**Status**: ✅ Ready for Production Deployment
