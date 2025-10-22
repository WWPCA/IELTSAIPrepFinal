# AWS Lambda WebSocket Deployment Guide for IELTS Speaking

## Prerequisites

1. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```

2. **AWS SAM CLI** installed
   ```bash
   brew install aws-sam-cli  # macOS
   # or
   pip install aws-sam-cli   # Python
   ```

3. **GCP Service Account** with Vertex AI permissions
   - Download JSON key file from Google Cloud Console
   - Name it `gcp-service-account.json`

---

## Step-by-Step Deployment

### **1. Store GCP Credentials in AWS Secrets Manager**

```bash
# Create secret
aws secretsmanager create-secret \
    --name gemini-vertex-ai-credentials \
    --description "GCP service account for Vertex AI Gemini" \
    --secret-string file://gcp-service-account.json \
    --region us-east-1
```

**Verify it was created:**
```bash
aws secretsmanager describe-secret \
    --secret-id gemini-vertex-ai-credentials \
    --region us-east-1
```

### **2. Deploy WebSocket Infrastructure**

```bash
cd deployment/

# Make deploy script executable
chmod +x deploy.sh

# Deploy to production
./deploy.sh production us-east-1 gcp-service-account.json
```

**What this does:**
- ✅ Stores GCP credentials in Secrets Manager
- ✅ Installs Python dependencies
- ✅ Builds Lambda function
- ✅ Creates API Gateway WebSocket API
- ✅ Deploys CloudFormation stack
- ✅ Returns WebSocket URL

### **3. Get Your WebSocket URL**

```bash
aws cloudformation describe-stacks \
    --stack-name ielts-speaking-production \
    --query 'Stacks[0].Outputs[?OutputKey==`WebSocketURL`].OutputValue' \
    --output text
```

Output example:
```
wss://abc123.execute-api.us-east-1.amazonaws.com/production
```

---

## WebSocket API Routes

Your WebSocket API supports these actions:

| Route | Description | Request Body |
|-------|-------------|--------------|
| `$connect` | Initial connection | N/A |
| `$disconnect` | Clean up session | N/A |
| `start_speaking` | Initialize Gemini session | `{action: "start_speaking", user_id, country_code}` |
| `audio_chunk` | Send audio data | `{action: "audio_chunk", audio: base64}` |
| `end_speaking` | Get final assessment | `{action: "end_speaking"}` |

---

## Frontend Integration Example

```javascript
// Connect to WebSocket
const ws = new WebSocket('wss://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/production');

ws.onopen = () => {
  console.log('Connected to speaking assessment');
  
  // Start speaking session
  ws.send(JSON.stringify({
    action: 'start_speaking',
    user_id: 'user123',
    country_code: 'US',
    assessment_type: 'speaking'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'session_ready':
      console.log('Maya is ready! Start speaking...');
      console.log('Connected to region:', data.region);
      break;
    
    case 'maya_transcript':
      console.log('Maya said:', data.text);
      break;
    
    case 'maya_audio':
      // Decode base64 audio and play
      const audioBytes = atob(data.audio);
      playAudio(audioBytes);
      break;
    
    case 'assessment_complete':
      console.log('Assessment:', data.assessment);
      console.log('Improvement plan:', data.assessment.improvement_plan);
      break;
    
    case 'error':
      console.error('Error:', data.message);
      break;
  }
};

// Send audio chunks
function sendAudioChunk(audioBlob) {
  const reader = new FileReader();
  reader.onload = () => {
    const base64Audio = btoa(
      new Uint8Array(reader.result)
        .reduce((data, byte) => data + String.fromCharCode(byte), '')
    );
    
    ws.send(JSON.stringify({
      action: 'audio_chunk',
      audio: base64Audio,
      mime_type: 'audio/wav'
    }));
  };
  reader.readAsArrayBuffer(audioBlob);
}

// End assessment
function endAssessment() {
  ws.send(JSON.stringify({
    action: 'end_speaking'
  }));
}
```

---

## Environment Variables

Lambda function uses these environment variables (set automatically):

```bash
ENVIRONMENT=production
GCP_CREDENTIALS_SECRET=gemini-vertex-ai-credentials
SESSIONS_TABLE=ielts-genai-prep-sessions
APIGW_ENDPOINT=https://YOUR_API.execute-api.REGION.amazonaws.com/production
LOG_LEVEL=INFO
```

---

## Monitoring & Debugging

### **View Lambda Logs:**
```bash
aws logs tail /aws/lambda/production-ielts-speaking-websocket --follow
```

### **Check WebSocket Connections:**
```bash
aws dynamodb scan \
    --table-name ielts-genai-prep-sessions \
    --filter-expression "session_status = :status" \
    --expression-attribute-values '{":status":{"S":"active"}}'
```

### **Test WebSocket Connection:**
```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c wss://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/production

# Send test message
{"action": "start_speaking", "user_id": "test", "country_code": "US"}
```

---

## IAM Permissions Required

Lambda execution role needs:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:gemini-vertex-ai-credentials-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/ielts-genai-prep-sessions"
    },
    {
      "Effect": "Allow",
      "Action": [
        "execute-api:ManageConnections"
      ],
      "Resource": "arn:aws:execute-api:*:*:*/*/POST/@connections/*"
    }
  ]
}
```

---

## Cost Estimation

**Per speaking assessment (14 minutes):**

| Service | Cost |
|---------|------|
| Lambda (2GB, 14min) | $0.0050 |
| API Gateway WebSocket | $0.0003 |
| Secrets Manager | $0.00001 |
| DynamoDB | $0.00001 |
| Gemini Flash (Vertex AI) | $0.025 |
| **Total** | **~$0.030** |

**For 1,000 assessments/month:** ~$30

---

## Troubleshooting

### **Error: "No active session"**
**Cause:** `audio_chunk` called before `start_speaking`  
**Fix:** Ensure `start_speaking` completes before sending audio

### **Error: "GoneException" on WebSocket send**
**Cause:** WebSocket connection closed  
**Fix:** Reconnect and reinitialize session

### **Error: "Failed to initialize Vertex AI"**
**Cause:** GCP credentials missing or invalid  
**Fix:** Check Secrets Manager secret content

### **Lambda timeout after 15 minutes**
**Cause:** Speaking test exceeded maximum duration  
**Fix:** This is a hard limit. Assessments must complete within 15 minutes

---

## Regional Routing

The system automatically routes to the nearest Vertex AI region:

| User Location | Optimal Region | Latency Reduction |
|---------------|----------------|-------------------|
| US/Canada | us-central1 | Baseline |
| Europe | europe-west1 | 30-40% |
| Asia | asia-southeast1 | 50-70% |
| Middle East | me-central1 | 30-40% |
| Australia | australia-southeast1 | 40-50% |

Users can override by passing `preferred_region` in `start_speaking` request.

---

## Next Steps

1. ✅ Deploy WebSocket API
2. ✅ Test with frontend
3. ✅ Monitor CloudWatch logs
4. Configure custom domain (optional)
5. Set up CloudWatch alarms
6. Enable X-Ray tracing

---

## Support

For issues:
1. Check CloudWatch logs
2. Review DynamoDB session data
3. Test with `wscat` CLI tool
4. Check Secrets Manager secret exists

**Common issues are documented in the Troubleshooting section above.**
