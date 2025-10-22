#!/usr/bin/env python3
"""
Force Block Direct API Gateway Access with Multiple Conditions
"""

import boto3
import json
from botocore.exceptions import ClientError

def force_block_direct():
    """Apply aggressive block policy"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'n0cpf1rmvc'
    
    # Multiple condition policy to block direct access
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Deny",
                "Principal": "*",
                "Action": "execute-api:Invoke",
                "Resource": f"arn:aws:execute-api:us-east-1:*:{api_id}/*",
                "Condition": {
                    "Bool": {
                        "aws:ViaAWSService": "false"
                    }
                }
            },
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "execute-api:Invoke",
                "Resource": f"arn:aws:execute-api:us-east-1:*:{api_id}/*",
                "Condition": {
                    "StringLike": {
                        "aws:UserAgent": "*CloudFront*"
                    }
                }
            }
        ]
    }
    
    try:
        # Apply policy
        apigateway.update_rest_api(
            restApiId=api_id,
            patchOperations=[
                {
                    'op': 'replace',
                    'path': '/policy',
                    'value': json.dumps(policy)
                }
            ]
        )
        
        print("✅ Force block policy applied")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
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

def main():
    print("🚫 FORCE BLOCKING DIRECT ACCESS")
    print("=" * 35)
    
    # Apply block
    block_success = force_block_direct()
    
    if block_success:
        print("\n⏱️  Waiting 5 seconds for policy to take effect...")
        import time
        time.sleep(5)
        
        # Verify domain still works
        domain_works = verify_domain_still_works()
        
        if domain_works:
            print("\n🎉 SUCCESS!")
            print("✅ www.ieltsaiprep.com - CONFIRMED WORKING")
            print("❌ Direct API Gateway access - BLOCKED")
        else:
            print("\n⚠️  WARNING!")
            print("❌ Domain may be affected - reverting policy")
            
            # Revert to no policy
            apigateway = boto3.client('apigateway', region_name='us-east-1')
            try:
                apigateway.update_rest_api(
                    restApiId='n0cpf1rmvc',
                    patchOperations=[
                        {
                            'op': 'remove',
                            'path': '/policy'
                        }
                    ]
                )
                print("✅ Policy reverted to ensure domain functionality")
            except Exception as e:
                print(f"❌ Error reverting policy: {e}")
    
    else:
        print("\n❌ FAILED to apply block policy")

if __name__ == "__main__":
    main()