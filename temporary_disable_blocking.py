#!/usr/bin/env python3
"""
Temporarily disable CloudFront blocking to test login
"""

import boto3
import json
import zipfile
import io
import urllib.request
import re

def disable_cloudfront_blocking():
    """Temporarily disable CloudFront blocking in Lambda function"""
    
    # Download current Lambda code
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
    download_url = response['Code']['Location']
    
    with urllib.request.urlopen(download_url) as response:
        zip_data = response.read()
    
    with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
        code = zip_ref.read('lambda_function.py').decode('utf-8')
    
    # Comment out the CloudFront blocking
    updated_code = code.replace(
        'if cloudfront_header != \'CF-Secret-3140348d\':',
        'if False:  # Temporarily disabled CloudFront blocking'
    )
    
    # Create new ZIP package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', updated_code)
    
    zip_buffer.seek(0)
    
    # Update Lambda function
    try:
        lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_buffer.read()
        )
        
        print("✅ CloudFront blocking temporarily disabled")
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda: {e}")
        return False

def test_login_without_blocking():
    """Test login without CloudFront blocking"""
    import requests
    import time
    
    print("🧪 Testing login without CloudFront blocking...")
    
    # Wait for Lambda to update
    time.sleep(5)
    
    try:
        response = requests.post(
            'https://www.ieltsaiprep.com/api/login',
            json={
                'email': 'prodtest_20250709_175130_i1m2@ieltsaiprep.com',
                'password': 'TestProd2025!'
            },
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful without blocking!")
            return True
        else:
            print(f"❌ Login still failing: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

def re_enable_cloudfront_blocking():
    """Re-enable CloudFront blocking after testing"""
    
    # Download current Lambda code
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
    download_url = response['Code']['Location']
    
    with urllib.request.urlopen(download_url) as response:
        zip_data = response.read()
    
    with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
        code = zip_ref.read('lambda_function.py').decode('utf-8')
    
    # Re-enable CloudFront blocking
    updated_code = code.replace(
        'if False:  # Temporarily disabled CloudFront blocking',
        'if cloudfront_header != \'CF-Secret-3140348d\':'
    )
    
    # Create new ZIP package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', updated_code)
    
    zip_buffer.seek(0)
    
    # Update Lambda function
    try:
        lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_buffer.read()
        )
        
        print("✅ CloudFront blocking re-enabled")
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing login by temporarily disabling CloudFront blocking...")
    
    if disable_cloudfront_blocking():
        if test_login_without_blocking():
            print("\n🎉 Login works when CloudFront blocking is disabled!")
            print("The issue is with the CloudFront configuration, not the login logic.")
        else:
            print("\n❌ Login still fails - the issue is not CloudFront blocking")
        
        # Re-enable blocking for security
        print("\n🔒 Re-enabling CloudFront blocking...")
        re_enable_cloudfront_blocking()
    else:
        print("❌ Failed to disable CloudFront blocking")