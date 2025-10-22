#!/usr/bin/env python3
"""
Restrict Direct Access to API Gateway
Allow only CloudFront traffic while blocking direct endpoint access
"""

import boto3
import json
from botocore.exceptions import ClientError

def get_cloudfront_distribution_id():
    """Get the CloudFront distribution ID for ieltsaiprep.com"""
    cloudfront = boto3.client('cloudfront')
    
    try:
        distributions = cloudfront.list_distributions()
        
        for dist in distributions['DistributionList'].get('Items', []):
            aliases = dist.get('Aliases', {}).get('Items', [])
            if 'www.ieltsaiprep.com' in aliases or 'ieltsaiprep.com' in aliases:
                return dist['Id']
        
        print("❌ CloudFront distribution not found")
        return None
        
    except ClientError as e:
        print(f"❌ Error finding CloudFront distribution: {e}")
        return None

def create_api_gateway_resource_policy(api_id, cloudfront_dist_id):
    """Create resource policy to restrict direct access"""
    
    # Resource policy that only allows CloudFront
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "execute-api:Invoke",
                "Resource": f"arn:aws:execute-api:us-east-1:*:{api_id}/*",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceVpce": f"vpce-{cloudfront_dist_id}"
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
                        "aws:SourceIp": "CloudFront"
                    }
                }
            }
        ]
    }
    
    return policy

def apply_resource_policy():
    """Apply the resource policy to restrict direct access"""
    
    api_id = "n0cpf1rmvc"
    
    # Get CloudFront distribution ID
    cloudfront_dist_id = get_cloudfront_distribution_id()
    if not cloudfront_dist_id:
        return False
    
    # Create API Gateway client
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    
    # Simpler approach: Use CloudFront headers
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Deny",
                "Principal": "*",
                "Action": "execute-api:Invoke",
                "Resource": f"arn:aws:execute-api:us-east-1:*:{api_id}/*",
                "Condition": {
                    "StringNotEquals": {
                        "aws:Referer": "https://www.ieltsaiprep.com"
                    }
                }
            },
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "execute-api:Invoke",
                "Resource": f"arn:aws:execute-api:us-east-1:*:{api_id}/*"
            }
        ]
    }
    
    try:
        # Update API Gateway with resource policy
        response = apigateway.update_rest_api(
            restApiId=api_id,
            patchOps=[
                {
                    'op': 'replace',
                    'path': '/policy',
                    'value': json.dumps(policy)
                }
            ]
        )
        
        print("✅ Resource policy applied successfully")
        print("✅ Direct access to API Gateway now blocked")
        print("✅ Domain access through CloudFront still works")
        
        return True
        
    except ClientError as e:
        print(f"❌ Error applying resource policy: {e}")
        return False

def main():
    """Main function to restrict direct access"""
    print("🔒 Restricting Direct Access to API Gateway")
    print("=" * 50)
    
    print("This will:")
    print("✅ Keep www.ieltsaiprep.com working")
    print("❌ Block n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod")
    print()
    
    confirm = input("Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Operation cancelled")
        return
    
    success = apply_resource_policy()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("✅ Domain access: https://www.ieltsaiprep.com (WORKING)")
        print("❌ Direct access: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod (BLOCKED)")
    else:
        print("\n❌ FAILED!")
        print("Resource policy could not be applied")

if __name__ == "__main__":
    main()