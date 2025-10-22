# Lambda Architecture - Complete Explanation

## 🎯 **THE PRODUCTION PATH (What Serves www.ieltsaiprep.com)**

```
User Browser
    ↓
www.ieltsaiprep.com (Route 53 DNS)
    ↓
CloudFront (E1EPXAU67877FR)
    ↓
API Gateway (n0cpf1rmvc) - Stage: prod
    ↓
Lambda: ielts-genai-prep-api ← **THIS IS PRODUCTION** ✅
    ↓
DynamoDB Tables (11 tables)
```

**Today's deployment went to:** `ielts-genai-prep-api` ✅ **CORRECT**

---

## 📋 **All Lambda Functions Explained**

### **1. Primary Application Lambdas (Flask Apps)**

| Lambda Name | Size | Purpose | Status |
|------------|------|---------|--------|
| **ielts-genai-prep-api** | 103 MB | **PRODUCTION WEBSITE** - Serves www.ieltsaiprep.com | ✅ **ACTIVE - Just deployed clean code** |
| ielts-genai-prep-lambda | 117 MB | **BACKUP/TESTING** - Alternative deployment (not connected to production) | 🟡 Standby |

**Impact of deploying to different ones:**
- Deploying to `ielts-genai-prep-api` → Updates production website immediately ✅
- Deploying to `ielts-genai-prep-lambda` → Updates nothing (isolated testing environment)

---

### **2. Microservice Lambdas (Individual Functions)**

These are **older microservice-style** functions from an earlier architecture:

| Lambda Name | Size | Purpose | Current Status |
|------------|------|---------|----------------|
| ielts-auth-handler | 20 KB | User authentication | 🔴 **Legacy** - Now handled in main app |
| ielts-user-handler | 10 KB | User management | 🔴 **Legacy** - Now handled in main app |
| ielts-purchase-handler | 10 KB | Purchase processing | 🔴 **Legacy** - Now handled in main app |
| ielts-assessment-handler | 10 KB | Assessment management | 🔴 **Legacy** - Now handled in main app |
| ielts-qr-auth-handler | 88 KB | QR code authentication | 🔴 **Legacy** - Feature removed today |
| ielts-nova-ai-handler | 10 KB | AI assessment scoring | 🔴 **Legacy** - Now handled in main app |
| ielts-email-service | 15 KB | Email notifications | 🔴 **Legacy** - Now handled in main app |

**Architecture Evolution:**
- **Old:** Microservices (each function separate)
- **Current:** Monolithic Flask app (`ielts-genai-prep-api`)
- **Why:** Simpler deployment, lower latency, easier debugging

---

### **3. AI Agent Lambdas (Active Support System)**

| Lambda Name | Size | Purpose | Status |
|------------|------|---------|--------|
| ielts-customer-support-agent | 5 KB | AI-powered email support via info@ieltsaiprep.com | ✅ **ACTIVE** |
| ielts-devops-agent | 6 KB | Code analysis & bug diagnosis | ✅ **ACTIVE** |

**These are separate and active** - Handle support automation independently.

---

## ⚠️ **What Happens When You Deploy to Different Lambdas?**

### **Scenario 1: Deploy to `ielts-genai-prep-api` (Production)**
```
✅ Changes go LIVE immediately
✅ www.ieltsaiprep.com updated
✅ Users see new code
```

### **Scenario 2: Deploy to `ielts-genai-prep-lambda` (Backup)**
```
🟡 No impact on production
🟡 Code updates isolated Lambda
🟡 Good for testing before production
```

### **Scenario 3: Deploy to Legacy Lambdas (microservices)**
```
🔴 No impact - these aren't connected
🔴 API Gateway doesn't route to them
🔴 Waste of deployment time
```

---

## 🎯 **Recommendation: ONE Lambda Strategy**

### **Going Forward:**

**ALWAYS deploy to:** `ielts-genai-prep-api`

**Why?**
1. ✅ Connected to production (CloudFront → API Gateway → This Lambda)
2. ✅ Contains complete application (no microservices needed)
3. ✅ Latest code with QR cleanup deployed
4. ✅ 103 MB size is optimal for Lambda

**Consider deleting:**
1. `ielts-genai-prep-lambda` - Unless you want it as backup
2. All legacy microservice Lambdas - No longer used
3. `ielts-qr-auth-handler` - Feature removed

**Keep:**
1. `ielts-genai-prep-api` ← **PRODUCTION**
2. `ielts-customer-support-agent` ← AI support
3. `ielts-devops-agent` ← AI DevOps

---

## 📊 **Cost Impact of Multiple Lambdas**

**Current monthly costs:**

| Lambda | Invocations/month | Cost |
|--------|------------------|------|
| ielts-genai-prep-api | ~100,000 | ~$2-5 |
| ielts-customer-support-agent | ~500 | ~$0.01 |
| ielts-devops-agent | ~50 | ~$0.001 |
| **Legacy Lambdas (7)** | 0 (unused) | **~$0 but waste space** |

**Recommendation:** Delete unused Lambdas to:
- Clean up AWS console
- Avoid confusion about which to deploy to
- Reduce clutter

---

## 🔧 **How to Clean Up (Optional)**

### **Safe to Delete:**
```bash
# Microservice Lambdas (replaced by main app)
aws lambda delete-function --function-name ielts-auth-handler --region us-east-1
aws lambda delete-function --function-name ielts-user-handler --region us-east-1
aws lambda delete-function --function-name ielts-purchase-handler --region us-east-1
aws lambda delete-function --function-name ielts-assessment-handler --region us-east-1
aws lambda delete-function --function-name ielts-nova-ai-handler --region us-east-1
aws lambda delete-function --function-name ielts-email-service --region us-east-1

# QR Auth (feature removed)
aws lambda delete-function --function-name ielts-qr-auth-handler --region us-east-1
```

### **Consider Keeping as Backup:**
```bash
# Backup/testing version of main app
ielts-genai-prep-lambda
```

---

## ✅ **Summary**

**Production Lambda:** `ielts-genai-prep-api` (103 MB)  
**Connected to:** CloudFront → API Gateway (n0cpf1rmvc) → Production  
**Last Deployed:** Oct 22, 2025 (Clean code, no QR)  
**Status:** ✅ Live and serving www.ieltsaiprep.com  

**Impact of Today's Deployments:**
- ✅ Deployed to production Lambda (`ielts-genai-prep-api`)
- ✅ Website updated with QR code removed
- ✅ Users now see simplified mobile-first flow
- ✅ No confusion - single source of truth

**Going forward:** Always deploy to `ielts-genai-prep-api` for production updates.

---

*Generated: October 22, 2025*
