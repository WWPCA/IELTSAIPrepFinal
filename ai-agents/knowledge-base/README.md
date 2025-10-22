# IELTS AI Prep - Knowledge Base Structure

This directory contains knowledge base files for both Customer Support and DevOps AI agents.

## Directory Structure

```
knowledge-base/
├── customer-support/          # FAQ knowledge base for Customer Support Agent
│   ├── faqs/
│   │   ├── purchase.json     # Purchase and payment FAQs
│   │   ├── qr-code.json      # QR code authentication FAQs
│   │   ├── audio-issues.json # Maya/audio troubleshooting
│   │   └── refund.json       # Refund policy and process
│   ├── troubleshooting/
│   └── policies/
│
└── internal-devops/           # Architecture docs for DevOps Agent
    ├── architecture/
    │   ├── gemini-regional-routing.md  # Gemini 21-region setup
    │   ├── dynamodb-schemas.md         # DynamoDB table structures
    │   ├── aws-lambda-websocket.md     # WebSocket architecture
    │   └── deployment-guide.md         # Deployment procedures
    ├── runbooks/
    └── codebase-index/        # Auto-generated from CodeCommit

## S3 Upload Instructions

### Prerequisites
1. Create S3 bucket: `ielts-knowledge-base`
2. Enable versioning on the bucket
3. Configure bucket policy for Bedrock access

### Upload Command
```bash
aws s3 sync ./knowledge-base s3://ielts-knowledge-base/ \
  --region us-east-1 \
  --delete \
  --exclude ".DS_Store"
```

### Bedrock Knowledge Base Configuration

#### Knowledge Base #1: Customer Support
- **Name:** ielts-customer-support-kb
- **Model:** Titan Embeddings G1
- **Data Source:** s3://ielts-knowledge-base/customer-support/
- **Chunking:** Fixed-size 500 tokens, 50 token overlap
- **Metadata:** category, confidence, keywords

#### Knowledge Base #2: Internal DevOps
- **Name:** ielts-devops-architecture-kb
- **Model:** Titan Embeddings G1
- **Data Sources:**
  - s3://ielts-knowledge-base/internal-devops/
  - CodeCommit: ielts-ai-prep (main branch)
  - CodeCommit: ielts-deployment (main branch)
- **Chunking:** Fixed-size 1000 tokens, 100 token overlap
- **Metadata:** service, file_path, repo

## File Formats

### FAQ JSON Structure
```json
{
  "category": "purchase",
  "questions": [
    {
      "id": "unique-id",
      "question": "How do I...?",
      "answer": "Detailed answer...",
      "keywords": ["keyword1", "keyword2"],
      "confidence": 0.95,
      "escalate": false
    }
  ],
  "template_responses": {
    "general": "Template text..."
  }
}
```

### Architecture Markdown Structure
- Use clear headings (##)
- Include code examples with language tags
- Add CloudWatch metric names
- Include file paths and line numbers
- Document common issues and fixes

## Maintenance

### Adding New FAQs
1. Edit appropriate JSON file in `customer-support/faqs/`
2. Follow existing format
3. Set appropriate confidence score
4. Upload to S3: `aws s3 cp file.json s3://ielts-knowledge-base/customer-support/faqs/`
5. Trigger KB re-sync

### Adding Architecture Docs
1. Create markdown file in `internal-devops/architecture/`
2. Include code snippets and examples
3. Upload to S3
4. Trigger KB re-sync

### CodeCommit Auto-Indexing
The DevOps KB automatically indexes these repos:
- `ielts-ai-prep` (main branch)
- `ielts-deployment` (main branch)

Trigger re-index after significant code changes:
```bash
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id <KB_ID> \
  --data-source-id <DATASOURCE_ID>
```

## Costs

### Knowledge Base Storage (S3)
- Customer Support: ~1 MB → $0.023/month
- DevOps Architecture: ~5 MB → $0.115/month
- CodeCommit index: ~50 MB → $1.15/month
- **Total:** ~$1.30/month

### Knowledge Base Queries
- $0.002 per 1,000 queries
- Expected: 1,000 queries/month → $0.002/month

### Titan Embeddings
- $0.0001 per 1,000 tokens
- Initial indexing: ~$0.05 one-time
- Updates: Minimal

**Total AI Agent KB Cost: ~$1.35/month** 🎉

## Security

- S3 bucket encryption: AES-256
- Bedrock KB uses IAM roles
- No public access to S3 bucket
- CodeCommit access: Read-only via IAM

## Monitoring

### CloudWatch Metrics
- `bedrock_kb_queries` - Query count
- `bedrock_kb_latency` - Response time
- `bedrock_kb_errors` - Failed queries

### Logs
- KB query logs: `/aws/bedrock/knowledge-bases/`
- S3 access logs: Enabled on bucket
