#!/usr/bin/env python3
"""
EMERGENCY: Restore www.ieltsaiprep.com Access
Revert all blocking changes to ensure domain works
"""

import boto3
import json
from botocore.exceptions import ClientError

def restore_domain_access():
    """Restore full access to ensure domain works"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'n0cpf1rmvc'
    
    try:
        # Re-enable execute API endpoint
        apigateway.update_rest_api(
            restApiId=api_id,
            patchOperations=[
                {
                    'op': 'replace',
                    'path': '/disableExecuteApiEndpoint',
                    'value': 'false'
                }
            ]
        )
        print("✅ Execute API endpoint re-enabled")
        
        # Remove resource policy completely
        apigateway.update_rest_api(
            restApiId=api_id,
            patchOperations=[
                {
                    'op': 'remove',
                    'path': '/policy'
                }
            ]
        )
        print("✅ Resource policy removed")
        
        # Recreate prod stage
        apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Emergency restoration deployment'
        )
        print("✅ Prod stage recreated")
        
        return True
        
    except ClientError as e:
        print(f"❌ Error restoring access: {e}")
        return False

def verify_domain_restored():
    """Verify domain is working again"""
    import requests
    
    try:
        response = requests.get('https://www.ieltsaiprep.com', timeout=15)
        if response.status_code == 200:
            print("✅ www.ieltsaiprep.com - RESTORED AND WORKING")
            return True
        else:
            print(f"❌ www.ieltsaiprep.com - Still blocked (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ www.ieltsaiprep.com - Error: {e}")
        return False

def main():
    print("🚨 EMERGENCY DOMAIN RESTORATION")
    print("=" * 40)
    
    print("Restoring www.ieltsaiprep.com access...")
    
    # Restore access
    success = restore_domain_access()
    
    if success:
        print("\n⏱️  Waiting 10 seconds for changes to propagate...")
        import time
        time.sleep(10)
        
        # Verify domain works
        domain_restored = verify_domain_restored()
        
        if domain_restored:
            print("\n🎉 DOMAIN RESTORED!")
            print("✅ www.ieltsaiprep.com - CONFIRMED WORKING")
            print("⚠️  Direct API Gateway access is also restored")
            
            # Save restoration log
            with open('domain_restoration_log.json', 'w') as f:
                json.dump({
                    'action': 'emergency_domain_restoration',
                    'timestamp': '2025-07-09',
                    'changes': [
                        'execute_api_endpoint_enabled',
                        'resource_policy_removed',
                        'prod_stage_recreated'
                    ],
                    'result': 'www.ieltsaiprep.com restored'
                }, f, indent=2)
            
            print("📄 Restoration log saved")
            
        else:
            print("\n❌ DOMAIN STILL BLOCKED!")
            print("Need immediate manual intervention")
    
    else:
        print("\n❌ FAILED TO RESTORE ACCESS")
        print("Manual AWS console intervention required")

if __name__ == "__main__":
    main()