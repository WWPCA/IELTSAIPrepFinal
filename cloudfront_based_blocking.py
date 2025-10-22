#!/usr/bin/env python3
"""
CloudFront-based blocking solution for API Gateway direct access
Adds custom header validation in Lambda function to block direct access
"""

import boto3
import json
import uuid
import zipfile
import io
from botocore.exceptions import ClientError

def generate_secret_header():
    """Generate a unique secret header for CloudFront"""
    return f"CF-Secret-{str(uuid.uuid4())[:8]}"

def get_current_lambda_code():
    """Download current Lambda function code"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
        
        # Download code
        import urllib.request
        download_url = response['Code']['Location']
        with urllib.request.urlopen(download_url) as response:
            zip_data = response.read()
        
        # Extract lambda function code
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
            code = zip_ref.read('lambda_function.py').decode('utf-8')
        
        return code
    except Exception as e:
        print(f"Error downloading Lambda code: {e}")
        return None

def modify_lambda_for_blocking(lambda_code, secret_header):
    """Modify Lambda code to block direct access"""
    
    # Find the lambda_handler function start
    handler_start = lambda_code.find('def lambda_handler(event, context):')
    if handler_start == -1:
        return None
    
    # Find the end of the try block start
    try_start = lambda_code.find('try:', handler_start)
    if try_start == -1:
        return None
    
    # Find the line after try:
    after_try = lambda_code.find('\n', try_start) + 1
    
    # Insert blocking logic after try:
    blocking_code = f'''        # Block direct API Gateway access
        headers = event.get('headers', {{}})
        cloudfront_header = headers.get('X-CloudFront-Secret', '')
        
        if cloudfront_header != '{secret_header}':
            print(f"[CLOUDWATCH] Blocking direct access - missing CloudFront header")
            return {{
                'statusCode': 403,
                'headers': {{'Content-Type': 'text/html'}},
                'body': """<!DOCTYPE html>
<html><head><title>Access Denied</title></head>
<body><h1>Access Denied</h1><p>Direct access not allowed.</p></body>
</html>"""
            }}
        
'''
    
    # Insert the blocking code
    modified_code = lambda_code[:after_try] + blocking_code + lambda_code[after_try:]
    
    return modified_code

def update_cloudfront_with_header(secret_header):
    """Update CloudFront distribution to add custom header"""
    cloudfront = boto3.client('cloudfront')
    
    try:
        # Find the distribution for ieltsaiprep.com
        distributions = cloudfront.list_distributions()
        distribution_id = None
        
        for dist in distributions['DistributionList'].get('Items', []):
            aliases = dist.get('Aliases', {}).get('Items', [])
            if 'www.ieltsaiprep.com' in aliases:
                distribution_id = dist['Id']
                break
        
        if not distribution_id:
            print("CloudFront distribution not found")
            return False
        
        # Get current distribution config
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        # Update origin with custom header
        for origin in config['Origins']['Items']:
            if 'n0cpf1rmvc.execute-api.us-east-1.amazonaws.com' in origin['DomainName']:
                # Add custom header
                if 'CustomHeaders' not in origin:
                    origin['CustomHeaders'] = {'Quantity': 0, 'Items': []}
                
                # Add or update the secret header
                header_exists = False
                for header in origin['CustomHeaders']['Items']:
                    if header['HeaderName'] == 'X-CloudFront-Secret':
                        header['HeaderValue'] = secret_header
                        header_exists = True
                        break
                
                if not header_exists:
                    origin['CustomHeaders']['Items'].append({
                        'HeaderName': 'X-CloudFront-Secret',
                        'HeaderValue': secret_header
                    })
                    origin['CustomHeaders']['Quantity'] = len(origin['CustomHeaders']['Items'])
                
                break
        
        # Update distribution
        cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print(f"CloudFront distribution updated with secret header")
        return True
        
    except Exception as e:
        print(f"Error updating CloudFront: {e}")
        return False

def deploy_modified_lambda(modified_code):
    """Deploy modified Lambda function"""
    
    # Create new ZIP package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', modified_code)
    
    zip_buffer.seek(0)
    
    # Update Lambda function
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_buffer.read()
        )
        
        print("Lambda function updated with blocking logic")
        return True
        
    except Exception as e:
        print(f"Error updating Lambda: {e}")
        return False

def test_blocking_implementation():
    """Test both URLs after implementation"""
    import requests
    import time
    
    print("Testing URLs after implementation...")
    
    # Wait for CloudFront to propagate
    print("Waiting 30 seconds for CloudFront propagation...")
    time.sleep(30)
    
    # Test domain (should work)
    try:
        response = requests.get('https://www.ieltsaiprep.com', timeout=10)
        if response.status_code == 200:
            print("✅ www.ieltsaiprep.com - WORKING")
        else:
            print(f"❌ www.ieltsaiprep.com - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ www.ieltsaiprep.com - ERROR: {e}")
    
    # Test direct access (should be blocked)
    try:
        response = requests.get('https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod', timeout=10)
        if response.status_code == 403:
            print("✅ Direct access - BLOCKED (403 Forbidden)")
        else:
            print(f"❌ Direct access - Still accessible (HTTP {response.status_code})")
    except Exception as e:
        print(f"✅ Direct access - BLOCKED (Connection error)")

def main():
    """Main function to implement CloudFront-based blocking"""
    
    print("🔒 CloudFront-Based API Gateway Blocking")
    print("=" * 45)
    
    # Generate secret header
    secret_header = generate_secret_header()
    print(f"Generated secret header: {secret_header}")
    
    # Get current Lambda code
    print("Downloading current Lambda code...")
    lambda_code = get_current_lambda_code()
    if not lambda_code:
        print("❌ Failed to download Lambda code")
        return
    
    # Modify Lambda code for blocking
    print("Modifying Lambda code to block direct access...")
    modified_code = modify_lambda_for_blocking(lambda_code, secret_header)
    if not modified_code:
        print("❌ Failed to modify Lambda code")
        return
    
    # Update CloudFront with secret header
    print("Updating CloudFront distribution...")
    if not update_cloudfront_with_header(secret_header):
        print("❌ Failed to update CloudFront")
        return
    
    # Deploy modified Lambda
    print("Deploying modified Lambda function...")
    if not deploy_modified_lambda(modified_code):
        print("❌ Failed to deploy Lambda")
        return
    
    # Test implementation
    test_blocking_implementation()
    
    # Save configuration
    config = {
        'blocking_method': 'cloudfront_header_validation',
        'secret_header': secret_header,
        'implementation_date': '2025-07-09',
        'purpose': 'Block direct API Gateway access using CloudFront header validation'
    }
    
    with open('cloudfront_blocking_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("📄 Configuration saved to cloudfront_blocking_config.json")
    print("\n🎉 Implementation complete!")
    print("✅ www.ieltsaiprep.com should work normally")
    print("❌ Direct API Gateway access should be blocked")

if __name__ == "__main__":
    main()