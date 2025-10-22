# Nova Micro → Nova Pro → Human Escalation Design

**Date**: October 22, 2025  
**Purpose**: Implement intelligent AI escalation to reduce human support costs while improving response quality

---

## 🎯 Business Case

**Current Flow**:
```
User Email → Nova Micro ($0.001/email)
  ↓ (confidence < 0.6)
Human Support ($5-10 per ticket)
```

**Proposed Flow**:
```
User Email → Nova Micro ($0.001/email)
  ↓ (confidence < 0.6 OR complex question)
Nova Pro Analysis ($0.01/email)
  ↓ (confidence < 0.7 OR urgent/refund)
Human Support ($5-10 per ticket)
```

**Expected Savings**:
- Current: 20% human escalation × $5/ticket = $1.00 average cost per email
- Proposed: Nova Pro handles 70% of complex cases = only 6% human escalation
- **New cost**: 0.80 × $0.001 + 0.20 × $0.01 + 0.06 × $5 = **$0.30 average** per email
- **Savings**: 70% cost reduction + better response quality

---

## 🏗️ Architecture Design

### Option 1: Nova Pro Within Customer Support Lambda ✅ RECOMMENDED

**Implementation**:
```python
def lambda_handler(event, context):
    # 1. Nova Micro first pass
    micro_response = generate_response_micro(email_data, kb_results)
    
    # 2. Check if Nova Pro needed
    if micro_response['confidence'] < 0.6 or is_complex_question(email_data):
        # 3. Escalate to Nova Pro (same Lambda)
        pro_response = generate_response_pro(email_data, kb_results, micro_response)
        
        # 4. Use Pro response if better
        if pro_response['confidence'] >= 0.7:
            send_email_response(pro_response)
            return
    
    # 5. If still low confidence, escalate to human
    if final_response['confidence'] < 0.7:
        notify_human_review(ticket)
```

**Pros**:
- ✅ Single Lambda function (simple deployment)
- ✅ No additional infrastructure
- ✅ Pro analysis has full context from Micro attempt
- ✅ Lower latency (no SNS/async overhead)

**Cons**:
- ⚠️ Longer Lambda execution time for escalated cases
- ⚠️ Higher memory usage when Pro model invoked

---

### Option 2: Separate Nova Pro Lambda

**Implementation**:
```
Customer Support (Micro) → SNS Topic → Nova Pro Lambda → Response
```

**Pros**:
- ✅ Clean separation of concerns
- ✅ Micro Lambda stays fast and lightweight

**Cons**:
- ❌ Additional Lambda function to manage
- ❌ Async overhead (slower response to customer)
- ❌ More complex error handling

---

### Option 3: Enhance DevOps Lambda for General Questions

**Implementation**:
Modify existing DevOps Lambda to handle both technical AND non-technical questions.

**Pros**:
- ✅ Reuses existing Nova Pro infrastructure

**Cons**:
- ❌ DevOps Lambda designed for code analysis
- ❌ Mixing concerns (technical vs customer support)
- ❌ Still async via SNS

---

## ✅ Recommended Approach: Option 1

Implement Nova Pro as a "second opinion" within the Customer Support Lambda.

---

## 🔧 Implementation Details

### 1. Model Comparison

| Feature | **Nova Micro** | **Nova Pro** |
|---------|---------------|--------------|
| **Cost** | $0.000035/1K input, $0.00014/1K output | $0.0008/1K input, $0.0032/1K output |
| **Context** | 128K tokens | 300K tokens |
| **Use Case** | Simple questions, FAQs, routine support | Complex reasoning, multi-step analysis |
| **Latency** | ~1-2 seconds | ~3-5 seconds |
| **Accuracy** | Good for straightforward queries | Superior for complex scenarios |

**Cost Example** (1,000 input + 500 output tokens):
- **Micro**: $0.000035 × 1 + $0.00014 × 0.5 = **$0.000105** (~$0.0001)
- **Pro**: $0.0008 × 1 + $0.0032 × 0.5 = **$0.0024** (~$0.0024)

**Pro is 24x more expensive, but still 2,000x cheaper than human support!**

---

### 2. Escalation Triggers

**Micro → Pro Escalation**:
```python
def should_escalate_to_pro(classification, micro_response, email_data):
    # Low confidence
    if micro_response['confidence'] < 0.6:
        return True
    
    # Complex question indicators
    complex_keywords = ['why', 'how does', 'explain', 'multiple', 'comparison']
    if any(kw in email_data['body'].lower() for kw in complex_keywords):
        return True
    
    # Technical questions
    if classification['category'] in ['technical', 'access']:
        return True
    
    # Multi-part questions
    if email_data['body'].count('?') > 2:
        return True
    
    return False
```

**Pro → Human Escalation**:
```python
def should_escalate_to_human(classification, pro_response):
    # Still low confidence after Pro
    if pro_response['confidence'] < 0.7:
        return True
    
    # High priority
    if classification['priority'] == 'urgent':
        return True
    
    # Sensitive categories
    if classification['category'] in ['refund', 'billing']:
        return True
    
    # Angry customer
    if classification['sentiment'] == 'angry':
        return True
    
    return False
```

---

### 3. Nova Pro Prompt Engineering

**Strategy**: Give Pro full context + Micro's attempt for refinement

```python
def generate_response_pro(email_data, kb_results, micro_response):
    prompt = f"""
You are a senior customer support specialist for IELTS AI Prep. A junior AI assistant 
(Nova Micro) attempted to answer this customer inquiry but couldn't provide a confident 
response. Your task is to provide a comprehensive, accurate answer.

CUSTOMER EMAIL:
From: {email_data['from']}
Subject: {email_data['subject']}
Message: {email_data['body']}

MICRO AI'S ATTEMPT:
Response: {micro_response['response']}
Confidence: {micro_response['confidence']}
Issues: Low confidence suggests the question is complex or requires deeper analysis.

KNOWLEDGE BASE CONTEXT:
{kb_results}

YOUR TASK:
1. Analyze the customer's question thoroughly
2. Provide a detailed, accurate response
3. Address any nuances the Micro AI may have missed
4. If this is technical, explain clearly for non-technical users
5. If you need human expert review, explicitly state why

IMPORTANT:
- Be comprehensive but clear
- Use simple language (customers are non-technical)
- If uncertain, recommend human review rather than guessing
- Score your confidence 0-1 (be conservative)

Generate response in this exact JSON format:
{{
    "response": "your detailed response here",
    "confidence": 0.85,
    "reasoning": "why this answer is appropriate",
    "requires_human": false,
    "suggested_actions": ["action 1", "action 2"]
}}
"""
    
    # Invoke Nova Pro
    response = bedrock_runtime.invoke_model(
        modelId='amazon.nova-pro-v1:0',
        body=json.dumps({
            "messages": [{"role": "user", "content": prompt}],
            "inferenceConfig": {
                "max_new_tokens": 2000,
                "temperature": 0.3  # Lower for more consistent responses
            }
        })
    )
    
    # Parse response
    result = json.loads(response['body'].read())
    return parse_pro_response(result)
```

---

### 4. Code Changes Required

**File**: `ai-agents/lambda_customer_support.py`

**New Functions**:
1. `generate_response_pro()` - Nova Pro response generation
2. `should_escalate_to_pro()` - Pro escalation logic
3. `is_complex_question()` - Complexity detection

**Modified Functions**:
1. `lambda_handler()` - Add Pro escalation step
2. `handle_escalation()` - Update to handle Pro → Human flow

**Modified Workflow**:
```python
# Line 94-104: After Micro response
ai_response_micro = generate_response(...)

# NEW: Check if Pro needed
if should_escalate_to_pro(classification, ai_response_micro, email_data):
    print(f"Escalating to Nova Pro for better analysis")
    ai_response_pro = generate_response_pro(
        email_data, kb_response, ai_response_micro
    )
    # Use Pro response
    final_response = ai_response_pro
    escalation_tier = 'pro'
else:
    final_response = ai_response_micro
    escalation_tier = 'micro'

# Determine if human needed
should_escalate_human = determine_escalation(
    classification, final_response['confidence']
)

# Save ticket with escalation tier
ticket = save_ticket(
    ticket_id, email_data, classification, 
    final_response, should_escalate_human, escalation_tier
)
```

---

### 5. DynamoDB Schema Updates

**Table**: `ielts-support-tickets`

**New Fields**:
```python
{
    'ticket_id': 'TICKET-20251022-ABC123',
    'escalation_tier': 'pro',  # NEW: 'micro', 'pro', or 'human'
    'micro_confidence': 0.55,  # NEW: Micro's confidence score
    'pro_confidence': 0.85,    # NEW: Pro's confidence score (if escalated)
    'processing_time_ms': 4500, # NEW: Total processing time
    'cost_estimate': 0.0024,   # NEW: Estimated AI cost
    # ... existing fields
}
```

---

### 6. Monitoring & Metrics

**CloudWatch Metrics to Track**:
1. `EscalationToProCount` - How often Micro → Pro
2. `EscalationToHumanCount` - How often Pro → Human
3. `ProSuccessRate` - % of Pro responses that don't need human
4. `AverageProcessingTime` - Latency impact
5. `EstimatedCostPerTicket` - Cost tracking

**Expected Metrics** (after implementation):
- Micro → Pro: 20% of tickets
- Pro → Human: 30% of Pro escalations = 6% total
- Pro success rate: 70%
- Average cost: $0.001 × 0.80 + $0.0024 × 0.20 = **$0.0013** per email (AI only)

---

### 7. Testing Plan

**Test Cases**:
1. **Simple FAQ** → Micro handles, no Pro escalation
2. **Complex technical question** → Micro → Pro → Auto-response
3. **Billing/refund question** → Micro → Pro → Human review
4. **Multi-part question** → Pro escalation triggered
5. **Angry customer** → Pro → Human (regardless of confidence)

**Success Criteria**:
- ✅ Pro reduces human escalation by 50%+
- ✅ Average response time < 10 seconds (including Pro)
- ✅ Customer satisfaction maintained or improved
- ✅ Cost per ticket < $0.01 (AI costs)

---

## 📊 Expected ROI

**Current Costs** (per 1,000 emails):
- Nova Micro: 1,000 × $0.001 = $1
- Human support: 200 × $5 = $1,000
- **Total**: $1,001

**New Costs** (per 1,000 emails):
- Nova Micro: 1,000 × $0.001 = $1
- Nova Pro: 200 × $0.01 = $2
- Human support: 60 × $5 = $300
- **Total**: $303

**Savings**: $698 per 1,000 emails = **70% cost reduction**

---

## 🚀 Deployment Plan

**Phase 1: Implementation** (1-2 hours)
1. Add `generate_response_pro()` function
2. Add `should_escalate_to_pro()` logic
3. Update `lambda_handler()` workflow
4. Add new DynamoDB fields

**Phase 2: Testing** (1 hour)
1. Unit tests for escalation logic
2. Integration tests with sample emails
3. Cost validation

**Phase 3: Deployment** (30 minutes)
1. Deploy updated Lambda function
2. Monitor CloudWatch logs
3. Validate first 10 Pro escalations

**Phase 4: Optimization** (ongoing)
1. Tune confidence thresholds
2. Refine Pro prompts
3. Adjust escalation criteria based on metrics

---

## ✅ Next Steps

1. ✅ Get user approval for this approach
2. Implement changes in `lambda_customer_support.py`
3. Test with sample customer emails
4. Deploy to production Lambda
5. Monitor metrics for 1 week
6. Adjust thresholds based on results

---

**Status**: AWAITING USER APPROVAL

**Implementation Time**: ~3 hours total  
**Expected Savings**: 70% reduction in support costs  
**Risk**: Low (can rollback to Micro-only if issues)
