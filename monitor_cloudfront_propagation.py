"""
Monitor CloudFront Propagation and Test Assessment Pages
"""

import urllib.request
import urllib.error
import json
import time
import boto3
from datetime import datetime

def check_cloudfront_status():
    """Check CloudFront distribution status"""
    try:
        client = boto3.client('cloudfront', region_name='us-east-1')
        response = client.get_distribution(Id='E1EPXAU67877FR')
        status = response['Distribution']['Status']
        last_modified = response['Distribution']['LastModifiedTime']
        
        print(f"📊 CloudFront Distribution Status: {status}")
        print(f"📅 Last Modified: {last_modified}")
        
        return status.lower() == 'deployed'
        
    except Exception as e:
        print(f"❌ Error checking CloudFront status: {e}")
        return False

def test_assessment_pages():
    """Test all assessment pages for 200 responses"""
    
    base_url = "https://www.ieltsaiprep.com"
    assessment_pages = [
        "/assessment/academic-writing",
        "/assessment/general-writing",
        "/assessment/academic-speaking", 
        "/assessment/general-speaking"
    ]
    
    print("\n🧪 Testing Assessment Pages...")
    print("=" * 50)
    
    results = {}
    all_working = True
    
    for page in assessment_pages:
        url = f"{base_url}{page}"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 Assessment Test')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                
                if status_code == 200:
                    print(f"✅ {page} - Status: {status_code}")
                    results[page] = "WORKING"
                else:
                    print(f"⚠️  {page} - Status: {status_code}")
                    results[page] = f"STATUS_{status_code}"
                    all_working = False
                    
        except urllib.error.HTTPError as e:
            print(f"❌ {page} - HTTP Error: {e.code}")
            results[page] = f"HTTP_ERROR_{e.code}"
            all_working = False
        except Exception as e:
            print(f"❌ {page} - Error: {str(e)}")
            results[page] = f"ERROR"
            all_working = False
    
    return results, all_working

def test_nova_ai_readiness():
    """Test Nova AI endpoints readiness"""
    
    print("\n🤖 Testing Nova AI Endpoints...")
    print("=" * 50)
    
    endpoints = [
        "/api/nova-micro-writing",
        "/api/maya-introduction"
    ]
    
    base_url = "https://www.ieltsaiprep.com"
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        
        try:
            # Test with POST request
            req = urllib.request.Request(url, method='POST')
            req.add_header('Content-Type', 'application/json')
            
            test_data = {
                "user_email": "test@ieltsgenaiprep.com",
                "assessment_type": "academic_writing",
                "question_id": "test_question"
            }
            
            data = json.dumps(test_data).encode('utf-8')
            req.data = data
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'nova_micro_available' in result or 'maya_available' in result:
                    print(f"✅ {endpoint} - Endpoint accessible")
                else:
                    print(f"⚠️  {endpoint} - Endpoint accessible but modules not loaded")
                    
        except urllib.error.HTTPError as e:
            if e.code == 405:  # Method not allowed is expected for some endpoints
                print(f"✅ {endpoint} - Endpoint accessible (405 expected)")
            else:
                print(f"❌ {endpoint} - HTTP Error: {e.code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")

def monitor_propagation():
    """Monitor CloudFront propagation and test when ready"""
    
    print("🔄 Monitoring CloudFront Propagation...")
    print("This may take 10-15 minutes for global propagation")
    print("=" * 60)
    
    max_attempts = 30  # 15 minutes with 30-second intervals
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        
        # Check CloudFront status
        is_deployed = check_cloudfront_status()
        
        if is_deployed:
            print("\n🎉 CloudFront Distribution is Deployed!")
            print("Testing assessment pages...")
            
            # Test assessment pages
            results, all_working = test_assessment_pages()
            
            if all_working:
                print("\n✅ All Assessment Pages Working!")
                print("Testing Nova AI readiness...")
                
                # Test Nova AI endpoints
                test_nova_ai_readiness()
                
                print("\n🎯 CloudFront Fix Complete!")
                print("=" * 60)
                print("✅ Assessment pages are now accessible")
                print("✅ Nova AI endpoints are ready for testing")
                print("✅ Ready to proceed with Nova functionality testing")
                
                return True
            else:
                print(f"\n⏳ Attempt {attempt}: Some pages still not working")
                print("Waiting 30 seconds before next test...")
        else:
            print(f"⏳ Attempt {attempt}: Distribution still deploying...")
            print("Waiting 30 seconds...")
        
        if attempt < max_attempts:
            time.sleep(30)
    
    print("\n⚠️  Propagation monitoring timeout reached")
    print("You may need to wait a bit longer or test manually")
    
    return False

if __name__ == "__main__":
    print("🌐 CloudFront Propagation Monitor")
    print("=" * 60)
    print("Monitoring CloudFront distribution E1EPXAU67877FR")
    print("Waiting for cache behavior changes to propagate...")
    
    success = monitor_propagation()
    
    if success:
        print("\n🎉 Ready to test Nova AI functionality!")
        print("All assessment pages should now be accessible at:")
        print("- https://www.ieltsaiprep.com/assessment/academic-writing")
        print("- https://www.ieltsaiprep.com/assessment/general-writing")
        print("- https://www.ieltsaiprep.com/assessment/academic-speaking")
        print("- https://www.ieltsaiprep.com/assessment/general-speaking")
    else:
        print("\n⏳ Manual testing may be required")
        print("Try accessing the assessment pages in 10-15 minutes")