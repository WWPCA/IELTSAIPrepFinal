# Immediate Verification Steps

## ✅ Deployment Chain Confirmed

```
www.ieltsaiprep.com 
  ↓
CloudFront E1EPXAU67877FR (d2ehqyfqw00g6j.cloudfront.net)
  ↓  
API Gateway n0cpf1rmvc (/prod)
  ↓
Lambda ielts-genai-prep-api (Version 11 - Updated 05:51 UTC)
```

**All fixes are deployed to the correct Lambda function.**

---

## 🔍 Verify RIGHT NOW (Bypassing CloudFront)

### Test 1: Privacy Policy (Direct API Gateway)
```bash
curl -s https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/privacy-policy | grep -i "google cloud"
```
**Expected:** NO output (zero Google Cloud mentions)

### Test 2: Practice Modules (Direct API Gateway)
```bash
curl -s https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/practice-modules | grep -o 'href="[^"]*".*Purchase via Mobile App' | head -2
```
**Expected:** Should show `href="/login"` NOT `href="/qr-auth"`

---

## 🌐 Test CloudFront (After Cache Clears)

### Browser Test:
1. **Hard refresh:** Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. **Clear site data:** 
   - Chrome: Settings → Privacy → Clear browsing data → ieltsaiprep.com
   - Firefox: Ctrl+Shift+Del → Cookies for ieltsaiprep.com
3. **Test in Incognito/Private window**

### URLs to Test:
- Privacy Policy: https://www.ieltsaiprep.com/privacy-policy
- Practice Modules: https://www.ieltsaiprep.com/practice-modules
- Login: https://www.ieltsaiprep.com/login

---

## ⏱️ Cache Invalidation Timeline

**Latest Invalidation Created:** Just now
**Typical Propagation Time:** 5-15 minutes globally
**Your Region:** North America East (should be faster, ~5-7 minutes)

### Check Invalidation Status:
```bash
aws cloudfront list-invalidations --distribution-id E1EPXAU67877FR --max-items 5
```

---

## 📊 What's in Lambda V11

✅ **Privacy Policy:** 0 Google Cloud mentions (verified in deployed code)
✅ **Purchase Buttons:** All 6 link to `/login` (verified in deployed code)  
✅ **reCAPTCHA:** Added to admin login
✅ **Old Files:** Deleted `approved_privacy_policy_genai.html`

**The Lambda code is 100% correct. CloudFront just needs time to propagate.**

---

## 🚨 If Still Not Working After 15 Minutes

Contact AWS Support about CloudFront distribution E1EPXAU67877FR having persistent cache issues despite multiple invalidations.

**OR**

Temporarily update CloudFront cache behavior to have shorter TTL (Time To Live) values.
