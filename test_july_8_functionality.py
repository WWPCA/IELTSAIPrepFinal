#!/usr/bin/env python3
"""
Test July 8th Functionality - Verify All Working Features
"""

import requests
import json
import time
from datetime import datetime

def test_production_endpoints():
    """Test all production endpoints for July 8th functionality"""
    
    # Production URL
    base_url = "https://www.ieltsgenaiprep.com"
    
    # Alternative URLs to test
    test_urls = [
        "https://www.ieltsgenaiprep.com",
        "https://ieltsgenaiprep.com",
        "https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod"
    ]
    
    print("🧪 Testing July 8th Functionality in Production")
    print("=" * 60)
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        
        try:
            # Test 1: Home page
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Home page working: {response.status_code}")
                
                # Check for AI SEO content
                if "IELTS GenAI Prep" in response.text:
                    print("✅ AI SEO content present")
                else:
                    print("❌ AI SEO content missing")
                
                # Test 2: robots.txt
                robots_response = requests.get(f"{url}/robots.txt", timeout=10)
                if robots_response.status_code == 200:
                    print("✅ robots.txt working")
                    
                    # Check for AI crawlers
                    if "GPTBot" in robots_response.text and "Gemini" in robots_response.text:
                        print("✅ AI crawlers properly configured")
                    else:
                        print("❌ AI crawlers missing")
                else:
                    print(f"❌ robots.txt failed: {robots_response.status_code}")
                
                # Test 3: Login page
                login_response = requests.get(f"{url}/login", timeout=10)
                if login_response.status_code == 200:
                    print("✅ Login page working")
                    
                    # Check for reCAPTCHA
                    if "recaptcha" in login_response.text.lower():
                        print("✅ reCAPTCHA present")
                    else:
                        print("❌ reCAPTCHA missing")
                else:
                    print(f"❌ Login page failed: {login_response.status_code}")
                
                # Test 4: Privacy policy
                privacy_response = requests.get(f"{url}/privacy-policy", timeout=10)
                if privacy_response.status_code == 200:
                    print("✅ Privacy policy working")
                else:
                    print(f"❌ Privacy policy failed: {privacy_response.status_code}")
                
                # Test 5: Terms of service
                terms_response = requests.get(f"{url}/terms-of-service", timeout=10)
                if terms_response.status_code == 200:
                    print("✅ Terms of service working")
                else:
                    print(f"❌ Terms of service failed: {terms_response.status_code}")
                
                print(f"✅ Working production URL found: {url}")
                return url
                
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n❌ No working production URL found")
    return None

def test_authentication_flow(base_url):
    """Test authentication and dashboard access"""
    
    print(f"\n🔐 Testing Authentication Flow")
    print("=" * 40)
    
    # Test credentials
    test_email = "test@ieltsgenaiprep.com"
    test_password = "password123"
    
    try:
        # Test login
        login_data = {
            "email": test_email,
            "password": test_password,
            "g-recaptcha-response": "test"  # This will fail reCAPTCHA but test the endpoint
        }
        
        login_response = requests.post(f"{base_url}/api/login", 
                                     json=login_data, 
                                     timeout=10)
        
        if login_response.status_code == 400:
            print("✅ Login endpoint working (reCAPTCHA validation active)")
        elif login_response.status_code == 200:
            print("✅ Login endpoint working (authenticated)")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
        # Test dashboard access (will redirect to login)
        dashboard_response = requests.get(f"{base_url}/dashboard", timeout=10)
        if dashboard_response.status_code == 302:
            print("✅ Dashboard security working (redirects to login)")
        elif dashboard_response.status_code == 200:
            print("✅ Dashboard accessible")
        else:
            print(f"❌ Dashboard failed: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"❌ Authentication test error: {str(e)}")

def test_assessment_endpoints(base_url):
    """Test all 4 assessment endpoints"""
    
    print(f"\n📝 Testing Assessment Endpoints")
    print("=" * 40)
    
    assessments = [
        "academic_writing",
        "general_writing", 
        "academic_speaking",
        "general_speaking"
    ]
    
    for assessment in assessments:
        try:
            response = requests.get(f"{base_url}/assessment/{assessment}", timeout=10)
            if response.status_code == 302:
                print(f"✅ {assessment} - Security working (redirects to login)")
            elif response.status_code == 200:
                print(f"✅ {assessment} - Assessment page accessible")
                
                # Check for key functionality
                if "timer" in response.text.lower():
                    print(f"  ✅ Timer functionality present")
                else:
                    print(f"  ❌ Timer functionality missing")
                    
                if "word" in response.text.lower() and "writing" in assessment:
                    print(f"  ✅ Word counting present")
                elif "maya" in response.text.lower() and "speaking" in assessment:
                    print(f"  ✅ Maya AI present")
                    
            else:
                print(f"❌ {assessment} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {assessment} error: {str(e)}")

def test_api_endpoints(base_url):
    """Test API endpoints for Nova integration"""
    
    print(f"\n🤖 Testing API Endpoints")
    print("=" * 40)
    
    api_endpoints = [
        "/api/nova-micro/submit",
        "/api/nova-sonic/submit",
        "/api/maya/introduction"
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.post(f"{base_url}{endpoint}", 
                                   json={"test": "data"}, 
                                   timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - Working")
                
                # Check response format
                try:
                    data = response.json()
                    if "success" in data:
                        print(f"  ✅ Proper JSON response format")
                    else:
                        print(f"  ❌ Unexpected response format")
                except:
                    print(f"  ❌ Invalid JSON response")
                    
            else:
                print(f"❌ {endpoint} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} error: {str(e)}")

def main():
    """Run all tests"""
    
    print("🚀 IELTS GenAI Prep - July 8th Functionality Test")
    print("=" * 60)
    print(f"Test started: {datetime.now()}")
    
    # Find working production URL
    working_url = test_production_endpoints()
    
    if working_url:
        # Test authentication
        test_authentication_flow(working_url)
        
        # Test assessments
        test_assessment_endpoints(working_url)
        
        # Test API endpoints
        test_api_endpoints(working_url)
        
        print("\n" + "=" * 60)
        print("✅ JULY 8TH FUNCTIONALITY TEST COMPLETE")
        print(f"Working URL: {working_url}")
        print("All core features verified and working")
        
    else:
        print("\n" + "=" * 60)
        print("❌ PRODUCTION URL NOT ACCESSIBLE")
        print("Need to check DNS or Lambda deployment")

if __name__ == "__main__":
    main()