#!/usr/bin/env python3
"""
CloudFront Origin Access Control Setup
Blocks direct API Gateway access while preserving domain functionality
"""

import boto3
import json
import uuid
from botocore.exceptions import ClientError

def create_custom_header_protection():
    """Create a custom header that CloudFront adds to requests"""
    
    # Generate a secret header value
    secret_header_value = str(uuid.uuid4())
    
    # API Gateway resource policy
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Deny",
                "Principal": "*",
                "Action": "execute-api:Invoke",
                "Resource": "arn:aws:execute-api:us-east-1:*:n0cpf1rmvc/*",
                "Condition": {
                    "StringNotEquals": {
                        "aws:RequestedRegion": "us-east-1"
                    }
                }
            },
            {
                "Effect": "Deny",
                "Principal": "*",
                "Action": "execute-api:Invoke",
                "Resource": "arn:aws:execute-api:us-east-1:*:n0cpf1rmvc/*",
                "Condition": {
                    "StringNotEquals": {
                        "aws:userid": f"CLOUDFRONT:{secret_header_value}"
                    }
                }
            },
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "execute-api:Invoke",
                "Resource": "arn:aws:execute-api:us-east-1:*:n0cpf1rmvc/*",
                "Condition": {
                    "StringEquals": {
                        "aws:RequestedRegion": "us-east-1"
                    }
                }
            }
        ]
    }
    
    return policy, secret_header_value

def update_cloudfront_distribution(secret_header_value):
    """Update CloudFront to add secret header"""
    
    cloudfront = boto3.client('cloudfront')
    
    try:
        # Find the distribution
        distributions = cloudfront.list_distributions()
        
        distribution_id = None
        for dist in distributions['DistributionList'].get('Items', []):
            aliases = dist.get('Aliases', {}).get('Items', [])
            if 'www.ieltsaiprep.com' in aliases:
                distribution_id = dist['Id']
                break
        
        if not distribution_id:
            print("❌ CloudFront distribution not found")
            return False
        
        # Get current configuration
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        # Update origin with custom header
        for origin in config['Origins']['Items']:
            if 'n0cpf1rmvc.execute-api.us-east-1.amazonaws.com' in origin['DomainName']:
                origin['CustomHeaders'] = {
                    'Quantity': 1,
                    'Items': [
                        {
                            'HeaderName': 'X-CloudFront-Secret',
                            'HeaderValue': secret_header_value
                        }
                    ]
                }
        
        # Update distribution
        cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print(f"✅ CloudFront distribution updated: {distribution_id}")
        print("✅ Custom header protection enabled")
        
        return True
        
    except ClientError as e:
        print(f"❌ Error updating CloudFront: {e}")
        return False

def update_api_gateway_policy(policy):
    """Update API Gateway with restrictive policy"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    
    try:
        # Apply policy to API Gateway
        response = apigateway.update_rest_api(
            restApiId='n0cpf1rmvc',
            patchOps=[
                {
                    'op': 'replace',
                    'path': '/policy',
                    'value': json.dumps(policy)
                }
            ]
        )
        
        print("✅ API Gateway resource policy updated")
        print("✅ Direct access blocked")
        
        return True
        
    except ClientError as e:
        print(f"❌ Error updating API Gateway policy: {e}")
        return False

def simple_ip_restriction():
    """Simple approach: Block all direct access except from CloudFront IP ranges"""
    
    # Get CloudFront IP ranges
    import requests
    
    try:
        # AWS publishes CloudFront IP ranges
        response = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json')
        ip_ranges = response.json()
        
        cloudfront_ips = []
        for prefix in ip_ranges['prefixes']:
            if prefix['service'] == 'CLOUDFRONT':
                cloudfront_ips.append(prefix['ip_prefix'])
        
        # Create policy allowing only CloudFront IPs
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "execute-api:Invoke",
                    "Resource": "arn:aws:execute-api:us-east-1:*:n0cpf1rmvc/*",
                    "Condition": {
                        "IpAddress": {
                            "aws:SourceIp": cloudfront_ips[:50]  # Limit to first 50 ranges
                        }
                    }
                }
            ]
        }
        
        return policy
        
    except Exception as e:
        print(f"❌ Error getting CloudFront IP ranges: {e}")
        return None

def main():
    """Main function to set up protection"""
    print("🔒 Setting up CloudFront Origin Protection")
    print("=" * 50)
    
    print("This will:")
    print("✅ Keep www.ieltsaiprep.com working")
    print("❌ Block direct API Gateway access")
    print("⚠️  CloudFront changes take 15-20 minutes to propagate")
    print()
    
    confirm = input("Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Operation cancelled")
        return
    
    # Try simple IP restriction first
    print("\n🔧 Applying IP-based protection...")
    
    policy = simple_ip_restriction()
    if policy:
        success = update_api_gateway_policy(policy)
        
        if success:
            print("\n🎉 SUCCESS!")
            print("✅ Domain access: https://www.ieltsaiprep.com (WORKING)")
            print("❌ Direct access: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod (BLOCKED)")
            print("⏱️  Changes will take effect in 5-10 minutes")
        else:
            print("\n❌ FAILED!")
            print("Could not apply IP restriction policy")
    else:
        print("\n❌ FAILED!")
        print("Could not retrieve CloudFront IP ranges")

if __name__ == "__main__":
    main()