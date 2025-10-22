#!/usr/bin/env python3
"""
Disable Execute API Endpoint Completely
This will disable the execute-api endpoint entirely while keeping CloudFront working
"""

import boto3
import json
from botocore.exceptions import ClientError

def disable_execute_api_endpoint():
    """Disable the execute-api endpoint"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'n0cpf1rmvc'
    
    try:
        # Update API Gateway to disable execute-api endpoint
        apigateway.update_rest_api(
            restApiId=api_id,
            patchOperations=[
                {
                    'op': 'replace',
                    'path': '/disableExecuteApiEndpoint',
                    'value': 'true'
                }
            ]
        )
        
        print("✅ Execute API endpoint disabled")
        return True
        
    except ClientError as e:
        print(f"❌ Error disabling endpoint: {e}")
        return False

def verify_complete_block():
    """Verify both conditions"""
    import requests
    
    print("\nVerifying results...")
    
    # Check domain
    try:
        response = requests.get('https://www.ieltsaiprep.com', timeout=10)
        if response.status_code == 200:
            print("✅ www.ieltsaiprep.com - WORKING")
            domain_ok = True
        else:
            print(f"❌ www.ieltsaiprep.com - HTTP {response.status_code}")
            domain_ok = False
    except Exception as e:
        print(f"❌ www.ieltsaiprep.com - ERROR: {e}")
        domain_ok = False
    
    # Check direct access
    try:
        response = requests.get('https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod', timeout=10)
        if response.status_code == 403:
            print("✅ Direct access - BLOCKED (403 Forbidden)")
            direct_blocked = True
        else:
            print(f"❌ Direct access - Still accessible (HTTP {response.status_code})")
            direct_blocked = False
    except Exception as e:
        print(f"✅ Direct access - BLOCKED (Connection error)")
        direct_blocked = True
    
    return domain_ok, direct_blocked

def main():
    print("🚫 DISABLING EXECUTE API ENDPOINT")
    print("=" * 40)
    
    print("This will:")
    print("✅ Keep www.ieltsaiprep.com working (CloudFront)")
    print("❌ COMPLETELY DISABLE n0cpf1rmvc.execute-api.us-east-1.amazonaws.com")
    print()
    
    # Disable endpoint
    success = disable_execute_api_endpoint()
    
    if success:
        print("\n⏱️  Waiting 10 seconds for changes to propagate...")
        import time
        time.sleep(10)
        
        # Verify results
        domain_ok, direct_blocked = verify_complete_block()
        
        if domain_ok and direct_blocked:
            print("\n🎉 PERFECT SUCCESS!")
            print("✅ www.ieltsaiprep.com - CONFIRMED WORKING")
            print("❌ Direct API Gateway access - COMPLETELY BLOCKED")
            
            # Save configuration
            with open('execute_api_disabled.json', 'w') as f:
                json.dump({
                    'action': 'execute_api_endpoint_disabled',
                    'api_id': 'n0cpf1rmvc',
                    'implementation_date': '2025-07-09',
                    'purpose': 'Completely disable direct API Gateway access'
                }, f, indent=2)
            
            print("📄 Configuration saved to execute_api_disabled.json")
            
        elif domain_ok:
            print("\n⚠️  PARTIAL SUCCESS!")
            print("✅ www.ieltsaiprep.com - WORKING")
            print("❌ Direct access may still be accessible")
            
        else:
            print("\n❌ CRITICAL FAILURE!")
            print("❌ Domain may be affected - need immediate attention")
    
    else:
        print("\n❌ FAILED to disable execute API endpoint")

if __name__ == "__main__":
    main()