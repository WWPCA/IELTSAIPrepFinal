"""
Test Assessment Pages After CloudFront Fix
This script tests all assessment pages once the cache behavior is fixed
"""

import urllib.request
import json
import time
from datetime import datetime

def test_assessment_page_access():
    """Test all assessment page URLs after CloudFront fix"""
    
    base_url = "https://www.ieltsaiprep.com"
    
    assessment_pages = [
        "/assessment/academic-writing",
        "/assessment/general-writing", 
        "/assessment/academic-speaking",
        "/assessment/general-speaking"
    ]
    
    print("🧪 Testing Assessment Pages After CloudFront Fix")
    print("=" * 60)
    
    results = {}
    
    for page in assessment_pages:
        url = f"{base_url}{page}"
        print(f"Testing: {url}")
        
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req) as response:
                status_code = response.getcode()
                content = response.read().decode('utf-8')
                
                if status_code == 200:
                    if "Academic Writing Assessment" in content or "General Writing Assessment" in content or \
                       "Academic Speaking Assessment" in content or "General Speaking Assessment" in content:
                        results[page] = "✅ WORKING - Assessment page loaded correctly"
                        print(f"   ✅ Status: {status_code} - Assessment page loaded")
                    else:
                        results[page] = "⚠️  PARTIAL - Page loaded but content may be incorrect"
                        print(f"   ⚠️  Status: {status_code} - Page loaded but content unclear")
                else:
                    results[page] = f"❌ ERROR - HTTP {status_code}"
                    print(f"   ❌ Status: {status_code} - Page not accessible")
                    
        except urllib.error.HTTPError as e:
            results[page] = f"❌ HTTP ERROR - {e.code}"
            print(f"   ❌ HTTP Error: {e.code}")
        except Exception as e:
            results[page] = f"❌ ERROR - {str(e)}"
            print(f"   ❌ Error: {str(e)}")
    
    return results

def test_nova_ai_functionality():
    """Test Nova AI endpoints after assessment pages are fixed"""
    
    print("\n🤖 Testing Nova AI Functionality")
    print("=" * 60)
    
    # Test Nova Micro endpoint
    try:
        nova_micro_url = "https://www.ieltsaiprep.com/api/nova-micro-writing"
        req = urllib.request.Request(nova_micro_url, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        test_data = {
            "user_email": "test@ieltsgenaiprep.com",
            "assessment_type": "academic_writing",
            "question_id": "academic_writing_1",
            "user_response": "This is a test response for Nova Micro evaluation."
        }
        
        data = json.dumps(test_data).encode('utf-8')
        req.data = data
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if 'nova_micro_available' in result and result['nova_micro_available']:
                print("   ✅ Nova Micro - Available and responding")
            else:
                print("   ⚠️  Nova Micro - Module not loaded (expected in .replit environment)")
                
    except Exception as e:
        print(f"   ❌ Nova Micro Error: {e}")
    
    # Test Maya AI endpoint
    try:
        maya_url = "https://www.ieltsaiprep.com/api/maya-introduction"
        req = urllib.request.Request(maya_url, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        test_data = {
            "user_email": "test@ieltsgenaiprep.com",
            "assessment_type": "academic_speaking",
            "question_id": "academic_speaking_1"
        }
        
        data = json.dumps(test_data).encode('utf-8')
        req.data = data
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if 'maya_available' in result and result['maya_available']:
                print("   ✅ Maya AI - Available and responding")
            else:
                print("   ⚠️  Maya AI - Module not loaded (expected in .replit environment)")
                
    except Exception as e:
        print(f"   ❌ Maya AI Error: {e}")

def test_direct_api_gateway_still_blocked():
    """Verify direct API Gateway access is still blocked"""
    
    print("\n🔒 Testing Direct API Gateway Blocking")
    print("=" * 60)
    
    direct_urls = [
        "https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/",
        "https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/assessment/academic-writing"
    ]
    
    for url in direct_urls:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                status_code = response.getcode()
                print(f"   ⚠️  {url} - Status: {status_code} (should be 403)")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print(f"   ✅ {url} - Properly blocked (403)")
            else:
                print(f"   ❌ {url} - Unexpected error: {e.code}")
        except Exception as e:
            print(f"   ❌ {url} - Error: {str(e)}")

def generate_test_report(assessment_results):
    """Generate comprehensive test report"""
    
    report = {
        'test_date': datetime.now().isoformat(),
        'assessment_pages': assessment_results,
        'cloudfront_fix_status': 'TESTING_AFTER_MANUAL_FIX',
        'overall_status': 'PENDING_CLOUDFRONT_FIX',
        'next_steps': [
            'Manual CloudFront cache behavior fix required',
            'Update /assessment/* behavior to match /api/* configuration',
            'Test Nova AI functionality after fix',
            'Proceed with app store submission'
        ]
    }
    
    working_count = sum(1 for result in assessment_results.values() if result.startswith('✅'))
    total_count = len(assessment_results)
    
    print(f"\n📊 Test Summary")
    print("=" * 60)
    print(f"Assessment Pages Working: {working_count}/{total_count}")
    print(f"CloudFront Fix Status: {report['cloudfront_fix_status']}")
    print(f"Overall Status: {report['overall_status']}")
    
    if working_count == total_count:
        print("\n🎉 All assessment pages are working!")
        print("✅ Ready to test Nova AI functionality")
        print("✅ Ready for app store submission")
    else:
        print("\n⏳ CloudFront cache behavior fix still needed")
        print("📋 Follow steps in cloudfront_assessment_fix_steps.md")
    
    return report

if __name__ == "__main__":
    print("🔍 IELTS GenAI Prep - Assessment Pages Test")
    print("=" * 60)
    print("This script tests assessment pages after CloudFront fix")
    print("Run this after updating the /assessment/* cache behavior")
    print()
    
    # Test assessment page access
    assessment_results = test_assessment_page_access()
    
    # Test Nova AI functionality
    test_nova_ai_functionality()
    
    # Test security (direct API Gateway blocking)
    test_direct_api_gateway_still_blocked()
    
    # Generate test report
    report = generate_test_report(assessment_results)
    
    print("\n🎯 Next Steps:")
    print("1. Fix CloudFront /assessment/* cache behavior (manual)")
    print("2. Run this test script again to verify")
    print("3. Test Nova AI functionality")
    print("4. Proceed with app store submission")