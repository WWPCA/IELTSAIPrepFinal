# 🔍 DynamoDB Table Name Audit - Complete System Analysis

**Date**: October 22, 2025  
**Audited By**: Replit Agent  
**Purpose**: Verify all DynamoDB table references match actual AWS infrastructure

---

## 📊 AWS Infrastructure - Actual Tables

### ✅ Tables Confirmed in AWS (from screenshots):

1. `ielts-assessment-questions` ✅
2. `ielts-devops-actions` ✅
3. `ielts-full-tests` ✅
4. `ielts-genai-prep-assessments` ✅
5. `ielts-genai-prep-auth-tokens` ✅
6. `ielts-genai-prep-entitlements` ✅
7. `ielts-genai-prep-reset-tokens` ✅
8. `ielts-genai-prep-rubrics` ✅
9. `ielts-genai-prep-sessions` ✅
10. `ielts-genai-prep-users` ✅
11. `ielts-listening-answers` ✅
12. `ielts-listening-questions` ✅
13. `ielts-listening-tests` ✅
14. `ielts-reading-answers` ✅
15. `ielts-reading-questions` ✅
16. `ielts-reading-tests` ✅
17. `ielts-support-tickets` ✅
18. `ielts-test-progress` ✅
19. `ielts-test-results` ✅

**Total AWS Tables**: 19

---

## 🔧 Code References - What's Actually Used

### **File: `deployment/dynamodb_dal.py` (lines 61-70)**

```python
self.table_names = {
    'users': 'ielts-genai-prep-users',           # ✅ MATCHES AWS
    'sessions': 'ielts-genai-prep-sessions',     # ✅ MATCHES AWS
    'assessments': 'ielts-genai-prep-assessments', # ✅ MATCHES AWS
    'entitlements': 'ielts-genai-prep-entitlements', # ✅ MATCHES AWS
    'questions': 'ielts-assessment-questions',   # ✅ MATCHES AWS
    'rubrics': 'ielts-assessment-rubrics',       # ⚠️ MISMATCH - See below
    'ai_safety_logs': 'ielts-ai-safety-logs',    # ❌ NOT IN AWS
    'content_reports': 'ielts-content-reports'   # ❌ NOT IN AWS
}
```

### **File: `deployment/dashboard_routes.py` (lines 18-19)**

```python
tickets_table = dynamodb.Table('ielts-support-tickets')  # ✅ MATCHES AWS
actions_table = dynamodb.Table('ielts-devops-actions')   # ✅ MATCHES AWS
```

### **File: `deployment/lambda_speaking_handler.py` (line 25)**

```python
sessions_table = dynamodb.Table(os.environ.get('SESSIONS_TABLE', 'ielts-genai-prep-sessions'))  # ✅ MATCHES AWS
```

---

## 📋 Workflow Analysis - Step-by-Step User Journey

### **WORKFLOW 1: Mobile App Registration**

**User Journey**: User downloads iOS/Android app → Registers account → Account created

| Step | Table Used | Table Name in Code | AWS Table Name | Status |
|------|-----------|-------------------|----------------|--------|
| 1. User submits registration | `users` | `ielts-genai-prep-users` | `ielts-genai-prep-users` | ✅ MATCH |
| 2. Create user record | `users` | `ielts-genai-prep-users` | `ielts-genai-prep-users` | ✅ MATCH |
| 3. Store password hash | `users` | `ielts-genai-prep-users` | `ielts-genai-prep-users` | ✅ MATCH |

**Files**: `deployment/mobile_api_routes.py` (lines 53-112), `deployment/dynamodb_dal.py` (UserDAL class)

---

### **WORKFLOW 2: In-App Purchase & Verification**

**User Journey**: User makes purchase → Receipt sent to backend → Entitlement granted

| Step | Table Used | Table Name in Code | AWS Table Name | Status |
|------|-----------|-------------------|----------------|--------|
| 1. Verify user exists | `users` | `ielts-genai-prep-users` | `ielts-genai-prep-users` | ✅ MATCH |
| 2. Check duplicate transaction | `entitlements` (TransactionIndex GSI) | `ielts-genai-prep-entitlements` | `ielts-genai-prep-entitlements` | ✅ MATCH |
| 3. Grant entitlement | `entitlements` | `ielts-genai-prep-entitlements` | `ielts-genai-prep-entitlements` | ✅ MATCH |
| 4. Store receipt data | `entitlements` | `ielts-genai-prep-entitlements` | `ielts-genai-prep-entitlements` | ✅ MATCH |

**Files**: `deployment/mobile_api_routes.py` (lines 114-233), `deployment/dynamodb_dal.py` (EntitlementDAL class)

---

### **WORKFLOW 3: User Login (Desktop Web)**

**User Journey**: User visits website → Logs in → Session created

| Step | Table Used | Table Name in Code | AWS Table Name | Status |
|------|-----------|-------------------|----------------|--------|
| 1. Verify credentials | `users` | `ielts-genai-prep-users` | `ielts-genai-prep-users` | ✅ MATCH |
| 2. Create session | `sessions` | `ielts-genai-prep-sessions` | `ielts-genai-prep-sessions` | ✅ MATCH |
| 3. Store session data | `sessions` | `ielts-genai-prep-sessions` | `ielts-genai-prep-sessions` | ✅ MATCH |
| 4. Update last_login | `users` | `ielts-genai-prep-users` | `ielts-genai-prep-users` | ✅ MATCH |

**Files**: `deployment/app.py` (login route), `deployment/dynamodb_dal.py` (SessionDAL class)

---

### **WORKFLOW 4: Taking an Assessment**

**User Journey**: User clicks assessment → Check entitlement → Load questions → Submit answers → Get score

| Step | Table Used | Table Name in Code | AWS Table Name | Status |
|------|-----------|-------------------|----------------|--------|
| 1. Verify session | `sessions` | `ielts-genai-prep-sessions` | `ielts-genai-prep-sessions` | ✅ MATCH |
| 2. Check entitlement | `entitlements` | `ielts-genai-prep-entitlements` | `ielts-genai-prep-entitlements` | ✅ MATCH |
| 3. Fetch questions | `questions` | `ielts-assessment-questions` | `ielts-assessment-questions` | ✅ MATCH |
| 4. Fetch rubrics | `rubrics` | `ielts-assessment-rubrics` | `ielts-genai-prep-rubrics` | ⚠️ **MISMATCH** |
| 5. Save assessment | `assessments` | `ielts-genai-prep-assessments` | `ielts-genai-prep-assessments` | ✅ MATCH |
| 6. Consume entitlement | `entitlements` | `ielts-genai-prep-entitlements` | `ielts-genai-prep-entitlements` | ✅ MATCH |

**Files**: `deployment/app.py` (assessment routes), `deployment/dynamodb_dal.py` (AssessmentDAL, EntitlementDAL)

**🚨 CRITICAL FINDING**: Rubrics table name mismatch detected!

---

### **WORKFLOW 5: Viewing Score Reports**

**User Journey**: User views dashboard → See past assessments → View detailed score

| Step | Table Used | Table Name in Code | AWS Table Name | Status |
|------|-----------|-------------------|----------------|--------|
| 1. Verify session | `sessions` | `ielts-genai-prep-sessions` | `ielts-genai-prep-sessions` | ✅ MATCH |
| 2. Fetch user assessments | `assessments` (UserIndex GSI) | `ielts-genai-prep-assessments` | `ielts-genai-prep-assessments` | ✅ MATCH |
| 3. Display scores | `assessments` | `ielts-genai-prep-assessments` | `ielts-genai-prep-assessments` | ✅ MATCH |

**Files**: `deployment/app.py` (profile/dashboard routes)

---

### **WORKFLOW 6: AI Support Tickets**

**User Journey**: User emails support → AI agent processes → Creates ticket

| Step | Table Used | Table Name in Code | AWS Table Name | Status |
|------|-----------|-------------------|----------------|--------|
| 1. Create support ticket | `tickets` | `ielts-support-tickets` | `ielts-support-tickets` | ✅ MATCH |
| 2. Store ticket data | `tickets` | `ielts-support-tickets` | `ielts-support-tickets` | ✅ MATCH |
| 3. Log DevOps action (if escalated) | `actions` | `ielts-devops-actions` | `ielts-devops-actions` | ✅ MATCH |

**Files**: `deployment/dashboard_routes.py`, `/ai-agents/lambda_customer_support.py`

---

## 🚨 DISCREPANCIES FOUND

### **1. CRITICAL MISMATCH - Rubrics Table Name**

**Code Reference**: `deployment/dynamodb_dal.py` line 67  
**Code Says**: `'rubrics': 'ielts-assessment-rubrics'`  
**AWS Has**: `ielts-genai-prep-rubrics`

**Impact**: 🔴 HIGH - Assessment scoring system will FAIL when loading rubrics  
**Action Required**: Update code to match AWS table name

**Fix Required**:
```python
# Change line 67 from:
'rubrics': 'ielts-assessment-rubrics',

# To:
'rubrics': 'ielts-genai-prep-rubrics',
```

---

### **2. MISSING TABLES - Not in AWS**

**Code References**:
- `deployment/dynamodb_dal.py` line 68: `'ai_safety_logs': 'ielts-ai-safety-logs'`
- `deployment/dynamodb_dal.py` line 69: `'content_reports': 'ielts-content-reports'`

**AWS Reality**: These tables do NOT exist in your AWS account

**Impact**: 🟡 MEDIUM - Features using these tables will fail  
**Action Required**: Either create these tables in AWS OR remove references from code

**Recommendation**: Remove from code since they're not being actively used

---

### **3. UNUSED TABLES - Exist in AWS but Not Referenced**

**Tables in AWS but NOT used in production code**:

1. `ielts-genai-prep-auth-tokens` - Email verification/OAuth tokens
2. `ielts-genai-prep-reset-tokens` - Password reset tokens
3. `ielts-reading-questions` - Reading module questions
4. `ielts-reading-answers` - Reading module answer keys
5. `ielts-reading-tests` - Reading test metadata
6. `ielts-listening-questions` - Listening module questions
7. `ielts-listening-answers` - Listening module answer keys
8. `ielts-listening-tests` - Listening test metadata
9. `ielts-full-tests` - Complete mock test configurations
10. `ielts-test-results` - Test result summaries
11. `ielts-test-progress` - User progress tracking

**Impact**: 🟢 LOW - These tables exist but aren't actively used  
**Reason**: Likely created for future Reading/Listening modules or legacy features  
**Action Required**: None immediately - keep for future feature development

---

## ✅ VERIFIED CORRECT MAPPINGS

All these table references are **CORRECT** and match AWS:

| Workflow Step | Code Reference | AWS Table | Status |
|--------------|---------------|-----------|--------|
| User registration | `ielts-genai-prep-users` | `ielts-genai-prep-users` | ✅ |
| Session management | `ielts-genai-prep-sessions` | `ielts-genai-prep-sessions` | ✅ |
| Purchase tracking | `ielts-genai-prep-entitlements` | `ielts-genai-prep-entitlements` | ✅ |
| Assessment storage | `ielts-genai-prep-assessments` | `ielts-genai-prep-assessments` | ✅ |
| Question bank | `ielts-assessment-questions` | `ielts-assessment-questions` | ✅ |
| Support tickets | `ielts-support-tickets` | `ielts-support-tickets` | ✅ |
| DevOps actions | `ielts-devops-actions` | `ielts-devops-actions` | ✅ |

---

## 🎯 Summary & Recommendations

### **Issues Found**: 3

1. ❌ **CRITICAL**: Rubrics table name mismatch (MUST FIX before deployment)
2. ⚠️ **MEDIUM**: Two tables referenced in code don't exist in AWS (should remove)
3. ℹ️ **INFO**: 11 tables exist in AWS but unused (future features - no action needed)

### **Next Steps**:

**Priority 1 - URGENT** 🔴:
```bash
# Fix rubrics table name
# File: deployment/dynamodb_dal.py line 67
'rubrics': 'ielts-genai-prep-rubrics',  # Changed from ielts-assessment-rubrics
```

**Priority 2 - Cleanup** 🟡:
```python
# Remove these lines from deployment/dynamodb_dal.py (lines 68-69):
# 'ai_safety_logs': 'ielts-ai-safety-logs',
# 'content_reports': 'ielts-content-reports'
```

**Priority 3 - Future** 🟢:
- Document unused tables for future Reading/Listening module development
- Consider creating auth_tokens and reset_tokens references when implementing password reset

---

## 📁 Files Audited

1. ✅ `deployment/dynamodb_dal.py` - Main table name configuration
2. ✅ `deployment/mobile_api_routes.py` - Mobile API endpoints
3. ✅ `deployment/app.py` - Main Flask application
4. ✅ `deployment/dashboard_routes.py` - Support ticket routes
5. ✅ `deployment/lambda_speaking_handler.py` - Speaking assessment handler

---

**Audit Status**: ⚠️ **CRITICAL ISSUES FOUND**  
**Action Required**: Fix rubrics table name before next deployment  
**Overall Health**: 7/10 tables correctly referenced, 2 phantom tables, 1 critical mismatch

---

**Auditor**: Replit Agent  
**Completed**: October 22, 2025
