#!/usr/bin/env python3
"""
Disable API Gateway Temporarily
Safer approach - disables the entire API Gateway while preserving configuration
"""

import boto3
from botocore.exceptions import ClientError

def disable_api_gateway():
    """Disable API Gateway by updating its configuration"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'n0cpf1rmvc'
    
    try:
        # Add a resource policy that denies all access
        deny_all_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "execute-api:Invoke",
                    "Resource": f"arn:aws:execute-api:us-east-1:*:{api_id}/*"
                }
            ]
        }
        
        # Apply the deny-all policy
        apigateway.update_rest_api(
            restApiId=api_id,
            patchOps=[
                {
                    'op': 'replace',
                    'path': '/policy',
                    'value': str(deny_all_policy).replace("'", '"')
                }
            ]
        )
        
        print("✅ API Gateway disabled with deny-all policy")
        print("❌ https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod - BLOCKED")
        print("❌ https://www.ieltsaiprep.com - ALSO BLOCKED")
        
        return True
        
    except ClientError as e:
        print(f"❌ Error disabling API Gateway: {e}")
        return False

def main():
    """Main function to disable API Gateway"""
    
    print("🔒 Disabling API Gateway Access")
    print("=" * 35)
    
    print("This will:")
    print("❌ Block https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod")
    print("❌ Also block https://www.ieltsaiprep.com")
    print("⚠️  Both URLs will return 403 Forbidden")
    print()
    
    confirm = input("Proceed? (y/N): ")
    
    if confirm.lower() != 'y':
        print("❌ Operation cancelled")
        return
    
    success = disable_api_gateway()
    
    if success:
        print("\n🎉 API GATEWAY DISABLED!")
        print("❌ Both URLs are now blocked")
        print("\n💡 To re-enable, remove the resource policy")
    else:
        print("\n❌ FAILED TO DISABLE")

if __name__ == "__main__":
    main()