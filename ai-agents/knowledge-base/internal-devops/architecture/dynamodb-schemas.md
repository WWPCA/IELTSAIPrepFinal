# DynamoDB Table Schemas

## Overview
IELTS AI Prep uses 11 DynamoDB tables for data persistence across all platform services.

## Core User Tables

### 1. ielts-genai-prep-users
**Purpose:** User accounts and profiles

**Schema:**
```
Partition Key: email (String)
```

**Attributes:**
- `email` - User email (primary key)
- `password_hash` - Bcrypt hash (256 chars min)
- `username` - Display name
- `created_at` - Registration timestamp
- `email_verified` - Boolean
- `verification_token` - Email verification token
- `last_login` - Last login timestamp
- `account_status` - active, suspended, deleted

**GSIs:**
- None (email-based lookups only)

---

### 2. ielts-genai-prep-sessions
**Purpose:** Active user sessions with auto-cleanup

**Schema:**
```
Partition Key: session_id (String)
```

**Attributes:**
- `session_id` - Unique session identifier
- `user_email` - Link to users table
- `created_at` - Session start timestamp
- `expires_at` - TTL for auto-deletion
- `ip_address` - Client IP
- `user_agent` - Browser/device info
- `qr_authenticated` - Boolean (true if QR login)

**TTL:** `expires_at` (24 hours from creation)

**GSIs:**
- `user_email-created_at-index` - User session history

---

### 3. ielts-genai-prep-qr-tokens
**Purpose:** QR code authentication tokens

**Schema:**
```
Partition Key: token (String)
```

**Attributes:**
- `token` - Unique QR token (UUID)
- `user_email` - Associated user
- `created_at` - Generation timestamp
- `expires_at` - TTL (5 minutes)
- `used` - Boolean (one-time use)
- `used_at` - When token was consumed
- `device_id` - Mobile device identifier

**TTL:** `expires_at` (5 minutes from creation)

**Security:**
- Tokens expire after 5 minutes
- One-time use only
- Automatically deleted via TTL

---

## Assessment Tables

### 4. ielts-genai-prep-assessments
**Purpose:** Completed assessment results and scores

**Schema:**
```
Partition Key: assessment_id (String)
Sort Key: user_id (String)
```

**Attributes:**
- `assessment_id` - Unique assessment identifier
- `user_id` - User email
- `assessment_type` - speaking_academic, speaking_general, writing_academic, writing_general
- `created_at` - Start timestamp
- `completed_at` - Completion timestamp
- `band_score` - Overall band (0-9)
- `scores` - JSON with detailed breakdown
- `ai_feedback` - Generated feedback text
- `improvement_plan` - Personalized suggestions
- `duration_minutes` - Time taken
- `status` - in_progress, completed, abandoned

**GSIs:**
- `user_id-created_at-index` - User assessment history
- `assessment_type-created_at-index` - Query by type

**Score Breakdown (JSON):**
```json
{
  "speaking": {
    "fluency_coherence": 7.5,
    "lexical_resource": 6.5,
    "grammatical_range": 7.0,
    "pronunciation": 6.0
  },
  "writing": {
    "task_achievement": 7.0,
    "coherence_cohesion": 7.5,
    "lexical_resource": 6.5,
    "grammatical_range": 7.0
  }
}
```

---

### 5. ielts-assessment-questions
**Purpose:** Question bank for all assessment types

**Schema:**
```
Partition Key: question_id (String)
Sort Key: assessment_type (String)
```

**Attributes:**
- `question_id` - Unique question identifier
- `assessment_type` - speaking_part1, speaking_part2, writing_task1, etc.
- `difficulty` - easy, medium, hard
- `topic` - work, education, technology, etc.
- `question_text` - Actual question
- `sample_answer` - Example response (for reference)
- `keywords` - Array of expected vocabulary
- `estimated_time` - Recommended time (minutes)

**Example Speaking Part 2:**
```json
{
  "question_id": "sp2-001",
  "question_text": "Describe a person who has influenced you...",
  "topic": "people",
  "difficulty": "medium",
  "estimated_time": 2
}
```

---

### 6. ielts-assessment-rubrics
**Purpose:** Official IELTS scoring rubrics

**Schema:**
```
Partition Key: rubric_id (String)
```

**Attributes:**
- `rubric_id` - Criteria identifier
- `skill_type` - speaking, writing
- `criterion` - fluency_coherence, task_achievement, etc.
- `band_descriptors` - JSON with band 0-9 descriptions
- `evaluation_prompts` - AI evaluation instructions

**Example:**
```json
{
  "rubric_id": "speaking-fluency",
  "criterion": "fluency_coherence",
  "band_descriptors": {
    "7": "Speaks at length without noticeable effort...",
    "6": "Willing to speak at length, some hesitation...",
    "5": "Produces simple speech fluently..."
  }
}
```

---

## Purchase & Entitlement Tables

### 7. ielts-genai-prep-entitlements
**Purpose:** User purchase and subscription tracking

**Schema:**
```
Partition Key: user_email (String)
Sort Key: product_id (String)
```

**Attributes:**
- `user_email` - User identifier
- `product_id` - writing, speaking, full_mock_test
- `platform` - ios, android
- `purchase_date` - Transaction timestamp
- `expires_at` - Access expiration (30 days)
- `receipt_data` - App Store/Play Store receipt
- `transaction_id` - Apple/Google transaction ID
- `price_paid` - Amount in USD
- `status` - active, expired, refunded

**GSIs:**
- `user_email-expires_at-index` - Active entitlements query

**Purchase Verification:**
- iOS: Apple receipt validation
- Android: Google Play billing verification

---

## AI Safety & Moderation Tables

### 8. ielts-ai-safety-logs
**Purpose:** AI content moderation logs for speaking tests

**Schema:**
```
Partition Key: log_id (String)
Sort Key: timestamp (Number)
```

**Attributes:**
- `log_id` - Unique log identifier
- `timestamp` - When event occurred
- `assessment_id` - Link to assessment
- `user_email` - User involved
- `content_type` - audio, text
- `moderation_action` - warn, block, none
- `confidence` - AI confidence (0-1)
- `categories` - Array of flagged categories
- `user_response` - What user said/wrote
- `ai_response` - How Maya responded

**Moderation Categories:**
```
["profanity", "hate_speech", "violence", "sexual_content", "spam"]
```

---

### 9. ielts-content-reports
**Purpose:** User-reported content tracking

**Schema:**
```
Partition Key: report_id (String)
Sort Key: created_at (Number)
```

**Attributes:**
- `report_id` - Unique report identifier
- `created_at` - Report timestamp
- `reporter_email` - User who reported
- `assessment_id` - Related assessment
- `report_type` - inappropriate_ai, bug, inaccurate_score
- `description` - User explanation
- `status` - new, investigating, resolved, dismissed
- `admin_notes` - Internal review notes

---

## AI Agent Tables

### 10. ielts-support-tickets
**Purpose:** Customer support agent tickets

**Schema:**
```
Partition Key: ticket_id (String)
Sort Key: created_at (Number)
```

**Attributes:**
- `ticket_id` - Unique ticket identifier
- `created_at` - When ticket created
- `user_email` - Customer email
- `subject` - Email subject
- `message` - Customer message
- `category` - purchase, qr_code, audio, refund, technical
- `priority` - urgent, high, normal, low
- `status` - new, in_progress, resolved, escalated
- `ai_response` - Auto-generated response
- `ai_confidence` - Confidence (0-1)
- `escalated_at` - When escalated to human
- `resolved_at` - Resolution timestamp
- `devops_action_id` - Link to DevOps action if technical

**GSIs:**
- `status-created_at-index` - Query by status
- `priority-created_at-index` - Urgent tickets
- `user_email-created_at-index` - User history

---

### 11. ielts-devops-actions
**Purpose:** DevOps agent diagnostic actions

**Schema:**
```
Partition Key: action_id (String)
Sort Key: timestamp (Number)
```

**Attributes:**
- `action_id` - Unique action identifier
- `timestamp` - Action timestamp
- `action_type` - diagnose, fix_proposed, fix_applied
- `ticket_id` - Originating support ticket
- `issue_description` - Technical problem
- `affected_service` - lambda, dynamodb, gemini, etc.
- `ai_analysis` - DevOps agent diagnosis
- `proposed_fix` - Code changes suggested
- `code_diff` - Git diff
- `status` - pending_review, approved, rejected, applied
- `reviewed_by` - Human reviewer
- `pr_url` - CodeCommit/GitHub PR link

**GSIs:**
- `status-timestamp-index` - Pending approvals
- `affected_service-timestamp-index` - Service issues
- `ticket_id-timestamp-index` - Link to ticket

---

## Table Access Patterns

### Common Queries

**1. Get user's assessments:**
```python
table.query(
    IndexName='user_id-created_at-index',
    KeyConditionExpression='user_id = :email'
)
```

**2. Get urgent support tickets:**
```python
table.query(
    IndexName='priority-created_at-index',
    KeyConditionExpression='priority = :urgent'
)
```

**3. Get pending DevOps actions:**
```python
table.query(
    IndexName='status-timestamp-index',
    KeyConditionExpression='status = :pending_review'
)
```

## Backup & Recovery

- **Point-in-Time Recovery:** Enabled on all tables
- **Backup Schedule:** Daily automated backups
- **Retention:** 35 days
- **Encryption:** AES-256 at rest, TLS 1.2 in transit

## Capacity Planning

- **Billing Mode:** PAY_PER_REQUEST (on-demand)
- **No provisioned capacity** - Auto-scales based on traffic
- **Cost:** ~$0.25 per million read/write requests

## Related Files
- `deployment/dynamodb_dal.py` - Data access layer (371 lines)
- `ai-agents/dynamodb_tables.py` - Table creation scripts
