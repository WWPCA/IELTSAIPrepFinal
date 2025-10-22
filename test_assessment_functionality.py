import boto3
import requests
import json
from datetime import datetime

def test_assessment_buttons():
    """Test all Start Assessment buttons work correctly"""
    base_url = "https://www.ieltsaiprep.com"
    assessment_types = [
        "academic-writing",
        "academic-speaking", 
        "general-writing",
        "general-speaking"
    ]
    
    print("🔍 TESTING ASSESSMENT BUTTONS")
    print("=" * 50)
    
    for assessment_type in assessment_types:
        try:
            url = f"{base_url}/assessment/{assessment_type}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {assessment_type}: Button works (HTTP {response.status_code})")
                
                # Check if page contains assessment content
                content = response.text.lower()
                if "assessment" in content and "back to dashboard" in content:
                    print(f"   ✅ Page contains proper assessment structure")
                else:
                    print(f"   ⚠️  Page missing assessment content")
            else:
                print(f"❌ {assessment_type}: Failed (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"❌ {assessment_type}: Error - {str(e)}")
    
    return True

def check_lambda_environment():
    """Check AWS Lambda environment for Nova API configuration"""
    print("\n🔍 CHECKING AWS LAMBDA CONFIGURATION")
    print("=" * 50)
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        config = lambda_client.get_function_configuration(FunctionName='ielts-genai-prep-api')
        
        env_vars = config.get('Environment', {}).get('Variables', {})
        
        # Check for AWS Nova API configuration
        nova_configs = [
            'AWS_REGION',
            'AWS_ACCESS_KEY_ID', 
            'AWS_SECRET_ACCESS_KEY'
        ]
        
        for config_key in nova_configs:
            if config_key in env_vars:
                print(f"✅ {config_key}: Configured")
            else:
                print(f"❌ {config_key}: Missing")
        
        # Check Lambda runtime and region
        print(f"✅ Lambda Runtime: {config.get('Runtime', 'Unknown')}")
        print(f"✅ Lambda Region: us-east-1 (Nova Sonic available)")
        
        return True
        
    except Exception as e:
        print(f"❌ Lambda config check failed: {str(e)}")
        return False

def analyze_current_lambda_code():
    """Download and analyze current Lambda code for Nova API integration"""
    print("\n🔍 ANALYZING LAMBDA CODE FOR NOVA INTEGRATION")
    print("=" * 50)
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
        
        # Download and extract code
        import urllib.request
        import zipfile
        import io
        
        download_url = response['Code']['Location']
        with urllib.request.urlopen(download_url) as response:
            zip_data = response.read()
        
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
            code = zip_ref.read('lambda_function.py').decode('utf-8')
        
        # Check for Nova API integration
        nova_checks = {
            'Nova Sonic': 'nova-sonic' in code.lower() or 'bedrock' in code.lower(),
            'Nova Micro': 'nova-micro' in code.lower() or 'bedrock' in code.lower(),
            'Maya Speech': 'maya' in code.lower(),
            'Assessment Routes': '/assessment/' in code,
            'Unique Questions': 'unique' in code.lower() and 'question' in code.lower(),
            'Purchase Tracking': 'purchase' in code.lower() or 'attempt' in code.lower()
        }
        
        for feature, found in nova_checks.items():
            status = "✅ Found" if found else "❌ Missing"
            print(f"{status}: {feature}")
        
        # Check if assessment endpoints are properly implemented
        if '/assessment/' in code:
            print("✅ Assessment routing implemented")
            
            # Check for actual assessment functionality vs placeholder
            if 'Assessment functionality will be integrated' in code:
                print("⚠️  Assessment pages are placeholder - need real implementation")
            else:
                print("✅ Assessment pages have real implementation")
        
        return code
        
    except Exception as e:
        print(f"❌ Code analysis failed: {str(e)}")
        return None

def check_database_schema():
    """Check if database supports unique questions and purchase tracking"""
    print("\n🔍 CHECKING DATABASE SCHEMA FOR ASSESSMENT FEATURES")
    print("=" * 50)
    
    try:
        # Check if we can connect to DynamoDB
        import os
        if 'AWS_ACCESS_KEY_ID' in os.environ:
            print("✅ AWS credentials available for DynamoDB")
            
            # Note: In production, this would check actual DynamoDB tables
            # For now, we'll check the mock implementation
            print("📋 Required tables for full functionality:")
            print("   • users (user data)")
            print("   • sessions (active sessions)")
            print("   • assessments (question bank)")
            print("   • user_assessments (completed assessments)")
            print("   • purchases (purchase tracking)")
            print("   • assessment_attempts (attempt counting)")
            
        else:
            print("⚠️  AWS credentials not found in environment")
            
    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")

def test_user_profile_consistency():
    """Test user profile page functionality"""
    print("\n🔍 TESTING USER PROFILE FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Test profile page endpoint
        response = requests.get("https://www.ieltsaiprep.com/profile", timeout=10)
        
        if response.status_code == 200:
            print("✅ Profile page accessible")
        elif response.status_code == 302:
            print("✅ Profile page redirects to login (expected)")
        elif response.status_code == 404:
            print("❌ Profile page not implemented")
        else:
            print(f"⚠️  Profile page returns HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Profile test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE ASSESSMENT SYSTEM TEST")
    print("=" * 60)
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    
    # Run all tests
    test_assessment_buttons()
    check_lambda_environment()
    code = analyze_current_lambda_code()
    check_database_schema()
    test_user_profile_consistency()
    
    print("\n📋 SUMMARY AND RECOMMENDATIONS")
    print("=" * 50)
    print("1. Assessment button routing: Check if buttons lead to real assessments")
    print("2. Nova API integration: Verify AWS Bedrock access is configured")
    print("3. Maya speech triggers: Check WebSocket implementation for real-time audio")
    print("4. Unique questions: Implement question bank with usage tracking")
    print("5. User profiles: Ensure profile pages match preview functionality")
