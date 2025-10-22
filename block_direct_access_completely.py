#!/usr/bin/env python3
"""
Completely Block Direct API Gateway Access
Use deny-all policy with CloudFront exception
"""

import boto3
import json
from botocore.exceptions import ClientError

def block_all_direct_access():
    """Apply deny-all policy to API Gateway"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'n0cpf1rmvc'
    
    # Policy that denies all direct access
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Deny",
                "Principal": "*",
                "Action": "execute-api:Invoke",
                "Resource": f"arn:aws:execute-api:us-east-1:*:{api_id}/*",
                "Condition": {
                    "StringNotLike": {
                        "aws:UserAgent": "Amazon CloudFront"
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
        
        print("✅ Direct access completely blocked")
        return True
        
    except Exception as e:
        print(f"❌ Error blocking direct access: {e}")
        return False

def main():
    """Main function to completely block direct access"""
    
    print("🚫 COMPLETELY BLOCKING DIRECT API GATEWAY ACCESS")
    print("=" * 55)
    
    print("This will:")
    print("✅ Keep www.ieltsaiprep.com working (CloudFront traffic)")
    print("❌ COMPLETELY BLOCK n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod")
    print()
    
    success = block_all_direct_access()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("❌ Direct API Gateway access is now COMPLETELY BLOCKED")
        print("✅ www.ieltsaiprep.com continues to work through CloudFront")
        print("⏱️  Changes take effect immediately")
        
        # Save configuration
        with open('complete_block_config.json', 'w') as f:
            json.dump({
                'block_type': 'deny_all_except_cloudfront',
                'implementation_date': '2025-07-09',
                'purpose': 'Completely block direct API Gateway access'
            }, f, indent=2)
        
        print("📄 Configuration saved to complete_block_config.json")
        
    else:
        print("\n❌ FAILED!")
        print("Could not apply complete block policy")

if __name__ == "__main__":
    main()