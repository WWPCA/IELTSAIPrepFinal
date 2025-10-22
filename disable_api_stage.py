#!/usr/bin/env python3
"""
Disable API Gateway Stage to Block Direct Access
This will disable the /prod stage while keeping CloudFront working
"""

import boto3
import json
from botocore.exceptions import ClientError

def disable_api_gateway_stage():
    """Disable the prod stage"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'n0cpf1rmvc'
    stage_name = 'prod'
    
    try:
        # Delete the stage
        apigateway.delete_stage(
            restApiId=api_id,
            stageName=stage_name
        )
        
        print(f"✅ Stage '{stage_name}' deleted")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NotFoundException':
            print(f"❌ Stage '{stage_name}' not found")
        else:
            print(f"❌ Error deleting stage: {e}")
        return False

def verify_domain_still_works():
    """Verify www.ieltsaiprep.com still works"""
    import requests
    
    try:
        response = requests.get('https://www.ieltsaiprep.com', timeout=10)
        if response.status_code == 200:
            print("✅ www.ieltsaiprep.com - WORKING")
            return True
        else:
            print(f"❌ www.ieltsaiprep.com - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ www.ieltsaiprep.com - ERROR: {e}")
        return False

def verify_direct_blocked():
    """Verify direct access is blocked"""
    import requests
    
    try:
        response = requests.get('https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod', timeout=10)
        if response.status_code == 403:
            print("✅ Direct access - BLOCKED (403 Forbidden)")
            return True
        else:
            print(f"❌ Direct access - Still accessible (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"✅ Direct access - BLOCKED (Connection error: {e})")
        return True

def main():
    print("🚫 DISABLING API GATEWAY STAGE")
    print("=" * 35)
    
    print("This will:")
    print("✅ Keep www.ieltsaiprep.com working (CloudFront)")
    print("❌ DISABLE n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod")
    print()
    
    # Disable stage
    stage_deleted = disable_api_gateway_stage()
    
    if stage_deleted:
        print("\n⏱️  Waiting 5 seconds for changes to take effect...")
        import time
        time.sleep(5)
        
        # Verify both conditions
        domain_works = verify_domain_still_works()
        direct_blocked = verify_direct_blocked()
        
        if domain_works and direct_blocked:
            print("\n🎉 PERFECT SUCCESS!")
            print("✅ www.ieltsaiprep.com - CONFIRMED WORKING")
            print("❌ Direct API Gateway access - CONFIRMED BLOCKED")
            
            # Save configuration
            with open('stage_disabled_config.json', 'w') as f:
                json.dump({
                    'action': 'stage_deleted',
                    'stage_name': 'prod',
                    'implementation_date': '2025-07-09',
                    'purpose': 'Block direct API Gateway access by disabling stage'
                }, f, indent=2)
            
            print("📄 Configuration saved to stage_disabled_config.json")
            
        elif domain_works:
            print("\n⚠️  PARTIAL SUCCESS!")
            print("✅ www.ieltsaiprep.com - WORKING")
            print("❌ Direct access blocking - NEEDS VERIFICATION")
        else:
            print("\n❌ FAILURE!")
            print("❌ Domain may be affected - investigate immediately")
    
    else:
        print("\n❌ FAILED to disable stage")

if __name__ == "__main__":
    main()